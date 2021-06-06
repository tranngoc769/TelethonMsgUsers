from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError
import sys
import csv
import random
import time
import time
import  configparser
parser = configparser.ConfigParser()
parser_set = configparser.RawConfigParser()
def _optionxform(s):
    try:
        newstr = s.decode('latin-1')
        newstr = newstr.encode('utf-8')
        return newstr
    except Exception as e:
        pass
parser_set.optionxform = _optionxform 
import logging
# VARIABLE
log_path = "erro.log"
accesslog_path = "access.log"
logger = None
check_logger = None
count = 0
api_id = 0
api_hash = ''
phone = ''
send_message = ''
def readMsg():
    try:
        with open('messages.bin', 'r', encoding="UTF-8") as file:
            data = file.read().replace('\n', '')
            return data
            return ""
    except:
        return ""
def get_list_users():
    users = []
    with open("data.csv", encoding='UTF-8') as f:
        rows = csv.reader(f,delimiter=",",lineterminator="\n")
        next(rows, None)
        for row in rows:
            user = {}
            user['username'] = row[0]
            users.append(user)
    return users
# END
def get_datetime():
    from datetime import datetime
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string
def access_log(msg):
    global count
    if count < 100:
        with open(accesslog_path,mode='a') as ff:
            ff.write(get_datetime()+ "- INFO - "+msg+"\n")
        count+=1
    else:
        with open(accesslog_path,mode='w') as ff:
            ff.write(get_datetime()+ "- INFO - "+msg+"\n")
        count=0
    
def get_parameter():
    global phone, api_id, api_hash, time_sleep,timeout, send_message,logger
    try:
        parser.read("app.cfn")
        # 
        time_sleep = int(parser.get("config", "time"))
        phone = parser.get("config", "phone")
        api_id = parser.get("config", "api_id")
        api_hash = parser.get("config", "api_hash")
        send_message = readMsg()
        # 
        logging.basicConfig(filename=log_path, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logger = logging.getLogger(__name__)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_path)
        c_handler.setLevel(logging.WARNING)
        f_handler.setLevel(logging.ERROR)
        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        # Add handlers to the logger
        if (logger.hasHandlers()):
            logger.handlers.clear()
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        logger.propagate = False
        return True
    except Exception as err:
        logger.error("Init parameter failed : "+str(err))
        return False
def send_thread():
    global phone, api_hash, api_id,send_message,time_sleep, logger
    SLEEP_TIME = time_sleep
    client = TelegramClient(phone, api_id, api_hash)
    client.connect()
    while not client.is_user_authorized(): 
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))
    users = get_list_users()
    messages= send_message
    for user in users:
        try:
            receiver = client.get_input_entity(user['username'])
            client.send_message(receiver, messages)
            access_log("Sending Message to:"+ user['username'])
            print("Sending Message to:"+ user['username'])
            time.sleep(SLEEP_TIME)
        except PeerFloodError as e:
            logger.error("PeerFloodError to "+ user['username']+ ": "+str(e))
            client.disconnect()
            sys.exit()
        except Exception as e:
            logger.error("Sending to "+ user['username']+ ": "+str(e))
            print("Trying to continue...")
            continue
    print("Done. Message sent to all users.")
    client.disconnect()
    access_log("Done. Message sent to all users.")
print("APP IS RUNNING")
status = get_parameter()
if status == False:
    print("Init parameter failed")
    logger.error("Init parameter failed")
    exit()
try:
    send_thread()
except Exception as e:
    logger.error("Sending faile: "+str(e))
    print("Sending faile: "+str(e))
