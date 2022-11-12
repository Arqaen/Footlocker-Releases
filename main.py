from datetime import datetime
import requests
import time
import json

# Import the ids already in the monitor
monitor = []
try:
    with open('monitor.txt', 'r') as f:
        for line in f:
            monitor.append(line.strip())
except:
    pass

# Import the data from the config.json file
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except:
    print("No config.json found")
    exit()

# Config variables
webhook_url = config['webhook_url']
avatar = config['avatar_url']
country = config['country']
timeout = config['timeout']
hookname = config['name']
sleep = config['sleep']

#  Url and headers for the request
url = f"https://www.footlocker.{country}/apigate/release-calendar"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'es-ES,es;q=0.6',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.69'
}

# Function to send the webhook and save the id
def sendWebhook(url, data, id):

    global monitor
    response = requests.post(url, json = data)
    time.sleep(0.5)
    if(response.status_code == 429):
        print("Rate limited")
        time.sleep(10)
            
    else:
        monitor.append(str(id)) 
        with open('monitor.txt', 'a') as f:
            f.write(f"{id}\n")

    return response.status_code

# Function to get the request and catchs the errors
def getRealeses(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            return None
    except Exception as e:
        print(e)
        return None

# Main loop for track the releases 
while True:

    # Get the data from the request and the time
    data = getRealeses(url, headers)
    now = time.time()
    
    # If the data is not None
    if data:

        try:
            # For loop for get all the releases
            size = len(data['releaseCalendarProducts'])            
            for release in data['releaseCalendarProducts']:

                # Get the data of the release
                name = release['name']
                brand = release['brandName']
                id = release['id']
                img = release['image']
                gender = release['gender']
                launch = release['skuLaunchDate']
                link = f"https://www.footlocker.{country}" + release['pdpLink']                
    
                # Format the data
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
                                                
                if "hasStock" in release:
                    stock = release['hasStock']
                else:
                    continue

                # If the release has no stock and its not launched yet and its not in the monitor
                fix = time.mktime(datetime.strptime(launch, "%b %d %Y %H:%M:%S GMT+0000").timetuple())        
                if(id not in monitor and fix > now):

                    # Send the webhook
                    code = sendWebhook(webhook_url, info, id)
                    print(f"Name: {name} - Id: {id}")  
                    print(f"Sent webhook {code}\n")  

        except Exception as e:
            print(e)
            data = None

    # Catch the errors
    if not data:
        print("Error")
        time.sleep(timeout)

    time.sleep(sleep)
