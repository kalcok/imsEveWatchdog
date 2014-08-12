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
import sqlite3
import re
import watchdog
import time
import calendar
from os.path import isfile

  
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

def truncateSubscriberName(subscriber):
    subscriber = subscriber.rstrip('>')
    subscriber = subscriber.lstrip('sip:<')
    return subscriber 

def subscriberExists(subscriber):
    db = '../db/eveWatchdog.db'
    if not isfile(db): 
        print 'ERROR: Database File does not exist. "%s"' % (db)
        exit()
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    insertTuple = subscriber,
    cur.execute('SELECT SIPname FROM subscribers WHERE SIPname=?', tuple(insertTuple))
    result = cur.fetchall()
    if len(result) > 0:
        conn.close()
        return True
    conn.close()
    return False

def getLastTimeChecked(ts):
    now = calendar.timegm(time.gmtime())
    diff = now - int(ts)
    inHours = diff/3600
    return inHours

  

class MyAccountCallback(pj.AccountCallback):
    sem = None
  
    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)
        global acc
        self.acc = acc
        
   
    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()
  
    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def on_pager(self, _from, _to, mime_type, body):

        pattern = re.compile('^register', re.IGNORECASE)
        match = pattern.match(body)
        if match:
            self.try_register(_from, body)
            return

        pattern = re.compile('^status', re.IGNORECASE)
        match = pattern.match(body)
        if match:
            self.getStatus(_from)
            return
        
        pattern = re.compile('^reminder', re.IGNORECASE)
        match = pattern.match(body)
        if match:
            self.reminder()
            return

        pattern = re.compile('^subscribe', re.IGNORECASE)
        match = pattern.match(body)
        if match:
            self.subscribe(_from, body)
            return

        pattern = re.compile('^unsubscribe', re.IGNORECASE)
        match = pattern.match(body)
        if match:
            self.unsubscribe(_from, body)
            return

    def unsubscribe(self, subscriber, body):
        subscriber = truncateSubscriberName(subscriber)
        pattern = re.compile('^unsubscribe \d{1}')
        match = pattern.match(body)
        if not match:
            acc.send_pager('sip:{0}'.format(subscriber), 'Wrong message format. Proper Unsubscribe Message: UNSUBSCRIBE {character_number}')
            return
        parsedBody = body.split(' ')
        character = parsedBody[1][0]
        charName = watchdog.setWatchdog(subscriber, character, 0)
        acc.send_pager('sip:{0}'.format(subscriber), 'Dear {0}, you succesfully unsubscribed your character {1}'.format(subscriber, charName))

    def subscribe(self, subscriber, body):
        subscriber = truncateSubscriberName(subscriber)
        pattern = re.compile('^subscribe \d{1}')
        match = pattern.match(body)
        if not match:
            acc.send_pager('sip:{0}'.format(subscriber), 'Wrong message format. Proper Subscribe Message: SUBSCRIBE {character_number}')
            return
        parsedBody = body.split(' ')
        character = parsedBody[1][0]
        charName = watchdog.setWatchdog(subscriber, character, 1)       
        acc.send_pager('sip:{0}'.format(subscriber), 'Dear {0}, you succesfully subscribed your character {1}'.format(subscriber, charName))

    def try_register(self, subscriber, body):
        subscriber = truncateSubscriberName(subscriber)
        if subscriberExists(subscriber):
            acc.send_pager('sip:{0}'.format(subscriber), 'Dear {0}, you are already subscribed :)'.format(subscriber))
            return
        match = re.compile('^register \d{7} \w{64}$')
        if match.match(body):
            body = body.split(' ')
            success = watchdog.register(subscriber, body[1], body[2])
            if not success:
                self.acc.send_pager('sip:{0}'.format(subscriber), ' API you provided is not valid. Please check API information you provided')
                return
            availableChars = watchdog.characterListUpdate(body[1], body[2])
            self.acc.send_pager('sip:{0}'.format(subscriber), 'You Successfuly registered your account\nFolowing are characters available on your account.\n\
1. {0}\n\
2. {1}\n\
3. {2}\n\
In order to recieve warnings about free space in skillqueue you !NEED! to subscribe \
at least 1 character to be watched. Please send message in format "subscribe {{character_number}}"'.format(*tuple(availableChars)))
            
        else:    
            acc.send_pager('sip:{0}'.format(subscriber), 'Malformed Registration request.\nProper formating: "REGISTER {keyID} {vCode}"')

    def reminder(self):
        eveInfo = watchdog.watchdog()
        responseSet = eveInfo.subscriberStatus
        for row in responseSet:
            sinceLastCheck = getLastTimeChecked(row['last_checked'])
            if row['hoursLeft'] < 24 and sinceLastCheck < 8:
                acc.send_pager('sip:{0}'.format(row['owner']), 'Dear {0} your character {1} has last {2} hours left in skill queue'.format(row['owner'], row['characterName'], row['hoursLeft']))
                eveInfo.setCheckedTime(row['characterID'])

    def getStatus(self, subscriber):
        subscriber = truncateSubscriberName(subscriber)
        eveInfo = watchdog.watchdog(subscriber)
        responseSet = eveInfo.subscriberStatus
        if not responseSet:
            response='You are not registered.\nPlease register by sending message in format: REGISTER {keyID} {vCode}'
            self.acc.send_pager('sip:{0}'.format(subscriber), response)
            return
        response = 'Dear {0}, '.format(subscriber)
        for row in responseSet:
            if 'Error' in row.keys():
                self.acc.send_pager('sip:{0}'.format(subscriber), 'Error fetching information from API')
                return
            response += 'Your cahracter {0} has {1} hours left in skill queue. Skillqueue ends at {2}\n'.format(row['characterName'], row['hoursLeft'], row['endTime'])
        self.acc.send_pager('sip:{0}'.format(subscriber), response)

config = readConfig()
print config

lib = pj.Lib()
  
try:
    lib.init(log_cfg = pj.LogConfig(level=4, callback=log_cb))
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
  
