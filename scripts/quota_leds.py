from time import sleep
from sys import argv
import subprocess
from optparse import OptionParser

import quota_paths
import quota_cfg


def init():
    """
    Initializes the GPIOs for the configured LEDs
    """
    cfg_lgs = quota_cfg.readElem("led_gpios")
    if cfg_lgs is None:
        print('Config error')
        return

    # 1.) GPIOs der LEDs einrichten
    print 'Exporting GPIOs...'
    for i in range(0, len(cfg_lgs)):
        cmd_export = 'echo "%d" > /sys/class/gpio/export; exit 0' % (cfg_lgs[i])
        # print 'cmd_export: ',cmd_export
        res_export = subprocess.check_output(cmd_export, stderr=subprocess.STDOUT, shell=True)
        if(res_export and res_export.strip()):
            print 'Error: ' + res_export
    sleep(0.3)  # to avoid Permission denied error when setting direction
    print 'Setting GPIO direction...'
    for i in range(0, len(cfg_lgs)):
        cmd_direction = 'echo "out" > /sys/class/gpio/gpio%d/direction; exit 0' % (cfg_lgs[i])
        # print 'cmd_direction:',cmd_direction
        res_direction = subprocess.check_output(cmd_direction, stderr=subprocess.STDOUT, shell=True)
        if(res_direction and res_direction.strip()):
            print 'Error: ' + res_direction


def control(led_gpio, state, minutes):
    if led_gpio >= 2 and led_gpio <= 27:
        # prepare target state
        s = "0"
        if state > 0:
            s = "1"
        # prepare command
        c = 'echo "'+s+'" > /sys/class/gpio/gpio%d/value' % (led_gpio)
        # prepare timer
        if minutes > 0:
            c = "echo \""+c+"\" | sudo at -q l now + %d minutes; exit 0" % (minutes)
        # execute
        res_c = subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)
        if(res_c and res_c.strip()):
            if not('warning: commands will be executed using /bin/sh' in res_c):
                print 'Error: ' + res_c


def cancelTimers():
    atqres = subprocess.check_output('sudo atq -q l', shell=True)
    if len(atqres) > 0:
        subprocess.call("sudo atrm $(sudo atq -q l | cut -f1)", shell=True)


def disableAll():
    cfg_lgs = quota_cfg.readElem("led_gpios")
    if cfg_lgs is None:
        print('Config error')
        return

    for g in cfg_lgs:
        control(g, 0, 0)


def animate_leds_on(units, dur_on):
    # Programs the ignition of the specified number of LEDs
    cfg_lgs = quota_cfg.readElem("led_gpios")
    if cfg_lgs is None:
        print('Config error')
        return

    n_leds = min(units, len(cfg_lgs))

    for i in range(0, n_leds):
        control(cfg_lgs[i], 1, 0)
        if i < (n_leds-1):
            sleep(dur_on)
    return


def animate_leds_off(units, dur_off):
    # Programs the extinction of the specified number of LEDs
    cfg_lgs = quota_cfg.readElem("led_gpios")
    if cfg_lgs is None:
        print('Config error')
        return

    n_leds = min(units, len(cfg_lgs))
    for i in range(0, n_leds):
        control(cfg_lgs[i], 0, ((n_leds-i)*dur_off))


def animate(units, dur_on, dur_off):
    # program animated switch-off. dur_on is in seconds (e.g. 0.3), dur_off is in minutes
    animate_leds_off(units, dur_off)

    # run animated switch-on (asynchronously in order not to block the caller)
    cmd_schedign = 'echo "python ' + quota_paths.LEDS + ' -n ' + str(units) + ' -m ' + str(dur_on) + '" | sudo at -q l now; exit 0'
    res_schedign = subprocess.check_output(cmd_schedign, stderr=subprocess.STDOUT, shell=True)
    if(res_schedign and res_schedign.strip()):  # todo: ab hier weg, hier unoetig, oder?
        if not('warning: commands will be executed using /bin/sh' in res_schedign):
            print 'Error: ' + res_schedign
    return


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def parse_params():
    parser = OptionParser("quota_led.py [options]")
    parser.add_option("-n", "--ani_leds",   dest="opt_leds",  default=None,  action="store", help="Animate (ignite) the specified number of LEDs")
    parser.add_option("-m", "--ani_ms",     dest="opt_ms",    default=None,  action="store", help="Interval between ignitions in seconds, e.g. 0.3 (use with -n)")
    (optionen, args) = parser.parse_args()

    if optionen.opt_leds and optionen.opt_leds.isdigit():
        # the script was called to start a LED animation
        n_leds = int(optionen.opt_leds)
        if n_leds > 0:
            dur = 0.0
            if optionen.opt_ms and isfloat(optionen.opt_ms):
                dur = float(optionen.opt_ms)
            else:
                print "No animation interval was specified. Using 0."
            animate_leds_on(n_leds, dur)
    else:
        print "No valid command was specified."


# Main / global:
# No activity unless this script was called directly (not included by another one)
if ("quota_leds.py" in argv[0]):
    parse_params()
