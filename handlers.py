from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode



router = Router()


user_state = {}
user_data = {}
botmsg=bot = Bot(token="YourToken", parse_mode=ParseMode.HTML)


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(f"{msg.from_user.username}, Добро пожаловать в компанию DamnIT !")
    await msg.answer(f"Напишите свое ФИО:")
    user_state[msg.from_user.id] = "FIO"


@router.message()
async def text_handler(msg: Message):
    user_id = msg.from_user.id
    if user_id not in user_state:
        await msg.answer("Чтобы начать, введите /start")
        return

    if user_state[user_id] == "FIO":
        if any(char.isdigit() for char in msg.text):
            await msg.answer("ФИО не должно содержать цифры. Пожалуйста, введите свое ФИО.")
            return
        user_data[user_id] = {"FIO": msg.text}
        user_state[user_id] = "PHONE"
        await msg.answer("Укажите Ваш номер телефона в формате 7 999 999 99 99:")
    elif user_state[user_id] == "PHONE":
        if not msg.text.replace(' ', '').isdigit() or len(msg.text.replace(' ', '')) != 11:
            await msg.answer("Номер телефона должен быть указан в формате 7 999 999 99 99. Пожалуйста, попробуйте еще раз.")
            return
        user_data[user_id]["PHONE"] = msg.text
        user_state[user_id] = "COMMENT"
        await msg.answer("Напишите любой комментарий:")
    elif user_state[user_id] == "COMMENT":
        user_data[user_id]["COMMENT"] = msg.text
        user_state[user_id] = "CONFIRMATION"
        path="test.pdf"
        await msg.answer_document(FSInputFile(path))
        await msg.answer("Последний шаг! Ознакомьтесь с вводными положениями и нажмите кнопку \"Ознакомлен\":",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Ознакомлен", callback_data="confirm")]
                         ]))
    elif user_state[user_id] == "CONFIRMATION":
        if msg.text.lower() == "ознакомлен":
            pathpic = FSInputFile('pic.jpg')
            await msg.answer_photo(photo=pathpic)
            await msg.answer("Спасибо за успешную регистрацию! Вот ваши данные:")
            #await main.bot.send_message(5224208100,f"ФИО: {user_data[user_id]['FIO']}" )
            await msg.answer(f"ФИО: {user_data[user_id]['FIO']}")
            await msg.answer(f"Номер телефона: {user_data[user_id]['PHONE']}")
            await msg.answer(f"Комментарий: {user_data[user_id]['COMMENT']}")
            del user_state[user_id]
            del user_data[user_id]
        else:
            await msg.answer("Пожалуйста, ознакомьтесь с вводными положениями и подтвердите, что ознакомились.")


@router.callback_query()
async def callback_handler(callback_query: types.CallbackQuery):
    if callback_query.data == "confirm":
        user_id = callback_query.from_user.id
        if user_id in user_state and user_state[user_id] == "CONFIRMATION":
            await callback_query.message.answer("Вы подтвердили ознакомление.")
            pathpic=FSInputFile('pic.jpg')
            await callback_query.message.answer_photo(photo=pathpic)
            await callback_query.message.answer("Спасибо за успешную регистрацию! Вот ваши данные:")
            await botmsg.send_message(5224208100, f"ФИО: {user_data[user_id]['FIO']}")
            await callback_query.message.answer(f"ФИО: {user_data[user_id]['FIO']}")
            await botmsg.send_message(5224208100, f"Номер телефона: {user_data[user_id]['PHONE']}")
            await callback_query.message.answer(f"Номер телефона: {user_data[user_id]['PHONE']}")
            await botmsg.send_message(5224208100, f"Комментарий: {user_data[user_id]['COMMENT']}")
            await callback_query.message.answer(f"Комментарий: {user_data[user_id]['COMMENT']}")
            del user_state[user_id]
            del user_data[user_id]
        else:
            await callback_query.message.answer("Чтобы продолжить, введите /start")
