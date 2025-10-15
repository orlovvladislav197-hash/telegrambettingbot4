import os
from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps
from dotenv import load_dotenv
import asyncpg, asyncio

load_dotenv()
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('ADMIN_SECRET', 'change-me')
DATABASE_URL = os.getenv('DATABASE_URL')

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

async def get_db_pool():
    if not hasattr(app, 'db_pool'):
        app.db_pool = await asyncpg.create_pool(DATABASE_URL)
    return app.db_pool

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == os.getenv('ADMIN_PASSWORD'):
            session['admin'] = True
            return redirect(url_for('index'))
        return 'Неверный пароль', 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
