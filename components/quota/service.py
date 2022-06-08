#!/usr/bin/env python3
import configparser
import os
import logging
import time
import json
import threading
import subprocess
from mpdclient import mpdClient
from iface_srv import quota_if_server
from RPi import GPIO

PLAYOUT = '/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh'  # regular phoniebox playout skript
AUDFOLDER = '/home/pi/RPi-Jukebox-RFID/components/quota/audiomsg/' # folder where mp3 files with the quota service's farewell messages reside
WDOG_TIME = 10.0 # Every n seconds the watchdog queue will check for elapsed (LED or shutdown) timeouts
GRACETIME = 20 # If no quota is left right from startup, this grants n seconds gracetime to unlock more quota e.g. using RFID or web interface.
MAX_TITWAIT = 5400 # maximum time (in seconds) that we will wait for the current title to finish until shutdown is enforced

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def checkAndParseJson(str):
    try:
        j = json.loads(str)
        return j
    except json.decoder.JSONDecodeError:
        return None

def isValidGpio(i):
    if i in range(2, 32): # 32 is exclusive, so 2-31 are valid
        return True
    return False
    
def getTimeSec(mode):
    floatsecs = 0.0
    if mode == 'epoch':
        floatsecs = time.time()
    elif mode == 'uptime':
        with open('/proc/uptime', 'r') as f:
            floatsecs = float(f.readline().split()[0])
    return int(round(floatsecs))

class title_watchdog:

    def __init__(self, timeout, logger=None):
        self.mpd = None
        self.tit = None
        self.logger = logger
        self.timeout = timeout
        self.enddate = 0
        self.log('title watchdog started')

    def log(self, str):
        if self.logger is not None:
            self.logger.info(str)

    def abort(self):
        if self.mpd is not None:
            self.mpd.disconnect()
            self.mpd = None

    def isFinished(self):
        # Initialize connection to mpd (if not done before)
        if self.mpd is None:
            self.mpd = mpdClient("localhost", logger=self.logger)
            if not self.mpd.connect():
                self.mpd = None
                return True

        # Check if a title is playing
        is_playing = self.mpd.is_playing()
        if is_playing > 0:
            # Get the current title
            title_str = self.mpd.get_title()
            if len(title_str) > 0:
                now_ut = getTimeSec('uptime')
                # Remember the title, if not done before
                if self.tit is None:
                    self.tit=title_str
                    self.enddate = now_ut+self.timeout
                    self.log('Waiting for title to finish: {} (timeout: {} seconds)'.format(title_str, self.timeout))
                    return False
                # Otherwise, compare it to the remembered one
                else:
                    if title_str == self.tit and now_ut < self.enddate:
                        self.log('Still playing {}...'.format(title_str))
                        return False
                    if title_str != self.tit:
                        self.log('Title {} is now finished.'.format(self.tit))
                    else:
                        self.log('Timeout exceeded...')
            else:
                self.log('Reading title from mpd failed')
        else:
            self.log('mpd not playing')
        self.mpd.disconnect()
        self.mpd = None
        return True

class quota_service:

    def __init__(self, config_path, logger=None):
        GPIO.setmode(GPIO.BCM)
        self.svccancel = False
        self.leds = []
        self.config_path = config_path
        self.config = None
        self.expirytime = 0
        self.extinguishtimes = []
        self.logger = logger
        self.tit_wd = None
        self.asyncstartat = 0
        self.is_synced = False
        self.customquota_since_boot = False
        self.force_immediate_shutdown = False
        self.loadConfig()

    def isSynced(self):
        if self.is_synced:
            return True;
        self.is_synced = os.path.exists('/run/systemd/timesync/synchronized')
        return self.is_synced
    
    def checkConfigInt(self, sect, key, vmin, vmax):
        try:
            c = self.config.getint(sect, key)
        except Exception as ex:
            return False
        if vmin is not None and c < vmin:
            return False
        if vmax is not None and c > vmax:
            return False
        return True

    def checkConfigFloat(self, sect, key, vmin, vmax):
        try:
            c = self.config.getfloat(sect, key)
        except Exception as ex:
            return False
        if vmin is not None and c < vmin:
            return False
        if vmax is not None and c > vmax:
            return False
        return True

    def checkConfigBool(self, sect, key):
        try:
            c = self.config.getboolean(sect, key)
        except Exception as ex:
            return False
        return True

    def checkConfig(self):
        if not self.checkConfigInt('QuotaConfig', 'default_quota', 1, None):
            return 'default_quota'
        if not self.checkConfigInt('QuotaConfig', 'reset_time', 0, None):
            return 'reset_time'
        if not self.checkConfigBool('QuotaConfig', 'quota_via_webif'):
            return 'quota_via_webif'
        if not self.checkConfigInt('LedConfig', 'led_duration', 0, None):
            return 'led_duration'
        if not self.checkConfigFloat('LedConfig', 'led_animation', 0.0, None):
            return 'led_animation'
        if not self.checkConfigInt('QuotaState', 'last_granttime', 0, None):
            return 'last_granttime'

        cfg_wm = self.config.get("QuotaConfig","shutdown_waitmode").lower()
        if cfg_wm != 'aftertrk' and cfg_wm != 'instant':
            return 'shutdown_waitmode'

        cfg_af = self.config.get('QuotaConfig', 'audiomsgfile')
        if cfg_af is None or not os.path.isfile(AUDFOLDER + cfg_af):
            return 'audiomsgfile'

        cfg_lg = self.config.get("LedConfig","led_gpios")
        js = checkAndParseJson(cfg_lg)
        if js is None or not isinstance(js, list):
            return 'led_gpios'
        for i in range(0, len(js)):
            if not isValidGpio(js[i]):
                return 'led_gpios'
        return None

    def loadConfig(self):
        if self.config is None:
            self.config = configparser.ConfigParser(inline_comment_prefixes=";")
        parsed = self.config.read(self.config_path)
        if(len(parsed)!=1):
            raise SyntaxError("Parsing failed")
        err_opt = self.checkConfig()
        if err_opt is not None:
            raise SyntaxError('Found invalid ini value for "{}"'.format(err_opt))

    def saveConfig(self):
        with open(self.config_path, 'w') as inifile:
            self.config.write(inifile)
            inifile.close()

    def isTimerActive(self):
        return self.expirytime > 0

    def log(self, str):
        if self.logger is not None:
            self.logger.info(str)

    def new_grant(self, now_ep):
        self.config.set('QuotaState', 'last_granttime', str(now_ep))
        self.saveConfig()
        self.log('last_granttime <= {} ({})'.format(now_ep, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now_ep))))

    def getRemainingMinutes(self):
        if self.isTimerActive():
            now = getTimeSec('uptime')
            left = int(round((self.expirytime-now)/60))
            return max(0, left)
        return -1

    def getStartingGrant(self, now_ep):
        """
        Calculates the starting grant (default grant minus recently consumed quota), in remaining seconds
        """
        cfg_dq = self.config.getint('QuotaConfig', 'default_quota')
        cfg_rt = self.config.getint('QuotaConfig', 'reset_time')
        cfg_lgt = min(self.config.getint('QuotaState', 'last_granttime'), now_ep)

        # self.log('last_granttime => {} ({})'.format(cfg_lgt, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(cfg_lgt)))))

        # 1.) Ermittele aktuellen Kontingentverbrauch (ggf. vor Reboot der Box)
        consumed = now_ep - cfg_lgt  # consumed quota in seconds
        if consumed >= (60*cfg_rt):  # if the consumed quota is older than reset_time, this is OK as well. We'll grant new default quota
            return 60*cfg_dq

        # 2.) Calculate how much quota may be granted this time
        remaining = (60*cfg_dq) - consumed        # remaining quota is default quota minus consumed quota
        if remaining <= 0:
            return 0

        return remaining

    def initLeds(self):
        l = checkAndParseJson(self.config.get("LedConfig","led_gpios"))
        if l is not None and isinstance(l, list):
            self.leds = l
            for i in range(0, len(self.leds)):
                self.log('Init GPIO {}...'.format(self.leds[i]))
                GPIO.setup(self.leds[i], GPIO.OUT)
                GPIO.output(self.leds[i], GPIO.LOW)
        else:
            self.leds = []

    def ledrow_on(self, n_leds, anitime = 0.0):
        cnt = min(n_leds, len(self.leds))

        for i in range(0, cnt):
            GPIO.output(self.leds[i], GPIO.HIGH)
            self.log('Switch LED {}({}) on'.format(i+1,self.leds[i]))
            if i < (cnt-1) and anitime > 0.0:
                time.sleep(anitime)
        return

    def ledrow_off(self, anitime = 0.0):
        cnt = len(self.leds)

        for i in range(0, cnt):
            GPIO.output(self.leds[(cnt-1)-i], GPIO.LOW)
            if i < (cnt-1) and anitime > 0.0:
                time.sleep(anitime)
        return

    def newTimer(self, dur_s_in, auto = False):
        dur_s = None
        now_ut = getTimeSec('uptime')
        dq = self.config.getint('QuotaConfig', 'default_quota')

        # First, cancel active timers
        if self.isTimerActive():
            self.cancelTimer()
            time.sleep(1.0)

        # If it's a user-defined quota grant, take this explicit quota
        if not auto:
            self.log('Registered custom quota event ({} min)'.format(round(dur_s_in/60,2)))
            self.customquota_since_boot = True
            dur_s = dur_s_in
        # Otherwise grant system-determined quota
        else:
            # If phoniebox does not have synced time yet or stands in an offline area, always grant default quota
            if not self.isSynced():
                self.log('Starting with unsynced time - we will try to fix this later...')
                self.asyncstartat = now_ut
                dur_s = 60 * dq
            # Otherwise determine starting grant according to current config file
            else:
                self.asyncstartat = 0
                now_ep = getTimeSec('epoch')
                dur_s = self.getStartingGrant(now_ep)
                if dur_s < GRACETIME:
                    dur_s = GRACETIME
                    self.force_immediate_shutdown = True
                    self.log('too little quota for a new reboot, shutting down...')

                elif(dur_s >= (60*dq)):
                    self.log('last grant is old enough, granting fresh quota...')
                    self.new_grant(now_ep)
                else:
                    self.log('found {} remaining minutes of previous quota...'.format(dur_s/60))

        # Setup expiration timer
        self.expirytime = now_ut+dur_s
        self.log('Expiration planned for {}, now is {}.'.format(self.expirytime, now_ut))

        # Setup LED timers 
        self.extinguishtimes = []
        cfg_ld = self.config.getint("LedConfig",'led_duration')
        n_leds = min(int(round(dur_s/(60*cfg_ld))), len(self.leds))
        if n_leds>0:
            self.log('Switch on up to {} LEDs.'.format(n_leds))
            self.ledrow_on(n_leds,self.config.getfloat("LedConfig","led_animation")) # LEDs on (animated)
            for i in range(0, n_leds):
                j = (n_leds-1) - i
                entry = [j, self.expirytime - (j+1)*(60*cfg_ld)]
                self.extinguishtimes.append(entry) # program switch-off times
            self.log('LED extinguish times are {}.'.format(self.extinguishtimes))

    def adjustTimer(self, diff, minexpiry = 0):
        for i in range(0, len(self.extinguishtimes)):
            self.extinguishtimes[i][1] += diff

        n_exp = self.expirytime + diff
        if minexpiry != 0 and n_exp < minexpiry:
            n_exp = minexpiry
            self.force_immediate_shutdown = True

        self.expirytime = n_exp

    def cancelTimer(self):
        if self.tit_wd is not None:
            self.tit_wd.abort()
            self.tit_wd = None
        self.expirytime = 0
        self.extinguishtimes = []
        self.ledrow_off()

    def stopservice(self):
        self.log('Quiting server...')
        if self.isTimerActive():
            self.cancelTimer()
        self.svccancel = True

    def shutdown(self):
        #Stop playing, play goodbye sound, shutdown
        self.log('Initializing shutdown...')
        
        subprocess.call(PLAYOUT+' -c=playerstop', shell=True)
        audpath = AUDFOLDER + self.config.get("QuotaConfig","audiomsgfile")
        subprocess.call(['/usr/bin/mpg123', audpath])
        
        subprocess.call(PLAYOUT+' -c=shutdown', shell=True)
        self.log('Shutdown initiated')

    def initalizeFromIniFile(self):
        self.log('initalizeFromIniFile executed')

        self.loadConfig()

        self.customquota_since_boot = False
        self.force_immediate_shutdown = False
        if self.isTimerActive():
            self.cancelTimer()
            time.sleep(1.0)

        self.initLeds()
        self.newTimer(0, True)

    def serviceloop(self):
        self.log('Quota watchdog loop started (watchdog interval: {}s'.format(WDOG_TIME))
        while not self.svccancel:
            now_ut = getTimeSec('uptime')

            # timer correction (if no time sync was available at box startup)
            if self.asyncstartat > 0:
                if self.isSynced():
                    now_ep = getTimeSec('epoch')
                    diff = now_ut - self.asyncstartat
                    self.log('Now we\'ve got real time ({} minutes passed since last quota grant).'.format(str(round(diff/60))))

                    # calculate real grant time and re-evaluate decision
                    real_gt = now_ep - diff
                    real_s = self.getStartingGrant(real_gt) # how much seconds of time quota should we have got if started with correct time at hand?
                    self.log('Preliminary quota grant was at {} ({}), we should have granted {} minutes of quota...'.format(str(real_gt), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(real_gt))), round(real_s/60)))

                    # correct last_granttime (if required)
                    cfg_dq = self.config.getint('QuotaConfig', 'default_quota')
                    if real_s >= (60*cfg_dq):
                        self.log("Correcting last_granttime")
                        self.new_grant(real_gt)

                    # adjust timers (if required)
                    if self.customquota_since_boot:
                        self.log("No need to adjust timers since a custom quota grant has been activated recently.")
                    else:
                        diff = real_s - (60*cfg_dq)
                        if diff < 0:
                            self.log('Adjusting timers by {} min ({} s)'.format(round(diff/60, 2), diff))
                            self.adjustTimer(diff, self.asyncstartat + GRACETIME)
                        else:
                            self.log('No need to adjust timers.')
                    self.asyncstartat = 0
                else:
                    self.log('Still awaiting time sync...')

            # Check if LEDs can be switched off
            if len(self.extinguishtimes) > 0:
                n_ext = 0 # counter telling how many LEDs have been extinguished (can be multiple at one in some cases)
                for i in range(0, len(self.extinguishtimes)):
                    if now_ut >= self.extinguishtimes[i][1]:
                        n_ext += 1
                        ledid = self.extinguishtimes[i][0]
                        if ledid >= 0 and ledid<len(self.leds):
                            self.log('Switching off LED {}, GPIO {}...'.format(ledid+1, self.leds[ledid]))
                            GPIO.output(self.leds[ledid], GPIO.LOW)
                    else:
                       self.log('Next LED ({}) will switch off in {} min'.format(self.extinguishtimes[i][0]+1, round((self.extinguishtimes[i][1]-now_ut)/60, 2)))
                       break
                self.extinguishtimes = self.extinguishtimes[n_ext:]

            # Check if expiry time is reached...
            if self.expirytime > 0:
                if now_ut < self.expirytime:
                    if self.force_immediate_shutdown:
                        self.log('Forced immediate shutdown will start in {} min.'.format(round((self.expirytime-now_ut)/60,2)))
                    else:
                        self.log('Shutdown action "{}" will start in {} min.'.format(self.config.get("QuotaConfig","shutdown_waitmode"), round((self.expirytime-now_ut)/60,2)))
                else:
                    self.log('Shutdown action "{}" running since {} min.'.format(self.config.get("QuotaConfig","shutdown_waitmode"), round((now_ut-self.expirytime)/60,2)))
                    mode = self.config.get("QuotaConfig","shutdown_waitmode").lower()
                    if mode == 'immediate' or self.force_immediate_shutdown:
                        self.shutdown()
                    elif mode == 'aftertrk':
                        if self.tit_wd is None:
                            self.tit_wd = title_watchdog(MAX_TITWAIT,self.logger)
                        if self.tit_wd.isFinished():
                            self.log('SHUTDOWN SHUTDOWN SHUTDOWN SHUTDOWN SHUTDOWN SHUTDOWN ')
                            self.tit_wd.abort()
                            self.tit_wd = None
                            self.expirytime = 0
                            self.shutdown()
                    else:
                        self.log('Unexpected shutdown_waitmode: {}'.format(mode))

            # Wait for next round to continue checks
            time.sleep(WDOG_TIME)
        self.log('Quota service loop exited')

def extif_server_thread(quota_svc, logger):
    logger.info('Starting TCP Server thread...')
    quota_svc.monitorSocket()
    logger.info('TCP server thread finished.')
    return None

if __name__ == "__main__":
    # Create logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel('INFO')

    quota_svc = None

    # Create service object
    try:
        quota_svc = quota_service(os.path.expanduser('/home/pi/RPi-Jukebox-RFID/settings/quota.ini'), logger)
    except SyntaxError as ex:
        logger.info('Error loading ini file: {}'.format(ex))
    except configparser.NoOptionError as ex:
        logger.info('Ini file misses required entry: {}'.format(ex))
    except Exception as ex:
        logger.info('Unexpected error loading ini file: {}'.format(ex))

    if quota_svc is not None:
        logger.info('Starting quota service...')

        # Create server interface
        quota_if = quota_if_server(quota_svc, logger)
        if not quota_if.initSocket():
            logger.info('Quota service stopped due to fail of interface initialization')
        else:
            quota_svc.initalizeFromIniFile()
            t = threading.Thread(target=extif_server_thread, args=(quota_if,logger))
            t.start()
            quota_svc.serviceloop()
            logger.info('Quota service stopped.')
            t.join()
