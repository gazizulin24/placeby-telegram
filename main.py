from config import TOKEN, CLOUD_NAME, API_KEY, API_SECRET
from aiogram import Bot, Dispatcher, executor, types
import json, random
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import time
import tracemalloc
import cloudinary
import cloudinary.uploader


tracemalloc.start()

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)

class location(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()
    Q6 = State()
    Q7 = State()

bot = Bot(TOKEN)						# Иницилизация aiogram
dp = Dispatcher(bot, storage=MemoryStorage())

def upload_photo(file_path):
    upload_result = cloudinary.uploader.upload(file_path)
    image_url = upload_result['secure_url']
    return image_url


async def loadPhoto(photo):              # Сохранение одного фото на комп
    file_id = photo.file_unique_id
    file_path = os.path.join('photos', f'{file_id}.jpg')
    await photo.download(destination_file=file_path)
    uploadedPhotoUrl = upload_photo(f"photos/{file_id}.jpg")
    return uploadedPhotoUrl

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

def writeDB(data):               # Вносит изменения в database.json
    database = open('database.json', 'w+')
    database.write(json.dumps(data, indent=4))
    database.close()

def readUsers():                        # Получает информацию с users.json
    database = open('users.json', 'r+')
    data = json.load(database)
    database.close()
    return data

def writeUsers(data):               # Вносит изменения в users.json
    database = open('users.json', 'w+')
    database.write(json.dumps(data, indent=4))
    database.close()

def addUser(user_id):
    data = readUsers()
    if user_id not in data:
        data["auth"].append(user_id)
        data["location"].append("none")
        writeUsers(data)

def newLocation(user_id):
    dataU = readUsers()
    number = dataU["auth"].index(user_id)

    if dataU["location"][number] == "none":
        data = readDB()
        location_id = len(data) + 1
        dataU["location"][number] = str(location_id)
        writeUsers(dataU)
        data[len(data) + 1] = {
            "nameOfPlace": "",
            "description": "",
            "photos": [],
            "longitude": 0,
            "latitude": 0,
            "types": [],
            "schedule": []
        }
        writeDB(data)

def addName(user_id, text):
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    data = readDB()
    data[location_id]["nameOfPlace"] = text
    writeDB(data)

def addLongitude(user_id, text):
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    data = readDB()
    data[location_id]["longitude"] = text
    writeDB(data)

def addDescription(user_id, text):
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    data = readDB()
    data[location_id]["description"] = text
    writeDB(data)

def addUrl(user_id, imageUrl):
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    data = readDB()
    print(imageUrl)
    data[location_id]["photos"] += [imageUrl]
    writeDB(data)

def addPhoto(user_id, text):
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    data = readDB()
    data[location_id]["photos"] = text
    writeDB(data)

def addLatitude(user_id, text):
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    data = readDB()
    data[location_id]["latitude"] = text
    writeDB(data)

def addType(user_id, text):
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    data = readDB()
    result = text.strip('[]').replace(' ', '').split(',')
    data[location_id]["types"] = result
    writeDB(data)

def addSchedule(user_id, schedule_text):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    dataU = readUsers()
    location_id = dataU["location"][dataU["auth"].index(user_id)]
    dataU["location"][dataU["auth"].index(user_id)] = "none"
    writeUsers(dataU)
    schedule = list(map(lambda x: list(map(lambda time: time + ":00", x.split(" - "))), schedule_text.split("\n")))
    data = readDB()
    for i, day in enumerate(schedule):
        data[location_id]["schedule"].append({"day_of_week": days[i], "start_time": day[0], "end_time": day[1]})
    writeDB(data)

@dp.message_handler(commands=['start']) 
async def start(msg: types.Message):
    addUser(str(msg.from_user.id))
    await msg.answer("Добро пожаловать в Yocation!\n\n| Добавить новую локацию: /locationnew\n\n| Получить файл с локациями: /locationsql\n\n| Получить json со всеми локациями: /locationjson")

@dp.message_handler(commands=['locationnew']) 
async def start(msg: types.Message, state: FSMContext):
    newLocation(str(msg.from_user.id))
    await location.Q1.set()
    await msg.answer("Давайте начнём!\n\nВведите название локации:")

@dp.message_handler(commands=['locationsql'])
async def start(msg: types.Message):
    createDocumentFromData()
    document_path = "locations.txt"
    with open(document_path, "rb") as document:
        await msg.answer_document(document)
        await msg.answer('| Добавить новую локацию: /locationnew\n\n| Получить файл с локациями: /locationsql\n\n| Получить json со всеми локациями: /locationjson')

@dp.message_handler(commands=['locationjson'])
async def start(msg: types.Message):
    createDocumentFromData()
    document_path = "database.json"
    with open(document_path, "rb") as document:
        await msg.answer_document(document)
        await msg.answer('| Добавить новую локацию: /locationnew\n\n| Получить файл с локациями: /locationsql\n\n| Получить json со всеми локациями: /locationjson')

@dp.message_handler(state=location.Q1) # Принимаем состояние
async def new_name_set(msg: types.Message, state: FSMContext):
    addName(str(msg.from_user.id), msg.text)
    await location.Q2.set()
    await msg.answer('Введите описание локации:')

@dp.message_handler(state=location.Q2) # Принимаем состояние
async def new_name_set(msg: types.Message, state: FSMContext):
    addDescription(str(msg.from_user.id), msg.text)
    await location.Q3.set()
    await msg.answer('Теперь отправляйте ПО ОДНОЙ фото локации или напишите ок для завершения добавления фото:')

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=location.Q3)
async def handle_photo(msg: types.Message):
    photo = msg.photo[-1]
    photo_url = await loadPhoto(photo)

    addUrl(str(msg.from_user.id), photo_url)
    await bot.send_message(msg.chat.id, 'Фотография сохранена! Отправьте еще фото или напишите ок для завершения добавления фото')

@dp.message_handler(state=location.Q3) # Принимаем состояние
async def new_name_set(msg: types.Message, state: FSMContext):

    if msg.text == "ок":
        await location.Q4.set()
        await msg.answer('Отправьте широту (latitude) локации:')
    else:
        await msg.answer('Отправьте ПО ОДНОМУ фото локации или напишите ок для завершения добавления фото')


@dp.message_handler(state=location.Q4) # Принимаем состояние
async def new_name_set(msg: types.Message, state: FSMContext):
    addLatitude(str(msg.from_user.id), msg.text)
    await location.Q5.set()
    await msg.answer('Отправьте долготу (longitude) локации:')

@dp.message_handler(state=location.Q5) # Принимаем состояние
async def new_name_set(msg: types.Message, state: FSMContext):
    addLongitude(str(msg.from_user.id), msg.text)
    await location.Q6.set()
    await msg.answer('1) Развлечения\n2) Новые\n3) Рыбалка\n4) Семьей\n5) Парой\n6) Знаковые места\n7) Активный отдых\n8) Большой компанией\n9) Разные\n\nОтправьте через запятую, номера, которые характеры для локации:')

@dp.message_handler(state=location.Q6) # Принимаем состояние
async def new_name_set(msg: types.Message, state: FSMContext):
    addType(str(msg.from_user.id), msg.text)
    await location.Q7.set()
    await msg.answer('Отправьте расписание места на неделю в формате (удобнее скопировать и изменить):')
    await msg.answer('00:00 - 00:00\n00:00 - 00:00\n00:00 - 00:00\n00:00 - 00:00\n00:00 - 00:00\n00:00 - 00:00\n00:00 - 00:00')
    await msg.answer('Важно! Если расписание в этот день круглосуточно, то укажите время 00:00 - 00:00, если круглосуточно то 00:00 - 24:00.')


@dp.message_handler(state=location.Q7) # Принимаем состояние
async def new_name_set(msg: types.Message, state: FSMContext):
    addSchedule(str(msg.from_user.id), msg.text)
    await state.finish()
    await msg.answer('Локация добавлена!')
    await msg.answer('| Добавить новую локацию: /locationnew\n\n| Получить файл с локациями: /locationsql\n\n| Получить json со всеми локациями: /locationjson')

if __name__ == '__main__':  # Бесконечный цикл
    print("start.")
    executor.start_polling(dp)