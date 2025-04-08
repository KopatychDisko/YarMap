'''fda'''

from aiogram.fsm.state import StatesGroup, State


class Admin(StatesGroup):
    '''fda'''
    district = State()
    coord = State()
    

class Markers(StatesGroup):
    ''''''
    point = State()
    name = State()
    addres = State()
    describe = State()
    stars = State()
    photo = State()
    end = State()
