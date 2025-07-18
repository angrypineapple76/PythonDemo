import aiosqlite
from aiogram import types

async def create_tables():
    async with aiosqlite.connect('quiz_bot.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state 
                         (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS user_records 
                         (user_id INTEGER PRIMARY KEY, username TEXT, max_score INTEGER)''')
        await db.commit()

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect('quiz_bot.db') as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', 
                        (user_id, index))
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            return results[0] if results is not None else 0

async def update_user_record(user_id, username, score):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT max_score FROM user_records WHERE user_id = ?', (user_id,)) as cursor:
            record = await cursor.fetchone()
            
            if record is None:
                await db.execute('INSERT INTO user_records (user_id, username, max_score) VALUES (?, ?, ?)',
                                (user_id, username, score))
            elif score > record[0]:
                await db.execute('UPDATE user_records SET max_score = ?, username = ? WHERE user_id = ?',
                                (score, username, user_id))
            
            await db.commit()

async def get_leaderboard():
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT username, max_score FROM user_records ORDER BY max_score DESC LIMIT 10') as cursor:
            return await cursor.fetchall()

async def get_user_max_score(user_id):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT max_score FROM user_records WHERE user_id = ?', (user_id,)) as cursor:
            record = await cursor.fetchone()
            return record[0] if record else 0