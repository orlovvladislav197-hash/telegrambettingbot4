import secrets
from decimal import Decimal

GAME_COEFFICIENTS = {
    'dice_even': Decimal('1.9'),
    'rps_win': Decimal('2.9'),
    'bowling_exact': Decimal('11.0'),
}

def play_roll(choice: str, bet_amount: Decimal):
    value = secrets.randbelow(6) + 1
    is_even = (value % 2 == 0)
    won = (is_even and choice=='even') or (not is_even and choice=='odd')
    profit = Decimal('0')
    if won:
        payout = (bet_amount * GAME_COEFFICIENTS['dice_even']).quantize(Decimal('0.00000001'))
        profit = payout - bet_amount
    return value, won, profit

def play_rps(choice: str, bet_amount: Decimal):
    moves = ['rock','paper','scissors']
    if choice not in moves:
        choice = 'rock'
    comp = secrets.choice(moves)
    if choice == comp:
        won = False
        profit = Decimal('0')
    else:
        wins = {('rock','scissors'),('scissors','paper'),('paper','rock')}
        if (choice, comp) in wins:
            won = True
            payout = (bet_amount * GAME_COEFFICIENTS['rps_win']).quantize(Decimal('0.00000001'))
            profit = payout - bet_amount
        else:
            won = False
            profit = Decimal('0')
    return comp, won, profit

def play_bowling(choice: str, bet_amount: Decimal):
    try:
        guess = int(choice)
    except:
        guess = 0
    if guess < 0 or guess > 10:
        guess = 0
    knocked = secrets.randbelow(11)
    won = (knocked == guess)
    profit = Decimal('0')
    if won:
        payout = (bet_amount * GAME_COEFFICIENTS['bowling_exact']).quantize(Decimal('0.00000001'))
        profit = payout - bet_amount
    return knocked, won, profit
