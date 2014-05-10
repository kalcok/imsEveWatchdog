#!/usr/bin/python
from xml.dom import minidom

def parseResult(result):
     
    for rowsetSG in result[0].getElementsByTagName('rowset'):
        print 'Big Name %s' % (rowsetSG.attributes['name'].value)
        for rowSG in rowsetSG.getElementsByTagName('row'):
            try:
                print 'Skill Group: %s' % (rowSG.attributes['groupName'].value)
            except:
                pass
            for rowsetS in rowSG.getElementsByTagName('rowset'):
                for rowS in rowsetS.getElementsByTagName('row'):
                    try:
                        print '  Skill: %s' % (rowS.attributes['typeName'].value)
                    except KeyError:
                        pass

inFile = minidom.parse('skilltree.xml')
result = inFile.getElementsByTagName('result')
parseResult(result)
 
