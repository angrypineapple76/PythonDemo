from aiogram import F, types
from aiogram.filters.command import Command
from aiogram import Dispatcher
from database import *
from keyboards import *
from questions_data import quiz_data

# Глобальный словарь для хранения счетчиков правильных ответов
user_scores = {}
user_answers = {}

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_quiz, F.text=="Начать игру")
    dp.message.register(cmd_quiz, Command("quiz"))
    dp.message.register(cmd_myrecord, F.text=="Мой рекорд")
    dp.message.register(cmd_myrecord, Command("myrecord"))
    dp.message.register(cmd_leaderboard, F.text=="Лидерборд")
    dp.message.register(cmd_leaderboard, Command("leaderboard"))
    dp.callback_query.register(right_answer, F.data == "right_answer")
    dp.callback_query.register(wrong_answer, F.data == "wrong_answer")

async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в квиз!",
        reply_markup=get_main_menu_keyboard()
    )

async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

async def new_quiz(message):
    user_id = message.from_user.id
    user_scores[user_id] = 0
    await update_quiz_index(user_id, 0)
    await get_question(message, user_id)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    
    await message.answer(
        f"{quiz_data[current_question_index]['question']}",
        reply_markup=generate_options_keyboard(opts, opts[correct_index])
    )

async def right_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    correct_answer = question_data['options'][question_data['correct_option']]
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    if user_id not in user_answers:
        user_answers[user_id] = []
    
    user_answers[user_id].append((
        question_data['question'],
        correct_answer,
        True
    ))

    user_id = callback.from_user.id
    if user_id not in user_scores:
        user_scores[user_id] = 0
    user_scores[user_id] += 1

    await callback.message.answer(f"✅ Верно! Ваш ответ: {correct_answer}")
    await handle_next_question(callback)

async def wrong_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    correct_answer = question_data['options'][question_data['correct_option']]
    
    chosen_answer = callback.data.split('_')[0]
    
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    if user_id not in user_answers:
        user_answers[user_id] = []
    
    user_answers[user_id].append((
        question_data['question'],
        chosen_answer,
        False
    ))

    await callback.message.answer(f"❌ Неверно! Правильный ответ: {correct_answer}")
    await handle_next_question(callback)

async def handle_next_question(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        score = user_scores.get(user_id, 0)
        total_questions = len(quiz_data)
        username = callback.from_user.username or callback.from_user.first_name
        
        await update_user_record(user_id, username, score)
        
        await callback.message.answer(
            f"Квиз завершен!\n"
            f"Ваш результат: {score} из {total_questions}\n"
            f"Ваш лучший результат: {await get_user_max_score(user_id)} из {total_questions}"
        )

async def cmd_myrecord(message: types.Message):
    user_id = message.from_user.id
    max_score = await get_user_max_score(user_id)
    await message.answer(f"Ваш лучший результат: {max_score} из {len(quiz_data)}")

async def cmd_leaderboard(message: types.Message):
    leaders = await get_leaderboard()
    
    if not leaders:
        await message.answer("Лидерборд пока пуст.")
        return
    
    leaderboard_text = "🏆 Топ-10 игроков:\n\n"
    for i, (username, score) in enumerate(leaders, 1):
        leaderboard_text += f"{i}. {username}: {score} из {len(quiz_data)}\n"
    
    await message.answer(leaderboard_text)