# nx_showptp
The script prints ptp information in an easy to read table format on NX-OS platforms.<br>
Additionaly the ptp interval configuration can be shown for each interface.<br>
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
   source nx_showptp.py -c
   ```
3. Configure an alias, e.g.
   ```
   cli alias name sptp source nx_showptp.py
   ```
4. Configure a list removing unnessacary characters form interfaces description
   ```
   event manager environment RMLIST "connected-to-, xxx-, yyy-, zzz"
   ```

The script was tested on N9K using 10.6.1 release.

## Sample Output
```
n9k-spine# sptp

*** PTP Parent ***

Parent Clock Identity:      ec:46:70:ff:fe:01:01:01 (Meindberg)

Parent IP: 192.168.20.11

Grandmaster Clock Identity: ec:46:70:ff:fe:01:01:01 (Meindberg)
Grandmaster Clock Quality (in GMC election order):
    Priority 1: 10
    Class: 6
    Accuracy: 33
    Offset (log variance): 13563
    Priority 2: 1

*** PTP Interface States and Counters ***

State:   m:master, s:slave, d:disabled, -:no state

------------------------------------------------------------------------------------------------------------------------------------
Port     Descr          State TX-Ann.  RX-Ann.  TX-Sync   RX-Sync   TX-FolUp   RX-FolUp  TX-DelReq  RX-DelResp RX-DelReq  TX-DelResp
------------------------------------------------------------------------------------------------------------------------------------
Eth1/5   VIAVI          d     160483   0        1277536   0         1277536    0         0          0          1148389    1148389
Eth1/6   IXIA           d     158850   0        1264520   0         1264520    0         0          0          1233872    1233872
Eth1/8   GMC-1          s     1        1902791  4         15222323  4          15222323  15145510   15145510   0          0
Eth1/9   GMC-2          m     1901840  2        15145541  8         15145541   8         0          0          0          0
Eth1/10  endpoint-1     m     1901830  0        15145465  0         15145465   0         0          0          8665395    8665395
Eth1/11  leaf-1-e1/53   m     1901587  5        15143522  24        15143522   24        0          0          14467113   14467113
Eth1/12  leaf-2-e1/54   m     1901580  7        15143466  31        15143465   31        0          0          0          0
Eth1/13  leaf-3         m     1901839  0        15145532  0         15145532   0         0          0          0          0
Eth1/14  leaf-4         m     1901635  0        15143908  0         15143908   0         0          0          13014387   13014387
Eth1/21  leaf-e1/53     m     1901860  2        15145698  12        15145698   12        0          0          15062762   15062762
Eth1/22  leaf-e1/54     m     1901859  3        15145691  23        15145691   23        0          0          0          0
Eth1/36  Interlink      m     1901828  0        15145451  0         15145451   0         0          0          0          0
```
