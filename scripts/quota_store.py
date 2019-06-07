from time import time
import os.path
import subprocess

PATH_LOCKFILE     = "/home/pi/jukelock.txt" # Datei, in der der Kontingentverbrauch ueber Neustarts hinweg festgehalten wird

def saveNew():
    cmd_t = 'sudo touch %s' % PATH_LOCKFILE 
    subprocess.call(cmd_t, shell=True) # Erzeuge dann Datei mit aktuellem Zeitstempel (d.h.: neues Kontingent ab jetzt)
    
def getConsumption():
    if not(os.path.isfile(PATH_LOCKFILE)):
        print 'lockfile does not exist, creating new one'
        saveNew()
        return 0
    
    verbraucht = (time() - os.path.getmtime(PATH_LOCKFILE)) / 60 # Das bereits verbrauchte Kontingent ist das Alter der Datei PATH_LOCKFILE
    print 'lockfile exists, age is', verbraucht
    return verbraucht
