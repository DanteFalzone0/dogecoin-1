from bs4 import BeautifulSoup
from math import floor
import requests
import json
import time
from time import sleep as wait
import os
import sys
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


def say(stuff, toggle):
    if toggle:
        os.system(f'spd-say -w \"{stuff}\"')


def send_sms_message(message, destination_number):
    api_key = open("apikey.txt", "r").read()
    result = requests.post(
        url="https://api.ecs.rocks/v0/sms/sendReminderSMS",
        json={
            "event-text": message,
            "destination-number": destination_number,
            "auth-api-key": api_key
        },
        headers={"Content-Type": "application/json"}
    )
    return result


def main(argv):
    ratelimit = 1
    if "-r" in argv:
        try:
            ratelimit = float(argv[argv.index("-r") + 1])
        except:
            print("Invalid arguments, try with ``-h'' for more info")
            exit(1)

    if "-h" in argv:
        print(
            "Options\n"
            "-q\n"
            "    quiet mode (suppresses audible output)\n"
            "-h\n"
            "    print this message and exit\n"
            "-r NUMBER\n"
            "    set ratelimiting to NUMBER seconds (defaults to 1)\n"
            "-s PHONE-NUMBER\n"
            "    price change announcements will be texted to PHONE-NUMBER\n"
            "    (must have apikey.txt in same directory)\n"
        )
        exit(0)

    sms_mode = ("-s" in argv)
    phone_number = None
    if sms_mode:
        print("SMS mode enabled")
        try:
            phone_number = argv[argv.index("-s") + 1]
        except:
            print("Invalid arguments, try with ``-h'' for more info")
            exit(1)
        print(f"Phone number {phone_number}")

    quiet_mode = not ("-q" in argv)
    previous_price = get_dogecoin_price()
    print(f"{time.asctime(time.localtime())} Ð1 = ${round(previous_price, 10)}")
    say(f"Current price of Dogecoin is {round(previous_price, 5)} dollars.", quiet_mode)
    while True:
        try:
            wait(ratelimit)
            price = get_dogecoin_price()
            if price == previous_price:
                print("Waiting for updated price data...")
                print("\x1b[A", end="")
            else:
                print(f"{time.asctime(time.localtime())} Ð1 = ${round(price, 10)} ",
                      end="")
                if previous_price < price:
                    print(colored("^", "green"))
                    if floor(100 * price) - floor(100 * previous_price) >= 1:
                        message = """Crypto market alert. Dogecoin price has increased
 by one or more cents since last alert. """ f"Current price of Dogecoin is {round(price, 5)} dollars."
                        say(message, quiet_mode)
                        if sms_mode:
                            send_sms_message(f"Alert: Dogecoin price has gone up to ${price}", phone_number)

                else:
                    print(colored("v", "red"))
                    if floor(100 * previous_price) - floor(100 * price) >= 1:
                        message = """Crypto market alert. Dogecoin price has decreased
 by one or more cents since last alert.""" f"Current price of Dogecoin is {round(price, 5)} dollars."
                        say(message, quiet_mode)
                        if sms_mode:
                            send_sms_message(f"Alert: Dogecoin price has gone down to ${price}", phone_number)

            previous_price = price

        except KeyboardInterrupt:
            print("")
            exit(0)


if __name__ == "__main__":
    main(sys.argv)
