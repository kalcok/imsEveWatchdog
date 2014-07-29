#!/usr/bin/python
  # $Id$
  #
  # SIP account and registration sample. In this sample, the program
  # will block to wait until registration is complete
  #
  # Copyright (C) 2003-2008 Benny Prijono <benny@prijono.org>
  #
  # This program is free software; you can redistribute it and/or modify
  # it under the terms of the GNU General Public License as published by
  # the Free Software Foundation; either version 2 of the License, or
  # (at your option) any later version.
  #
  # This program is distributed in the hope that it will be useful,
  # but WITHOUT ANY WARRANTY; without even the implied warranty of
  # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  # GNU General Public License for more details.
  #
  # You should have received a copy of the GNU General Public License
  # along with this program; if not, write to the Free Software
  # Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
  #
import sys
import pjsua as pj
import threading
  
  
def log_cb(level, str, len):
    print str,

def readConfig():
    config ={}
    for line in open('./sip.conf', 'r'):
        line = line.rstrip('\n')
        if line is '':
            continue
        if (line[0] is '' or
            line[0] is ' ' or 
            line[0] is '#'):
            continue
        linesplit = line.split('=')
        config[linesplit[0]] = linesplit[1]
    return config
            
  
class MyAccountCallback(pj.AccountCallback):
    sem = None
  
    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)
  
    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()
  
    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def on_pager(call_id, _from, _to, mime_type, body):
        print 'DOSTAL SOM SPRAAAVUUU'

config = readConfig()
print config

lib = pj.Lib()
  
try:
    lib.init(log_cfg = pj.LogConfig(level=4, callback=log_cb))
    print int(config['port'])
    lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(int(config['port'])))
    lib.start()
 
    acc = lib.create_account(pj.AccountConfig(config['domain'], config['user'], config['password']))
  
    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()
  
    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
            "(" + acc.info().reg_reason + ")"
    print "\nPress ENTER to quit"
    sys.stdin.readline()
  
    lib.destroy()
    lib = None
  
except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
  
