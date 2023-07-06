import requests
import time
import datetime
from dhooks import Webhook, Embed

webhook = "WEBHOOK_HERE"
sleep_time = 300
Current_VINS = {}
# {
#     "price": int,
#     "image": str,
#     "title": str,
#     "link": str,
#     "interior": str,
# }

def printt(msg):
    print(f'[{datetime.datetime.now()}] | {msg}')

def fill_vins():
    try:
        headers = {
            'authority': 'www.tesla.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.tesla.com/inventory/used/m3?TRIM=LRAWD,LRRWD&arrangeby=plh&zip=75074',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }

        params = {
            'query': '''{
                "query": {
                    "model": "m3",
                    "condition": "used",
                    "options": {
                        "TRIM": [
                            "LRAWD",
                            "LRRWD"
                        ]
                    },
                    "arrangeby": "Price",
                    "order": "asc",
                    "market": "US",
                    "language": "en",
                    "super_region": "north america",
                    "lng": -96.6745042,
                    "lat": 33.0243206,
                    "zip": "75074",
                    "range": 0,
                    "region": "TX"
                },
                "offset": 0,
                "count": 50,
                "outsideOffset": 0,
                "outsideSearch": false
            }''',
        }

        res = requests.get(
            'https://www.tesla.com/inventory/api/v1/inventory-results',
            params=params,
            headers=headers,
        )

        res_json = res.json()
        
        for i in res_json["results"]:
            temp = {
                "price": i["TotalPrice"],
                "image": f"https://static-assets.tesla.com/configurator/compositor?&bkba_opt=1&view=STUD_3QTR&size=1400&model=m3&options={i['OptionCodeList']}&crop=1400,850,300,130&",
                "title": f"{i['Year']} {i['TrimName']}",
                "link": f"https://www.tesla.com/m3/order/{i['VIN']}?postal=75074&range=50&region=TX&coord=33.0243206,-96.6745042&titleStatus=used&redirect=no#overview",
                "interior": i["INTERIOR"][0],
                "milage": i["Odometer"]
            }
            Current_VINS[i["VIN"]] = temp

        return True

    except Exception as e:
        printt("fill_vins error")
        print(e)
        #time.sleep(180)
        return False

def stock_check():
    #print("checking stock!")
    try:
        headers = {
            'authority': 'www.tesla.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.tesla.com/inventory/used/m3?TRIM=LRAWD,LRRWD&arrangeby=plh&zip=75074',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }

        params = {
            'query': '''{
                "query": {
                    "model": "m3",
                    "condition": "used",
                    "options": {
                        "TRIM": [
                            "LRAWD",
                            "LRRWD"
                        ]
                    },
                    "arrangeby": "Price",
                    "order": "asc",
                    "market": "US",
                    "language": "en",
                    "super_region": "north america",
                    "lng": -96.6745042,
                    "lat": 33.0243206,
                    "zip": "75074",
                    "range": 0,
                    "region": "TX"
                },
                "offset": 0,
                "count": 50,
                "outsideOffset": 0,
                "outsideSearch": false
            }''',
        }

        res = requests.get(
            'https://www.tesla.com/inventory/api/v1/inventory-results',
            params=params,
            headers=headers,
        )

        res_json = res.json()

        new_vins = []
        oos_vins = []
        tmp = []
        tmp2 = list(Current_VINS.keys())

        #print("checking difference for new vin!")
        for i in res_json["results"]:
            tmp.append(i["VIN"])

            if i["VIN"] not in Current_VINS:
                temp = {
                    "price": i["TotalPrice"],
                    "image": f"https://static-assets.tesla.com/configurator/compositor?&bkba_opt=1&view=STUD_3QTR&size=1400&model=m3&options={i['OptionCodeList']}&crop=1400,850,300,130&",
                    "title": f"{i['Year']} {i['TrimName']}",
                    "link": f"https://www.tesla.com/m3/order/{i['VIN']}?postal=75074&range=50&region=TX&coord=33.0243206,-96.6745042&titleStatus=used&redirect=no#overview",
                    "interior": i["INTERIOR"][0],
                    "milage": i["Odometer"]
                }
                Current_VINS[i["VIN"]] = temp
                new_vins.append(i["VIN"])
                printt("found new vin! " + i["VIN"])
            
        #print("checking oos!")
        for i in tmp2:
            if i not in tmp:
                oos_vins.append(i)
                printt("VIN went OOS! " + i)

        return new_vins, oos_vins

    except Exception as e:
        printt("stock_check error")
        print(e)
        time.sleep(180)
        return [], []

def main():
    while True:
        printt(list(Current_VINS.keys()))
        new_vins, oos_vins = stock_check()

        for i in new_vins:
            print("sending webhook - new stock!")
            hook = Webhook(webhook)

            curr_car = Current_VINS[i]

            embed_restock = Embed(
                title=f"**{curr_car['title']}**",
                description="In Stock!",
                url=curr_car["link"],
                color=0x66ff00,
                timestamp="now"
            )
            
            embed_restock.add_field(name="Price:",value=f"${curr_car['price']:,}",inline=True)
            embed_restock.add_field(name="Interior:",value=f"{curr_car['interior']}",inline=True)
            embed_restock.add_field(name="Milage:",value=f"{curr_car['milage']}",inline=True)
            embed_restock.set_image(url=f"{curr_car['image']}")

            hook.send(embed=embed_restock)

        for i in oos_vins:
            print("sending webhook - OOS!")
            hook = Webhook(webhook)

            curr_car = Current_VINS[i]

            embed_oos = Embed(
                title=f"**{curr_car['title']}**",
                description="Out of stock!",
                url=curr_car["link"],
                color=0xff0000,
                timestamp="now"
            )
            
            embed_oos.add_field(name="Price:",value=f"${curr_car['price']:,}",inline=True)
            embed_oos.add_field(name="Interior:",value=f"{curr_car['interior']}",inline=True)
            embed_oos.add_field(name="Milage:",value=f"{curr_car['milage']}",inline=True)
            embed_oos.set_image(url=f"{curr_car['image']}")

            hook.send(embed=embed_oos)
            Current_VINS.pop(i, None)
        
        time.sleep(sleep_time)
        continue

if __name__ == "__main__":
    success = fill_vins()
    print(success)
    printt(list(Current_VINS.keys()))
    if success:
        time.sleep(sleep_time)
        main()
