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
from handler_marker import upload_html_to_github

router_districts = Router()

router_districts.message.filter(
    ChatTypeFilter(chat_type="private")
)


@router_districts.message(Command("give_map"))
async def give_map(msg: Message):
    '''Give us map url'''
    map_to_html('../data/yar_districts.json', '../data/markers.json', '../data/index.html')
    
    upload_html_to_github('../data/index.html')
    
    await msg.answer('Вот Ваша карта:\nhttps://yar-available-environment.onrender.com')
    

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

    kb = [[types.KeyboardButton(text=name)] for name in df['name']]

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
    df = pd.read_json('../data/yar_districts.json')
    
    if msg.text not in df['name'].values:
        await msg.answer('В данных нет такого района, попробуй другой')
        return
    
    await state.set_data({'name': msg.text})
    await msg.answer('Вписывай координаты:', reply_markup=types.ReplyKeyboardRemove())
    
    await state.set_state(Admin.coord)


@router_districts.message(Admin.coord, F.text.lower() == 'все')
async def end(msg: Message, state: FSMContext):
    '''fad'''
    await msg.reply_sticker('CAACAgIAAxkBAAIBCGfxUWZsKHKtdCfe-CA9DzshPuV5AAIEYQACoL2BSheQaxkxNRHbNgQ')
    await msg.answer('Реально? Тогда сейчас скину карту')
    await state.clear()
    
    map_to_html('../data/yar_districts.json', '../data/markers.json', '../data/index.html')
    
    upload_html_to_github('../data/index.html')
    
    await msg.answer(f'Вот ваша карта: \nhttps://yar-available-environment.onrender.com')

    
@router_districts.message(Admin.coord)
async def data(msg: Message, state: FSMContext):
    '''fad'''
    data = await state.get_data()
    
    df = pd.read_json('../data/yar_districts.json')
    
    coord = [[float(coord) for coord in point.split(', ')] for point in msg.text.splitlines()]
    
    row_idx = df[df['name'] == data['name']].index[0]

    if len(df.at[row_idx, 'geometry'][0]) == 5:
        df.at[row_idx, 'geometry'] = [[[]]]
    
    df.at[row_idx, 'geometry'][0].extend(coord)
    
    if len(df.at[row_idx, 'geometry'][0][0]) != 2:
        df.at[row_idx, 'geometry'][0].pop(0)
    
    df.to_json('../data/yar_districts.json', orient='records', indent=4, force_ascii=False)
    
    await msg.answer('Записал! Если больше нет, напиши все, иначе просто шли еще')