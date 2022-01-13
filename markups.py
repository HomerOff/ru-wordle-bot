from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

btnNewGame = KeyboardButton('Новая игра')
btnRules = KeyboardButton('Правила')
btnStatistic = KeyboardButton('Статистика')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)

mainMenu.add(btnNewGame).add(btnRules, btnStatistic)