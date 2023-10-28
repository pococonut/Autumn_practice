from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Кнопка с меню в зависимости от типа пользователя
menu = InlineKeyboardMarkup()

m_b1 = InlineKeyboardButton(text="Просмотр задач", callback_data="tasks")
m_b2 = InlineKeyboardButton(text="Рейтинг", callback_data="tasks")
m_b3 = InlineKeyboardButton(text="Личные данные", callback_data="info")
menu.add(m_b1).add(m_b2).add(m_b3)

# Клавиатура для получения основного меню
chat_ikb = InlineKeyboardMarkup(row_width=2)
chat_ikb.add(menu)

# Клавиатура выбора между регистрацией и авторизацией для незарегистрированного пользователя
new_user_ikb = InlineKeyboardMarkup(row_width=2)
new_user_ib1 = InlineKeyboardButton(text="Регистрация", callback_data="student")
new_user_ib2 = InlineKeyboardButton(text="Авторизация", callback_data="authorization")
new_user_ikb.add(new_user_ib1, new_user_ib2)
