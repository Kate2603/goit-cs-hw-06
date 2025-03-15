import socket
import json
import datetime
import os
from pymongo import MongoClient

# Конфігурація MongoDB
MONGO_HOST = "mongodb"
MONGO_PORT = 27017
DB_NAME = "messages_db"
COLLECTION_NAME = "messages"

# Конфігурація сокету
SOCKET_HOST = "0.0.0.0"
SOCKET_PORT = 5000

# Файл для зберігання повідомлень, якщо MongoDB недоступна
JSON_PATH = "storage/data.json"

# Підключення до MongoDB
try:
    client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)  # Таймаут 5 сек
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    client.server_info()  # Перевірка з'єднання
    mongo_available = True
    print("✅ Connected to MongoDB")
except Exception as e:
    mongo_available = False
    print(f"⚠️ Error connecting to MongoDB: {e}. The data will be saved in JSON..")

# Функція збереження повідомлень у JSON
def save_to_json(message):
    if not os.path.exists("storage"):
        os.makedirs("storage") # Створюємо папку storage, якщо її немає

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = [] # Якщо файлу немає або він порожній

    data.append(message)

    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Запуск UDP-сокет-сервера
def start_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SOCKET_HOST, SOCKET_PORT))

    print(f"🟢 Socket server running on port {SOCKET_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())

        message["date"] = str(datetime.datetime.now())

        if mongo_available:
            try:
                collection.insert_one(message)
                print(f"✅ The message is saved in MongoDB: {message}")
            except Exception as e:
                print(f"⚠️ MongoDB Write Error: {e}. Save in JSON.")
                save_to_json(message)
        else:
            save_to_json(message)
            print(f"💾 The message is saved in JSON: {message}")

if __name__ == "__main__":
    start_socket_server()
