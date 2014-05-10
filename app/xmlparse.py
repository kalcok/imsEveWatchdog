#!/usr/bin/python
from xml.dom import minidom
import pprint

def parseResult(result):
    for rowset in result[0].getElementsByTagName('rowset'):
        print'API call: %s \n' % (rowset.attributes['name'].value)
        columns = []
        for key in str(rowset.attributes['columns'].value).split(','):
            columns.append(key)
        for row in rowset.getElementsByTagName('row'):
            for key in columns:
                print '%s: %s' % (key,row.attributes[key].value)
            print '\n'


xmldoc = minidom.parse('sheet.xml')
result = xmldoc.getElementsByTagName('result')
parseResult(result)

