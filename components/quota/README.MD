# Time Quota Service

This service adds enforcement of time quota to the Phoniebox: When the Phoniebox audience runs out of time (quota), the box will shutdown - either instantly or after the current track has finished.

A default amount of quota can be configured which is granted automatically on startup if enough time has passed since the the previous session.

Optionally, a row of LEDs can be used to indicate the amount of remaining quota (each illuminated LED stands for a configurable amount of remaining time).

The exact amount of remaining time (in minutes) is also accessible in the web interface at &lt;ip address&gt;/settings.php.

## Installation
* Run `sudo install.sh` in this folder (`components/quota`).

## How to edit configuration files?
The install script creates a default configuration file is located at `~/RPi-Jukebox-RFID/settings/quota.ini`.

It consists of three sections:
```
[QuotaConfig]
...
[LedConfig]
...
[QuotaState]
...
```

The meaning of each section is described below.
After editing the configuration file (e.g. using `nano RPi-Jukebox-RFID/settings/quota.ini`) the service has to be restarted by running `sudo systemctl restart phoniebox-gpio-control` which will activate the new settings.

### Section [QuotaConfig]

Basic configuration of the quota service. These options are mandatory.

Example configuration:
```
[QuotaConfig]
default_quota = 180
reset_time = 360
shutdown_waitmode = AfterTrk
```
* **default_quota**: Default quota, in minutes. This is the time that will be granted after booting the box (if the last grant was more than reset_time ago). The example of 180 stands for 3 hours.
* **reset_time**: Minimum amount of time (in minutes) that must have passed since the last grant of fresh quota (e.g.: a prior start of the phoniebox) before new fresh quota will be granted (at a later restart of the phoniebox). The example of 360 stands for 6 hours (which is 3 hours after the previous quota of 3 hours elapsed).
* **shutdown_waitmode**: What shall happen after the quota ran out:
  * *Immediate*: Immediate shutdown. The track currently playing will be disrupted.
  * *AfterTrk*: Waits for current title to finish. Few seconds afterwards the box will shutdown.

### Section [LedConfig]

Configuration of status LEDs. TODO: optional vs. mandatory
If you consider to use LEDs, note out hints in the concluding section.

Example configuration:
```
[LedConfig]
led_gpios = [9, 10, 11, 18, 17]
led_duration: 30
led_animation: 0.3
```

* **led_gpios**: A list of GPIO numbers used to control the LEDs. The list is ordered such that the hindmost LEDs will switch off first. If no LEDs are used, set this to `[]`.
* **led_duration**: Amount of remaining quota (in minutes) indicated by each LED. Each time after this time interval, one LED will switch off (if LEDs are used)
* **led_animation**: Time interval in seconds for animated LED illumination (time between each two ignitions; use 0 for simultaneous illumination of all LEDs)

### Section [QuotaState]
This section is managed by the quota service itself. It stores the timestamp of the last grant as `last_granttime`. Resetting this value to 0 guarantees fresh quota at next service restart. Further kinds of manipulation are not recommended.


## How to temporarily adjust the current quota?

There are two ways to manually change the current quota on a running PhonieBox: Using the web interface and using special RFID cards.
Independent of which way you use, all these settings are transient, i.e. do NOT change the quota configuration in `~/RPi-Jukebox-RFID/settings/quota.ini`. Thus, your Phoniebox will revert to normal behavior after next reboot.

### Changing quota using web interface:
The `Settings` page (&lt;ip address&gt;/settings.php) containes a section `Time quota`.
* **Grant time quota**: Use this button to set the current quota to an arbitrary amount of remaining minutes (enter this number into the box right beneath)
* **Decontrol quota**: Use this button to disable the quota. This disables any oncoming shutdowns by the quota service.

### Changing quota using RFID cards:
The sample configuration for the RFID control configuration (`~/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf.sample`) features the following commands that can assigned to RFID cards.
* **GRANTQUOTA60**: Grants 60 minutes of fresh quota
* **GRANTQUOTA90**: Grants 90 minutes of fresh quota
* **GRANTQUOTA120**: Grants 120 minutes of fresh quota
* **GRANTQUOTA150**: Grants 150 minutes of fresh quota
* **GRANTQUOTA180**: Grants 180 minutes of fresh quota
* **GRANTQUOTA240**: Grants 240 minutes of fresh quota
* **GRANTQUOTA300**: Grants 300 minutes of fresh quota
* **QUOTA_OFF**: Temporarily disables quota enforcement

Following that file's documentation, these commands can be linked to the IDs of RFID cards, e.g. like
```
GRANTQUOTA120="1234567890"
```

Hint: Parents might want to use RFID transponders instead of cards since these have a more "privileged" look and can simply be attached to any key ring.

## Further information

### Information on system startup without quota
If the box is restarted too soon after shutdown (i.e. before fresh quota will be granted) it will shutdown again.
However, there is a gracetime of 20 seconds which can be used to manually grant quota using the web interface or an RFID card or transponder (as described above).
If you need to edit this value, it is hardcoded as GRACETIME in components/quota/service.py and can only be changed there. 

### Hints about using LEDs
Note 1: The current quota service implementation assumes that setting a GPIO to High (3.3V) will illuminate a LED and setting it to Low (0 V) will switch it off.

Note 2: Some GPIO pins of the Raspberry Pi are initially High.
When powering up the system, LEDs controlled via these GPIOs will illuminate instantly (until the quota service will initialize and take over control).
Also, while the system shuts down, such LEDs will illuminate again until power is removed.
This behavior can not be changed by software so you might want to avoid such GPIO pins. Instead, use GPIOs that are initially low.

Note 3: Depending on which and how many LEDs you plan to use, note that powering them directly using the GPIO pins might damage your device.
The Raspberry Pi GPIOs are told to have a maximum allowed current of 16 mA per pin, while also a total maximum current (through all GPIO pins) of 50 mA applies.
You should calculate the current for each pin based on the LED and series resistor you use.
To avoid such problems it is recommended to power the LEDs externally (e.g. using the dedicated 3.3 or 5.0V pins) and use transistors or similar you control via the GPIO (which draws less current from the GPIO pins).

### Further status information / debugging
If you need more status information on the quota service, you can access its live status output, e.g. by running `journalctl -u phoniebox-quota.service -f`.
Alternatively, you can stop the quota service (`sudo systemctl stop phoniebox-quota.service`) and start it directly from the shell by running `python3 service.py` in the folder `~/RPi-Jukebox-RFID/components/quota`.
