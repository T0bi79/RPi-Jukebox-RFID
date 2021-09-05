#!/usr/bin/env python3
import socket
from optparse import OptionParser

QIF_TCPSOCKET = 54711
            
# Sending of commands (Simple TCP interface to the Phoniebox Quota service)
def sendcmd(cmd):
    ip = 'localhost'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((ip, QIF_TCPSOCKET))
    try: 
        s.send(cmd.encode())
        antwort = s.recv(1024)
        print("{}".format(antwort.decode()))
    finally:
        s.close()

# Command line interface
if __name__ == "__main__":
    parser = OptionParser('ext_interface.py [options]')
    parser.add_option('-r', '--reconfigure',  dest='opt_cmd',  default=False, action='store_const', const='ini_reload',  help='Reinitialize from ini file')
    parser.add_option('-n', '--newtimer',     dest='opt_timer',default=None,  action='store',                            help='Activates new quota (in minutes)')
    parser.add_option('-a', '--aborttimers',  dest='opt_cmd',  default=False, action='store_const', const='canceltimer', help='Aborts current quota/shutdown timers')
    parser.add_option('-s', '--shutdown',     dest='opt_cmd',  default=False, action='store_const', const='sd_aftertrk', help='Shutdown after current mpd title')
    parser.add_option('-S', '--shutdownnow',  dest='opt_cmd',  default=False, action='store_const', const='sd_instant',  help='Shutdown instantly')
    parser.add_option('-g', '--getremaining', dest='opt_cmd',  default=False, action='store_const', const='getquota',    help='Gets current quota (in remaining minutes)')
    parser.add_option('-w', '--iswebquotaok', dest='opt_cmd',  default=False, action='store_const', const='getwebok',    help='Gets current flag if new quota is accepted from web interface')
    parser.add_option('-q', '--quitscript',   dest='opt_cmd',  default=False, action='store_const', const='Quit',        help='Quits the server-side service (debug feature)')
    (options, args) = parser.parse_args()
    
    cmd = None
    if options.opt_cmd:
        cmd = options.opt_cmd
    elif options.opt_timer and options.opt_timer.isdigit():
        t = int(options.opt_timer)
        if t > 0:
            cmd = 'grantquota {}'.format(60*t)
        elif t == 0:
            cmd = 'canceltimer'
        else:
            print('No valid duration given')
    elif options.opt_cfg:
        cmd = 'setconfig {}'.format(options.opt_cfg)
    else:
        print('No valid command given')

    if cmd is not None:
        sendcmd(cmd)
