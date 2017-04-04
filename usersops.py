from settings import *

@app.route('/userops')
def userops_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            query = """SELECT ID, USERNAME, EMAIL FROM USERS"""
            cursor.execute(query)
            user_data = json.dumps(cursor.fetchall())
            users = json.loads(user_data)

            query = """SELECT ID FROM USERS"""
            cursor.execute(query)
            user_ids = json.dumps(cursor.fetchall())
            ids = json.loads(user_ids)

    now = datetime.datetime.now()
    return render_template('userops.html', current_time=now.ctime(), users=users, ids=ids)

@app.route('/userops/insert', methods=["POST"])
def userops_insert():
    username = request.form['user_name']
    email = request.form['user_email']
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if username and email:
                statement = """INSERT INTO USERS (USERNAME, EMAIL)
                            VALUES (%s, %s)"""
                cursor.execute(statement, (username,email))

    return redirect(url_for('userops_page'))

@app.route('/userops/delete', methods=["POST"])
def userops_delete():
    id = request.form["select"]
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if id:
                statement = """DELETE FROM USERS
                            WHERE (ID = %s)"""
                cursor.execute(statement, (id))

    return redirect(url_for('userops_page'))

@app.route('/userops/delete_all')
def userops_delete_all():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            query = """DELETE FROM USERS"""
            cursor.execute(query)

    return redirect(url_for('userops_page'))

@app.route('/userops/update', methods=["POST"])
def userops_update():
    id = request.form['user_ID']
    username = request.form['user_name']
    email = request.form["user_email"]
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if username:
                statement = """UPDATE USERS
                            SET (USERNAME) = (%s)
                            WHERE (ID = %s)"""
                cursor.execute(statement, (username,id))
            if email:
                statement = """UPDATE USERS
                            SET (EMAIL) = (%s)
                            WHERE (ID = %s)"""
                cursor.execute(statement, (email,id))

    return redirect(url_for('userops_page'))
