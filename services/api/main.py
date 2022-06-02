import requests
from fastapi import FastAPI, HTTPException, status
import datetime
from datetime import datetime
from pymongo import MongoClient
import uvicorn
import time
from enum import unique
from pydantic import ValidationError
from typing import List
import requests
from telebot import types
from typing import Optional
from fastapi import FastAPI, Form, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from random import randint, choice, randrange
from datetime import datetime, timedelta
import datetime
import copy
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import gunicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pymongo import MongoClient
import logging
import cv2

class Database:
    def __init__(self):
        self.client = MongoClient('mongodb://database:27017/')
        self.db = self.client['inGate_upravdom']
        self.check = self.db['check']
        self.gate = self.db['gate']
        self.photo = self.db['photo']
        self.active = self.db['active']
        self.archive = self.db['archive']
        self.qr = self.db['qr']
        self.white = self.db['white']
        self.black = self.db['black']

    def insert(self, table, data):
        if type(data) == list:
            result = table.insert_many(data)
            for d in data:
                d["_id"] = None
        else:
            result = table.insert_one(data)
            data["_id"] = None
        return result

    def get_only_one(self, table):
        try:
            result = table.find_one({}, {'_id': False})
            return dict(result)
        except:
            return None

    def get_one(self, table, key, data):
        try:
            result = table.find_one({key: data}, {'_id': False})
            return dict(result)
        except:
            return None

    def get_all(self, table):
        try:
            result = table.find({}, {'_id': False})
            return list(result)
        except:
            return None

    def delete(self, table):
        result = table.delete_many({})
        return result
    
    def delete_one(self, table):
        result = table.delete_one({})
        return result
    
    def delete_exact_one(self, table, key, data):
        result = table.delete_one({key: data}, {'_id': False})
        return result


DB = Database()

app = FastAPI(
    version="1.0.0",
    contact={
        "name": "take",
    }
)   

@app.get("/add_active", tags=['add_active'])
async def add_active(controller:dict):
    DB.insert(DB.active, controller)
    return "added successfully"

@app.get("/search_active", tags=['search_active'])
async def search_active(plate:str):
    check=DB.get_one(DB.active, "plate", plate)
    return check

@app.get("/add_archive", tags=['add_archive'])
async def add_archive(controller:dict):
    DB.insert(DB.archive, controller)
    return "added successfully"

@app.get("/list_active", tags=['list_active'])
async def list_active():
    controllers = DB.get_all(DB.active)
    return controllers

@app.get("/list_archive", tags=['list_archive'])
async def list_archive():
    controllers = DB.get_all(DB.archive)
    return controllers

@app.post("/delete_active")
async def delete_active():    
    DB.delete_one(DB.active)
    return "added successfully"

@app.post("/delete_archive")
async def delete_archive():    
    DB.delete_one(DB.archive)
    return "added successfully"

def count_minutes(inn, out):
    Y=int(out[2]+out[3])-int(inn[2]+inn[3])
    M=int(out[5]+out[6])-int(inn[5]+inn[6])
    D=int(out[8]+out[9])-int(inn[8]+inn[9])
    h=(int((out[11]+out[12]))+6)-int(inn[11]+inn[12])
    m=int(out[14]+out[15])-int(inn[14]+inn[15])
    ans=(m+(h*60)+(D*1440)+(M*43800)+(Y*525600))
    return ans

@app.get("/add_white", tags=['add_white'])
async def add_white(plate:str):
    door={'plate':plate}
    DB.insert(DB.white, door)
    return "added successfully"

@app.get("/add_black", tags=['add_black'])
async def add_black(plate:str):
    door={'plate':plate}
    DB.insert(DB.black, door)
    return "added successfully"

@app.get("/list_white", tags=['list_white'])
async def list_white():
    controllers = DB.get_all(DB.white)
    return controllers

@app.get("/list_black", tags=['list_black'])
async def list_black():
    controllers = DB.get_all(DB.black)
    return controllers

@app.post("/delete_white")
async def delete_white():    
    DB.delete(DB.white)
    return "deleted successfully"

@app.post("/delete_black")
async def delete_black():    
    DB.delete(DB.black)
    return "deleted successfully"

@app.get("/qr", tags=['qr'])
async def qr(plate:str, entry_date:str):
    black=DB.get_one(DB.black,'plate',plate)
    if black: 
        text='машина в черном списке'
        requests.get("https://api.telegram.org/bot5338192218:AAFI0hR1ViFYt-hyZ1OK0BrYOnKXQ9AxBCk/sendMessage?chat_id=-1001661843552&text=%s"%text)
        return 'black list'

    white=DB.get_one(DB.white,'plate',plate)
    date = datetime.datetime.now()
    minutes=count_minutes(str(entry_date),str(date))
    if white:
        DB.gate.find_one_and_update({'gate': '2'},{"$set":{'status': '1'}})
        door={
            'plate': str(plate),
            'date_in': str(entry_date),
            'date_out': str(date),
            'time_spent': str(minutes),
            'payment': 'yes',
            'money': str(minutes*2),
            'gate_in': '1',
            'gate_out': '2',
            'comment': 'undefined'
        }
        DB.delete_exact_one(DB.active, 'plate', plate)
        DB.insert(DB.archive, door)
        strin='машина из белого списка'+'\n'+'гос. номер: '+door['plate']+'\n'+'время входа: '+ door['date_in']+'\n'+'время выхода: '+door['date_out']+'\n'+'проведенное время: '+door['time_spent'] +'мин'+'\n'+'платеж: '+door['payment']+'\n'+'сумма: '+door['money']+'тенге'+'\n'+'номер входа: '+door['gate_in']+'\n'+'номер выхода: '+door['gate_out']
        requests.get("https://api.telegram.org/bot5338192218:AAFI0hR1ViFYt-hyZ1OK0BrYOnKXQ9AxBCk/sendMessage?chat_id=-1001661843552&text=%s"%strin)
        return "white list"

    car=DB.get_one(DB.active, "plate", plate)
    if car:
        text="qr готов"+'\n'+"сумма: %s"%(minutes*2)
        requests.get("https://api.telegram.org/bot5338192218:AAFI0hR1ViFYt-hyZ1OK0BrYOnKXQ9AxBCk/sendMessage?chat_id=-1001661843552&text=%s"%text)
        door={
            'plate': plate,
            'date_in':entry_date,
            'minutes': str(minutes)
        }
        DB.delete(DB.qr)
        DB.insert(DB.qr,door)
    else:
        text='машина  не заходила'
        requests.get("https://api.telegram.org/bot5338192218:AAFI0hR1ViFYt-hyZ1OK0BrYOnKXQ9AxBCk/sendMessage?chat_id=-1001661843552&text=%s"%text)



@app.get("/new", tags=['new'])
async def doors():
    DB.check.find_one_and_update({'new': '0'},{"$set":{'new': '1'}})

@app.get("/pay", tags=['pay'])
async def paid():
    DB.check.find_one_and_update({'pay': '0'},{"$set":{'pay': '2'}})

@app.get("/new_back", tags=['new_back'])
async def new_back():
    DB.check.find_one_and_update({'new': '1'},{"$set":{'new': '0'}})

@app.get("/pay_back", tags=['pay_back'])
async def pay_back():
    DB.check.find_one_and_update({'pay': '2'},{"$set":{'pay': '0'}})


@app.get("/status", tags=['status'])
async def status(gate: str):
    DB.gate.find_one_and_update({'gate': gate},{"$set":{'status': '1'}})

@app.get("/ask", tags=['ask'])
async def ask(gat: str):
    ans=DB.gate.find_one({'gate': gat}, {'_id': False})
    DB.gate.find_one_and_update({'gate': gat},{"$set":{'status': '0'}})
    return ans['status']

@app.get("/ask_qr", tags=['ask_qr'])
async def ask_qr():
    try:
        DB.gate.find_one_and_update({'gate': '2'},{"$set":{'status': '1'}})
        last=DB.get_only_one(DB.qr)
        if last:
            DB.delete(DB.qr)
            date=datetime.datetime.now()
            door={
                'plate': str(last['plate']),
                'date_in': str(last['date_in']),
                'date_out': str(date),
                'time_spent': str(last['minutes']),
                'payment': 'yes',
                'money': str(int(last['minutes'])*2),
                'gate_in': '1',
                'gate_out': '2',
                'comment': 'undefined'
            }
            # DB.delete_exact_one(DB.active, 'plate', last['plate'])
            DB.insert(DB.archive, door)
            strin='гос. номер: '+door['plate']+'\n'+'время входа: '+ door['date_in']+'\n'+'время выхода: '+door['date_out']+'\n'+'проведенное время: '+door['time_spent'] +'мин'+'\n'+'платеж: '+door['payment']+'\n'+'сумма: '+door['money']+'тенге'+'\n'+'номер входа: '+door['gate_in']+'\n'+'номер выхода: '+door['gate_out']
            requests.get("https://api.telegram.org/bot5338192218:AAFI0hR1ViFYt-hyZ1OK0BrYOnKXQ9AxBCk/sendMessage?chat_id=-1001661843552&text=%s"%strin)
        else: return "not found"
    except:
        return "something went wrong"

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=7788, reload=True, workers=4)

# @app.get("/count", tags=['count'])
# async def count():
#     DB.check.find_one_and_update({'count': '0'},{"$set":{'count': '2'}})

# @app.get("/photo", tags=['photo'])
# async def photo(num: str):
#     ch=DB.get_only_one(DB.photo)
#     if ch:
#         DB.delete(DB.photo)
    
#     door={
#         "last": num
#     }
#     DB.insert(DB.photo,door)

# @app.get("/get_photo", tags=['get_photo'])
# async def get_photo():
#     ch=DB.get_only_one(DB.photo)
#     return ch["last"]


@app.get("/list", tags=['list'])
async def list_():
        controllers = DB.get_only_one(DB.check)
        ans=controllers
        #if controllers['new']!='0': DB.check.find_one_and_update({'new': controllers['new']},{"$set":{'new':'0'}})
        #if controllers['count']!='0': DB.check.find_one_and_update({'count': controllers['count']},{"$set":{'count':'0'}})
        #if controllers['pay']!='0': DB.check.find_one_and_update({'pay': controllers['pay']},{"$set":{'pay':'0'}})
        return ans

# @app.get("/list_gate", tags=['list_gate'])
# async def list_gate():
#         controllers = DB.get_all(DB.gate)
#         return controllers