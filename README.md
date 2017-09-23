# IoT Gateway

IoT Gateway on the Raspberry Pi 3 using PubNub + APIs + Security Policy.

[Clients/Things] <---[PubNub]---> [RPi3 Gateway] <---[APIs]---> [End-Devices/Things]

* RPi3 Gateway uses Security Policy located on another server/RPi device, also communicated with through PubNub.
* Using Python 3.6.x
* Using `master` version of [IoTDB SmartThings](https://github.com/dpjanes/iotdb-smartthings) to support [Samsung SmartThings](http://docs.smartthings.com/en/latest/getting-started/overview.html)

Additional modules  needed:
* [PyMySQL (0.7.11)](https://github.com/PyMySQL/PyMySQL/) -> `pip install PyMySQLs`
