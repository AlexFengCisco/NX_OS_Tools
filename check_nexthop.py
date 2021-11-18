'''
  NOTE： for static ecmp route ONLY!
  Check static route table for specific vrf, and collect all ecmp routes with next hops and preference value
  ping next hop count 3 timeout 1
  when ping next hop failed , change related route preference to 200
  when ping valid , and if related static route preference is 200 , change prefernce to 1

  Usage:
   checknh.py vrf <vrf_name>

  For scheduling @ 1-minute interval or higher, use the NX/OS scheduler:
  feature scheduler
     scheduler job name track-next-hop
      python bootflash:/checknh.py vrf xxx      (or "source Routetrack.py ...")
      exit
     scheduler schedule name track-next-hop
      time start now repeat 00:00:01

  For configuring @ 10-second interval, use EEM:
      event manager applet track-next-hop
        event snmp oid 1.3.6.1.2.1.1.3.0 get-type exact entry-op ge entry-val 0 poll-interval 10
        action 1.0 cli command python bootflash:/checknh.py vrf xxx  (or "source RouteTrack.py ...")

  Alex Feng

'''
import sys
import json
import cli
import re
import cisco
import syslog

self = sys.argv[0]
argv = sys.argv[1:]

# command line input with vrf name
if argv[0] != 'vrf':
    err = 'error ,miss key word "vrf".'
    syslog.syslog(1, err)

if argv[1]:
    vrf = argv[1]

# collect static ecmp routing table with next hop and preference
show_route_json = cli.clid('show ip route static vrf ' + vrf)
show_route = json.loads(show_route_json)
prefix_info = show_route["TABLE_vrf"]["ROW_vrf"]["TABLE_addrf"]["ROW_addrf"]["TABLE_prefix"]["ROW_prefix"]

route_ecmp = []
next_hops = []
for prefix in prefix_info:
    if type(prefix["TABLE_path"]["ROW_path"]) == list:
        for next_hop in prefix["TABLE_path"]["ROW_path"]:
            if next_hop["ipnexthop"] not in next_hops:  # unique next hop to save ping respnose time
                next_hops.append(next_hop["ipnexthop"])
            route_ecmp.append([prefix["ipprefix"], next_hop["ipnexthop"], next_hop["pref"]])

    else:
        # not list , not ecmp
        pass

# ping all next hops
for next_hop in next_hops:
    ping_next_hop = cli.cli('ping ' + next_hop + ' vrf ' + vrf + ' count 3 timeout 1')
    pingvalid = True if re.search(r"packet loss", ping_next_hop) else False
    pingfailed = True if re.search(r"100.00% packet loss", ping_next_hop) else False

    if pingfailed:

        for route in route_ecmp:
            # change route pre to 200 and syslog
            if route[1] == next_hop and route[2] == '1':
                syslog.syslog(1, 'ping next hop ' + next_hop + ' failed.')
                syslog.syslog(1, 'change vrf context ' + vrf + '  ip route ' + route[0] + ' ' + next_hop + ' 200')
                cli.cli('conf t ; vrf context ' + vrf + ' ; ip route ' + route[0] + ' ' + next_hop + ' 200')

    else:
        for route in route_ecmp:
            # change route pre to 1 and syslog
            if route[1] == next_hop and route[2] == '200':
                syslog.syslog(1, 'Next hop ' + next_hop + ' valid.')
                syslog.syslog(1, 'change vrf context ' + vrf + '  ip route ' + route[0] + ' ' + next_hop + ' 1')
                cli.cli('conf t ; vrf context ' + vrf + ' ; ip route ' + route[0] + ' ' + next_hop + ' 1')


