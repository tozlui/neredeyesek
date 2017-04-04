from settings import *

@app.route('/restaurant')
def restaurant_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            query = """SELECT ID, NAME, TRANSPORTATION, STATE, WEATHER, SCORE, VOTE FROM RESTAURANTS"""
            cursor.execute(query)
            restaurant_data = json.dumps(cursor.fetchall())
            restaurants = json.loads(restaurant_data)

            query = """SELECT ID FROM RESTAURANTS"""
            cursor.execute(query)
            restaurant_ids = json.dumps(cursor.fetchall())
            ids = json.loads(restaurant_ids)

    now = datetime.datetime.now()
    return render_template('restaurant.html', current_time=now.ctime(), restaurants=restaurants, ids=ids)

@app.route('/restaurant/insert', methods=["POST"])
def restaurant_insert():
    name = request.form['restaurant_name']
    transportation = request.form['restaurant_transportation']
    state = request.form['restaurant_state']
    weather = request.form['restaurant_weather']
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if name and transportation and state and weather:
                statement = """INSERT INTO RESTAURANTS (NAME, TRANSPORTATION, STATE, WEATHER)
                            VALUES (%s, %s, %s, %s)"""
                cursor.execute(statement, (name,transportation,state,weather))

    return redirect(url_for('restaurant_page'))

@app.route('/restaurant/delete', methods=["POST"])
def restaurant_delete():
    id = request.form["select"]
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if id:
                statement = """DELETE FROM RESTAURANTS
                            WHERE (ID = %s)"""
                cursor.execute(statement, (id))

    return redirect(url_for('restaurant_page'))

@app.route('/restaurant/delete_all')
def restaurant_delete_all():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            query = """DELETE FROM RESTAURANTS"""
            cursor.execute(query)

    return redirect(url_for('restaurant_page'))

@app.route('/restaurant/update', methods=["POST"])
def restaurant_update():
    id = request.form['restaurant_ID']
    name = request.form['restaurant_name']
    transportation = request.form["restaurant_transportation"]
    state = request.form["restaurant_state"]
    weather = request.form["restaurant_weather"]
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if name:
                statement = """UPDATE RESTAURANTS
                            SET (NAME) = (%s)
                            WHERE (ID = %s)"""
                cursor.execute(statement, (username,id))
            if transportation:
                statement = """UPDATE RESTAURANTS
                            SET (TRANSPORTATION) = (%s)
                            WHERE (ID = %s)"""
                cursor.execute(statement, (transportation,id))
            if state:
                statement = """UPDATE RESTAURANTS
                            SET (STATE) = (%s)
                            WHERE (ID = %s)"""
                cursor.execute(statement, (state,id))
            if weather:
                statement = """UPDATE RESTAURANTS
                            SET (WEATHER) = (%s)
                            WHERE (ID = %s)"""
                cursor.execute(statement, (weather,id))

    return redirect(url_for('restaurant_page'))
