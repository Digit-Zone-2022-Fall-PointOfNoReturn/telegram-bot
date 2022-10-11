import utils 
import json
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from typing import Optional, Union, Dict, List
from DataState import ClientState
from config import settings
from keyboards import general_keyboards
from decimal import Decimal
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
 
logger.add(
    settings["LOG_FILE"],
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="1 week",
    compression="zip",
)

class DeliveryTelegramBot(Bot):
    BASE_API_URL = 'http://80.78.246.47/api'
    def __init__(self, *, token, parse_mode = types.ParseMode.HTML):
        super().__init__(token, parse_mode=parse_mode)
      
bot = DeliveryTelegramBot(token=settings["TELEGRAM_BOT_TOKEN"])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage) 

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
     response = await utils.make_async_post_request(DeliveryTelegramBot.BASE_API_URL + f'/users/{message.from_id}')
     markup: ReplyKeyboardMarkup = general_keyboards.get_main_menu()
     msg:str = '''Привет! 👋🤖 Я бот-магазин по подаже товаров любой категории.'''
     await message.answer(msg, reply_markup=markup)   

@dp.message_handler(filters.Text(equals="Создать группу"))
async def create_group_process(message_from: types.Message, state: FSMContext) -> None:
    msg:str = '''
    Преред добавдлением людей в гурппу, каждый участник должен отправить боту команду /start. 
    Введите название группы и перечислите id участников. Например: Группа1 @user1 @user2 @user3'''
    await message_from.reply(msg)
    await state.set_state(ClientState.creating_group) 

@dp.message_handler(filters.Text(equals="Выбрать группу"))
async def choice_group_process(message_from: types.Message, state: FSMContext) -> None:
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    msg:str = '''Вы не состоите в группах '''
    
    groups:Union[Dict, List] = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/', params={"user": message_from.from_id})
    if groups:
        for group in groups:
            response:Union[Dict, List] = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{group["group"]}')
            markup.add(InlineKeyboardButton(f'{response["name"]} ', callback_data=f'group_{group["group"]}'))
        await message_from.reply('Выберите группу', reply_markup=markup)
        await state.set_state(ClientState.choosing_group)
    else:
        await message_from.answer(msg, reply_markup=markup)   

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('group'), state=ClientState.choosing_group)
async def choiced_group(callback_query: types.CallbackQuery, state: FSMContext):
    id_group:str = callback_query.data.split('_')[1]
    murkup:ReplyKeyboardMarkup = general_keyboards.choice_restoraunts()
    await state.update_data(group=id_group)
    await bot.send_message(callback_query.from_user.id, f'Группа выбрана! Теперь выберите ресторан.', reply_markup=murkup)
    await state.set_state(ClientState.choosing_restoraunt) 

@dp.message_handler(state=ClientState.creating_group)
async def choose_restoraunts_process(message: types.Message, state: FSMContext):
    group_name, *users = message.text.split(' ')
    id_users:List[int] = await utils.telegram_usernames_to_ids(users)
    print(id_users)
    payload={"name": group_name, "admin": message.from_id, "users": id_users}
    headers={'Content-Type': 'application/json'}
    
    response:Optional[str] = await utils.make_async_post_request('http://80.78.246.47/api/groups/', headers=headers, payload=json.dumps(payload))
    if response:
        group_id:str = response["id"]
        print("GROUP ID: ", group_id)    
        await state.update_data(group=group_id)
        markup = general_keyboards.choice_restoraunts()
        await message.answer("Отлично! Теперь выберите ресторан.", reply_markup=markup)
        await state.set_state(ClientState.choosing_restoraunt) 
    else:
        print('XYI')
    
@dp.message_handler(filters.Text(equals="Выбрать ресторан"), state=ClientState.choosing_restoraunt)
async def list_restoraunts_process(callback_query: types.CallbackQuery, state: FSMContext):
    msg:str = f'Выберите адрес'
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    
    markets:Union[Dict, List] = await utils.make_async_get_request('http://80.78.246.47/api/stores/')
    for place in markets:
        markup.add(InlineKeyboardButton(f'{place["name"]} {place["address"]}', callback_data=f'address_{place["id"]}'))
    await bot.send_message(callback_query.from_user.id, msg, reply_markup=markup)
    await state.set_state(ClientState.choosing_restoraunt) 
    
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('address'), state=ClientState.choosing_restoraunt)
async def adress_choice_handler(callback_query: types.CallbackQuery, state: FSMContext):
    id_market:str = callback_query.data.split('_')[1]
    msg:str = f'Заведение выбрано!'
    markup:InlineKeyboardMarkup = general_keyboards.start_collecting()
    await state.update_data(id_market=id_market)
    await bot.send_message(callback_query.from_user.id, msg, reply_markup=markup)
    await state.set_state(ClientState.choosed_restoraunt) 
    
@dp.callback_query_handler(lambda c: c.data and c.data == 'change_market', state=ClientState.choosed_restoraunt)
async def change_restoraunt(callback_query: types.CallbackQuery, state: FSMContext):
    markup:ReplyKeyboardMarkup = general_keyboards.choice_restoraunts()
    msg:str = "Выберите ресторан."
    await bot.send_message(callback_query.from_user.id, msg, reply_markup=markup)
    await state.set_state(ClientState.choosing_restoraunt) 

@dp.callback_query_handler(lambda c: c.data and c.data == 'collect_start', state=ClientState.choosed_restoraunt)
async def go_catalog_process(callback_query: types.CallbackQuery, state: FSMContext):
    # !!! Добавить проверку на вступление юзера в группу
    msg:str = f'Время сделать заказы!'
    user_state_data = await state.get_data()
  
    await utils.make_async_post_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/stores/start')
    
    group_members: List = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/')
    # массовая рассылка
    for user in group_members:
        await bot.send_message(user["user"], msg, reply_markup=general_keyboards.go_to_catalog(user_state_data["id_market"])) 

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('catalog'))
async def catalog_process(callback_query: types.CallbackQuery, state: FSMContext):
    id_market:str = callback_query.data.split('_')[1]
    user_state_data = await state.get_data()
    
    group_info = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}')
    
    markup: Optional[ReplyKeyboardMarkup] = None
    if utils.is_admin(callback_query.from_user.id, group_info["admin"]):
        markup = general_keyboards.collect_commands()
    else:
        markup = general_keyboards.get_cart_catalog_menu()
    await bot.send_message(callback_query.from_user.id, reply_markup=markup)
    
    products:List = await utils.make_async_get_request(f'http://80.78.246.47/api/stores/{id_market}/products/')
    for product in products:
        msg:str = utils.render_product(product)
        buttons:InlineKeyboardMarkup = general_keyboards.get_product(product)
        await bot.send_message(callback_query.from_user.id, msg, reply_markup=buttons) 

    await state.set_state(ClientState.in_catalog)
    
@dp.message_handler(filters.Text(equals="Каталог"))
async def get_catalog_process(callback_query: types.CallbackQuery, state: FSMContext):
    id_market:str = callback_query.data.split('_')[1]
    
    # если человек админ группы - дать кнопки закончить сбор
    user_state_data = await state.get_data()
    group_info = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}')
    
    markup: Optional[ReplyKeyboardMarkup] = None
    if utils.is_admin(callback_query.from_user.id, group_info["admin"]):
        markup = general_keyboards.collect_commands()
    else:
        markup = general_keyboards.get_cart_catalog_menu()
    await bot.send_message(callback_query.from_user.id, reply_markup=markup)
    
    products:List = await utils.make_async_get_request(f'http://80.78.246.47/api/stores/{id_market}/products/')
    for product in products:
        msg:str = utils.render_product(product)
        buttons:InlineKeyboardMarkup = general_keyboards.get_product(product)
        await bot.send_message(callback_query.from_user.id, msg, reply_markup=buttons) 

    await state.set_state(ClientState.in_catalog)
    
'''
> Helltraitor:
Корзина это товары, которые выбраны пользователями относительно группы и магазина

> Helltraitor:
Ты собираешь все продукты группы и выбранного магаза и работаешь с этим всем

> Helltraitor:
Там же указаны пользователи и количество товаров

'''
@dp.message_handler(filters.Text(equals="Корзина"))
async def card_process(callback_query: types.CallbackQuery, state: FSMContext):
    user_state_data = await state.get_data()
    response:List[Dict] = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/stores/{user_state_data["id_market"]}/carts')
    cart_items = response
    products:Dict = []
    for item in cart_items:
        product:Dict = await utils.make_async_get_request(f'http://80.78.246.47/api/stores/{user_state_data["id_market"]}/products/{item["product"]}')
        msg:str = utils.render_product(product)
        buttons = general_keyboards.get_product(product)
        products.append(product)
        await bot.send_message(callback_query.from_user.id, msg, reply_markup=buttons)
        
    msg:str = f'Стоимость корзины:{utils.calculate_cart(products)}'
    murkup:ReplyKeyboardMarkup = general_keyboards.get_card_buttons()
    
    await bot.send_message(callback_query.from_user.id, msg)  
    await bot.send_message(callback_query.from_user.id, reply_markup=murkup)
    await state.set_state(ClientState.in_cart)
     
@dp.message_handler(filters.Text(equals="Назад"), state=ClientState.in_cart)
async def back_process(callback_query: types.CallbackQuery, state: FSMContext):
    markup:InlineKeyboardMarkup = general_keyboards.go_to_catalog()
    await bot.send_message(callback_query.from_user.id, reply_markup=markup) 
    await state.set_state(ClientState.choosed_restoraunt)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('add'), state=ClientState.in_catalog)
async def add_product_process(callback_query: types.CallbackQuery, state: FSMContext):
    user_state_data = await state.get_data()
    id_product:str = callback_query.data.split('_')[1]
    payload={"amount": 1}
    headers={'Content-Type': 'application/json'}
    await utils.make_async_put_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/{callback_query.from_user.id}/stores/{user_state_data["id_market"]}/product/{id_product}/cart',
                                         headers=headers, payload=json.dumps(payload))
    
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('del'), state=ClientState.in_catalog)
async def del_product_process(callback_query: types.CallbackQuery, state: FSMContext):
    user_state_data = await state.get_data()
    id_product:str = callback_query.data.split('_')[1]
    payload={"amount": 1}
    headers={'Content-Type': 'application/json'}
    await utils.make_async_delete_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/{callback_query.from_user.id}/stores/{user_state_data["id_market"]}/product/{id_product}/cart',
                                            headers=headers, payload=json.dumps(payload))

@dp.message_handler(filters.Text(equals="Завершить сбор"), state=ClientState.in_catalog)
async def finish_collect_process(message_from: types.Message, state: FSMContext) -> None:
    user_state_data = await state.get_data()
    
    await utils.make_async_post_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/stores/stop')
    
    response = response = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/')
    group_members: List = response
    for user in group_members:
        id_user:int = user['user']
        cart:Union[Dict, List] = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/{id_user}/stores/{user_state_data["id_market"]}/cart/')
        
        products:List[Dict] = []
        for cart_item in cart:
            product:Dict = await utils.make_async_get_request(f'http://80.78.246.47/api/stores/{user_state_data["id_market"]}/products/{cart_item["product"]}')
            products.append(product)
            
        client_order:str = utils.print_cart(products)
        await bot.send_message(id_user, client_order) 
      
    msg:str = f'Можно оформить заказ!' 
    murkup:ReplyKeyboardMarkup = general_keyboards.get_order_buttons()   
    
    group_info:Dict = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}')
    if message_from.from_id == group_info["admin"]:
        await bot.send_message(message_from.from_id, msg, reply_markup=murkup)
    await state.set_state(ClientState.order_process)

@dp.message_handler(filters.Text(equals="Отменить сбор"), state=ClientState.in_catalog)
async def cancel_collect_process(message_from: types.Message, state: FSMContext) -> None:
    user_state_data:Dict = await state.get_data()
    markup:ReplyKeyboardMarkup = general_keyboards.get_main_menu()
    msg:str = 'Привет! 👋🤖 Я бот-магазин по подаже товаров.'
    
    await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/stores/drop')
    
    group_members: List = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/')
    for user in group_members:                                                    
        await utils.make_async_delete_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/{user["user"]}/stores/{user_state_data["id_market"]}/cart/')
    
    await message_from.answer(msg, reply_markup=markup) 
    await state.finish()

@dp.message_handler(filters.Text(equals="Оформить заказ"), state=ClientState.order_process)
async def order_process(message_from: types.Message, state: FSMContext) -> None:
    # получить телефон/номер карты, разослать всем
    user_state_data:Dict = await state.get_data()
    group_cart_render_message = ''
    group_sum = Decimal("0.0")
    murkup:ReplyKeyboardMarkup = general_keyboards.get_card_buttons()
    msg:str = f'\nУкажите номер телефона или карту'
    
    group_members: List = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/')
    for user in group_members:
        cart:Union[Dict, List] = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/{user["user"]}/stores/{user_state_data["id_market"]}/cart/')

        products:List[Dict] = []
        for cart_item in cart:
            product:Dict = await utils.make_async_get_request(f'http://80.78.246.47/api/stores/{user_state_data["id_market"]}/products/{cart_item["product"]}')
            products.append(product)
            
        group_cart_render_message += utils.print_cart(products)
        group_sum += utils.calculate_cart(products)
    
    group_cart_render_message += f'Итог: {group_sum} '
    await message_from.answer(group_cart_render_message + msg) 
    await message_from.answer(reply_markup=murkup)   
    await state.set_state(ClientState.make_order)
    
@dp.message_handler(state=ClientState.make_order)
async def confitm_process(message_from: types.Message, state: FSMContext) -> None:
    card_phone:str = message_from.text
    msg:str = f'Отправьте деньги на номер: {card_phone}'
    user_state_data:Dict = await state.get_data()
    markup:ReplyKeyboardMarkup = general_keyboards.confirm() 
    
    group_members: List = await utils.make_async_get_request(f'http://80.78.246.47/api/groups/{user_state_data["group"]}/users/')
    for user in group_members:
        await bot.send_message(user['user'], msg) 
 
    await message_from.answer(reply_markup=markup) 
    await state.set_state(ClientState.finish_order)

@dp.message_handler(filters.Text(equals="Подтвердить"), state=ClientState.finish_order)
async def finish_process(message_from: types.Message, state: FSMContext) -> None:    
    markup: ReplyKeyboardMarkup = general_keyboards.get_main_menu()
    msg:str = 'Привет! 👋🤖 Я бот-магазин по подаже товаров любой категории.'
    await message_from.answer(msg, reply_markup=markup)   
    await state.finish()
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


'''
@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    payload={"name": 'dffddffd', "admin": 333, "users": [111, 222, 333]}
    headers={'Content-Type': 'application/json'}
    response:Optional[str] = await utils.make_async_post_request('http://80.78.246.47/api/groups/', headers=headers, payload=json.dumps(payload))
'''
# !!! Фабрика колбеков CallbackData


# https://github.com/NikolaySimakov/Shop-bot

# https://ru.stackoverflow.com/questions/1284888/%D0%9A%D0%B0%D0%BA-%D1%81%D0%B4%D0%B5%D0%BB%D0%B0%D1%82%D1%8C-%D0%BC%D0%BD%D0%BE%D0%B3%D0%BE%D1%83%D1%80%D0%BE%D0%B2%D0%BD%D0%B5%D0%B2%D1%83%D1%8E-%D0%BA%D0%BB%D0%B0%D0%B2%D0%B8%D0%B0%D1%82%D1%83%D1%80%D1%83-%D0%B4%D0%BB%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%BD%D0%B0-aiogram

# https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html

# https://mastergroosha.github.io/aiogram-3-guide/fsm/