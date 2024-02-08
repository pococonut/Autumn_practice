from aiogram import types, F
from create import dp
from keyboards import menu_ikb
from commands.url_requests import read_languages


def get_list_available_langs(result):
    """
    Функция возвращает строку с названиями допустимых языков программирования
    Args:
        result: Результат запроса БД

    Returns: Строка с названиями допустимых ЯП
    """

    return "\n▫️ ".join([i['name'] for i in result])


@dp.callback_query(F.data == 'lang')
async def languages(callback: types.CallbackQuery):
    """
    Функция для получения списка доступных языков программирования
    """

    langs = read_languages()
    if langs:
        available_langs = get_list_available_langs(langs)
        await callback.message.edit_text(f'Решения принимаются на языках:\n▫️ {available_langs}',
                                         reply_markup=menu_ikb)
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_ikb)
