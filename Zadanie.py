# Dołączanie modułu flask

from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from flask import Flask, session
from flask_session import Session
import sqlite3

DATABASE = 'database.db'

# Tworzenie aplikacji
app = Flask("Flask - Lab")

# Tworzenie obsługi sesji
sess = Session()


@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT, password TEXT, admin INTEGER)')
    conn.execute('CREATE TABLE books (author TEXT, title TEXT)')
    # Zakończenie połączenia z bazą danych
    conn.close()

    return index()

@app.route('/', methods=['GET', 'POST'])
def index():
    con = sqlite3.connect(DATABASE)
    # Sprawdzenie czy w sesji dla danego klienta zapisana jest nazwa użytkownika
    cur = con.cursor()
    cur.execute("select * from books")
    books = cur.fetchall();

    # return render_template('t4.html', users=users)
    if 'user' in session:
        return render_template('zalogowany.html', books=books, userdata=session['user'])
    else:
        return render_template('niezalogowany.html', books=books)

@app.route('/users', methods=['GET', 'POST'])
def users():
        con = sqlite3.connect(DATABASE)
        # Sprawdzenie czy w sesji dla danego klienta zapisana jest nazwa użytkownika
        cur = con.cursor()
        cur.execute("select * from users")
        users = cur.fetchall();

        # return render_template('t4.html', users=users)
        if 'user' in session:
            return render_template('users.html', users=users, userdata=session['user'])
        else:
            return render_template('niezalogowany.html')

# Endpoint umożliwiający podanie parametru w postaci string'a
@app.route('/users/<username>')
def user_by_name(username):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("select * from users WHERE username LIKE \'" + username + "\'")
    user = cur.fetchone()
    con.close()
    return render_template('user.html', user=user)

# Endpoint umożliwiający podanie parametru w postaci int'a
@app.route('/users/<int:get_id>')
def user_by_id(get_id):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("select * from users WHERE id = " + str(get_id))
    user = cur.fetchone()
    con.close()
    return render_template('user.html', user=user)


@app.route('/login', methods=['POST'])
def login():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    cur.execute("select * from users WHERE username LIKE \'" + request.form['login'] + "\' AND password LIKE \'" + request.form['password'] + "\'")
    user = cur.fetchone()
    con.close()
    if user:
        session['user'] = request.form['login']
        return "Login successful! <br> <a href='/'> Return </a> "
    else:
        return "Login unsuccessful! <br> <a href='/'> Return </a> "



@app.route('/logout', methods=['GET'])
def logout():
    # Jeżeli sesja klienta istnieje - usunięcie sesji
    if 'user' in session:
        session.pop('user')
    else:
        # Przekierowanie klienta do strony początkowej
        redirect(url_for('index'))

    return "Logout successful. <br>  <a href='/'> Return </a>"

@app.route('/add', methods=['POST'])
def add():
        author = request.form['author']
        title = request.form['title']


        # Dodanie użytkownika do bazy danych
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("INSERT INTO books (author,title) VALUES (?,?)",(author,title) )
        con.commit()
        con.close()

        return "Book added. <br>" + index()

@app.route('/add_user', methods=['POST'])
def add_user():
        username = request.form['username']
        password = request.form['password']
        admin = request.form.get('admin')
        if admin:
            admin = 1
        else:
            admin = 0


        # Dodanie użytkownika do bazy danych
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("INSERT INTO users (username,password,admin) VALUES (?,?,?)",(username,password,admin) )
        con.commit()
        con.close()

        con = sqlite3.connect(DATABASE)
        # Sprawdzenie czy w sesji dla danego klienta zapisana jest nazwa użytkownika
        cur = con.cursor()
        cur.execute("select * from users")
        users = cur.fetchall();
        con.close()

        return render_template('users.html', users=users, userdata=session['user'])

# Uruchomienie aplikacji w trybie debug
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()