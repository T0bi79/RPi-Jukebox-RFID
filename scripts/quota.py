from time import sleep, time
import os
import os.path
from optparse import OptionParser
import subprocess

import quota_store  # quota storage
import quota_shut   # shutdown scheduler
import quota_leds   # LED scheduler

MINUTES_PER_UNIT = 30         # Anzahl der Minuten, nach der 1 Zeiteinheit ablaueft (und jeweils 1 LED aus geht, falls verbaut)
DEFAULT_LIMIT    = 4          # Anzahl der Zeiteinheiten, die nach Anschalten der Box defaultmaessig gewaehrt wird (abzgl. etwaigen Kontingentverbrauchs vor Neustart)
UNLOCK_HOURS     = 8          # Dauer in Stunden, nach der ein verbrauchtes Start-Kontingent wieder freigegeben wird

PATH_SELF       = '/home/pi/RPi-Jukebox-RFID/scripts/quota.py'             # Ablageort dieses Skriptes
PATH_WAITSCRIPT = '/home/pi/RPi-Jukebox-RFID/scripts/mpd_wait.py'          # Ablageort des Skripts zum Warten auf Ende des aktuellen mpd-Titels
PATH_GOODBYEMP3 = '/home/pi/RPi-Jukebox-RFID/misc/quota_end.mp3'           # Ablageort zur MP3-Datei, die vor dem Herunterfahren abgespielt wird
PATH_PLAYOUT    = '/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh'  # Ablageort des Playout-Skripts


def get_start_limit():
    """
    Ermittelt beim Hochfahren das Startkontingent (Default-Kontingent abzgl. kuerzlicher Verbrauch) in ganzen Zeiteinheiten
    """
    print "get_start_limit"
    # 1.) Ermittele aktuellen Kontingentverbrauch (ggf. vor Reboot der Box)
    verbraucht = quota_store.getConsumption()  # verbrauchtes Kontingent in Minuten.
    if (verbraucht / 60) >= UNLOCK_HOURS:                        # Wenn das verbrauchte Kontingent aelter ist als UNLOCK_HOURS, ist das auch OK. Vergebe neues Kontingent
        print 'lockfile is old enough, granting new time quota'
        quota_store.saveNew()
        verbraucht = 0

    # 2.) Ermittele, wie lange die Box nun nach Start freigeschaltet werden darf
    # Das Rest-Kontingent (Default-Zeit abzgl. verbrauchtes Kontingent) wird zu naheliegendster voller Zeiteinheit auf/abgerundet
    # D.h. bei sehr wenig Restzeit (unter halbe Zeiteinheit) wird nach einem Neustart kein Kontingent mehr gewaehrt
    default_limit = DEFAULT_LIMIT * MINUTES_PER_UNIT  # Default-Kontingent in Minuten
    current_limit = default_limit - verbraucht        # Rest-Kontingent in Minuten
    print 'remaining quota is', current_limit
    current_limit -= (MINUTES_PER_UNIT/2)
    if int(current_limit) <= 0:
        print 'too little quota for a new reboot'
        return 0                                      # Keine Starterlaubnis
    granted_limit = int(current_limit / MINUTES_PER_UNIT)
    if (int(current_limit) % MINUTES_PER_UNIT > 0):
        granted_limit += 1
    print 'granting %d time intervals' % granted_limit
    return granted_limit                              # Starterlaubnis fuer (granted limit) Zeiteinheiten


def f_init():
    """
    Initialisiert die GPIO-Ports fuer die LEDs (einmalig nach Systemstart noetig) und Default-Abschaltzeit
    """
    print "f_init"
    quota_leds.init()

    # 2.) Ermittle Abschaltzeit (Defaultwert oder Restkontingent) und...
    time_units = get_start_limit()
    if time_units > 0:
        print 'Create new timer for %d periods.' % time_units
        f_newtimer(time_units)  # ...aktiviere Abschaltzeit oder ...
    else:                   # ...fahre Box wieder herunter
        print 'Shutting down since time elapsed.'
        f_canceltimers()
        quota_shut.prepare_shutdown(PATH_PLAYOUT+' -c=shutdown', PATH_GOODBYEMP3, 4, 6, 0)


def f_newtimer(units):
    """
    Erstellt einen neuen Abschalttimer (etwaige noch Bestehende werden zuvor entfernt)
    """
    print "f_newtimer"
    f_canceltimers()  # Beinhaltet Abschalten evtl. noch leuchtender LEDs
    quota_shut.prepare_shutdown("python "+PATH_SELF+" -s", None, 0, 6, MINUTES_PER_UNIT*units*60)
    quota_leds.animate(units, 0.3, MINUTES_PER_UNIT)


def f_canceltimers():
    """
    Entfernt alle Timer und macht alle LEDs aus
    """
    print "f_canceltimers"
    quota_shut.cancelTimers()
    quota_leds.cancelTimers()
    quota_leds.disableAll()


def f_shutdown(allow_last_title):
    """
    Kontrollierter Abschaltprozess (es kann gewartet werden, bis der aktuelle mpd-Titel zu Ende gespielt ist)
    """
    print "f_shutdown"
    if allow_last_title:
        subprocess.call(['python', PATH_WAITSCRIPT])

    subprocess.call(PATH_PLAYOUT+' -c=playerstop', shell=True)
    subprocess.call(['/usr/bin/mpg123', PATH_GOODBYEMP3])
    subprocess.call(PATH_PLAYOUT+' -c=shutdown', shell=True)


def parse_params():
    parser = OptionParser("timeout.py [Optionen]")
    parser.add_option("-i", "--init",         dest="opt_init",     default=False, action="store_true", help="Initialisierung (inkl. GPIOs fuer LEDs)")
    parser.add_option("-n", "--newtimer",     dest="opt_timer",    default=None,  action="store",      help="Programmiert einen Abschalttimer")
    parser.add_option("-c", "--canceltimers", dest="opt_cancel",   default=False, action="store_true", help="Deaktiviert den aktuellen Abschalttimer")
    parser.add_option("-s", "--shutdown",     dest="opt_shutdown", default=False, action="store_true", help="Herunterfahren nach aktuellem VLC-Titel")
    (optionen, args) = parser.parse_args()

    if optionen.opt_init:
        f_init()

    elif optionen.opt_cancel:
        f_canceltimers()

    elif optionen.opt_timer and optionen.opt_timer.isdigit():
        t = int(optionen.opt_timer)
        if t > 0:
            quota_store.saveNew()
            f_newtimer(t)
        else:
            print "Keine gueltige Dauer uebergeben"

    elif optionen.opt_shutdown:
        f_shutdown(True)

    else:
        print "Kein gueltiges Kommando angegeben"


# Main / global:
parse_params()
