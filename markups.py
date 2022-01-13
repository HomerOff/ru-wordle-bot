from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Меню
btnNewGame = KeyboardButton('Новая игра')
btnRules = KeyboardButton('Правила')
btnStatistic = KeyboardButton('Статистика')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
mainMenu.add(btnNewGame).add(btnRules, btnStatistic)

# Подтверждение действий
btnDeny = KeyboardButton('🚫')
btnApply = KeyboardButton('✅')

mainChoice = ReplyKeyboardMarkup(resize_keyboard=True)
mainChoice.add(btnDeny, btnApply)
