from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import Dict, Union

def get_main_menu() -> ReplyKeyboardMarkup:
    create_group_btn = KeyboardButton('Создать группу')
    choice_group_btn = KeyboardButton('Выбрать группу')
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(create_group_btn, choice_group_btn)
    return markup

def choice_restoraunts() -> ReplyKeyboardMarkup:
    restoraunt_choice_btn = KeyboardButton('Выбрать ресторан')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(restoraunt_choice_btn)
    return markup


def start_collecting() -> InlineKeyboardMarkup:
    change_market_btn = InlineKeyboardButton('Сменить ресторан', callback_data='change_market')
    start_assembly_btn = InlineKeyboardButton('Инициировать сбор', callback_data='collect_start')

    markup = InlineKeyboardMarkup(resize_keyboard=True)
    markup.row(change_market_btn, start_assembly_btn)
    return markup

def go_to_catalog(id_market:Union[str, int]) -> InlineKeyboardMarkup:
    show_catalog = InlineKeyboardButton('Перейти в каталог', callback_data=f'catalog_{id_market}')
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    markup.row(show_catalog)
    return markup

def get_product(product:Dict) -> InlineKeyboardMarkup:
    decrease_product = InlineKeyboardButton('Убрать из корзины (1 шт.)', callback_data=f'del_{product["id"]}')
    increase_product = InlineKeyboardButton('Добавить в корзину (1 шт.)', callback_data=f'add_{product["id"]}')
    
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    markup.row(decrease_product, increase_product)
    return markup

def collect_commands() -> ReplyKeyboardMarkup:
    finish_collect = KeyboardButton('Завершить сбор')
    cancel_collect = KeyboardButton('Отменить сбор')
    get_my_cart = KeyboardButton('Корзина')
    catalog = KeyboardButton('Каталог')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(finish_collect, cancel_collect)
    markup.row(get_my_cart, catalog)
    return markup

def get_cart_catalog_menu() -> ReplyKeyboardMarkup:
    get_my_cart = KeyboardButton('Корзина')
    catalog = KeyboardButton('Каталог')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(get_my_cart, catalog)
    return markup


def get_order_buttons() -> ReplyKeyboardMarkup:
    get_order = KeyboardButton('Оформить заказ')
    cancel = KeyboardButton('Отмена')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(get_order, cancel)
    return markup

def get_card_buttons() -> ReplyKeyboardMarkup:
    back = KeyboardButton('Назад')
    claer_cart = KeyboardButton('Очистить корзину')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(back, claer_cart)
    return markup

def confirm() -> ReplyKeyboardMarkup:
    confirm = KeyboardButton('Подтвердить')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(confirm)
    return markup

