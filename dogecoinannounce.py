from bs4 import BeautifulSoup
import requests
import json
import time
import os
from termcolor import colored


def get_dogecoin_price():
    cmc = requests.get("https://coinmarketcap.com"
                       "/currencies/dogecoin/")
    soup = BeautifulSoup(cmc.content, "html.parser")
    data = soup.find("script",
                     id="__NEXT_DATA__",
                     type="application/json")

    coin_data = json.loads(data.contents[0])
    price = coin_data["props"]["initialProps"]["pageProps"]["info"]["statistics"]["price"]
    return price


def say(stuff):
    os.system(f'spd-say -w \"{stuff}\"')


previous_price = get_dogecoin_price()
print(f"{time.asctime(time.localtime())} Ð1 = ${previous_price}")
say(f"Current price of Dogecoin is {round(previous_price, 5)} dollars.")
while True:
    try:
        price = get_dogecoin_price()
        if price == previous_price:
            print("Waiting for updated price data...")
            print("\x1b[A", end="")
        else:
            print(f"{time.asctime(time.localtime())} Ð1 = ${price} ",
                  end="")
            if previous_price < price:
                print(colored("^", "green"))
                if int(100 * price) - int(100 * previous_price) >= 1:
                    say("Crypto market alert. Dogecoin price has increased"
                        " by one cent since last alert.")
                    say(f"Current price of Dogecoin is {round(price, 5)} dollars.")
            else:
                print(colored("v", "red"))
                if int(100 * previous_price) - int(100 * price) >= 1:
                    say("Crypto market alert. Dogecoin price has decreased"
                        " by one cent since last alert.")
                    say(f"Current price of Dogecoin is {round(price, 5)} dollars.")
        previous_price = price
    except KeyboardInterrupt:
        print("")
        exit(0)
