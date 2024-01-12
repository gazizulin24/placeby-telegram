import subprocess
import time
import json


def runCommand(command):
    subprocess.run(["osascript", "-e", f'tell application "Terminal" to do script "{command}" in front window'])

async def runServer():
    runCommand("heroku ps:scale web=1 -a placeby")
    time.sleep(2)

async def stopServer():
    runCommand("heroku ps:scale web=0 -a placeby")
    time.sleep(2)

async def startDB():
    runCommand("heroku addons:create heroku-postgresql -a placeby")
    time.sleep(5)
    print('типо стартанул')

async def stopDB():
    runCommand("heroku addons:remove heroku-postgresql -a placeby --confirm placeby")
    time.sleep(5)


async def fillDB():
    runCommand("heroku pg:psql -a placeby")
    time.sleep(5)
    with open("schema.txt", "r") as file:
        schema = file.readlines()
    for line in schema:
        runCommand(line)
    createDocumentFromData()
    with open("locations.txt", "r") as file:
        locations = file.readlines()
    for line in locations:
        runCommand(line)
    runCommand("exit;")
    runCommand("")
    time.sleep(5)



def createDocumentFromData():            # Создание из данных документа
    data = readDB()
    text = ""
    for id, place in data.items():
        text += f"INSERT INTO place (name_of_place, description, longitude, latitude) VALUES ('{place['nameOfPlace']}', '{place['description']}', {place['longitude']}, {place['latitude']});\n"
        text += "INSERT INTO photos (place_id, photo_url) VALUES "
        for photoUrl in place["photos"]:
            text += f"({id}, '{photoUrl}'),"
        text = text[:-1]
        text += ";\n"
        text += "INSERT INTO place_type (place_id, type_id) VALUES "
        for placeType in place["types"]:
            text += f"({id}, {placeType}),"
        text = text[:-1]
        text += ";\n"
        text += "INSERT INTO timetable (place_id, day_of_week, start_time, end_time) VALUES "
        for day in place["schedule"]:
            text += f"({id}, '{day['day_of_week']}', '{day['start_time']}', '{day['end_time']}'),"
        text = text[:-1]
        text += ";\n\n"
    with open("locations.txt", 'w') as file:
        file.write(text)


def readDB():                        # Получает информацию с database.json
    database = open('database.json', 'r+')
    data = json.load(database)
    database.close()
    return data