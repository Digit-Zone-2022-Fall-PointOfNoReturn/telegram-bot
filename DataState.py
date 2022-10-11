from aiogram.dispatcher.filters.state import StatesGroup, State


class ClientState(StatesGroup):
    creating_group = State()
    choosing_group = State()
    choosing_restoraunt = State()
    choosed_restoraunt = State()
    in_catalog = State()
    order_process = State()
    in_cart = State()
    make_order = State()
    finish_order = State()
    
    
    
# https://lolz.guru/threads/3769612/