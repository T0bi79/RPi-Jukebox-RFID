from time import time
from optparse import OptionParser
import subprocess

import quota_paths  # relevant paths
import quota_cfg    # quota configuration
import quota_shut   # shutdown scheduler
import quota_leds   # LED scheduler


def get_remaining_minutes():
    """
    Calculates the starting grant (default grant minus recently consumed quota), in remaining minutes
    """
    print 'get_remaining_minutes'
    now = int(round(time()))

    # read config
    cfg = quota_cfg.readCfg()
    if((not cfg) or ('default_minutes' not in cfg) or ('minutes_to_reset' not in cfg) or ('last_quota_activation' not in cfg) or ('led_minutes' not in cfg)):
        print('Config error')
        return

    cfg_dl = cfg['default_minutes']
    cfg_mtr = cfg['minutes_to_reset']
    cfg_lqa = min(cfg['last_quota_activation'], now)
    cfg_lm = cfg['led_minutes']

    # 1.) Ermittele aktuellen Kontingentverbrauch (ggf. vor Reboot der Box)
    consumed = (now - cfg_lqa) / 60  # consumed quota in minutes
    if consumed >= cfg_mtr:          # if the consumed quota is older than cfg[minutes_to_reset], this is OK as well. We'll grant new default quota
        print 'last grant is old enough, granting new time quota'
        cfg['last_quota_activation'] = now
        quota_cfg.writeCfg(cfg)
        consumed = 0

    # 2.) Calculate how much quota may be granted this time
    remaining = cfg_dl - consumed        # remaining quota is default quota minus consumed quota
    print 'remaining quota is', remaining, 'minutes'
    if remaining <= 0:
        print 'too little quota for a new reboot'
        return 0
    print 'granting %d minutes' % remaining
    return remaining


def f_init():
    """
    Default initialization sequence (init GPIO for LEDs, check if new default quota is to be granted)
    """
    print 'f_init'
    quota_leds.init()

    remaining = get_remaining_minutes()
    if remaining > 0:
        print 'Create new timer for %d minutes.' % remaining
        f_newtimer(remaining)
    else:
        print 'Shutting down since time elapsed.'
        f_canceltimers()
        quota_shut.prepare_shutdown(quota_paths.PLAYOUT+' -c=shutdown', quota_paths.GBYEMP3, 4, 6, 0)


def f_newtimer(minutes):
    """
    Creates a new shutdown timer (pre-existing timers are removed initially)
    """
    print 'f_newtimer'
    f_canceltimers()  # includes switching of LEDs that might still be active
    quota_shut.prepare_shutdown('python '+quota_paths.MAIN+' -s', None, 0, 6, minutes*60)
    quota_leds.animate(minutes)


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
    (options, args) = parser.parse_args()

    if options.opt_init:
        f_init()

    elif options.opt_gpioupd:
        quota_leds.init()

    elif options.opt_cancel:
        f_canceltimers()

    elif options.opt_timer and options.opt_timer.isdigit():
        t = int(options.opt_timer)
        if t > 0:
            quota_cfg.writeElem('last_quota_activation', int(round(time())))
            f_newtimer(t)
        else:
            print 'No valid duration given'

    elif options.opt_shutdown:
        f_shutdown(True)

    else:
        print 'No valid command given'


# Main / global:
parse_params()
