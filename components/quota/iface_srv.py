#!/usr/bin/env python3
import socket

QIF_TCPSOCKET = 54711

# Simple TCP server interface to the Phoniebox Quota service
class quota_if_server():

    def __init__(self, quota_svc, logger=None):
        self.sock = None
        self.ifcancel = False
        self.quota_svc = quota_svc
        self.logger = logger
        
    def log(self, str):
        if self.logger is not None:
            self.logger.info(str)
    
    # Socket initialization
    def initSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind(("", QIF_TCPSOCKET))
        except OSError as serr:
            self.log('TCP port {} already in use.'.format(QIF_TCPSOCKET))
            self.quota_svc.stopservice()
            self.sock.close()
            return False

        self.log('Bound to TCP socket {}.'.format(QIF_TCPSOCKET))
        return True

    # Receiving of commands
    def monitorSocket(self):
        self.log('Monitoring TCP Socket {}.'.format(QIF_TCPSOCKET))
        self.sock.listen(1)
        while not self.ifcancel:
            komm, addr = self.sock.accept()
            while not self.ifcancel: 
                data = komm.recv(1024)
                if not data: 
                    komm.close()
                    break
                request = data.decode()
                self.log('Received: [{}] {}'.format(addr[0], request))
                response = 'OK'
                resp = self.handleCommand(request.lower())
                if resp is not None:
                    response = '{}'.format(resp)
                komm.send(response.encode()) 
                self.log('Response: {}'.format(response))
        self.sock.close()
        self.sock = None
        self.log('Stopped monitoring TCP Socket {}.'.format(QIF_TCPSOCKET))

    # Handling of commands
    def handleCommand(self, cmd):
        ret = None
        if cmd.startswith('grantquota'):
            param = cmd[10:].strip()
            if param.isdigit():
                secs = int(param)
                self.log('Granting new quota of {}sec. ..'.format(secs))
                self.quota_svc.newTimer(secs)
            else:
                self.log('Parameter missing or invalid...')
        elif cmd == 'canceltimer':
            self.quota_svc.cancelTimer()
        elif cmd == 'sd_aftertrk':
            self.quota_svc.shutdown(False)
        elif cmd == 'sd_instant':
            self.quota_svc.shutdown(True)
        elif cmd == 'getquota':
            ret = self.quota_svc.getRemainingMinutes()
        elif cmd == 'ini_reload':
            self.quota_svc.initalizeFromIniFile()
        elif cmd == 'getwebok':
            ret = '1' if self.quota_svc.config.getboolean('QuotaConfig', 'quota_via_webif') else '0'
        elif cmd == 'quit':
            self.ifcancel = True
            self.quota_svc.stopservice()

        return ret
            
# Command line interface (client-side)
if __name__ == "__main__":
    pass