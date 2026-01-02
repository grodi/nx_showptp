# nx_showptp
The script prints ptp information in an easy to read table format on NX-OS platforms.
To reduce the table width a filter can be configured which shortens the interface descriptions as well as cdp/lldp hostnames. <br>
```event manager environment RMLIST "connected-to-, .mydom.dom, yyy-, zzz"```

To use:
1. Copy script to N9K switch ```bootflash:scripts/```
2. Execute using:
```
source nx_showptp.py
```
or
```
source nx_showptp.py -n
```

4. Configure an alias, e.g.
```
cli alias name sptp source nx_showptp.py
```

 5. Configure a list removing unnessacary characters form interfaces description or the cdp/lldp neighbor hostname
```
event manager environment RMLIST "connected-to-, xxx-, yyy-, zzz"
```

The script was tested on N9K using 10.6.1 release.

