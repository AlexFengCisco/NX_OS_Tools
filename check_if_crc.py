'''
  to solve NX OS has no port guard or port level guard to disable interface when crc cunter reach threshold
'''
import cli
import time
import json
import syslog

# collect intterface brief
intBriJson = json.loads(cli.clid("show int brief"))
intList = intBriJson['TABLE_interface_brief_fc']['ROW_interface_brief_fc']
intUpList = []

# add up interdace to uplist
for int in intList:
    if int[u'status'] == u'down' and int[u'interface_fc']:
        intUpList.append(int[u'interface_fc'])

# check crc counter for each up interface
for int in intUpList:
    showIntCmd = 'show int ' + str(int)
    # print(showIntCmd)
    intInfoJson = json.loads(cli.clid(showIntCmd))
    # print(intInfoJson[u'TABLE_interface'][u'ROW_interface'][u'invalid_crc'])
    if int(intInfoJson[u'TABLE_interface'][u'ROW_interface'][u'invalid_crc']) > 100:
        syslog.syslog(1, 'Warnning , interface ' + str(int) + ' crc counter excced 100.')
    if int(intInfoJson[u'TABLE_interface'][u'ROW_interface'][u'invalid_crc']) > 200:
        syslog.syslog(1, 'Alarm , interface ' + str(int) + ' crc counter excced 200.')
        cli.cli("conf t ; int fc 2/4 ; shutdown")
