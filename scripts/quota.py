from time import sleep, time
import os
import os.path
from optparse import OptionParser
import subprocess

import quota_paths  # relevant paths
import quota_cfg    # quota configuration
import quota_shut   # shutdown scheduler
import quota_leds   # LED scheduler


def get_remaining_time_units():
    """
    Calculates the starting grant (default grant minus recently consumed quota), rounded to full time units
    """
    print 'get_remaining_time_units'
    now = int(round(time()))

    # read config
    cfg = quota_cfg.readCfg()
    if((not cfg) or ('minutes_per_unit' not in cfg) or ('default_units' not in cfg) or ('minutes_to_reset' not in cfg) or ('last_quota_activation' not in cfg)):
        print('Config error')
        return

    cfg_mpu = cfg['minutes_per_unit']
    cfg_dl = cfg['default_units']
    cfg_mtr = cfg['minutes_to_reset']
    cfg_lqa = min(cfg['last_quota_activation'], now)

    # 1.) Ermittele aktuellen Kontingentverbrauch (ggf. vor Reboot der Box)
    verbraucht = (now - cfg_lqa) / 60  # verbrauchtes Kontingent in Minuten.
    if verbraucht >= cfg_mtr:          # Wenn das verbrauchte Kontingent aelter ist als cfg[minutes_to_reset], ist das auch OK. Vergebe neues Kontingent
        print 'lockfile is old enough, granting new time quota'
        cfg['last_quota_activation'] = now
        quota_cfg.writeCfg(cfg)
        verbraucht = 0

    # 2.) Ermittele, wie lange die Box nun nach Start freigeschaltet werden darf
    # Das Rest-Kontingent (Default-Zeit abzgl. verbrauchtes Kontingent) wird zu naheliegendster voller Zeiteinheit auf/abgerundet
    # D.h. bei sehr wenig Restzeit (unter halbe Zeiteinheit) wird nach einem Neustart kein Kontingent mehr gewaehrt
    default_limit = cfg_dl * cfg_mpu  # Default-Kontingent in Minuten
    current_limit = default_limit - verbraucht        # Rest-Kontingent in Minuten
    print 'remaining quota is', current_limit, 'minutes'
    current_limit -= (cfg_mpu/2)
    if int(current_limit) <= 0:
        print 'too little quota for a new reboot'
        return 0                                      # Keine Starterlaubnis
    granted_limit = int(current_limit / cfg_mpu)
    if (int(current_limit) % cfg_mpu > 0):
        granted_limit += 1
    print 'granting %d time units' % granted_limit
    return granted_limit                              # Starterlaubnis fuer (granted limit) Zeiteinheiten


def f_init():
    """
    Default initialization sequence (init GPIO for LEDs, check if new default quota is to be granted)
    """
    print 'f_init'
    quota_leds.init()

    # 2.) Ermittle Abschaltzeit (Defaultwert oder Restkontingent) und...
    time_units = get_remaining_time_units()
    if time_units > 0:
        print 'Create new timer for %d periods.' % time_units
        f_newtimer(time_units)  # ...aktiviere Abschaltzeit oder ...
    else:                   # ...fahre Box wieder herunter
        print 'Shutting down since time elapsed.'
        f_canceltimers()
        quota_shut.prepare_shutdown(quota_paths.PLAYOUT+' -c=shutdown', quota_paths.GBYEMP3, 4, 6, 0)


def f_newtimer(units):
    """
    Creates a new shutdown timer (pre-existing timers are removed initially)
    """
    print 'f_newtimer'
    cfg_mpu = quota_cfg.readElem('minutes_per_unit')
    cfg_la = quota_cfg.readElem('led_animation')
    if cfg_mpu is None or cfg_la is None:
        print('Config error')
        return

    f_canceltimers()  # Beinhaltet Abschalten evtl. noch leuchtender LEDs
    quota_shut.prepare_shutdown('python '+quota_paths.MAIN+' -s', None, 0, 6, cfg_mpu*units*60)
    quota_leds.animate(units, cfg_la, cfg_mpu)


def f_canceltimers():
    """
    Removes all timers and switches of the LEDs
    """
    print 'f_canceltimers'
    quota_shut.cancelTimers()
    quota_leds.cancelTimers()
    quota_leds.disableAll()


def f_shutdown(allow_last_title):
    """
    Controlled shutdown process (it can wait for the current mpd titel to finish)
    """
    print 'f_shutdown'
    if allow_last_title:
        subprocess.call(['python', quota_paths.MPDWAIT])

    subprocess.call(quota_paths.PLAYOUT+' -c=playerstop', shell=True)
    subprocess.call(['/usr/bin/mpg123', quota_paths.GBYEMP3])
    subprocess.call(quota_paths.PLAYOUT+' -c=shutdown', shell=True)


def parse_params():
    parser = OptionParser('quota.py [options]')
    parser.add_option('-i', '--init',         dest='opt_init',     default=False, action='store_true', help='Initialisation script (call this first)')
    parser.add_option('-g', '--gpioupd',      dest='opt_gpioupd',  default=False, action='store_true', help='Notifies about changed GPIO config')
    parser.add_option('-n', '--newtimer',     dest='opt_timer',    default=None,  action='store',      help='Programs a shutdown timer')
    parser.add_option('-c', '--canceltimers', dest='opt_cancel',   default=False, action='store_true', help='Deactivates a shutdown timer')
    parser.add_option('-s', '--shutdown',     dest='opt_shutdown', default=False, action='store_true', help='Shutdown after current mpd title')
    (optionen, args) = parser.parse_args()

    if optionen.opt_init:
        f_init()

    elif optionen.opt_gpioupd:
        quota_leds.init()

    elif optionen.opt_cancel:
        f_canceltimers()

    elif optionen.opt_timer and optionen.opt_timer.isdigit():
        t = int(optionen.opt_timer)
        if t > 0:
            quota_cfg.writeElem('last_quota_activation', int(round(time())))
            f_newtimer(t)
        else:
            print 'No valid duration given'

    elif optionen.opt_shutdown:
        f_shutdown(True)

    else:
        print 'No valid command given'


# Main / global:
parse_params()
