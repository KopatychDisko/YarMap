'''gfa'''
import pandas as pd

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import types

from state import Admin

from filter import ChatTypeFilter

from map.map_creator import map_to_html

router_districts = Router()

router_districts.message.filter(
    ChatTypeFilter(chat_type="private")
)

@router_districts.message(Command("start"))
async def start(msg: Message):
    await msg.answer('Приветствую тебя! Я помогу тебе создать карту доступности, начни с команды /change')

@router_districts.message(Command("cancel"))
async def cancel(msg: Message, state: FSMContext):
    'Cancel all state'
    await state.clear()
    await msg.answer('Хорошо начнем с начала', reply_markup=types.ReplyKeyboardRemove())
    

@router_districts.message(Command("change"))
async def greetings(msg: Message):
    'First'
    kb = [
        [types.KeyboardButton(text="Район")],
        [types.KeyboardButton(text="Метки")]
    ]
  
    builder = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        row_width=1,
        one_time_keyboard=True,
        input_field_placeholder='Выбирайте, с чем будем работать?'
        )

    text = '''
        Что будем менять?
    '''
    await msg.answer(text=text, reply_markup=builder)


@router_districts.message(F.text == 'Район')
async def district(msg: Message, state: FSMContext):
    '''fad'''
    await state.set_state(state=Admin.district)

    df = pd.read_json('../data/yar_districts.json')

    kb = [[types.KeyboardButton(text=name)] for name in df.index]

    builder = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        row_width=1,
        one_time_keyboard=True,
        input_field_placeholder='Какому районы будем писать координаты?'
        )

    await msg.answer('Введи название района:', reply_markup=builder)

  
@router_districts.message(Admin.district)
async def coord(msg: Message, state: FSMContext):
    '''fad'''
    await state.set_data({'name': msg.text})
    await msg.answer('Вписывай координаты:')
    await state.set_state(Admin.coord)

@router_districts.message(Admin.coord, F.text.lower() == 'все')
async def end(msg: Message, state: FSMContext):
    '''fad'''
    await msg.reply_sticker('CAACAgIAAxkBAAIBCGfxUWZsKHKtdCfe-CA9DzshPuV5AAIEYQACoL2BSheQaxkxNRHbNgQ')
    await msg.answer('Реально? Тогда сейчас скину карту')
    await state.clear()
    
    map_to_html('../data/yar_districts.json', '../data/map.html')
    
    file = types.FSInputFile('../data/map.html')
    await msg.answer_document(file, caption='Вот ваша карта 📄')
    
@router_districts.message(Admin.coord)
async def data(msg: Message, state: FSMContext):
    '''fad'''
    data = await state.get_data()
    
    df = pd.read_json('../data/yar_districts.json')
    
    coord = [[float(coord) for coord in point.split(', ')] for point in msg.text.splitlines()]
    
    if len(df.loc[data['name'], 'geometry'][0]) == 5:
        df.loc[data['name'], 'geometry'] = [[[]]]
    
    df.loc[data['name'], 'geometry'][0].extend(coord)
    
    if len(df.loc[data['name'], 'geometry'][0][0]) != 2:
        df.loc[data['name'], 'geometry'][0].pop(0)
    
    df.to_json('../data/yar_districts.json')
    
    await msg.answer('Записал! Если больше нет, напиши все, иначе просто шли еще')