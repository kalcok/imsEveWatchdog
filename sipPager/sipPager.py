#!/usr/bin/python
import sys
import pjsua as pj
import threading
from PyQt4 import QtGui as qgui
from PyQt4.QtCore import *
from functools import partial
DEFAULT=0
ERROR=1
SUCCESS=2

class popupMessage(qgui.QWidget):
    def __init__(self, _from, message):
        super(popupMessage, self).__init__()
        self._from = _from
        self.body = message
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 250, 520, 150)
        self.setMinimumSize(320, 150)
        self.setWindowTitle('Message Recieved')
        self.setWindowIcon(qgui.QIcon('../misc/icon.jpg'))

        self.label1 = qgui.QLabel()
        self.label1.setText('From: {0}'.format(self._from))
        
        self.label2 = qgui.QLabel()
        self.label2.setText('Message:')
        
        self.message1 = qgui.QTextEdit()
        self.message1.setReadOnly(True)
        
        self.form1 = qgui.QFormLayout()
        self.form1.addRow(self.label1)
        self.form1.addRow(self.label2)
        self.form1.addRow(self.message1)

        self.setLayout(self.form1)
        
        printMessage(self.message1, self.body)
        self.show()
       


class pagerWindow(qgui.QWidget):
    def __init__(self, parent, acc):
        super(pagerWindow, self).__init__()
        self.acc = acc
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 200, 520, 300)
        self.setMinimumSize(320, 300)
        self.setWindowTitle('Sip Pager')
        self.setWindowIcon(qgui.QIcon('../misc/icon.jpg'))

        self.label1 = qgui.QLabel()
        self.label1.setText('To:')

        self.label2 = qgui.QLabel()
        self.label2.setText('Text Message:')

        self.btn1 = qgui.QPushButton('Send', self)
        self.btn1.clicked.connect(self.onBtn1)
        self.btn1.setMaximumWidth(75)
        self.btn1.setAutoDefault(True)
        self.btn1.setDefault(True)

        self.btn2 = qgui.QPushButton('Logout', self)
        self.btn2.clicked.connect(self.onBtn2)
        self.btn2.setMaximumWidth(75)

        self.edit1 = qgui.QLineEdit()
        self.edit1.returnPressed.connect(self.btn1.click)
        self.edit1.setMaximumWidth(200)
        self.edit1.setToolTip('Recipient example: <b>alice@example.org</b>')
        self.edit1.setPlaceholderText('alice@example.org')

        self.message1 = qgui.QTextEdit()
        self.message1.setReadOnly(False)
        self.message1.setMaximumWidth(500)
        
        self.form1 = qgui.QFormLayout()
        self.form1.addRow(self.label1, self.edit1)

        self.form2 = qgui.QFormLayout()
        self.form2.addRow(self.label2)
        self.form2.addRow(self.message1)

        self.vbox1 = qgui.QVBoxLayout()
        self.vbox1.addLayout(self.form1)
        self.vbox1.addLayout(self.form2)
        self.vbox1.addWidget(self.btn1)
        self.vbox1.addWidget(self.btn2)
        self.setLayout(self.vbox1)
        self.show()

    def onBtn1(self):
        _to = str(self.edit1.text())
        body = str(self.message1.toPlainText())
        self.acc.send_pager('sip:{0}'.format(_to), body)

    def onBtn2(self):
        self.parent.lib.destroy()
        printMessage(self.parent.log1, 'Succesfuly logged out (Please dont try to log back, not implemented yet :D)')
        self.parent.show()
        self.close()

class loginWindow(qgui.QWidget):
    def __init__(self):
        super(loginWindow, self).__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 200, 520, 300)
        self.setMinimumSize(320, 300)
        self.setWindowTitle('Sip Pager (Login)')
        self.setWindowIcon(qgui.QIcon('../misc/icon.jpg'))

        self.label1 = qgui.QLabel()
        self.label1.setText('Server address')

        self.label2 = qgui.QLabel()
        self.label2.setText('Login')

        self.label3 = qgui.QLabel()
        self.label3.setText('Password')

        self.btn1 = qgui.QPushButton('Connect', self)
        self.btn1.clicked.connect(self.onBtn1)
        self.btn1.setMaximumWidth(75)
        self.btn1.setAutoDefault(True)
        self.btn1.setDefault(True)

        self.edit1 = qgui.QLineEdit()
        self.edit1.returnPressed.connect(self.btn1.click)
        self.edit1.setMaximumWidth(200)
        self.edit1.setToolTip('Address example: <b>192.168.2.1:8080</b> or <b>example.org</b>')
        self.edit1.setPlaceholderText('Leave blank for localhost')

        self.edit2 = qgui.QLineEdit()
        self.edit2.returnPressed.connect(self.btn1.click)
        self.edit2.setMaximumWidth(200)
        self.edit2.setToolTip('Your Login name')
        self.edit2.setPlaceholderText('Smith')

        self.edit3 = qgui.QLineEdit()
        self.edit3.returnPressed.connect(self.btn1.click)
        self.edit3.setMaximumWidth(200)
        self.edit3.setToolTip('Your password')
        self.edit3.setPlaceholderText('******')

        self.form1 = qgui.QFormLayout()
        self.form1.addRow(self.label1, self.edit1)
        self.form1.addRow(self.label2, self.edit2)
        self.form1.addRow(self.label3, self.edit3)
        self.form1.addRow(self.btn1)

        self.log1 = qgui.QTextEdit()
        self.log1.setReadOnly(True)
        self.log1.setMaximumWidth(500)

        self.vbox1 = qgui.QVBoxLayout()
        self.vbox1.addLayout(self.form1)
        self.vbox1.addWidget(self.log1)
        self.setLayout(self.vbox1)
        self.show()

    def onBtn1(self):
        server = str(self.edit1.text())
        login = str(self.edit2.text())
        passwd = str(self.edit3.text())
        connInfo = self.sipConnect(login, passwd, server)
        self.acc = connInfo[0]
        self.lib = connInfo[1]
        if not self.acc:
            return
        self.pgw = pagerWindow(self, self.acc)
        self.hide()

    def showMsg(self, _from, body):
        self.popup=popupMessage(_from, body)

    def sipConnect(self, login, passwd, server):
        try:
            lib = pj.Lib()
            lib.init(log_cfg = pj.LogConfig(level=4, callback=log_cb))
            lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5062))
            lib.start()
         
            acc = lib.create_account(pj.AccountConfig(server, login, passwd))
         
            acc_cb = MyAccountCallback(acc, self)
            acc.set_callback(acc_cb)
            acc_cb.wait()
            
            if acc.info().reg_status is 200:
                msg = "Registration complete, status=", acc.info().reg_status, \
                        "(" + acc.info().reg_reason + ")"
                printMessage(self.log1, msg, SUCCESS)
                return [acc, lib]
            else:
                msg = "Registration Failed, status=", acc.info().reg_status, \
                        "(" + acc.info().reg_reason + ")"
                printMessage(self.log1, msg, ERROR)
                lib.destroy()
                return None

        except pj.Error, e:
            msg = "Exception: " + str(e)
            printMessage(self.log1, msg, ERROR)
            lib.destroy()
            return None
     
 
def log_cb(level, str, len):
    print str,
  
class MyAccountCallback(pj.AccountCallback, QObject):
    sem = None
    trigger = pyqtSignal()
    def __init__(self, account, display):
        QObject.__init__(self)
        pj.AccountCallback.__init__(self, account)
        self.display = display
  
    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()
  
    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def on_pager(self, _from, _to, mime_type, body):
        self.trigger.connect(partial(self.display.showMsg, _from, body))
        self.trigger.emit()

def printMessage(textedit, message, _type=0):
    if _type == ERROR:
        textedit.append('<font color="red">'+str(message)+'</font>')
    elif _type == SUCCESS:
        textedit.append('<font color="green">'+str(message)+'</font>')
    elif _type == DEFAULT:
        textedit.append(message)
    textedit.ensureCursorVisible()


def sendMsg():
    global acc
    f = open('./msg','r')
    
    _to = f.readline()
    body = f.readline()


app = qgui.QApplication(sys.argv)
logWindow = loginWindow()
sys.exit(app.exec_())


