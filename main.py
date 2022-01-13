import asyncio
import logging
import re
from datetime import datetime
import random

import aioschedule

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from db import Database
from config import bot, photo_id, admin_id, user_dictionary, bot_dictionary, date_start
from markups import mainMenu

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=bot)
dp = Dispatcher(bot, storage=MemoryStorage())

db = Database('database.db')

with open(user_dictionary, "r", encoding='utf-8') as word_list:
    user_dictionary_list = word_list.read().split('\n')


class NewGame(StatesGroup):
    line_1 = State()
    line_2 = State()
    line_3 = State()
    line_4 = State()
    line_5 = State()
    line_6 = State()


async def new_word():
    with open(bot_dictionary, "r", encoding='utf-8') as word_list:
        bot_dictionary_list = word_list.read().split('\n')
    db.add_word(random.choice(bot_dictionary_list))
    await bot.send_message(admin_id, 'Новое слово сегодня №' + str((datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days) + ' - ' + db.get_word(), reply_markup=mainMenu)


async def scheduler():
    aioschedule.every().day.at("00:01").do(new_word)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
        await bot.send_photo(message.from_user.id, photo_id,
                             "Добро пожаловать в русскую адаптацию игры Wordle!\n"
                             "Угадайте Вордли за 6 попыток. После каждой отгадки цвет плитки будет меняться, "
                             "чтобы показать, насколько близко Ваше слово к искомому. Пример приведен ниже.\n")
        await bot.send_message(message.from_user.id,
                               "*КОРКА*\n"
                               "🟩⬜️⬜️️️⬜️⬜️\n"
                               "_Буква К находится в загаданном слове и в правильном месте._\n"
                               "\n*ПИЛОТ*\n"
                               "⬜️⬜️🟨️️⬜️⬜️\n"
                               "_Буква Л есть в загаданном слове, но в неправильном месте._\n"
                               "\n*ЧЕРВИ*\n"
                               "⬜️⬜️⬜️⬜️⬜️\n"
                               "_Все буквы отсутствуют в загаданном слове на любом месте._\n", parse_mode='Markdown',
                               reply_markup=mainMenu)
    else:
        await bot.send_message(message.from_user.id, "Добро пожаловать еще раз!", reply_markup=mainMenu)


@dp.message_handler(commands=['now_word'])
async def bot_now_word(message: types.Message):
    if message.from_user.id == admin_id:
        await bot.send_message(message.from_user.id,
                               db.get_word(),
                               reply_markup=mainMenu)


@dp.message_handler(commands=['new_word'])
async def bot_new_word(message: types.Message):
    if message.from_user.id == admin_id:
        await new_word()
        await bot.send_message(message.from_user.id,
                               'Вы изменили слово!',
                               reply_markup=mainMenu)


@dp.message_handler(content_types=['text'])
async def bot_menu(message: types.Message):
    if message.text == 'Новая игра':
        if not (datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days == db.get_played_time(message.from_user.id):
            await bot.send_message(message.from_user.id, "Игра началась!\n"
                                                         "Введите Ваше слово:",
                                   reply_markup=types.ReplyKeyboardRemove())
            await NewGame.line_1.set()
        else:
            await bot.send_message(message.from_user.id,
                                   "Вы уже играли сегодня! Завтра будет доступно следующее слово.",
                                   reply_markup=mainMenu)
    elif message.text == 'Правила':
        await bot.send_message(message.from_user.id,
                               "Угадайте Вордли за 6 попыток. После каждой отгадки цвет плитки будет меняться, "
                               "чтобы показать, насколько близко Ваше слово к искомому. Пример приведен ниже.\n")
        await bot.send_message(message.from_user.id,
                               "*КОРКА*\n"
                               "🟩⬜️⬜️️️⬜️⬜️\n"
                               "_Буква К находится в загаданном слове и в правильном месте._\n"
                               "\n*ПИЛОТ*\n"
                               "⬜️⬜️🟨️️⬜️⬜️\n"
                               "_Буква Л есть в загаданном слове, но в неправильном месте._\n"
                               "\n*ЧЕРВИ*\n"
                               "⬜️⬜️⬜️⬜️⬜️\n"
                               "_Все буквы отсутствуют в загаданном слове на любом месте._\n", parse_mode='Markdown',
                               reply_markup=mainMenu)
    elif message.text == 'Статистика':
        if db.get_played_time(message.from_user.id):
            winning = db.get_winning(message.from_user.id)
            losing = db.get_losing(message.from_user.id)
            current_streak = db.get_current_streak(message.from_user.id)
            max_streak = db.get_max_streak(message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   f"Сыграно: *{winning + losing}*\n"
                                   f"Выигрыши: *{round(winning / (winning + losing) * 100, 1)}%*\n"
                                   f"Текущая череда побед: *{current_streak}*\n"
                                   f"Максимальная череда побед: *{max_streak}*\n", parse_mode='Markdown',
                                   reply_markup=mainMenu)
        else:
            await bot.send_message(message.from_user.id, "Вы еще ни разу не играли!", reply_markup=mainMenu)
    else:
        await bot.send_message(message.from_user.id, "Ошибка!", reply_markup=mainMenu)


@dp.message_handler(content_types=['photo'])
async def bot_get_photo(message: types.Message):
    if message.from_user.id == admin_id:
        document_id = message.photo
        await bot.send_message(message.from_user.id, f"ID файла:\n{document_id}")


def check_line(message):
    if not bool(re.search('[а-яА-Я]', message)):
        return 'Введены некорректные символы!\nВведите другое слово:'
    elif not len(message) == 5:
        return 'Необходимо ввести слово состоящие из 5 букв!\nВведите другое слово:'
    elif not message in user_dictionary_list:
        return 'Такого слова нет в словаре!\nВведите другое слово:'
    else:
        return False


def get_blocks(message, word):
    blocks = ""
    for i, letter in enumerate(message, 0):
        if letter == word[i]:
            blocks += "🟩"
        elif word.find(letter) > -1:
            blocks += "🟨️"
        else:
            blocks += "⬜️"
    return blocks


def set_winner(id):
    db.add_winning(id)
    db.add_current_streak(id, True)
    if db.get_current_streak(id) > db.get_max_streak(id):
        db.add_max_streak(id)
    db.add_played_time(id)


@dp.message_handler(state=NewGame.line_1)
async def set_line_1(message: types.Message, state: FSMContext):
    check_result = check_line(message.text.lower())
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['original_word'] = db.get_word()
            data['line_1'] = get_blocks(message.text.lower(), data['original_word'])
        if data['original_word'] == message.text.lower():
            set_winner(message.from_user.id)
            await bot.send_message(message.from_user.id, "Поздравляем! Вы угадали слово.")
            await bot.send_message(message.from_user.id, f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} 1/6\n\n"
                                                         f"{data['line_1']}", reply_markup=mainMenu)
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, f"{data['line_1']}\n"
                                                         f"\nВведите следующее слово:")
            await NewGame.next()


@dp.message_handler(state=NewGame.line_2)
async def set_line_2(message: types.Message, state: FSMContext):
    check_result = check_line(message.text.lower())
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['line_2'] = get_blocks(message.text.lower(), data['original_word'])
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!", reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                set_winner(message.from_user.id)
                await bot.send_message(message.from_user.id, "Поздравляем! Вы угадали слово.")
                await bot.send_message(message.from_user.id, f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} 2/6\n\n"
                                                             f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n", reply_markup=mainMenu)
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_3)
async def set_line_3(message: types.Message, state: FSMContext):
    check_result = check_line(message.text.lower())
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['line_3'] = get_blocks(message.text.lower(), data['original_word'])
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!", reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                set_winner(message.from_user.id)
                await bot.send_message(message.from_user.id, "Поздравляем! Вы угадали слово.")
                await bot.send_message(message.from_user.id, f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} 3/6\n\n"
                                                             f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"{data['line_3']}\n", reply_markup=mainMenu)
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"{data['line_3']}\n"
                                                             f"\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_4)
async def set_line_4(message: types.Message, state: FSMContext):
    check_result = check_line(message.text.lower())
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['line_4'] = get_blocks(message.text.lower(), data['original_word'])
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!", reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                set_winner(message.from_user.id)
                await bot.send_message(message.from_user.id, "Поздравляем! Вы угадали слово.")
                await bot.send_message(message.from_user.id, f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} 4/6\n\n"
                                                             f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"{data['line_3']}\n"
                                                             f"{data['line_4']}\n", reply_markup=mainMenu)
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"{data['line_3']}\n"
                                                             f"{data['line_4']}\n"
                                                             f"\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_5)
async def set_line_5(message: types.Message, state: FSMContext):
    check_result = check_line(message.text.lower())
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['line_5'] = get_blocks(message.text.lower(), data['original_word'])
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!", reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                set_winner(message.from_user.id)
                await bot.send_message(message.from_user.id, "Поздравляем! Вы угадали слово.")
                await bot.send_message(message.from_user.id, f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} 5/6\n\n"
                                                             f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"{data['line_3']}\n"
                                                             f"{data['line_4']}\n"
                                                             f"{data['line_5']}\n", reply_markup=mainMenu)
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"{data['line_3']}\n"
                                                             f"{data['line_4']}\n"
                                                             f"{data['line_5']}\n"
                                                             f"\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_6)
async def set_line_6(message: types.Message, state: FSMContext):
    check_result = check_line(message.text.lower())
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['line_6'] = get_blocks(message.text.lower(), data['original_word'])
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!", reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                set_winner(message.from_user.id)
                await bot.send_message(message.from_user.id, "Поздравляем! Вы угадали слово.")
                await bot.send_message(message.from_user.id, f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} 6/6\n\n"
                                                             f"{data['line_1']}\n"
                                                             f"{data['line_2']}\n"
                                                             f"{data['line_3']}\n"
                                                             f"{data['line_4']}\n"
                                                             f"{data['line_5']}\n"
                                                             f"{data['line_6']}\n", reply_markup=mainMenu)
                await state.finish()
            else:
                db.add_losing(message.from_user.id)
                db.add_current_streak(message.from_user.id, False)
                db.add_played_time(message.from_user.id)
                await bot.send_message(message.from_user.id, f"Вы не угадали слово - {data['original_word']}")
                await bot.send_message(message.from_user.id,
                                       f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} X/6*\n\n"
                                       f"{data['line_1']}\n"
                                       f"{data['line_2']}\n"
                                       f"{data['line_3']}\n"
                                       f"{data['line_4']}\n"
                                       f"{data['line_5']}\n"
                                       f"{data['line_6']}\n", reply_markup=mainMenu)
                await state.finish()


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=False, on_startup=on_startup)
