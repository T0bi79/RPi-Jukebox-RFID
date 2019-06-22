<?php

$QUOTA_JSON_PATH = "/home/pi/RPi-Jukebox-RFID/settings/quota_cfg.json";

# description of the configuration.
# - minutes_per_unit:      Duration of 1 time unit (in minutes). After each passed time unit, 1 LED will switch off (if LEDs are used)
# - default_units:         Number of time units that will granted after booting the box (if the last grant was more than minutes_to_reset ago)
# - minutes_to_reset:      Number of minutes after which an expired time quota gets renewed on reboot
# - last_quota_activation: Unix timestamp (rounded to full seconds) stating the timestamp when the current quota was granted
# - led_gpios:             Ordered list of GPIO numbers for all mounted LEDs
# - led_animation:         Time interval in seconds which is used for animated LED ignition (time between two ignitions, e.g 0.3)


function internal_defaultcfg(){
    # Default values for all configuration values.
    # The entire default config may be used if the cfg file cannot be opened or loaded correctly
    # Single default values may be used if single config values are out of the allowed range
    $cfg = [];
    $cfg["minutes_per_unit"] = 30;
    $cfg["default_units"] = 4;
    $cfg["minutes_to_reset"] = 480;
    $cfg["last_quota_activation"] = time();
    $cfg["led_gpios"] = [];
    $cfg["led_animation"] = 0.3;
    return $cfg;
}

function internal_checkInteger($i, $minval=null, $maxval=null){
    # Check if the specified value is an integer and in the allowed range (if passed)
    if($i != null && is_int($i)){
        $is_ok = True;
        if($minval !== null && $i < $minval) $is_ok = False;
        if($maxval !== null && $i > $maxval) $is_ok = False;
        if($is_ok) return True;
    }
    return False;
}

function internal_checkFloat($f, $minval=null, $maxval=null){
    # Check if the specified value is a float (or integer) and in the allowed range (if passed)
    if($f != null && (is_float($f) || is_double($f) || is_int($f))){
        $is_ok = True;
        if($minval !== null && $f < $minval) $is_ok = False;
        if($maxval !== null && $f > $maxval) $is_ok = False;
        if($is_ok) return True;
    }
    return False;
}

function internal_checkIntegerArray($a, $minval=null, $maxval=null){
    # Check if the specified value is an array of integers and each element is in the allowed range (if passed)
    if($a !== null && is_array($a)){
        $all_ok = True;
        foreach ($a as $e) {
            if(!is_int($e)) $all_ok = False;
            if($minval !== null && $e < $minval) $all_ok = False;
            if($maxval !== null && $e > $maxval) $all_ok = False;
        }
        if($all_ok != False) return True;
    }
    return False;
}


function checkImmediateValue($key, $value, &$default=null){
    if($key == "minutes_per_unit"){
        if(internal_checkInteger($value, 1)) return True;
    }
    else if($key == "default_units"){
        if(internal_checkInteger($value, 1)) return True;
    }
    else if($key == "minutes_to_reset"){
        if(internal_checkInteger($value, 1)) return True;
    }
    else if($key == "last_quota_activation"){
        if(internal_checkInteger($value)) return True;
    }
    else if($key == "led_gpios"){
        if(internal_checkIntegerArray($value, 2, 31)) return True;
    }
    else if($key == "led_animation"){
        if(internal_checkFloat($value, 0.0, 10.0)) return True;
    }
    else return False;

    # if we reach here we have a known key with an illegal value. Pass default value if requested
    if($default !== null && is_array($default)){
        $defaultcfg = internal_defaultcfg();
        if(isset($defaultcfg[$key])){
            $default[0] = $defaultcfg[$key];
        }
    }
    return False;
}

function checkConfigValue(&$cfg, $key, $allow_def){
    if(!$cfg) return False;
    
    $v = (isset($cfg[$key]) ? $cfg[$key] : null);
    $default = [null];
    
    if(checkImmediateValue($key, $v, $default)) return True;
    
    if($allow_def && $default[0] !== null){
        $cfg[$key]=$default[0];
        return True;
    }
    return False;
}

function checkcfg(&$cfg, $allow_def){
    # Checks a configuration for the presence and validity of all elements
    # If $allow_def is set, it corrects all missing/illegal values to their defaults
    # Returns true if cfg is (now) valid
    if(!$cfg) return False;

    if(!checkConfigValue($cfg, "minutes_per_unit",      $allow_def)) return False;
    if(!checkConfigValue($cfg, "default_units",         $allow_def)) return False;
    if(!checkConfigValue($cfg, "minutes_to_reset",      $allow_def)) return False;
    if(!checkConfigValue($cfg, "last_quota_activation", $allow_def)) return False;
    if(!checkConfigValue($cfg, "led_gpios",             $allow_def)) return False;
    if(!checkConfigValue($cfg, "led_animation",         $allow_def)) return False;
    return True;
}


function readCfg($allow_def = True){
    global $QUOTA_JSON_PATH;
    # Reads a config from the configured file and returns as list
    $fcont = file_get_contents($QUOTA_JSON_PATH);
    if($fcont){
        $cfg = json_decode($fcont, True);
        if($cfg){
            if(checkcfg($cfg, $allow_def)){
                return $cfg;
            }
        }
    }
    # file open or json load error
    if($allow_def){
        $cfg = internal_defaultcfg();
        writeCfg($cfg);
        return $cfg;
    }

    return null;
}


function writeCfg($cfg, $allow_def = True){
    global $QUOTA_JSON_PATH;

    # Writes a config list to the configured file
    if(!checkcfg($cfg, $allow_def)){
        return False;  # only reached if allow_def=False
    }

    $fp = fopen($QUOTA_JSON_PATH, 'w');
    if($fp){
        $re = fwrite($fp, json_encode($cfg));
        fclose($fp);
        chmod($QUOTA_JSON_PATH, 0666);  # Both, pi and www-data should be able to modify this file
        return True;
    }
    # Config file could not be saved
    return False;
}


function readElem($key, $cfg=null, $allow_def = True){
    # Reads the specified value. Config is auto-opened if not passed as argument
    if(!$cfg){
        $cfg = readCfg($allow_def);
    }
    if($cfg && isset($cfg[$key])){
        return $cfg[$key];
    }
    return null;
}


function writeElem($key, $newval, $cfg=null, $allow_def = True){
    # Saves the Config while updating one value. Config is auto-opened if not passed as argument
    if(!$cfg){
        $cfg = readCfg($allow_def);
    }
    if($cfg){
        $cfg[$key] = $newval;
        if(writeCfg($cfg, $allow_def)) return True;
        # Error writing
    }
    return False;
}

?>