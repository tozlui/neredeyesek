from settings import *
from usersops import *
from restaurant import *
from user import *
from flask.helpers import url_for
from time import sleep
from flask.globals import session

@app.route('/',  methods=['GET','POST'])
def home_page():
    return render_template('home.html')

@app.route('/login',  methods=['POST'])
def login_page():
    username = request.form['username']
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            statement = """SELECT USERNAME FROM USERS"""
            cursor.execute(statement)
            user_data = json.dumps(cursor.fetchall())
            users = json.loads(user_data)
            if username == 'admin':
                return redirect(url_for('admin_page'))
            else:
                for user in users:
                    if [username] == user:
                        session['username'] = username
                        return redirect(url_for('user_page'))
    return render_template('home.html')

@app.route('/template',  methods=['POST'])


@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP DOMAIN IF EXISTS SCORES CASCADE"""
        cursor.execute(query)

        query = """CREATE DOMAIN SCORES AS FLOAT
                    CHECK ((VALUE >= 0.0) AND (VALUE <= 10.0))"""
        cursor.execute(query)

        query = """DROP DOMAIN IF EXISTS TRANSPORTATION_TYPES CASCADE"""
        cursor.execute(query)

        query = """CREATE DOMAIN TRANSPORTATION_TYPES AS VARCHAR(255)
                    CHECK ((VALUE = 'On Foot') OR (VALUE = 'By Car'))"""
        cursor.execute(query)

        query = """DROP DOMAIN IF EXISTS ACTIVITY CASCADE"""
        cursor.execute(query)

        query = """CREATE DOMAIN ACTIVITY AS VARCHAR(255)
                    CHECK ((VALUE = 'Active') OR (VALUE = 'Inactive'))"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE USERS (
                ID SERIAL PRIMARY KEY,
                USERNAME VARCHAR(255) NOT NULL,
                EMAIL VARCHAR(255),
                VOTING VARCHAR(255) DEFAULT 'NOT VOTED',
                VOTES INTEGER DEFAULT 0 
                )"""
        cursor.execute(query)

        query = """INSERT INTO USERS (USERNAME, EMAIL)
                    VALUES ('dinar', 'berkandinar@hotmail.com'),
                           ('tozlui', 'itozlu93@gmail.com'),
                           ('yildirimanil', 'anilyildirim922@gmail.com')"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS RESTAURANTS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE RESTAURANTS (
                ID SERIAL PRIMARY KEY,
                NAME VARCHAR(255) NOT NULL,
                TRANSPORTATION TRANSPORTATION_TYPES,
                STATE ACTIVITY,
                WEATHER BOOLEAN DEFAULT FALSE, 
                SCORE FLOAT DEFAULT 0,
                VOTE INTEGER DEFAULT 0
                )"""
        cursor.execute(query)

        query = """INSERT INTO RESTAURANTS (NAME, TRANSPORTATION, STATE)
                    VALUES ('Zohre Ustanin Yeri', 'On Foot', 'Active'),
                           ('Doydos Burger', 'On Foot', 'Active'),
                           ('Ari Mola', 'By Car', 'Active')"""
        cursor.execute(query)
        
        query = """DROP TABLE IF EXISTS STATISTICS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE STATISTICS (
                ID SERIAL PRIMARY KEY,
                RESTAURANT_NAME VARCHAR(255) NOT NULL,
                ON_FOOT BOOLEAN DEFAULT FALSE,
                SCORE SCORES DEFAULT 0,
                WEATHER BOOLEAN DEFAULT FALSE,
                DATE VARCHAR(255) 
                )"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/logout')
def logout_page():
    return redirect(url_for('home_page'))


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

if __name__ == '__main__':

    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)
