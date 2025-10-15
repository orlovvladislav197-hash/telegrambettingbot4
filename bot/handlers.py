from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states import BetStates
from bot.games import play_roll, play_rps, play_bowling
from decimal import Decimal
import os

router = Router()

def get_main_kb(telegram_id=None):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Кубик (Чёт/Нечёт)', callback_data='game_dice')],
        [InlineKeyboardButton(text='Камень/Ножницы/Бумага', callback_data='game_rps')],
        [InlineKeyboardButton(text='Боулинг (0-10)', callback_data='game_bowling')],
        [InlineKeyboardButton(text='Баланс', callback_data='balance')],
        [InlineKeyboardButton(text='Пополнить', url=get_deposit_url(telegram_id))]
    ])
    return kb

def get_deposit_url(telegram_id):
    botname = os.getenv('CRYPTO_BOT_USERNAME', 'CryptoBot')
    if telegram_id:
        return f'https://t.me/{botname}?start={telegram_id}'
    return f'https://t.me/{botname}'

@router.message(Command('start'))
async def cmd_start(message: Message):
    pool = message.bot['db_pool']
    async with pool.acquire() as conn:
        rec = await conn.fetchrow('SELECT id FROM users WHERE telegram_id=$1', message.from_user.id)
        if not rec:
            await conn.execute('INSERT INTO users(telegram_id, username) VALUES($1,$2)', message.from_user.id, message.from_user.username)
    await message.reply('Добро! Выберите игру.', reply_markup=get_main_kb(message.from_user.id))

@router.callback_query(lambda c: c.data and (c.data.startswith('game_') or c.data in ('balance','deposit')))
async def handle_cb(cb: CallbackQuery, state: FSMContext):
    pool = cb.bot['db_pool']
    if cb.data == 'game_dice':
        await state.update_data(game='dice')
        await state.set_state(BetStates.waiting_for_amount)
        await cb.message.answer('Ставка на кубик (чёт/нечёт). Введите: amount even|odd (например: 0.01 even)')
        await cb.answer()
        return
    if cb.data == 'game_rps':
        await state.update_data(game='rps')
        await state.set_state(BetStates.waiting_for_amount)
        await cb.message.answer('Камень/Ножницы/Бумага. Введите: amount rock|paper|scissors (например: 0.05 rock)')
        await cb.answer()
        return
    if cb.data == 'game_bowling':
        await state.update_data(game='bowling')
        await state.set_state(BetStates.waiting_for_amount)
        await cb.message.answer('Боулинг. Угадай падение кеглей 0-10. Введите: amount number (например: 0.02 7)')
        await cb.answer()
        return
    if cb.data == 'balance':
        async with pool.acquire() as conn:
            row = await conn.fetchrow('SELECT balance FROM users WHERE telegram_id=$1', cb.from_user.id)
            bal = row['balance'] if row else 0
        await cb.message.answer(f'Ваш баланс: {bal}')
        await cb.answer()
        return

@router.message()
async def on_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('game'):
        await message.reply('Сначала выберите игру.')
        return
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.reply('Формат: amount choice. Например: 0.01 even')
        return
    try:
        amount = Decimal(parts[0])
    except:
        await message.reply('Некорректная сумма.')
        return
    choice = parts[1].lower()
    pool = message.bot['db_pool']
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT id, balance FROM users WHERE telegram_id=$1 FOR UPDATE', message.from_user.id)
        if not user:
            await message.reply('Юзер не найден. Набери /start')
            await state.clear()
            return
        if user['balance'] < amount:
            await message.reply('Недостаточно средств')
            await state.clear()
            return
        await conn.execute('UPDATE users SET balance = balance - $1 WHERE id = $2', amount, user['id'])
        bet_row = await conn.fetchrow('INSERT INTO bets(user_id, bet_amount, choice, choice_text) VALUES($1,$2,$3,$4) RETURNING id', user['id'], amount, data['game'], choice)
    if data['game'] == 'dice':
        result_value, won, profit = play_roll(choice, amount)
        result_msg = f'Выпало: {result_value}. {"Вы выиграли!" if won else "Вы проиграли."}'
        result_field = str(result_value)
    elif data['game'] == 'rps':
        comp_move, won, profit = play_rps(choice, amount)
        result_msg = f'Компьютер: {comp_move}. {"Вы выиграли!" if won else "Вы проиграли."}'
        result_field = comp_move
    elif data['game'] == 'bowling':
        knocked, won, profit = play_bowling(choice, amount)
        result_msg = f'Попадание: {knocked} кеглей. {"Вы выиграли!" if won else "Вы проиграли."}'
        result_field = str(knocked)
    else:
        await message.reply('Неизвестная игра.')
        await state.clear()
        return
    async with pool.acquire() as conn:
        await conn.execute('UPDATE bets SET result_value=$1, win=$2, profit=$3 WHERE id=$4', result_field, won, profit, bet_row['id'])
        if won:
            await conn.execute('UPDATE users SET balance = balance + $1 WHERE id = $2', amount + profit, user['id'])
    await message.reply(result_msg)
    await state.clear()
