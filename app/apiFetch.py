#!/usr/bin/python
import requests
import ast
import logging
from xml.dom import minidom
from sys import exit

uri = {'characters' : 'account/characters.xml.aspx', 'skillQueue' : 'char/SkillQueue.xml.aspx'}
eveURL = 'https://api.eveonline.com/'
class APIFetch:
    

    def __init__(self, req, keyID, vCode, characterID=None):
        self.req = uri[req]
        self.payload = {'keyID' : keyID, 'vCode' : vCode, 'characterID' : characterID}
        self.result = []
        print 'Call {0}{1}  {2}'.format(eveURL,self.req, self.payload)
        try:
            r = requests.get(eveURL+self.req, params = self.payload)
        except requests.exceptions.ConnectionError:
            print('ERROR: Could not connect to %s') % (eveURL)
            return None 

        response = minidom.parseString(r.text)
        xmlResult = response.getElementsByTagName('result')

        if not xmlResult:
            self.result = False
            return

        self.parseResult(xmlResult)
        return

    def parseResult(self, result):
        
        parsedRowset = []
        parsedRow = {}
        for rowset in result[0].getElementsByTagName('rowset'):
            columns = []
            for key in str(rowset.attributes['columns'].value).split(','):
                columns.append(key)
            for row in rowset.getElementsByTagName('row'):
                for key in columns:
                    parsedRow[str(key)] = str(row.attributes[key].value)
                parsedRowset.append(parsedRow)
                parsedRow = {}
            self.result.append(parsedRowset)
        


