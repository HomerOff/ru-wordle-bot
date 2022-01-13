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
from markups import mainMenu, mainChoice

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


class AdminMessage(StatesGroup):
    user_message = State()
    user_apply = State()


class AdminEdits(StatesGroup):
    user_apply = State()


async def new_word():
    with open(bot_dictionary, "r", encoding='utf-8') as word_list:
        bot_dictionary_list = word_list.read().split('\n')
    db.add_word(random.choice(bot_dictionary_list))
    await bot.send_message(admin_id, 'Новое слово сегодня №' + str(
        (datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days) + ' - ' + db.get_word(),
                           reply_markup=mainMenu)


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
        await bot.send_message(message.from_user.id, db.get_word(), reply_markup=mainMenu)
    else:
        await bot.send_message(message.from_user.id, "Ошибка\nВы не администратор!")


@dp.message_handler(commands=['new_word'])
async def bot_new_word(message: types.Message):
    if message.from_user.id == admin_id:
        await bot.send_message(message.from_user.id, 'Выполнить данное действие?', reply_markup=mainChoice)
        await AdminEdits.user_apply.set()
    else:
        await bot.send_message(message.from_user.id, "Ошибка\nВы не администратор!")


@dp.message_handler(commands=['count_users'])
async def bot_notice(message: types.Message):
    if message.from_user.id == admin_id:
        await bot.send_message(message.from_user.id, f"Количество пользователей: {db.get_count_users()}",
                               reply_markup=mainMenu)
    else:
        await bot.send_message(message.from_user.id, "Ошибка\nВы не администратор!")


@dp.message_handler(commands=['users_notice'])
async def bot_notice(message: types.Message):
    if message.from_user.id == admin_id:
        await bot.send_message(message.from_user.id, "Укажите сообщение, которое будет отправлено всем пользователям: ")
        await AdminMessage.user_message.set()
    else:
        await bot.send_message(message.from_user.id, "Ошибка\nВы не администратор!")


@dp.message_handler(content_types=['text'])
async def bot_menu(message: types.Message):
    if message.text == 'Новая игра':
        if not (datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days == db.get_played_time(
                message.from_user.id):
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


def check_line(message, user_words=[]):
    if not bool(re.search('[а-яА-Я]', message)):
        return 'Введены некорректные символы!\nВведите другое слово:'
    elif not len(message) == 5:
        return 'Необходимо ввести слово состоящие из 5 букв!\nВведите другое слово:'
    elif not (message in user_dictionary_list):
        return 'Такого слова нет в словаре!\nВведите другое слово:'
    elif message in user_words:
        return 'Вы уже вводили это слово!\nВведите другое слово:'
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


def set_winner(user_id):
    db.add_winning(user_id)
    db.add_current_streak(user_id, True)
    if db.get_current_streak(user_id) > db.get_max_streak(user_id):
        db.add_max_streak(user_id)
    db.add_played_time(user_id)


def set_loser(user_id):
    db.add_losing(user_id)
    db.add_current_streak(user_id, False)
    db.add_played_time(user_id)


async def user_win(user_id, lines):
    set_winner(user_id)
    await bot.send_message(user_id, "Поздравляем! Вы угадали слово.")
    backslash = '\n'
    await bot.send_message(user_id,
                           f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} {len(lines)}/6\n\n"
                           f"{backslash.join(lines)}", reply_markup=mainMenu)


@dp.message_handler(state=NewGame.line_1)
async def set_line_1(message: types.Message, state: FSMContext):
    check_result = check_line(message.text.lower())
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['user_words'] = []
            data['lines'] = []
            data['original_word'] = db.get_word()
            data['user_words'].append(message.text.lower())
            data['lines'].append(get_blocks(message.text.lower(), data['original_word']))
        if data['original_word'] == message.text.lower():
            await user_win(message.from_user.id, data['lines'])
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, '\n'.join(data['lines']) + "\n\nВведите следующее слово:")
            await NewGame.next()


@dp.message_handler(state=NewGame.line_2)
async def set_line_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    check_result = check_line(message.text.lower(), data['user_words'])
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['user_words'].append(message.text.lower())
            data['lines'].append(get_blocks(message.text.lower(), data['original_word']))
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!",
                                   reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                await user_win(message.from_user.id, data['lines'])
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, '\n'.join(data['lines']) + "\n\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_3)
async def set_line_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    check_result = check_line(message.text.lower(), data['user_words'])
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['user_words'].append(message.text.lower())
            data['lines'].append(get_blocks(message.text.lower(), data['original_word']))
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!",
                                   reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                await user_win(message.from_user.id, data['lines'])
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, '\n'.join(data['lines']) + "\n\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_4)
async def set_line_4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    check_result = check_line(message.text.lower(), data['user_words'])
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['user_words'].append(message.text.lower())
            data['lines'].append(get_blocks(message.text.lower(), data['original_word']))
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!",
                                   reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                await user_win(message.from_user.id, data['lines'])
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, '\n'.join(data['lines']) + "\n\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_5)
async def set_line_5(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    check_result = check_line(message.text.lower(), data['user_words'])
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['user_words'].append(message.text.lower())
            data['lines'].append(get_blocks(message.text.lower(), data['original_word']))
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!",
                                   reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                await user_win(message.from_user.id, data['lines'])
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, '\n'.join(data['lines']) + "\n\nВведите следующее слово:")
                await NewGame.next()


@dp.message_handler(state=NewGame.line_6)
async def set_line_6(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    check_result = check_line(message.text.lower(), data['user_words'])
    if check_result:
        await bot.send_message(message.from_user.id, check_result)
    else:
        async with state.proxy() as data:
            data['user_words'].append(message.text.lower())
            data['lines'].append(get_blocks(message.text.lower(), data['original_word']))
        if not db.get_word() == data['original_word']:
            await bot.send_message(message.from_user.id, "Слово уже было изменено. Начните новую игру!",
                                   reply_markup=mainMenu)
            await state.finish()
        else:
            if data['original_word'] == message.text.lower():
                await user_win(message.from_user.id, data['lines'])
                await state.finish()
            else:
                set_loser(message.from_user.id)
                await bot.send_message(message.from_user.id, f"Вы не угадали слово - {data['original_word']}")
                backslash = '\n'
                await bot.send_message(message.from_user.id,
                                       f"@RuWordleBot {(datetime.now() - datetime.strptime(date_start, '%Y-%m-%d')).days} X/6*\n\n"
                                       f"{backslash.join(data['lines'])}", reply_markup=mainMenu)
                await state.finish()


@dp.message_handler(state=AdminMessage.user_message)
async def set_admin_choice(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_message'] = message.text
    await AdminMessage.next()
    await bot.send_message(message.from_user.id, 'Выполнить данное действие?', reply_markup=mainChoice)


@dp.message_handler(state=AdminMessage.user_apply)
async def set_admin_result(message: types.Message, state: FSMContext):
    if message.text == '✅':
        async with state.proxy() as data:
            data['user_apply'] = message.text
        await bot.send_message(message.from_user.id, 'Сообщения отправляются, ожидайте...',
                               reply_markup=types.ReplyKeyboardRemove())
        user_count = 0
        for user in db.get_users():
            try:
                await bot.send_message(user[0], data['user_message'])
                user_count += 1
            except:
                await bot.send_message(message.from_user.id, f'Юзер с ID {str(user[0])} не найден!')
        await bot.send_message(message.from_user.id, f'Сообщение было отправлено всем пользователям!\n'
                                                     f'Количество отправленных сообщений: {str(user_count)}',
                               reply_markup=mainMenu)
    else:
        await bot.send_message(message.from_user.id, 'Сообщение НЕ было отправлено!', reply_markup=mainMenu)
    await state.finish()


@dp.message_handler(state=AdminEdits.user_apply)
async def set_admin_word(message: types.Message, state: FSMContext):
    if message.text == '✅':
        await new_word()
        await bot.send_message(message.from_user.id, f'Вы изменили слово дня!\nНовое слово: {db.get_word()}',
                               reply_markup=mainMenu)
    else:
        await bot.send_message(message.from_user.id, 'Слово дня НЕ было изменено!', reply_markup=mainMenu)
    await state.finish()


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=False, on_startup=on_startup)
