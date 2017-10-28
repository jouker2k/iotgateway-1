# IoT Gateway

IoT Gateway on the Raspberry Pi 3 using PubNub + APIs + Security Policy.

[Clients/Things] <---[PubNub]---> [RPi3 Gateway] <---[APIs]---> [End-Devices/Things]

* RPi3 Gateway uses Security Policy located on another server/RPi device, also communicated with through PubNub.
* Using Python 3.6.x
* Using [IoTDB SmartThings](https://github.com/dpjanes/iotdb-smartthings) to support [Samsung SmartThings](http://docs.smartthings.com/en/latest/getting-started/overview.html)
* Using [Python-LGTV](https://github.com/grieve/python-lgtv) to find LG Smart TVs -> Copyright (c) 2014 Ryan Grieve
* Using [PyLGTV](https://github.com/TheRealLink/pylgtv) to operate LG Smart TVs -> Copyright (c) 2017 Dennis Karpienski
* Using [pastebin-reader](https://github.com/lnus/pastebin-reader/) to parse code from PasteBin

Additional modules  needed:
* [PyMySQL (0.7.11)](https://github.com/PyMySQL/PyMySQL/) -> `pip install PyMySQL`
* [RPi.GPIO (0.6.3)](http://sourceforge.net/projects/raspberry-gpio-python/) -> `pip install python3-rpi.gpioL`
