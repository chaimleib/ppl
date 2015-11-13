# Print PList (ppl)

This utility is designed to convert Apple PList files to xml, json and yaml. I/O can be specified as arguments, or via command-line arguments.

Unlike Apple's plutil, ppl can output data fields in json. Also, ppl outputs yaml.

```
$ ./ppl.py -h
usage: ppl.py [-h] [-j] [-y] [-p] [-x] [-o OFILE] [IFILE]

Converts plists to xml, yaml and json.

positional arguments:
  IFILE                 the file to convert (default: stdin)

optional arguments:
  -h, --help            show this help message and exit
  -j, --json            output in json format
  -y, --yaml            output in yaml format
  -p, --pprint          output in Python's pprint format
  -x, --xml             output as plist xml (default)
  -o OFILE, --out OFILE
                        the file to write the result to (default: stdout)
```

For example, if I wanted to view detailed info about my laptop's battery:

```
$ ioreg -arc "AppleSmartBattery" | ./ppl.py -y
- AdapterInfo: 0
  Amperage: -1602
  AvgTimeToEmpty: 297
  AvgTimeToFull: 65535
  BatteryInstalled: true
  BatteryInvalidWakeSeconds: 30
  BatterySerialNumber: DEADBEEFYUMYUMYUM
  BootPathUpdated: 1447099812
  CellVoltage:
  - 4246
  - 4245
  - 4245
  - 0
  CurrentCapacity: 7922
  CycleCount: 75
  DesignCapacity: 8440
  DesignCycleCount9C: 1000
  DeviceName: bq20z451
  ExternalChargeCapable: false
  ExternalConnected: false
  FirmwareSerialNumber: 1
  FullPathUpdated: 1447390164
  FullyCharged: true
  IOGeneralInterest: IOCommand is not serializable
  IOObjectClass: AppleSmartBattery
  IOObjectRetainCount: 6
  IORegistryEntryID: 1234567890
  IORegistryEntryName: AppleSmartBattery
  IOServiceBusyState: 0
  IOServiceBusyTime: 20399
  IOServiceState: 30
  InstantAmperage: 63814
  InstantTimeToEmpty: 65535
  IsCharging: false
  LegacyBatteryInfo:
    Amperage: -1602
    Capacity: 8255
    Current: 7922
    Cycle Count: 75
    Flags: 4
    Voltage: 12735
  Location: 0
  ManufactureDate: 17658
  Manufacturer: SMP
  ManufacturerData: "\0\0\0\0\a\x02\0\x01\x12\x06\0\0\x03J45\x03003\x03ATL\x02\x15\0"
  MaxCapacity: 8255
  MaxErr: 1
  OperationStatus: 58435
  PackReserve: 200
  PermanentFailureStatus: 0
  PostChargeWaitSeconds: 120
  PostDischargeWaitSeconds: 120
  Temperature: 3020
  TimeRemaining: 297
  UserVisiblePathUpdated: 1447390464
  Voltage: 12735
```

