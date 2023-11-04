from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Кнопка с меню в зависимости от типа пользователя
menu_keyboard = InlineKeyboardMarkup()
m_b1 = InlineKeyboardButton(text="Просмотр задач", callback_data="tasks")
m_b2 = InlineKeyboardButton(text="Рейтинг", callback_data="rating")
m_b3 = InlineKeyboardButton(text="Личные данные", callback_data="info")
m_b4 = InlineKeyboardButton(text="Доступные языки", callback_data="lang")
menu_keyboard.add(m_b1).add(m_b2).add(m_b3).add(m_b4)


# Клавиатура выбора между регистрацией и авторизацией для незарегистрированного пользователя
new_user_ikb = InlineKeyboardMarkup(row_width=2)
new_user_ib1 = InlineKeyboardButton(text="Регистрация", callback_data="student")
new_user_ib2 = InlineKeyboardButton(text="Авторизация", callback_data="authorization")
new_user_ikb.add(new_user_ib1, new_user_ib2)

# Клавиатура просмотра списка задач
tasks_navigation = InlineKeyboardMarkup()
tn_b1 = InlineKeyboardButton(text="Меню", callback_data="menu_inline")
tn_b2 = InlineKeyboardButton(text="Назад", callback_data="left_task")
tn_b3 = InlineKeyboardButton(text="Вперед", callback_data="right_task")
tn_b4 = InlineKeyboardButton(text="Отправить решение", callback_data="solution")
tasks_navigation.add(tn_b1).add(tn_b2, tn_b3).add(tn_b4)

languages_ikb = InlineKeyboardMarkup()
l_b1 = InlineKeyboardButton(text="C", callback_data="lang_C")
l_b2 = InlineKeyboardButton(text="C++", callback_data="lang_C++")
l_b3 = InlineKeyboardButton(text="Java", callback_data="lang_Java")
l_b4 = InlineKeyboardButton(text="Python 3", callback_data="Python 3")
languages_ikb.add(l_b1, l_b2, l_b3, l_b4)
