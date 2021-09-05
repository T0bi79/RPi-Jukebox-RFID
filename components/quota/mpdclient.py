#!/usr/bin/env python3
"""
    This module allows to control an mpd instance through a python interface.
    ~~~~~~~~~

    Adopted and stripped version of VLCClient. Original info:

    :author: Michael Mayr <michael@dermitch.de>
    :licence: MIT License
    :version: 0.2.0

"""

import telnetlib
import logging
from socket import error as socket_error

DEFAULT_PORT = 6600

class mpdClient:
    """
    Connection to a running mpd instance with telnet interface.
    """

    def __init__(self, server, port=DEFAULT_PORT, timeout=5, logger=None):
        self.server = server
        self.port = port
        self.timeout = timeout
        self.logger = logger

        self.telnet = None
        self.server_version = None

    def log(self, str):
        if self.logger is not None:
            self.logger.info(str)

    def connect(self):
        """
        Connect to mpd and login
        """
        assert self.telnet is None, "connect() called twice"

        try:

            self.telnet = telnetlib.Telnet()
            self.telnet.open(self.server, self.port, self.timeout)

            # Parse version
            result = self.telnet.expect([
                r"OK MPD ([\d.])+".encode("utf-8"),
            ], 20)

            if(result[0] < 0):
                self.log('unexpected mpd banner, exiting.')
                self.disconnect()
                return False

            self.server_version = result[1].group(0)[3:]
            self.log('Connected {} =) '.format(self.server_version))

            return True
            
        except socket_error as serr:
            self.log('mpd not running (socket error {})'.format(serr.errno))
            return False


    def disconnect(self):
        """
        Disconnect and close connection
        """
        if self.telnet is not None:
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
        # self.log('State: {}'.format(st))
        stl = st.splitlines()
        for s in stl:
            #self.log('Debug s={}.'.format(s))
            
            if(s.startswith(b'state:')):
                if(s.startswith(b'state: play')):
                    return 1
                if(s.startswith(b'state: pause')):
                    return 2
                if(s.startswith(b'state: stop')):
                    return 0
        return -1

    def get_title(self):
        cs = self._send_command("currentsong")
        trk = 'n/a'
        csl = cs.splitlines()
        for s in csl:
            # self.log('Entry {}'.format(s))
            if(s.startswith(b'file: ')):
                trk = s[6:]
        return trk


