#!/usr/bin/python
import apiFetch
import sqlite3
import datetime
import pprint
from os.path import isfile

def parseTime(timeString):
    splitDate = timeString.split(' ')
    date = splitDate[0].split('-')
    time = splitDate[1].split(':')
    parsedTime = {'year' : int(date[0]), 'month' : int(date[1]), 'day' : int(date[2]), 'hour' : int(time[0]), 'minute' : int(time[1])}
    return parsedTime

db = '../db/eveWatchdog.db'

if not isfile(db): 
    print 'ERROR: Database File does not exist. "%s"' % (db)
    exit()

conn = sqlite3.connect(db)
cursor = conn.cursor()

cursor.execute('SELECT keys.keyID, keys.vCode, keys.owner, characters.characterID, characters.characterName\
                FROM keys JOIN characters \
                WHERE (keys.character1=characters.characterID OR \
                       keys.character2=characters.characterID OR \
                       keys.character3=characters.characterID) AND \
                       characters.watchdog=1')

fetchList = []
fetchLine = {}

for row in cursor.fetchall():
    fetchLine['keyID'] = str(row[0])
    fetchLine['vCode'] = str(row[1])
    fetchLine['owner'] = str(row[2])
    fetchLine['characterID'] = str(row[3])
    fetchLine['characterName'] = str(row[4])
    fetchList.append(fetchLine)
    fetchLine = {}

#TODO: warn only if less than 24h
for line in fetchList:
    result = apiFetch.APIFetch('skillQueue', line['keyID'], line['vCode'], line['characterID'])
    for rowset in result.result:
        row = rowset[-1]
        endTime = parseTime(row['endTime'])
        timeLeft = (datetime.datetime(endTime['year'],endTime['month'],endTime['day'],endTime['hour'],endTime['minute']) - datetime.datetime.utcnow())
        hoursLeft = (int(datetime.timedelta.total_seconds(timeLeft))) / 3600
        minutesLeft = ((int(datetime.timedelta.total_seconds(timeLeft))) /60)  % 60
        localEndTime = datetime.datetime.now() + datetime.timedelta(hours=hoursLeft, minutes=minutesLeft)
        print 'Dear %s, skill queue of your Character-%s ends in %d hours, at %s' % (line['owner'], line['characterName'], hoursLeft, localEndTime.strftime('%Y-%m-%d %H:%M'))







