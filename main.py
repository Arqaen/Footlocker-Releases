from datetime import datetime
import requests
import time
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Android 5.0; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"
}

monitor = []
try:
    with open('monitor.txt', 'r') as f:
        for line in f:
            monitor.append(line.strip())
except:
    pass

try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except:
    print("No config.json found")
    exit()

webhook_url = config['webhook_url']
avatar = config['avatar_url']
country = config['country']
timeout = config['timeout']
hookname = config['name']
sleep = config['sleep']

url = f"https://www.footlocker.{country}/apigate/release-calendar"

def getRealeses(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

while True:

    data = getRealeses(url, headers)
    now = time.time()

    if data:

        try:
            size = len(data['releaseCalendarProducts'])
            print(size)
            
            for release in data['releaseCalendarProducts']:

                name = release['name']
                brand = release['brandName']
                id = release['id']
                img = release['image']
                gender = release['gender']
                launch = release['skuLaunchDate']
                link = "https://www.footlocker.nl" + release['pdpLink']

                
                if "hasStock" in release:
                    stock = release['hasStock']
                else:
                    continue
                
                info = {
                    "username": hookname,
                    "avatar_url": avatar,
                    "embeds": [
                        {
                            "title" : name,
                            "url": link,
                            "description" : f"**Name**: {name}\n**Brand**: {brand}\n**Gender**: {gender}\n**Id**: {id}\n\n**Launch**: {launch}\n",
                            "color": 14957809,
                            "thumbnail": {"url": img}
                        }
                    ]
                }
                
                fix = time.mktime(datetime.strptime(launch, "%b %d %Y %H:%M:%S GMT+0000").timetuple())
                if(id not in monitor and fix > now):

                    response = requests.post(webhook_url, json = info)
                    time.sleep(0.5)
                    if(response.status_code == 429):
                        print("Rate limited")
                        time.sleep(10)
                            
                    else:
                        monitor.append(str(id)) 
                        with open('monitor.txt', 'a') as f:
                            f.write(f"{id}\n")

                    print(f"Name: {name} - Id: {id}")  
                    print(f"Sent webhook {response.status_code}\n")  

        except:
            data = None

    if not data:
        print("Error")
        time.sleep(timeout)

    time.sleep(sleep)