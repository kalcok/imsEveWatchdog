#!/usr/bin/python
import sys
import pjsua as pj
import threading

def log_cb(level, str, len):
    print str,

class MyAccountCallback(pj.AccountCallback):
    sem = None
  
    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)
        self.acc = account

        
   
    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()
  
    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def on_pager(self, _from, _to, mime_type, body):
        pass



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



def remind():
    try:
        config = readConfig()
        lib = pj.Lib()
        lib.init(log_cfg = pj.LogConfig(level=4, callback=log_cb))
        lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5065))
        lib.start()
     
        acc = lib.create_account(pj.AccountConfig(config['domain'], config['user'], config['password']))
     
        acc_cb = MyAccountCallback(acc)
        acc.set_callback(acc_cb)
        acc_cb.wait()
        
        acc.send_pager('sip:eve_watchdog@10.0.2.15', 'reminder')   

        lib.destroy()
    except pj.Error, e:
        print "Exception: " + str(e)
        lib.destroy()


remind()
