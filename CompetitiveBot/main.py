import asyncio
import logging
from aiogram.methods import DeleteWebhook
from create import dp, bot
from commands import get_tasks, get_languages, submit_solution, get_result, get_scoreboard, add_user, get_user_info, menu


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())

