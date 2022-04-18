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
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['inGate_upravdom']
        self.check = self.db['check']
        if self.check.count_documents({}) == 0:
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
        door = {
            "new": "0",
            "count": "0",
            "pay": "0"
        }
        self.insert(self.check, door)

DB = Database()

app = FastAPI(
    version="1.0.0",
    contact={
        "name": "take",
    }
)   

@app.get("/new", tags=['new'])
async def doors(controller_id: str):
    DB.check.find_one_and_update({'new': '0'},{"$set":{'new': controller_id}})


@app.get("/count", tags=['count'])
async def count(controller_id: str):
    DB.check.find_one_and_update({'count': '0'},{"$set":{'count': controller_id}})

@app.get("/pay", tags=['pay'])
async def paid(controller_id: str):
    DB.check.find_one_and_update({'pay': '0'},{"$set":{'pay': controller_id}})

@app.get("/list", tags=['list'])
async def list_():
        controllers = DB.get_one(DB.check)
        ans=controllers
        if controllers['new']!='0': DB.check.find_one_and_update({'new': controllers['new']},{"$set":{'new':'0'}})
        if controllers['count']!='0': DB.check.find_one_and_update({'count': controllers['count']},{"$set":{'count':'0'}})
        if controllers['pay']!='0': DB.check.find_one_and_update({'pay': controllers['pay']},{"$set":{'pay':'0'}})
        return ans
