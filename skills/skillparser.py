#!/usr/bin/python
from xml.dom import minidom
import sqlite3
import requests
from os.path import isfile

def xmlToDb(conn, result):
    cursor = conn.cursor()
    for rowsetSG in result[0].getElementsByTagName('rowset'):
        if rowsetSG.attributes['name'].value == 'skills':
           break
        print 'Big Name %s' % (rowsetSG.attributes['name'].value)
        for rowSG in rowsetSG.getElementsByTagName('row'):
            try:
                print 'Skill Group: %s' % (rowSG.attributes['groupName'].value)
            except:
                pass
            for rowsetS in rowSG.getElementsByTagName('rowset'):
                for rowS in rowsetS.getElementsByTagName('row'):
                    try:
                        skillID = int(rowS.attributes['typeID'].value)
                        skillName = rowS.attributes['typeName'].value
                        cursor.execute('''INSERT OR REPLACE INTO skills (skillID, skillName) values(?,?)''', (skillID, skillName))
                        print '  Skill: %s | ID: %d' % (skillName,skillID)
                    except KeyError:
                        
                        pass
    conn.commit()


skillTreeUrl = 'https://api.eveonline.com/eve/SkillTree.xml.aspx'
db = '../db/eveWatchdog.db'

if not isfile(db): 
    print 'ERROR: Database File does not exist. "%s"' % (db)
    exit()
conn = sqlite3.connect(db)


try:
    r = requests.get(skillTreeUrl)
except requests.exceptions.ConnectionError:
    print('Error: Could not connect to %s') % (skillTreeUrl)
    exit()

try:
    xmlFile = open('skilltree.xml', 'w')
    xmlFile.write(r.text)
    xmlFile.close()
except (IOError, NameError) as exception:
    print 'Error opening skilltree.xml'
    exit()

xmlFile = minidom.parse('skilltree.xml')
result = xmlFile.getElementsByTagName('result')
xmlToDb(conn, result)
 
