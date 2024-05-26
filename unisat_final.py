import requests
import json
import telegram
from telegram.ext import Updater, CommandHandler
import threading
import time
import multiprocessing
import itertools
from datetime import datetime


# Telegram Bot API Token
TOKEN = '6754412358:AAGLXMl5ZOpYYw7Yjb5KmiO--qSaDLMsMac'

api_keys = ['f40345eb3ac5af0c295397cc17673924c16c2ed07cd46ff2543298cdc62de5c0',
'97afed70e776b1247ba2ef1120bb994ce484fb5d278cb24e36e58cf3531f0abf',
'406d7208e02cc058385951fc058780f3077e3cb743384270b46b7ae99e893337',
'6d7d9af91fa889e8c89ea2b74d6896f244928294e4876b358d062558843b7524',
'4b9aee52c7e773d7ee200dc9885ecfde40ce278900dbd173b59f53ad534caed1',
'32c18a3e60126ab83dbb0aa026d684ec296a09196b5610086bf5938f58718457',
'5e97cff44beffeccc37c6138d25d1c87f7fe64746ad10e375b4c428f0ac38e16',
'a437c67b944778dbd51a588583473946054a0743f499d10d64c2d74fb0969c6b',
'37896a2be319ee075eca4bc13c24db22f57564bca958da34d5d76d24a976ef8e',
'84b09716f24f6d507d12526e160cabe4fab5971774361ecc914259c3572013f3',
'4565baddf5fe10ce2666935c6d03aa68c7c9079814c46e5202b226ee9bf2fc83',
'91db9b94aa12e15d6372de5c4058646c65e931e6f54cdb8b1d92086dec651ef9',
'650ac28e362f5cfe6d38edb8a22a9914b6c3d70e57ca8d0c5fdb0632e4a899e1',
'aaa4d7c5bb3d5218a3aa2d944c50dbacfc94def3077a5dd600a66f3b6154ac31',
'0fbc8e4651b6bef2ba67170d5bb921be6af5258a3c44aee36bcc31611e448042',
'd96986da56cab739bf221f0182a92a2c2d43dde0cee712091d68c8e315df1d67',
'd2b5a3aabcd6f35bc243066eedfc1327f4b092cc4971ceb319208533704629db',
'35c62dff08edb83ca7a5c53225fc975d51d5a3715a31e14b430976925a04bbed',
'6a101442c0b6a6d51697e105dd3abed056a569b80eb0af92770b3a10fdd9502b',
'e9a2f71f0ce23d29fa4ea41dbd550a5dc56c34ae7e2d48c8dddcab3386fe9b86',
]

api_keys_gen = itertools.cycle(api_keys)
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
        param = update.message.text[5:]
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
    prev_inscriptions = args[0]
    tick = args[1][0]
    value = args[1][1]

    url = f'https://open-api.unisat.io/v3/market/brc20/auction/list'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {next(api_keys_gen)}' 
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
        print("11", tick, e)
        return None

def get_final_message(prev_inscriptions):
    message = ''
    # Number of processes to use
    num_processes = multiprocessing.cpu_count()
    # Create a pool of workers
    args = [[prev_inscriptions, x] for x in requirements.items()]
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
    while True:
        start = time.time()
        if requirements=={}:
            message = "Set Requirements First!"
            time.sleep(10)
        else:
            message = get_final_message(prev_inscriptions=prev_inscriptions)
            print("------------------------------", datetime.now())
        try:
            if message:
               send_message(chat_id, message)
            taken  = time.time() - start
            wait = 45*(len(requirements)/len(api_keys))
            if wait > taken:
                time.sleep(wait-taken)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
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
