import requests
import json
import telegram
from telegram.ext import Updater, CommandHandler
import threading
import time
import multiprocessing
import itertools


# Telegram Bot API Token
TOKEN = '6754412358:AAGLXMl5ZOpYYw7Yjb5KmiO--qSaDLMsMac'

api_keys = [
'93654c6d1d7a4894242147a8e1a102f04047d869c70bf13d1b2b317a2ac6d1fb',
'3347945c3e532f0295e7a786072382c49b92372087e1f193dd82586649e16f21',
'b4ac73e8ddce26c3b96d7173c10d0ffdecbd34cf9f17af8bd090979cd958d0ad',
'eb6d380268b19c2d9b9a18cd60a48f0aef1ce222f8840a2ff8745a33121b6a08',
'0d053671240536da7fbb16603fbc546a62d1336df90f293c68b9426aedeb44ca',
'aafbb0f0b73a4fb31e716b70c7dbf751116ccbe78b5deff6c84ac3c9bb622caf',
'58250b2d5428edd150088690259da4ff0e7c9ca3c5c329284ecd6efb9076a808',
'01ff21444aeddfc5c4875d01d1d80b7bca45f0df8e265f209b192acd823a0ff0',
'df32dd910ba95152ff871ee6dca831afdf0e8ad0fd236c4b292bb1e95be529d9',
'bd1acdac826cb5ddfaec2cad6c7e8d1426ef1bef046273c42fadb4d5dc59529c',
'270387fb3fa2ea06a5a6f99dde982ed4636e48ff665b6b253c93b1f7b9e49242',
'6b92d718fe97f8d619e4b21846a15c2ce0f1b94085ec1e2ff8fbb66a40ffe9df',
'83af13b1ed6766a5bfe3e0cb7ea80cbd10771361899e0b409bf59c12349d82aa',
'b73167f5b35a4948ac60516d8c2bad6bd75a45ed338a0fb96b7c7f6917aa75d0',
'55a334e79ebeadf441e7157d2ef299c6ff128c95bfb58f5d650b275d24b81d89',
'ef71fb26534a66be95a23713c375fb7c5d6e5f7bab2da20596bd1aaf184cb129',
'f2cf08ae10ccabd1999b937234ed3ae5396d996723e623ecfb89e89c54cf065f',
'f8f84856a8b8b64e90a0b35aad055c0bbbd25672bd267f284589fdd7ad13d9d4',
'3d499d5e99bdca589702113a99393d3a5ab48cb407b8cb89ac201868192c64cd',
'dcad58b767f6819beaca34568dcd296156e58d6af072abaef9f00819b4c402f0',
'442b8755fdeb315339456011416f6a1cebd7b558d646f632955920454bb10882',
'a6a0ac6f3d262c4ee0db462f32afb993037a26791e07d8182dfcdd89abe7a42e',
'c17168107e3deac2c6bdc8d54b9cf4fa2bd2dfa5f74deb558bfe1fc9beba4725',
'ed9fd6160e2c93869f9df18f21f6fbde1dbb58fd9d774cef918fd2037a733967',
'e419a22deccaa8485f6f9138548d01a9464a6188239e6e7ea2dbd77058136278',
'3df105de46eee11620ecab5b7fb9541fbbfb3dc2bec7aeba4109d513cd231fee',
'58c5f088af1d7c37c324e10f65eaea4bf081b46896344127eff2139633e262b4',
'92627ab93776604644b0bc504156ceb4ab1ab6fea0cb408dc1695261dc807c9f',
'c06cd296bd4f6cc6b34c22df1f68712e84aa3ea14a53b86a68f55740efad4d88',
'bc4a21c2129f432c2faed9039ad9cc0ba18a9da779471ed9df69c0ed050e8994',
'7d7f9b28559e2d9d0bb35d396e7ec08bc9102778711ec82100c333c04456c1c7',
'e1243e192f8fc4895ae919cf4e9845e79491f3834446c1deaa6edc588fc175f0',
'e502beb4e419ff11b29c6654e4dcff1c449c1fd8d544dfc8b734241226f40af0',
'71b508d4a4e467743bd9e6a1ebb59ddbfc3f21969265af9cb94553c981114fc2',
'3cf690a45ed6606e6a3905e53a573c54342fed4de225495b14466b552252b687',
'599765ed833b3b3d05fca79f622d8587595674b3cc4271640c84c97ae6a54810',
'f40345eb3ac5af0c295397cc17673924c16c2ed07cd46ff2543298cdc62de5c0',
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
        # print("here 1", tick)
        inscription = response.json()["data"]["list"][0]
        # print("here 2", tick)
        if tick not in prev_inscriptions.keys():
            # print("here 3", tick)
            prev_inscriptions[tick] = [inscription['inscriptionNumber'], inscription['unitPrice']]
            return None
        else:
            # print("here 4", tick)
            if prev_inscriptions[tick] == [inscription['inscriptionNumber'], inscription['unitPrice']]:
                # print("here 5", tick)
                return None
            else:
                # print("here 6", tick)
                prev_inscriptions[tick] = [inscription['inscriptionNumber'], inscription['unitPrice']]
                convertion_factor = get_convertion_factor()
                if value : #since value is in form of str $(a float) or None
                    # print("here 7", tick)
                    if inscription['unitPrice']*convertion_factor < float(value[1:]):
                        # print("here 8", tick)
                        message = f"Tick: {tick}\nQuantity: {inscription['amount']}\nUnit Price: ${inscription['unitPrice']*convertion_factor}\nTotal Price: ${inscription['price']*convertion_factor}\nInscription Number: {inscription['inscriptionNumber']}\n\n\n"
                        return message
                    else:
                        # print("here 9", tick)
                        return None
                else:
                    # print("here 10", tick)
                    message = f"Tick: {tick}\nQuantity: {inscription['amount']}\nUnit Price: ${inscription['unitPrice']*convertion_factor}\nTotal Price: ${inscription['price']*convertion_factor}\nInscription Number: {inscription['inscriptionNumber']}\n\n\n"
                    return message
    except:
        # print("here 11", tick)
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
    chat_id = '887980481'
    manager = multiprocessing.Manager()
    prev_inscriptions = manager.dict() 
    while True:
        start = time.time()
        if requirements=={}:
            message = "Set Requirements First!"
            time.sleep(10)
        else:
            message = get_final_message(prev_inscriptions=prev_inscriptions)
            # print("------------------------------")
        try:
            if message:
               send_message(chat_id, "ORDINALS\n\n\n"+message)
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
    dp.add_handler(CommandHandler("seto", set_requirements))
    dp.add_handler(CommandHandler("showo", show_requirements))

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Starting Bot....")
    threading.Thread(target=message_sender).start()
    main()
