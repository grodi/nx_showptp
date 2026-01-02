#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Athor:       grodi, chgrodde@googlemail.com
# Version:     1.1
# Description:
# The script prints ptp information in an easy to read table format on NX-OS platforms.
# To reduce the table width a filter can be configured which shortens the interface descriptions as well as cdp/lldp hostnames. 
# event manager environment RMLIST "connected-to-, .mydom.dom, yyy-, zzz"
#
#
# To use:
#   1. Copy script to N9K switch bootflash:scripts/
#   2. Execute using:
# source nx_showptp.py
#   or
# source nx_showptp.py -n
#
#   3. Configure an alias, e.g.
# cli alias name sptp source nx_showptp.py
#
#   4. Configure a list removing unnessacary characters form interfaces description or the cdp/lldp neighbor hostname
# event manager environment RMLIST "connected-to-, xxx-, yyy-, zzz"
#
# The script was tested on N9K using 10.6.1 release.
#

from __future__ import division

import sys
import xml.etree.cElementTree as ET
import re
from optparse import OptionParser

try:
    from cli import cli
except:
    ignore = None

# max column width
max_descr_width = 23      # interface description
max_neigh_width = 30      # cdp/lldp neighbor column, must be >= 13

# a list of elements removed from interface description to shorten the table width
#ifdescr_rm_list = ["connected-to-", "n93108-", "n93k-"]

# MAC address to vendor mapping
mac_vendors = {
    "00:fc:ba": "Cisco",
    "9c:a9:b8": "Cisco",
    "cc:7f:76": "Cisco",
    "ec:46:70": "Meindberg"
}

def args_parser():
    usage = (
        "\n  source nx_showptp.py [option(s)]\n"
        "      valid option is -c \n"
        )
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--configuration",
                      action="store_true",
                      dest="c_flag",
                      default=False,
                      help="shows additionally the PTP message interval configuration per interface")
    options, args = parser.parse_args()

    if len(args) > 0:
        parser.error("No valid option!")

    return options


def rmlist_parser():
    ## Get character remove list from environment command
    # Run CLI command to fetch the line(s)
    try:
        with open("RMLIST.txt", "r") as f:
            env_cmd = f.read().strip()
        #env_cmd = cli('show running-config | include "event manager environment"')
    except Exception as e:
        print(f"Error running command: {e}")
        env_cmd = None

    # init character remove list with none
    rm_list = None

    if env_cmd:
        # Regex pattern for: event manager environment <VAR> "<VALUE>"
        pattern = r"event manager environment\s+(\S+)\s+\"([^\"]+)\""

        matches = re.findall(pattern, env_cmd)
        params = {key: value for key, value in matches}

        # convert to dict RMLIST to a list
        if "RMLIST" in params:
            raw_value = params["RMLIST"]
            # Split into list if you want
            rm_list = [item.strip() for item in raw_value.split(",") if item.strip()]
            # print(f"List form: {rm_list}")
            
    return rm_list


def getifdescr(l_interface, l_if_descr_root, l_rm_list):
    if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
    ifdescr = ('---')
    for d in l_if_descr_root.iter(if_manager + 'ROW_interface'):
        try:
            interface = d.find(if_manager + 'interface').text
            #print (interface)
            if interface == l_interface:
                if "loopback" in interface:
                    ifdescr = "removed"
                    break
                ifdescr = d.find(if_manager + 'desc').text
                # optimize description width
                for r in (l_rm_list or []):
                     ifdescr = ifdescr.replace(r, "")
                ifdescr = ifdescr.replace("Ethernet", "e")
                ifdescr = ifdescr[:max_descr_width-1]
                break
        except:
            pass
    return ifdescr


### Main Program ###

### Get script options
# d_flag: show interfaces with a description on it
# neigh_flag: show cdp neighbor or if not cdp try lldp neigh

option = args_parser()

print ()
print ("*** PTP Parent ***")
print ()


sys.stdout.flush()

# get ptp parent information
ptp_parent_tree = ET.ElementTree(ET.fromstring(cli('show ptp parent | xml | exclude "]]>]]>"')))
ptp_parent_root = ptp_parent_tree.getroot()
ptp = '{http://www.cisco.com/nxos:1.0:ptp}'  # same Namespace for every PTP command

# show ptp parent information
clock_id = ptp_parent_root.find('.//' + ptp + 'clock-id').text
cprefix = ":".join(clock_id.split(":")[:3])
parent_clock_vendor = mac_vendors.get(cprefix, "Unknown vendor")

parent_ip = ptp_parent_root.find('.//' + ptp + 'parent-ip').text

gm_id = ptp_parent_root.find('.//' + ptp + 'gm-id').text
gmprefix = ":".join(gm_id.split(":")[:3])
gm_vendor = mac_vendors.get(gmprefix, "Unknown vendor")

gm_class = ptp_parent_root.find('.//' + ptp + 'gm-class').text
gm_accuracy = ptp_parent_root.find('.//' + ptp + 'gm-accuracy').text
gm_scaled_log_variance = ptp_parent_root.find('.//' + ptp + 'gm-scaled-log-variance').text
gm_priority1 = ptp_parent_root.find('.//' + ptp + 'gm-priority1').text
gm_priority2 = ptp_parent_root.find('.//' + ptp + 'gm-priority2').text

print (f"Parent Clock Identity:      {clock_id} ({parent_clock_vendor})")
print ()
print (f"Parent IP: {parent_ip}")
print ()
print (f"{'Grandmaster Clock Identity:'} {gm_id} ({gm_vendor})")
print ('Grandmaster Clock Quality (in GMC election order):')
print ('    Priority 1: ' + gm_priority1)
print ('    Class: ' + gm_class)
print ('    Accuracy: ' + gm_accuracy)
print ('    Offset (log variance): ' + gm_scaled_log_variance)
print ('    Priority 2: ' + gm_priority2)
print ()

print ()
print ("*** PTP Interface States and Counters ***")
print ()

# get interface description in xml format
if_descr_tree = ET.ElementTree(ET.fromstring(cli('show interface ' + ptp_interface + ' description | xml | exclude "]]>]]>"')))
if_descr_root = if_descr_tree.getroot()
if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}' # Namespace for show interface commands

# get ptp interface state information
ptp_brief_tree = ET.ElementTree(ET.fromstring(cli('show ptp brief | xml | exclude "]]>]]>"')))
ptp_brief_root = ptp_brief_tree.getroot()

# get ptp counter format
ptp_counters_tree = ET.ElementTree(ET.fromstring(cli('show ptp counters all | xml | exclude "]]>]]>"')))
ptp_counters_root = ptp_counters_tree.getroot()

## get remove list from NX-configuration
rm_list = rmlist_parser()


# print some explanations about the table
print ('State:   m:master, s:slave, d:disabled, -:no state')
print ('MsgIntv: The PTP message interval configuration per port (Announce/Sync/DelayReq)' if option.c_flag else '')

# prepare table header
header = (
     f"{'Port':9}"
     f"{'Descr':{max_descr_width}}"
     f"{'State':6}"
     + (f"{'MsgIntv':9}" if option.c_flag else '')
     + f"{'TX-Ann.':9}{'RX-Ann.':9}"
     f"{'TX-Sync':10}{'RX-Sync':10}"
     f"{'TX-FolUp':11}{'RX-FolUp':11}"
     f"{'TX-DelReq':11}{'RX-DelResp':11}"
     f"{'RX-DelReq':11}{'TX-DelResp':11}"
)

# print table header
print ("-" * len(header))
print (header)
print ("-" * len(header))


# Find and display PTP interfaces
for i in ptp_counters_root.iter(ptp + 'ROW_ptp'):
    ptp_interface = i.find(ptp + 'interface_name').text

    # find interface description
    ptp_interface = ptp_interface.replace("Eth", "Ethernet") # normalize ptp interface name to Ethernetx/y
    if_descr = getifdescr(ptp_interface, if_descr_root, rm_list)
    ptp_interface = ptp_interface.replace("Ethernet", "Eth") # shorten the ptp interface name

    # find ptp state for a given ptp_interface
    state = ('-')
    for row in ptp_brief_root.iter(ptp + 'ROW_ptp'):
        ptp_ifindex = row.find(ptp + 'ptp-ifindex').text
     
        if ptp_ifindex is not None and ptp_ifindex == ptp_interface:
            state = row.find(ptp + 'state').text
            state = state[:1] # use only the first letter
            break


    # get ptp message interval configuration per interface when -c option is set
    if option.c_flag:
        ptp_port_tree = ET.ElementTree(ET.fromstring(cli('show ptp port interface ' + ptp_interface + ' | xml | exclude "]]>]]>"')))
        ptp_port_root = ptp_port_tree.getroot()

        # extract ptp interval configuration
        ann_intv = ptp_port_root.find('.//' + ptp + 'ann-intv').text
        sync_intv = ptp_port_root.find('.//' + ptp + 'sync-intv').text
        ann_rx_tout = ptp_port_root.find('.//' + ptp + 'ann-rx-tout').text
        delay_req_intv = ptp_port_root.find('.//' + ptp + 'delay-req-intv').text

  
    # extract ptp counter
    tx_announce_pkts = i.find(ptp + 'tx-announce-pkts').text
    rx_announce_pkts = i.find(ptp + 'rx-announce-pkts').text
    tx_sync_pkts = i.find(ptp + 'tx-sync-pkts').text
    rx_sync_pkts = i.find(ptp + 'rx-sync-pkts').text
    tx_follow_up_pkts = i.find(ptp + 'tx-follow-up-pkts').text
    rx_follow_up_pkts = i.find(ptp + 'rx-follow-up-pkts').text
    tx_delay_req_pkts = i.find(ptp + 'tx-delay-req-pkts').text
    rx_delay_resp_pkts = i.find(ptp + 'rx-delay-resp-pkts').text
    tx_delay_resp_pkts = i.find(ptp + 'tx-delay-resp-pkts').text
    rx_delay_req_pkts = i.find(ptp + 'rx-delay-req-pkts').text

    print(
        f'{ptp_interface:9}'
        f'{if_descr:{max_descr_width}}'
        f'{state:6}'
        + (f"{ann_intv:1}/{sync_intv:2}/{delay_req_intv:2}  " if option.c_flag else '')
        + f'{tx_announce_pkts:9}{rx_announce_pkts:9}'
        f'{tx_sync_pkts:10}{rx_sync_pkts:10}'
        f'{tx_follow_up_pkts:11}{rx_follow_up_pkts:11}'
        f'{tx_delay_req_pkts:11}{rx_delay_resp_pkts:11}'
        f'{rx_delay_req_pkts:11}{tx_delay_resp_pkts:11}'
    )

sys.exit()
