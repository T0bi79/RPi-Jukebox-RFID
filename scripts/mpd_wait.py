"""
    This module allows to control an mpd instance through a python interface.
    ~~~~~~~~~

    Adopted and stripped version of VLCClient. Original info:

    :author: Michael Mayr <michael@dermitch.de>
    :licence: MIT License
    :version: 0.2.0

"""

import telnetlib

from socket import error as socket_error
from time import sleep, time

DEFAULT_PORT = 6600


class mpdClient(object):
    """
    Connection to a running mpd instance with telnet interface.
    """

    def __init__(self, server, port=DEFAULT_PORT, timeout=5):
        self.server = server
        self.port = port
        self.timeout = timeout

        self.telnet = None
        self.server_version = None

    def connect(self):
        """
        Connect to mpd and login
        """
        assert self.telnet is None, "connect() called twice"

        self.telnet = telnetlib.Telnet()
        self.telnet.open(self.server, self.port, self.timeout)

        # Parse version
        result = self.telnet.expect([
            r"OK MPD ([\d.])+".encode("utf-8"),
        ], 20)

        if(result[0] < 0):
            return 0

        self.server_version = result[1].group(0)[3:]
        print 'Connected %s =) ' % (self.server_version)

        return 1

    def disconnect(self):
        """
        Disconnect and close connection
        """
        self.telnet.close()
        self.telnet = None

    def _send_command(self, line):
        """
        Sends a command to mpd and returns the text reply.
        This command may block.
        """
        self.telnet.write((line + "\n").encode("utf-8"))
        result = self.telnet.read_until("OK\n".encode("utf-8"))
        return result

    #
    # Commands
    #
    def is_playing(self):
        st = self._send_command("status")
        # print "State: ", st
        stl = st.splitlines()
        for s in stl:
            if(s.startswith('state:')):
                if(s.startswith('state: play')):
                    return 1
                if(s.startswith('state: pause')):
                    return 2
                if(s.startswith('state: stop')):
                    return 0
        return -1

    def get_title(self):
        cs = self._send_command("currentsong")
        trk = 'n/a'
        csl = cs.splitlines()
        for s in csl:
            # print "Entry ",s
            if(s.startswith('file: ')):
                trk = s[6:]
        return trk


def WaitForTitleFinish(interval_s, timeout_m):
    mpd = mpdClient("localhost")
    cr = 0
    try:
        cr = mpd.connect()
    except socket_error as serr:
        print "mpd not running (socket error %d)" % (serr.errno)
        return
    if(cr < 1):
        print "unexpected mpd banner, exiting."
        return
    is_playing = mpd.is_playing()
    if is_playing < 1:
        print 'mpd not playing'
        return
    title_str1 = mpd.get_title()
    if len(title_str1) < 1:
        print "Reading title from mpd failed"
        return
    print "Waiting for title to finish: %s (timeout: %d minutes)" % (title_str1, timeout_m)
    start = time()
    while True:
        sleep(interval_s)
        title_str2 = mpd.get_title()
        print "current title: %s" % (title_str2)
        if title_str1 != title_str2:
            break
        if timeout_m > 0 and ((time() - start) / 60) > timeout_m:
            break


if __name__ == '__main__':
    WaitForTitleFinish(5, 90)  # Checke alle 5 Sekunden, warte hoechstens 90 Minuten
