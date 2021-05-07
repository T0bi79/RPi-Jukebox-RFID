# GPIO CONTROL

This service enables the control of different GPIO input & output devices for controlling the Phoniebox.
It uses to a configuration file to configure the active devices.

## How to create and run the service?
* The service can be activated during installation with the installscript.
* If the service was not activated during installation, you can alternatively use `sudo install.sh` in this folder (`components/gpio_control`).

## How to edit configuration files?
The configuration file is located here: `~/RPi-Jukebox-RFID/settings/gpio_settings.ini` 
Editing the configuration file and restarting the service with `sudo systemctl restart phoniebox-gpio-control` will activate the new settings.

In the following the different devices are described. 
Each device can have actions which correspond to function calls.
Up to now the following input devices are implemented:
* **Button**: 
   A simple button which has a hold and repeat functionality as well as a delayed action. 
   Its main parameters are: `Pin` (**use GPIO number here**) and `functionCall`. For additional options, see [extended documentation below](#doc_button).

* **RotaryEncoder**:
    Control of a rotary encoder, for example KY040, see also in 
    [Wiki](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/Audio-RotaryKnobVolume)
    it can be configured using pinA (**use GPIO number here**), pinB (**use GPIO number here**), functionCallIncr, functionCallDecr, timeBase=0.1

* **TwoButtonControl**:
    This Device uses two Buttons and implements a third action if both buttons are pressed together.
    
Each section needs to be activated by setting `enabled: True`.

Many example files are located in `~/RPi-Jukebox-RFID/components/gpio_control/example_configs/`.

# Extended documentation
## Button<a name="doc_button"></a> 
At the most basic level, a button can be created using a `ini` entry like this:
```
[PlayPause]
enabled: True
Type: Button
Pin: 27
functionCall: functionCallPlayerPause
```
* **enabled**: This needs to be 'True' for the button to work.
* **Pin**: GPIO number
* **functionCall**: The function that you want to be called on a button press. See  [function documentation below](#doc_funcs).

However, a button has more parameters than this. In the following comprehensive list you can also find the default values which are used if you leave out these settings;
* **hold_mode**: Specifies what shall happen if the button is held pressed for longer than `hold_time`:
  *  `None` (Default): Nothing special will happen.
  *  `Repeat`: The same function call will be repeated after each `hold_time` interval.
  *  `Postpone`: The function will not be called before `hold_time`, i.e. the button needs to be pressed this long to activate the function
  *  `SecondFunc`: After the instant execution of `functionCall`, holding the button for at least `hold_time` will execute a different function `functionCall2`.
  
  Holding the button even longer than `hold_time` will cause no further function calls unless you are in the `Repeat` mode.
* **hold_time**: Reference time for this buttons `hold_mode` feature in seconds. Default is `0.3`. This setting is ignored if `hold_mode` is unset or `None`
* **pull_up_down**: Configures the internal Pull up/down resistors. Valid settings:
  * `pull_up` (Default). Internal pull-up resistors are activated. Use this if you attached a button to `GND` to the GPIO pin without any external pull-up resistor.
  * `pull_down`. Use this if you need the internal pull-down resistor activated.
  * `pull_off`. Use this to deactivate internal pull-up/pulldown resistors. This is useful if your wiring includes your own (external) pull up / down resistors.
* **edge**: Configures the events in which the GPIO library shall trigger the callback function. Valid settings:
  * `falling` (Default). Triggers if the GPIO voltage goes down.
  * `rising`. Trigegrs only if the GPIO voltage goes up.
  * `both`. Triggers in both cases.
* **bouncetime**: This is a setting of the GPIO library to limit bouncing effects during button usage. Default is `500` ms.
* **antibouncehack**: Despite the integrated bounce reduction of the GPIO library some users notice false triggers of their buttons (e.g. unrequested / double actions when releasing the button. If you encounter such problems, set this setting to `True` to activate an additional countermeasure.


## Functions<a name="doc_funcs"></a> 
Functions can be found here: TODO
