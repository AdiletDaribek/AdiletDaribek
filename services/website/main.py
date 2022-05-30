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
        if self.check.count_documents({}) == 0 or self.gate.count_documents({}) == 0:
            self.initial_populate()

    def insert(self, table, data):
        if type(data) == list:
            result = table.insert_many(data)
            for d in data:
                d["_id"] = None
        else:
            result = table.insert_one(data)
            data["_id"] = None
        return result

    def get_one(self, table):
        try:
            result = table.find_one({}, {'_id': False})
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
    
    def initial_populate(self):
        if self.check.count_documents({}) == 0:
            door = {
                "new": "0",
                "count": "0",
                "pay": "0"
            }
            self.insert(self.check, door)
        if self.gate.count_documents({}) == 0:
            door = {
                "gate": "1",
                "status": "0"
            }
            self.insert(self.gate, door)
            door = {
                "gate": "2",
                "status": "0"
            }
            self.insert(self.gate, door)


DB = Database()

app = FastAPI(
    version="1.0.0",
    contact={
        "name": "take",
    }
)   

@app.get("/new", tags=['new'])
async def doors():
    DB.check.find_one_and_update({'new': '0'},{"$set":{'new': '1'}})

@app.get("/count", tags=['count'])
async def count():
    DB.check.find_one_and_update({'count': '0'},{"$set":{'count': '2'}})

@app.get("/pay", tags=['pay'])
async def paid():
    DB.check.find_one_and_update({'pay': '0'},{"$set":{'pay': '2'}})

@app.get("/new_back", tags=['new_back'])
async def new_back():
    DB.check.find_one_and_update({'new': '1'},{"$set":{'new': '0'}})

@app.get("/pay_back", tags=['pay_back'])
async def pay_back():
    DB.check.find_one_and_update({'pay': '2'},{"$set":{'pay': '0'}})

@app.get("/photo", tags=['photo'])
async def photo(num: str):
    ch=DB.get_one(DB.photo)
    if ch:
        DB.delete(DB.photo)
    
    door={
        "last": num
    }
    DB.insert(DB.photo,door)

@app.get("/get_photo", tags=['get_photo'])
async def get_photo():
    ch=DB.get_one(DB.photo)
    return ch["last"]


@app.get("/list", tags=['list'])
async def list_():
        controllers = DB.get_one(DB.check)
        ans=controllers
        #if controllers['new']!='0': DB.check.find_one_and_update({'new': controllers['new']},{"$set":{'new':'0'}})
        #if controllers['count']!='0': DB.check.find_one_and_update({'count': controllers['count']},{"$set":{'count':'0'}})
        #if controllers['pay']!='0': DB.check.find_one_and_update({'pay': controllers['pay']},{"$set":{'pay':'0'}})
        return ans

@app.get("/list_gate", tags=['list_gate'])
async def list_gate():
        controllers = DB.get_all(DB.gate)
        return controllers

@app.get("/status", tags=['status'])
async def status(gate: str):
    DB.gate.find_one_and_update({'gate': gate},{"$set":{'status': '1'}})

@app.get("/ask", tags=['ask'])
async def ask(gat: str):
    ans=DB.gate.find_one({'gate': gat}, {'_id': False})
    DB.gate.find_one_and_update({'gate': gat},{"$set":{'status': '0'}})
    return ans['status']

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=7788, reload=True, workers=4)