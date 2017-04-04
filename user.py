from settings import *
from flask.helpers import url_for
from flask.globals import session
from os import name

@app.route('/user', methods=["GET"])
def user_page():
    username = session.get('username', None)
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT NAME, TRANSPORTATION, STATE, WEATHER, SCORE FROM RESTAURANTS"""
        cursor.execute(query)
        restaurant_data = json.dumps(cursor.fetchall())
        restaurants = json.loads(restaurant_data)

    return render_template('user.html', restaurants=restaurants, username=username)

@app.route('/user/grading')
def grading_page():
    username = session.get('username', None)
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        statement = """SELECT VOTING FROM USERS
                           WHERE (USERNAME = %s)"""
        cursor.execute(statement, (username,))
        vote_data = json.dumps(cursor.fetchall())
        vote = json.loads(vote_data)
        if vote == [['NOT VOTED']]:
            query = """SELECT ID, NAME FROM RESTAURANTS
                    WHERE (STATE = 'Active')"""
            cursor.execute(query)
            restaurant_data = json.dumps(cursor.fetchall())
            restaurants = json.loads(restaurant_data)
            return render_template('grading.html', restaurants=restaurants, username=username)
        else:
            return render_template('outgrading.html', username=username)

@app.route('/user/statistics')
def statistics_page():
    username = session.get('username', None)
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        statement = """SELECT RESTAURANT_NAME, ON_FOOT, SCORE, WEATHER, DATE FROM STATISTICS"""
        cursor.execute(statement, (username,))
        statistic_data = json.dumps(cursor.fetchall())
        statistics = json.loads(statistic_data)
    
    return render_template('statistics.html', statistics=statistics, username=username)

@app.route('/user/grading/grade', methods=["POST"])
def user_grade():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
                query = """SELECT ID FROM RESTAURANTS
                           WHERE (STATE = 'Active')"""
                cursor.execute(query)
                id_data = json.dumps(cursor.fetchall())
                ids = json.loads(id_data)        
    for i in ids:
        restaurant = request.form['restaurant_ID' + str(i[0])]
        score = request.form['restaurant_score' + str(i[0])]
        if score == '':
            score = 0
        print(restaurant)
        username = request.form['user_name' + str(i[0])]
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                    query = """SELECT COUNT(ID) FROM RESTAURANTS
                               WHERE (STATE = 'Active')"""
                    cursor.execute(query)
                    count_data = json.dumps(cursor.fetchall())
                    count = json.loads(count_data)
                    statement = """UPDATE RESTAURANTS
                                   SET SCORE = (SCORE*VOTE + %s) / (VOTE + 1),
                                   VOTE = VOTE + 1
                                   WHERE (ID = %s)"""
                    cursor.execute(statement, (score,restaurant))
                    statement = """UPDATE USERS
                                   SET VOTES = VOTES + 1
                                   WHERE (USERNAME = %s)"""
                    cursor.execute(statement, (username,))
                    statement = """SELECT VOTES FROM USERS
                                   WHERE (USERNAME = %s)"""
                    cursor.execute(statement, (username,))
                    votes_data = json.dumps(cursor.fetchall())
                    votes = json.loads(votes_data)
                    if votes == count:
                        statement = """UPDATE USERS
                                   SET VOTING = 'VOTED'
                                   WHERE (USERNAME = %s)"""
                        cursor.execute(statement, (username,))
    return redirect(url_for('user_page'))