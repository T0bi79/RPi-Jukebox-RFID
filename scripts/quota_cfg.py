import json
import os
from time import time

import quota_paths

# description of the configuration.
# - minutes_per_unit:      Duration of 1 time unit (in minutes). After each passed time unit, 1 LED will switch off (if LEDs are used)
# - default_units:         Number of time units that will granted after booting the box (if the last grant was more than minutes_to_reset ago)
# - minutes_to_reset:      Number of minutes after which a elapsed quota may renew on reboot
# - last_quota_activation: Unix timestamp (rounded to full seconds) stating the timestamp when the current quota was granted
# - led_gpios:             Ordered list of GPIO numbers for all mounted LEDs
# - led_animation:         Time interval in seconds which is used for animated LED ignition (time between two ignitions, e.g 0.3)


def internal_defaultcfg():
    # Default values for all configuration values.
    # The entire default config may be used if the cfg file cannot be opened or loaded correctly
    # Single default values may be used if single config values are out of the allowed range
    cfg = {}
    cfg['minutes_per_unit'] = 30
    cfg['default_units'] = 4
    cfg['minutes_to_reset'] = 480
    cfg['last_quota_activation'] = int(round(time()))
    cfg['led_gpios'] = []
    cfg['led_animation'] = 0.3
    return cfg


def internal_checkInteger(i, minval=None, maxval=None):
    # Check if the specified value is an integer and in the allowed range (if passed)
    if i is not None and isinstance(i, (int, long)):
        is_ok = True
        if(minval is not None and i < minval):
            is_ok = False
        if(maxval is not None and i > maxval):
            is_ok = False
        if is_ok:
            return True

    return False


def internal_checkFloat(f, minval=None, maxval=None):
    # Check if the specified value is a float (or integer) and in the allowed range (if passed)
    if f is not None and isinstance(f, (int, long, float)):
        is_ok = True
        if(minval is not None and f < minval):
            is_ok = False
        if(maxval is not None and f > maxval):
            is_ok = False
        if is_ok:
            return True

    return False


def internal_checkIntegerList(a, minval=None, maxval=None):
    # Check if the specified value is an array of integers and each element is in the allowed range (if passed)
    if a is not None and isinstance(a, list):
        all_ok = True
        for e in a:
            if not isinstance(e, (int, long)):
                all_ok = False
            if(minval is not None and e < minval):
                all_ok = False
            if(maxval is not None and e > maxval):
                all_ok = False
        if all_ok:
            return True

    return False


def checkImmediateValue(key, value, default=None):
    if(key == "minutes_per_unit"):
        if(internal_checkInteger(value, 1)):
            return True
    elif(key == "default_units"):
        if(internal_checkInteger(value, 1)):
            return True
    elif(key == "minutes_to_reset"):
        if(internal_checkInteger(value, 1)):
            return True
    elif(key == "last_quota_activation"):
        if(internal_checkInteger(value)):
            return True
    elif(key == "led_gpios"):
        if(internal_checkIntegerList(value, 2, 31)):
            return True
    elif(key == "led_animation"):
        if(internal_checkFloat(value, 0.0, 10.0)):
            return True
    else:
        return False

    #  if we reach here we have a known key with an illegal value. Pass default value if requepostGetIntsted
    if default is not None and isinstance(default, list):
        defaultcfg = internal_defaultcfg()
        if key in defaultcfg:
            default[0] = defaultcfg[key]

    return False


def checkConfigValue(cfg, key, allow_def):
    if not cfg:
        return False

    v = None
    if key in cfg:
        v = cfg[key]
    default = [None]

    if checkImmediateValue(key, v, default):
        return True

    if allow_def and default[0] is not None:
        cfg[key] = default[0]
        return True

    return False


def checkcfg(cfg, allow_def):
    # Checks a configuration for the presence and validity of all elements
    # If $allow_def is set, it corrects all missing/illegal values to their defaults
    # Returns true if cfg is (now) valid
    if not cfg:
        return False
    if not checkConfigValue(cfg, "minutes_per_unit", allow_def):
        return False
    if not checkConfigValue(cfg, "default_units", allow_def):
        return False
    if not checkConfigValue(cfg, "minutes_to_reset", allow_def):
        return False
    if not checkConfigValue(cfg, "last_quota_activation", allow_def):
        return False
    if not checkConfigValue(cfg, "led_gpios", allow_def):
        return False
    if not checkConfigValue(cfg, "led_animation", allow_def):
        return False
    return True


def readCfg(allow_def=True):
    # Reads a config from the configured file and returns as list
    try:
        with open(quota_paths.CFG) as json_file:
            cfg = json.load(json_file)
            if checkcfg(cfg, allow_def):
                return cfg
    except:  # file open or json load error
        if allow_def:
            cfg = internal_defaultcfg()
            writeCfg(cfg)
            return cfg
    return None


def writeCfg(cfg, allow_def=True):
    # Writes a config list to the configured file
    if not checkcfg(cfg, allow_def):
        return False  # only reached if allow_def=False

    result = False
    try:
        with open(quota_paths.CFG, "w") as json_file:
            json.dump(cfg, json_file)
            result = True
    except:
        print "Config file could not be saved"

    try:
        os.chmod(quota_paths.CFG, 0o666)  # Both, pi and www-data should be able to modify this file
    except:
        pass
    return result


def readElem(key, cfg=None, allow_def=True):
    # Reads the specified value. Config is auto-opened if not passed as argument
    if not cfg:
        cfg = readCfg(allow_def)
    if cfg and key in cfg:
        return cfg[key]
    return None


def writeElem(key, newval, cfg=None, allow_def=True):
    # Saves the Config while updating one value. Config is auto-opened if not passed as argument
    if not cfg:
        cfg = readCfg(allow_def)
    if cfg:
        cfg[key] = newval
        if writeCfg(cfg, allow_def):
            return True
    return False
