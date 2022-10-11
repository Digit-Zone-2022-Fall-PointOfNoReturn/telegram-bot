import aiohttp
import config
from decimal import Decimal
from pyrogram import Client
from pyrogram.raw.functions.contacts import ResolveUsername
from typing import Optional, Dict, List

def is_admin(user_id:int, admin_id:int) -> bool:
    return user_id == admin_id


# https://docs.aiohttp.org/en/stable/client_quickstart.html#
async def make_async_get_request(url:str, headers:Optional[Dict]=None, params:Optional[Dict]=None, payload:Optional[Dict]=None) -> Optional[str]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, headers=headers, params=params) as response:
            print('POST RESPONSE STATUS: ', response.status)
            if response.status in (200, 201):
                if response:
                    return await response.json()
            else:
                return None

async def make_async_post_request(url:str, headers:Optional[Dict]=None, payload:Optional[Dict]=None) -> Optional[str]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            print('POST RESPONSE STATUS: ', response.status)
            if response.status in (200, 201):
                if response:
                    return await response.json()
            else:
                return None
            #pass

async def make_async_delete_request(url:str, headers:Optional[Dict]=None, params:Optional[Dict]=None) -> Optional[str]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.delete(url, headers=headers, params=params) as response:
            print('POST RESPONSE STATUS: ', response.status)
            if response.status in (200, 201):
                if response:
                    return await response.json()
            else:
                return None

async def make_async_put_request(url:str, headers:Optional[Dict]=None, payload:Optional[Dict]=None) -> Optional[str]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            print('POST RESPONSE STATUS: ', response.status)
            if response.status in (200, 201):
                if response:
                    return await response.json()
            else:
                return None


def make_async_patch_request(url, headers=None, payload=None):
    pass


async def telegram_usernames_to_ids(usernames: List[str]) -> List[int]:
    telegram_id_users:List[int] = []
    for username in usernames:
        username = username.lstrip('@ ')
        if all([char.isdigit() for char in username]):
            telegram_id_users.append(int(username))
            continue
        
        telegram_id_user:str = ""
        try:
            telegram_id_user = await resolve_username_to_user_id(username)
        except:
            continue
        
        telegram_id_users.append(int(telegram_id_user))
        
    return telegram_id_users


def render_product(product: Dict) -> str:
    message = f'''
    <b>{product["name"]}</b>
    
    Описание: {product["description"]}
    
    Цена: {product["price"]}
    '''
    return message

async def resolve_username_to_user_id(username: str) -> Optional[int]:
    pyrogram_client = Client(
    "bot",
    api_id=config.settings['TELEGRAM_APP_API_ID'],
    api_hash=config.settings['TELEGRAM_APP_API_HASH'],
    bot_token=config.settings['TELEGRAM_BOT_TOKEN'],
    app_version="7.7.2",
    device_model="Lenovo Z6 Lite",
    system_version="11 R")
    
    async with pyrogram_client:
        r = await pyrogram_client.invoke(ResolveUsername(username=username))
        if r.users:
            return r.users[0].id
        return None

def calculate_cart(products:List) -> Decimal:
    # Сделать расчёт скидки !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    sum = Decimal("0.0")
    for product in products:
        sum += Decimal(product["price"])
    return sum

def print_cart(cart_items:List) -> str:
    cart_view:str = ''
    for item in cart_items:
        cart_view += f'<b>{item["name"]}</b>\n<i>{item["description"]}</i>\nЦена:{item["price"]}\n'
    cart_view += f'Всего: {calculate_cart(cart_items) }'
    return cart_view