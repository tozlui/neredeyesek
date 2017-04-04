from settings import *
import feedparser
import smtplib
import time
from docutils.parsers import null
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

restaurant_list = []
user_emails = []
period = 3

class restaurant:
    def __init__(self, name, score, on_foot, weather_sensitivity):
        self.name = name
        self.score = score
        self.on_foot = on_foot
        self.weather_sensitivity = weather_sensitivity                  #restoran hava durumuna duyarli ise true

    def display_restaurant(self):
        all_info = "%s (Puan: %d)" % (self.name, self.score)
        return all_info

def find_a_restaurant(list_of_restaurants, weather_condition):  # weather condition true ise hava yagmurlu vs. demek
    max_score = 0
    backup_list = list_of_restaurants
    selected_restaurant = restaurant(None, None, None, None)
    statement = """SELECT RESTAURANT_NAME FROM STATISTICS"""
    cursor.execute(statement)
    restaurant_data = json.dumps(cursor.fetchall())
    restaurants = json.loads(restaurant_data)
    statement = """SELECT ON_FOOT FROM STATISTICS"""
    cursor.execute(statement)
    onfoot_data = json.dumps(cursor.fetchall())
    onfoots = json.loads(onfoot_data)
    if len(restaurants) != 0:
        if len(onfoots) < 2:
            thing = restaurants[len(restaurants) - 1][0]
            for t in list_of_restaurants:
                if thing == t.name:
                    list_of_restaurants.remove(t)
                    break
        else:
            thing = restaurants[len(restaurants) - 1][0]
            thing2 = onfoots[len(onfoots) - 1][0]
            thing3 = onfoots[len(onfoots) - 2][0]
            for t in list_of_restaurants:
                if thing == t.name:
                    list_of_restaurants.remove(t)
                    break
            if thing2 == False or thing3 == False:
                for t in list_of_restaurants:
                    if t.on_foot == False:
                        list_of_restaurants.remove(t)
                   
    for val in list_of_restaurants:
        if weather_condition and (val.on_foot or val.weather_sensitivity):
            continue
        if val.score > max_score:
            max_score = val.score
            selected_restaurant = val
    if selected_restaurant == restaurant(None, None, None, None):
        max_score = 0
        for val in backup_list:
            if val.score > max_score:
                max_score = val.score
                selected_restaurant = val
    return selected_restaurant


# locCode=EUR|TR|06420|ANKARA| > KITA|ULKE|POSTAKODU|IL


def weather_checker():
    parse = feedparser.parse("http://rss.accuweather.com/rss/liveweather_rss.asp?metric=1&locCode=EUR|TR|34467"
                             "|ISTANBUL|")
    parse = parse["entries"][0]["summary"]
    parse = parse.split()
    for j in range(0, len(parse)):
        if parse[j] == "Showers" or parse[j] == "T-storms" or parse[j] == "Rain" or parse[j] == "Flurries" or parse[j] == "Snow" or parse[j] == "Snow" or parse[j] == "Ice" or parse[j] == "Sleet" or parse[j] == "Hot" or parse[j] == "Cold":
            return True
        else:
            return False
    # print(parse[0], parse[1], parse[2], parse[3], parse[4], parse[5], parse[6], parse[7], parse[8])

def email_sender():
    a = found
    b = """
    Merhabalar,
    Bugun sizin icin en uygun restoran olarak """ + a + """ belirlendi.
    Afiyet olsun.
    """
    fromaddr = "proje2denememail@gmail.com"
    toaddr = user_emails
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Subject'] = "NeredeYesek Restoran Onerisi"
    body = MIMEText(b)
    msg.attach(body)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "proje2deneme_mail")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print('Email sent!')

#names = ["Los Pollos Hermanos", "Burger King", "McDonalds"]
#scores = [4, 3, 5]
#on_foots = [False, True, True]
#weather_sensitivities = [True, False, False]

with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT COUNT(ID) FROM USERS"""
        cursor.execute(query)
        user_data = json.dumps(cursor.fetchall())
        users = json.loads(user_data)
        query = """SELECT NAME FROM RESTAURANTS
                   WHERE (STATE = 'Active')"""
        cursor.execute(query)
        names_data = json.dumps(cursor.fetchall())
        names = json.loads(names_data)
        query = """SELECT VOTE FROM RESTAURANTS
                   WHERE (NAME = %s)"""
        cursor.execute(query, (names[0][0],))
        vote_data = json.dumps(cursor.fetchall())
        vote = json.loads(vote_data)
        if vote[0][0] == users[0][0]:
            query = """SELECT SCORE FROM RESTAURANTS
                       WHERE (STATE = 'Active')"""
            cursor.execute(query)
            score_data = json.dumps(cursor.fetchall())
            scores = json.loads(score_data)
            print(scores)
            query = """SELECT TRANSPORTATION FROM RESTAURANTS
                       WHERE (STATE = 'Active')"""
            cursor.execute(query)
            onfoot_data = json.dumps(cursor.fetchall())
            on_foots = json.loads(onfoot_data)
            print(on_foots)
            query = """SELECT WEATHER FROM RESTAURANTS
                       WHERE (STATE = 'Active')"""
            cursor.execute(query)
            weather_data = json.dumps(cursor.fetchall())
            weather_sensitivities = json.loads(weather_data)
            print(weather_sensitivities)
            query = """SELECT EMAIL FROM USERS"""
            cursor.execute(query)
            email_data = json.dumps(cursor.fetchall())
            emails = json.loads(email_data)
            for i in emails:
                user_emails.append(i[0])
            for i in range(0, len(names)):
                if on_foots[i] == ['On Foot']:
                    on_foots[i][0] = True
                else:
                    on_foots[i][0] = False 
                restaurant_list.append(restaurant(names[i][0], scores[i][0], on_foots[i][0], weather_sensitivities[i][0]))
            found = find_a_restaurant(restaurant_list, weather_checker()).display_restaurant()
            print(found)
            record = find_a_restaurant(restaurant_list, weather_checker())    
            now = time.strftime("%d/%m/%Y")
            statement = """INSERT INTO STATISTICS (RESTAURANT_NAME, ON_FOOT, SCORE, WEATHER, DATE)
                            VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(statement, (record.name,record.on_foot,record.score,record.weather_sensitivity, str(now)))
            record.score = record.score-1
            statement = """UPDATE RESTAURANTS
                        SET (SCORE) = (%s)
                        WHERE (NAME = %s)"""
            cursor.execute(statement, (record.score, record.name))
            statement = """SELECT COUNT(ID) FROM STATISTICS"""
            cursor.execute(statement)
            term_data = json.dumps(cursor.fetchall())
            term = json.loads(term_data)
            if term[0][0] == period:
                statement = """DELETE FROM STATISTICS"""
                cursor.execute(statement)
                a = float(0)
                statement = """UPDATE RESTAURANTS
                            SET (SCORE) = (%s),
                            VOTE = 0"""
                cursor.execute(statement, (a,))
                statement = """UPDATE USERS
                            SET VOTING = 'NOT VOTED',
                            VOTES = 0"""
                cursor.execute(statement)
            email_sender()
        else:
            print("There are still users that did not vote the restaurants!")        
# for val in restaurant_list:
# val.display_restaurant()

#email_sender()