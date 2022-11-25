from datetime import datetime
import cloudscraper
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

#  Url for the request
url = f"https://www.footlocker.{country}/apigate/release-calendar"

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
def getRealeses(url):
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
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
    data = getRealeses(url)
    now = time.time()
    print("Checking\n")
    
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
