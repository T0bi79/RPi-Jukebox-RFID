from time import time
import subprocess


def prepare_shutdown(shutcmd, farewell_mp3, farewell_dur, canceltime_dur, schedule_dur):
    min_wait_secs = 0  # this variable will receive the minimum amount of seconds for which the shutdown will be sheduled

    # respect the passed amound of seconds that the user has cancel the shutdown
    min_wait_secs += canceltime_dur

    # respect the length of a passed farewell sound
    if farewell_mp3 and farewell_dur > 0:
        min_wait_secs += msg_mp3_len

    # respect the passed shedule time
    if schedule_dur > 0:
        min_wait_secs += schedule_dur

    # "at" only has minute resulution, so we have to determine the closest duration
    minutes_to_wait = min_wait_secs / 60  # first, round down
    if((min_wait_secs % 60) > (60 - (time() % 60))):
        minutes_to_wait += 1  # if the remainder does not fit into the rest of the running minute, add 1 minute

    cmd_schedshut = 'echo "'+shutcmd+'" | sudo at -q q now + '+str(minutes_to_wait)+' minutes; exit 0'
    res_schedshut = subprocess.check_output(cmd_schedshut, stderr=subprocess.STDOUT, shell=True)
    if(res_schedshut and res_schedshut.strip()):
        if not('warning: commands will be executed using /bin/sh' in res_schedshut):
            print 'Error: '+res_schedshut

    # Info vorspielen, dass gleich ausgeht
    if farewell_mp3:
        subprocess.call(['/usr/bin/mpg123', farewell_mp3])


def cancelTimers():
    atqres = subprocess.check_output('sudo atq -q q', shell=True)
    if len(atqres) > 0:
        subprocess.call("sudo atrm $(sudo atq -q q | cut -f1)", shell=True)
