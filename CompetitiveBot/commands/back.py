from create import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import menu_keyboard


@dp.callback_query_handler(text='back', state="*")
async def back_func1(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_reply_markup()
    keyboard = menu_keyboard
    await callback.message.edit_text('Действие отменено.', reply_markup=keyboard)