import requests
import json
import telegram
from telegram.ext import Updater, CommandHandler
import threading
import time
import multiprocessing
from datetime import datetime


# Telegram Bot API Token
TOKEN = 'YOUR TOKEN'

api_keys = [
    "ENTER YOUR API KEYS"
]

requirements = {}

# Initialize the bot
bot = telegram.Bot(token=TOKEN)

# Define the /show command handler
def show_requirements(update, context):
    update.message.reply_text(f"{json.dumps(requirements, indent=4)}")

# Define the /set command handler
def set_requirements(update, context):
    global requirements
    global prev_inscriptions
    try:
        new_requirements = {}
        param = update.message.text[4:]
        param = param.split(',')
        param = [x.strip() for x in param if x.strip()]
        param = [x.split() for x in param]
        for i in param:
            if len(i)==2:
                new_requirements[i[0]] = '$'+str(float(i[1]))
            else:
                new_requirements[i[0]] = None
        requirements = new_requirements
        update.message.reply_text(f"Requirements set successfully.\n\n\n{json.dumps(requirements, indent=4)}")
        prev_inscriptions = {}
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")


def send_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(f"An error occurred while sending message: {e}")
    

def get_convertion_factor():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'5',
    'convert':'USD'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'YOUR API KEY',
    }

    try:
        response = requests.get(url, params=parameters, headers=headers)
        if response.status_code == 429:
            print('Please Change Conversion Api. CoinMarketCap')
            return 0.0
        data = json.loads(response.text)
        return data['data'][0]['quote']['USD']['price']/100_000_000
    except Exception as e:
        print(f"Error fetching conversion factor: {str(e)}")
        return 0.0


def get_message(args):
    api_key_index = args[0]
    prev_inscriptions = args[1]
    tick = args[2][0]
    value = args[2][1]


    api_key = api_keys[api_key_index.value%len(api_keys)]
    api_key_index.value += 1

    url = f'https://open-api.unisat.io/v3/market/brc20/auction/list'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}' 
    }


    payload = {
        'filter': {
            'nftType': 'brc20',
            'isEnd': False,
            'tick': tick,
        },
        'sort': {
            'unitPrice': 1,
        },
        'start': 0,
        'limit': 1
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for non-2xx responses
        print("1", tick)
        inscription = response.json()["data"]["list"][0]
        print("2", tick)
        if tick not in prev_inscriptions.keys():
            print("3", tick)
            prev_inscriptions[tick] = [inscription['inscriptionNumber'], inscription['unitPrice']]
            return None
        else:
            print("4", tick)
            if prev_inscriptions[tick] == [inscription['inscriptionNumber'], inscription['unitPrice']]:
                print("5", tick)
                return None
            else:
                print("6", tick)
                prev_inscriptions[tick] = [inscription['inscriptionNumber'], inscription['unitPrice']]
                convertion_factor = get_convertion_factor()
                if value : #since value is in form of str $(a float) or None
                    print("7", tick)
                    if inscription['unitPrice']*convertion_factor < float(value[1:]):
                        print("8", tick)
                        message = f"Tick: {tick}\nQuantity: {inscription['amount']}\nUnit Price: ${inscription['unitPrice']*convertion_factor}\nTotal Price: ${inscription['price']*convertion_factor}\nInscription Number: {inscription['inscriptionNumber']}\n\n\n"
                        return message
                    else:
                        print("9", tick)
                        return None
                else:
                    print("10", tick)
                    message = f"Tick: {tick}\nQuantity: {inscription['amount']}\nUnit Price: ${inscription['unitPrice']*convertion_factor}\nTotal Price: ${inscription['price']*convertion_factor}\nInscription Number: {inscription['inscriptionNumber']}\n\n\n"
                    return message
    except Exception as e:
        print("11", tick, str(e))
        return None

def get_final_message(api_key_index, prev_inscriptions):
    message = ''
    # Number of processes to use
    num_processes = multiprocessing.cpu_count()
    # Create a pool of workers
    args = [[api_key_index, prev_inscriptions, x] for x in requirements.items()]
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Map the worker function to the tasks
        results = pool.map(get_message, args)

    for i in results:
        if i:
            message += i + "\n\n\n"
    
    return message


def message_sender():
    chat_id = 'YOUR CHAT ID'
    manager = multiprocessing.Manager()
    prev_inscriptions = manager.dict() 
    api_key_index = manager.Value('i', 0)

    while True:
        start = time.time()
        if requirements=={}:
            message = "Set Requirements First!"
            time.sleep(10)
        else:
            message = get_final_message(api_key_index=api_key_index, prev_inscriptions=prev_inscriptions)
            print("------------------------------", datetime.now())
        try:
            if message:
               send_message(chat_id, message)
            taken  = time.time() - start
            wait = 50*(len(requirements)/len(api_keys))
            if wait > taken:
                time.sleep(wait-taken)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            continue


def main():
    # Initialize bot
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add command handler for /set, /show
    dp.add_handler(CommandHandler("set", set_requirements))
    dp.add_handler(CommandHandler("show", show_requirements))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Starting Bot....")
    threading.Thread(target=message_sender).start()
    main()
