from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

back_b = InlineKeyboardButton(text='Отмена', callback_data='back')
menu_inline_b = InlineKeyboardButton(text="Меню", callback_data="menu_inline")

back_ikb = InlineKeyboardBuilder()
back_ikb = back_ikb.add(back_b).adjust(1).as_markup()

menu_ikb = InlineKeyboardBuilder()
menu_ikb = menu_ikb.add(menu_inline_b).adjust(1).as_markup()

# Клавиатура для информации о пользователе
user_info_ikb = InlineKeyboardBuilder()
user_info_b1 = InlineKeyboardButton(text="Решенные задачи", callback_data="solved_tasks")
user_info_ikb = user_info_ikb.add(user_info_b1, menu_inline_b).adjust(1).as_markup()

# Клавиатура для регистрации пользователя
registration_ikb = InlineKeyboardBuilder()
r_b1 = InlineKeyboardButton(text="Регистрация", callback_data="registration")
registration_ikb = registration_ikb.add(r_b1).adjust(1).as_markup()

# Кнопка с меню в зависимости от типа пользователя
menu_keyboard = InlineKeyboardBuilder()
m_b1 = InlineKeyboardButton(text="Просмотр задач", callback_data="tasks")
m_b2 = InlineKeyboardButton(text="Рейтинг", callback_data="rating")
m_b3 = InlineKeyboardButton(text="Личные данные", callback_data="info")
m_b4 = InlineKeyboardButton(text="Доступные языки", callback_data="lang")
menu_keyboard = menu_keyboard.add(m_b1, m_b2, m_b3, m_b4).adjust(1).as_markup()

# Клавиатура с уровнями задач
level_ikb = InlineKeyboardBuilder()
l_b1 = InlineKeyboardButton(text="Легкий", callback_data="A")
l_b2 = InlineKeyboardButton(text="Средний", callback_data="B")
l_b3 = InlineKeyboardButton(text="Сложный", callback_data="C")
level_ikb = level_ikb.add(l_b1, l_b2, l_b3).adjust(1).as_markup()

# Клавиатура просмотра списка задач
tasks_navigation = InlineKeyboardBuilder()
tn_b1 = InlineKeyboardButton(text="Подробнее", callback_data="more_task")
tn_b2 = InlineKeyboardButton(text="Отправить решение", callback_data="solution")
tn_b3 = InlineKeyboardButton(text="Назад", callback_data="left_task")
tn_b4 = InlineKeyboardButton(text="Вперед", callback_data="right_task")
tn_b5 = InlineKeyboardButton(text="Выбрать уровень", callback_data="tasks")
tasks_navigation.add(tn_b1, tn_b2, tn_b3, tn_b4, tn_b5, menu_inline_b)
tasks_navigation = tasks_navigation.adjust(1, 1, 2, 1).as_markup()

# Клавиатура после вывода исходного кода
source_code_ikb = InlineKeyboardBuilder()
source_code_ikb = source_code_ikb.add(user_info_b1, menu_inline_b).adjust(1, 1).as_markup()

# Клавиатура после получения результата тестирования задачи
after_result_ikb = InlineKeyboardBuilder()
ar_b1 = InlineKeyboardButton(text="Исходный код", callback_data="code_source")
after_result_ikb = after_result_ikb.add(m_b1, menu_inline_b).adjust(1).as_markup()

# Клавиатура просмотра списка решенных задач
solved_tasks_nav = InlineKeyboardBuilder()
stn_b1 = InlineKeyboardButton(text="Назад", callback_data="left_s")
stn_b2 = InlineKeyboardButton(text="Вперед", callback_data="right_s")
solved_tasks_nav = solved_tasks_nav.add(stn_b1, stn_b2, ar_b1, m_b3, menu_inline_b).adjust(2, 1).as_markup()

# Клавиатура для выбора языка
languages_ikb = InlineKeyboardBuilder()
l_b1 = InlineKeyboardButton(text="C", callback_data="lang_C")
l_b2 = InlineKeyboardButton(text="C++", callback_data="lang_C++")
l_b3 = InlineKeyboardButton(text="Java", callback_data="lang_Java")
l_b4 = InlineKeyboardButton(text="Python 3", callback_data="lang_Python")
languages_ikb = languages_ikb.add(l_b1, l_b2, l_b3, l_b4).adjust(2).as_markup()

# Клавиатура для просмотра результата решения задачи
check_result_ikb = InlineKeyboardBuilder()
check_result_b1 = InlineKeyboardButton(text="Получить результат", callback_data="check_result")
check_result_ikb = check_result_ikb.add(check_result_b1).adjust(1).as_markup()

# Клавиатура для возврата к просмотру результата решения
return_result_ikb = InlineKeyboardBuilder()
rr_b1 = InlineKeyboardButton(text="Назад", callback_data="check_result")
return_result_ikb = return_result_ikb.add(rr_b1, menu_inline_b).adjust(1).as_markup()
