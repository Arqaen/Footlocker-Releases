# Footlocker releases monitor

![footlocker](https://www.footlocker.es/built/232/images/FLEU/logo.svg)

A monitor that tracks every new realese of footlocker product and notifiy to discord with webhooks.
The monitor.txt will save the ids of the notified products.

##  Requirements

-Python <https://www.python.org/downloads/>

Python libraries requiered:
```
pip install -r requirements.txt
```

##  Tutorial

Edit the config.json with your webhook data and select the country you want to track.

Put the Internet country code top-level domain. 
```
Examples: 
"nl" - Netherlands
"es" - Spain
```

Also you can adjust the times of the monitor.


Start:
`py main.py`
