from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

back_b = InlineKeyboardButton('Отмена', callback_data='back')
menu_inline_b = InlineKeyboardButton(text="Меню", callback_data="menu_inline")

back_ikb = InlineKeyboardMarkup()
back_ikb.add(back_b)
menu_ikb = InlineKeyboardMarkup()
menu_ikb.add(menu_inline_b)

# Клавиатура для информации о пользователе
user_info_ikb = InlineKeyboardMarkup()
user_info_b1 = InlineKeyboardButton(text="Решенные задачи", callback_data="solved_tasks")
user_info_ikb.add(user_info_b1).add(menu_inline_b)

# Клавиатура для регистрации пользователя
registration_ikb = InlineKeyboardMarkup()
r_b1 = InlineKeyboardButton(text="Регистрация", callback_data="registration")
registration_ikb.add(r_b1)

# Кнопка с меню в зависимости от типа пользователя
menu_keyboard = InlineKeyboardMarkup()
m_b1 = InlineKeyboardButton(text="Просмотр задач", callback_data="tasks")
m_b2 = InlineKeyboardButton(text="Рейтинг", callback_data="rating")
m_b3 = InlineKeyboardButton(text="Личные данные", callback_data="info")
m_b4 = InlineKeyboardButton(text="Доступные языки", callback_data="lang")
menu_keyboard.add(m_b1).add(m_b2).add(m_b3).add(m_b4)

# Клавиатура с уровнями задач
level_ikb = InlineKeyboardMarkup()
l_b1 = InlineKeyboardButton(text="Легкий", callback_data="A")
l_b2 = InlineKeyboardButton(text="Средний", callback_data="B")
l_b3 = InlineKeyboardButton(text="Сложный", callback_data="C")
level_ikb.add(l_b1).add(l_b2).add(l_b3)

# Клавиатура выбора между регистрацией и авторизацией для незарегистрированного пользователя
new_user_ikb = InlineKeyboardMarkup(row_width=2)
new_user_ib1 = InlineKeyboardButton(text="Регистрация", callback_data="student")
new_user_ib2 = InlineKeyboardButton(text="Авторизация", callback_data="authorization")
new_user_ikb.add(new_user_ib1, new_user_ib2)

# Клавиатура просмотра списка задач
tasks_navigation = InlineKeyboardMarkup()
tn_b1 = InlineKeyboardButton(text="Подробнее", callback_data="more_task")
tn_b2 = InlineKeyboardButton(text="Отправить решение", callback_data="solution")
tn_b3 = InlineKeyboardButton(text="Назад", callback_data="left_task")
tn_b4 = InlineKeyboardButton(text="Вперед", callback_data="right_task")
tn_b5 = InlineKeyboardButton(text="Выбрать уровень", callback_data="tasks")
tasks_navigation.add(tn_b1).add(tn_b2).add(tn_b3, tn_b4).add(tn_b5).add(menu_inline_b)

# Клавиатура после получения результата тестирования задачи
after_result_ikb = InlineKeyboardMarkup()
ar_b1 = InlineKeyboardButton(text="Исходный код", callback_data="code_source")
after_result_ikb.add(user_info_b1).add(m_b3).add(menu_inline_b)

# Клавиатура просмотра списка решенных задач
solved_tasks_nav = InlineKeyboardMarkup()
stn_b1 = InlineKeyboardButton(text="Назад", callback_data="left_s")
stn_b2 = InlineKeyboardButton(text="Вперед", callback_data="right_s")
solved_tasks_nav.add(stn_b1, stn_b2).add(ar_b1).add(m_b3).add(menu_inline_b)

# Клавиатура для выбора языка
languages_ikb = InlineKeyboardMarkup()
l_b1 = InlineKeyboardButton(text="C", callback_data="lang_C")
l_b2 = InlineKeyboardButton(text="C++", callback_data="lang_C++")
l_b3 = InlineKeyboardButton(text="Java", callback_data="lang_Java")
l_b4 = InlineKeyboardButton(text="Python 3", callback_data="lang_Python")
languages_ikb.add(l_b1, l_b2, l_b3, l_b4)

# Клавиатура для просмотра результата решения задачи
check_result_ikb = InlineKeyboardMarkup()
check_result_b1 = InlineKeyboardButton(text="Получить результат", callback_data="check_result")
check_result_ikb.add(check_result_b1)

# Клавиатура для возврата к просмотру результата решения
return_result_ikb = InlineKeyboardMarkup()
rr_b1 = InlineKeyboardButton(text="Назад", callback_data="check_result")
return_result_ikb.add(rr_b1).add(menu_inline_b)