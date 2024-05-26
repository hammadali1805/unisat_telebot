import requests
import json
import telegram
from telegram.ext import Updater, CommandHandler
import threading
import time
import multiprocessing
from datetime import datetime


# Telegram Bot API Token
TOKEN = '6721024126:AAG9ucuRn5GlG1WV_C0US0bKpXs5Cy7icSA'

api_keys = [
'549cb2ee274c05c15b3bef793c0021c04679569a098bdf82ef3712989d881259',
'2168124d16b20587e5eb59e626171d2ca4614203975d2da10c1ae7ea332a0636',
'82bc288a7ebb1d33b245e98b595ffe8c7d11ce2b513350d904eef674e2465de7',
'a3bebe5090256c82f6a3a87dbf5e56b11efcaed8cafe1e48c40dbadd5d154fc1',
'd9a407e7c49af1368991f8bcbd62b0a055ba1e6db8818cd67d68abc80f02944c',
'13d8901c38289e65606deef2246af53f94114c530740067462a96231047f7f78',
'19ae690c5db593437a688c4c412c435520f5593830d1078d613743f7ec449ddc',
'e2005c425d01f71115f6ed25f27a080a2216e5644d9bed8b27e56c7f1a5f703d',
'b6d7ade8f71d48c5ec309fbbda50000c539d9577256812dc4c6c79a656ca57c3',
'447dd889df3277a7a5cbda8c1bb23407cac34316843499fb99b0a393d0d41683',
'4574d534af39435f91df5e00f132a814cf174aefd5eec200084d495bf9d610e4',
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
    'X-CMC_PRO_API_KEY': '090cddf5-43a9-4fc9-819d-f310f94570b3',
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


    url = f'https://open-api.unisat.io/v3/market/runes/auction/list'

    print(api_key)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}' 
    }


    payload = {
        'filter': {
            'nftType': 'runes',
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
                        message = f"Tick: {tick}\nQuantity: {inscription['amount']}\nUnit Price: ${inscription['unitPrice']*convertion_factor}\nTotal Price: ${inscription['price']*convertion_factor}\n\n\n"
                        return message
                    else:
                        print("9", tick)
                        return None
                else:
                    print("10", tick)
                    message = f"Tick: {tick}\nQuantity: {inscription['amount']}\nUnit Price: ${inscription['unitPrice']*convertion_factor}\nTotal Price: ${inscription['price']*convertion_factor}\n\n\n"
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
    chat_id = '5473882256'
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