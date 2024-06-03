import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://user:userpass@cluster0.gncylxf.mongodb.net/?retryWrites=true&w=majority')