from pymongo import MongoClient

MONGO_URI = 'mongodb://192.168.0.109:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5'


def dbConnection():
    try:
        client = MongoClient(MONGO_URI)
        db = client["Universidad_Estadias"]
        print("si jala we")
        return db
    except Exception as e:
        print('Error de conexión con la BD:', e)
        return None
