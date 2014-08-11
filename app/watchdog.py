#!/usr/bin/python
import apiFetch
import sqlite3
import datetime
import time
import calendar
import pprint
from os.path import isfile

def sanitizeVcode(vCode):
    return vCode[:64]

def register(subscriber, keyID, vCode):
    vCode = sanitizeVcode(vCode)
    result = apiFetch.APIFetch('characters', keyID, vCode)
    if not result.result:
        return False

    db = '../db/eveWatchdog.db'
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    insertTuple=(subscriber, 'SIP subscriber')
    cur.execute('INSERT INTO subscribers VALUES(?,?)', insertTuple)
    insertTuple=(keyID, vCode, subscriber)
    cur.execute('INSERT INTO keys(keyID, vCode, owner) VALUES(?,?,?)',insertTuple)
    conn.commit()
    conn.close()
    return True


def characterListUpdate(keyID, vCode):
    vCode = sanitizeVcode(vCode)
    characters = [None, None, None]
    result = apiFetch.APIFetch('characters', keyID, vCode)
    nameList = [None, None, None]    

    if not result.result:
        return False

    for row in result.result:
        for i, character in enumerate(row):
            characters[i] = {'name' : character['name'] , 'characterID' : character['characterID']}
            nameList[i] = character['name']
    
    db = '../db/eveWatchdog.db'
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    insertList = []
    for character in characters:
        if character is None:
            insertList.append(None)
            continue
        insertList.append(character['characterID'])

    cur.execute('UPDATE keys SET character1=?, character2=?, character3=?', tuple(insertList))
    conn.commit()
    for character in characters:
        if character:
            cur.execute('INSERT INTO characters VALUES(?,?,0)',(character['characterID'], character['name']) )
            conn.commit()
    conn.close()
    
    
    return nameList

class watchdog:

    def __init__(self, subscriber=None):
        db = '../db/eveWatchdog.db'

        if not isfile(db): 
            print 'ERROR: Database File does not exist. "%s"' % (db)
            exit()
        self.getSubscriberDetails(db, subscriber)
        
    def getSubscriberDetails(self, db, subscriber=None):
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        if subscriber is None:
            cursor.execute('SELECT keys.keyID, keys.vCode, keys.owner, characters.characterID, characters.characterName, characters.last_checked\
                           FROM keys JOIN characters \
                            WHERE (keys.character1=characters.characterID OR \
                                   keys.character2=characters.characterID OR \
                                   keys.character3=characters.characterID) AND \
                                   characters.watchdog=1')
        else:
            cursor.execute('SELECT keys.keyID, keys.vCode, keys.owner, characters.characterID, characters.characterName, characters.last_checked\
                           FROM keys JOIN characters \
                           WHERE keys.owner="{0}" AND \
                                 (keys.character1=characters.characterID OR \
                                 keys.character2=characters.characterID OR \
                                 keys.character3=characters.characterID) AND \
                                 characters.watchdog=1'.format(subscriber))

        fetchList = []
        fetchLine = {}
        for row in cursor.fetchall():
            fetchLine['keyID'] = str(row[0])
            fetchLine['vCode'] = str(row[1])
            fetchLine['owner'] = str(row[2])
            fetchLine['characterID'] = str(row[3])
            fetchLine['characterName'] = str(row[4])
            fetchLine['last_checked'] = str(row[5])
            fetchList.append(fetchLine)
            fetchLine = {}
        self.fetchStatus(fetchList)
    
    def fetchStatus(self, fetchList):
        self.subscriberStatus = []        
        client = {}
        for line in fetchList:
            result = apiFetch.APIFetch('skillQueue', line['keyID'], line['vCode'], line['characterID'])
            if not result.result:
                self.subscriberStatus.append({'Error':'Error Fetching informations from API'})
                continue
            for rowset in result.result:
                row = rowset[-1]
                endTime = parseTime(row['endTime'])
                timeLeft = (datetime.datetime(endTime['year'],endTime['month'],endTime['day'],endTime['hour'],endTime['minute']) - datetime.datetime.utcnow())
                hoursLeft = (int(datetime.timedelta.total_seconds(timeLeft))) / 3600
                minutesLeft = ((int(datetime.timedelta.total_seconds(timeLeft))) /60)  % 60
                localEndTime = datetime.datetime.now() + datetime.timedelta(hours=hoursLeft, minutes=minutesLeft)
                client = {'owner' :line['owner'], 
                          'characterName' : line['characterName'], 
                          'hoursLeft' : hoursLeft,
                          'endTime'  :localEndTime.strftime('%Y-%m-%d %H:%M'),
                          'last_checked' : line['last_checked'],
                          'characterID' : line['characterID']}
                self.subscriberStatus.append(client)
                client = {}

        return
        
    def setCheckedTime(self, characterID):
        db = '../db/eveWatchdog.db'
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        now = calendar.timegm(time.gmtime())
            
        cursor.execute('UPDATE characters set last_checked=? where characterID=?', (now, characterID))
        conn.commit()
        conn.close()

def parseTime(timeString):
    splitDate = timeString.split(' ')
    date = splitDate[0].split('-')
    time = splitDate[1].split(':')
    parsedTime = {'year' : int(date[0]), 'month' : int(date[1]), 'day' : int(date[2]), 'hour' : int(time[0]), 'minute' : int(time[1])}
    return parsedTime






