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
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client["inGate_Adilet"]
        self.active = self.db['active']
        self.archive = self.db['archive']
        if self.active.count_documents({}) == 0:
            self.initial_populate()

    def insert(self, table, data):
        table.insert_one(data)
        data["_id"] = None

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
        result = table.delete_one({key: data})
        return result    

    def get_all(self, table):
        try:
            result = table.find({}, {'_id': False})
            return list(result)
        except: 
            return None

    def initial_populate(self):
        user = {
            "username": "UpravDom",
            "user_id": "1",
        }
        self.insert(self.active, user)

def count_minutes(inn, out):
        Y=int(out[2]+out[3])-int(inn[2]+inn[3])
        M=int(out[5]+out[6])-int(inn[5]+inn[6])
        D=int(out[8]+out[9])-int(inn[8]+inn[9])
        h=int(out[11]+out[12])-int(inn[11]+inn[12])
        m=int(out[14]+out[15])-int(inn[14]+inn[15])
        ans=(m+(h*60)+(D*1440)+(M*43800)+(Y*525600))
        return ans

    
DB = Database()

app = FastAPI()

@app.get("/list", tags=["list"])
async def list_active():
    return DB.get_all(DB.active)

@app.post("/add_number", tags=["add_number"])
async def add_number(plate):
    data = datetime.now()
    plates = {
        "plate": plate,
        "data_in": data
    }
    return DB.insert(DB.active, plates)


@app.get("/get_number", tags=["get_number"])
async def get_number(number:str):
    DB.get_one(DB.active, "plate", number)

@app.get("/list_archive", tags=["list_archive"])
async def list_archive():
    return DB.get_all(DB.archive)

@app.get("/exit",tags=["exit"])
async def exit_s(number):
    res = DB.get_one(DB.active, "plate", number)
    data = datetime.now()
    da = datetime.strptime(str(res['data_in']) ,"%Y-%m-%d %H:%M:%S.%f")
    tspend = str(data - da)
    money = count_minutes(str(res['data_in']),str(data))
    plates = { 
        "plate": res['plate'],
        "data_in": res['data_in'],
        "data_out": data,
        "time_spend": tspend,
        "money": money
    }
    arc =  DB.insert(DB.archive ,plates)
    DB.delete_exact_one(DB.active,"plate",number)
    return arc

import cv2
frame = cv2.imread('images/img3.jpeg')
plate=segmentation.run_models(frame) 


@app.post("/test",tags=["test"])
async def test():
    data = datetime.now()
    plates = {
        "plate": plate,
        "data_in": data
    }
    return DB.insert(DB.active, plates)

@app.post("/test2",tags=["test2"])
async def test2():
    res = DB.get_one(DB.active, "plate", plate)
    data = datetime.now()
    da = datetime.strptime(str(res['data_in']) ,"%Y-%m-%d %H:%M:%S.%f")
    tspend = str(data - da)
    money = countminutes(str(res['data_in']),str(data))
    plates = { 
        "plate": res['plate'],
        "data_in": res['data_in'],
        "data_out": data,
        "time_spend": tspend,
        "money": money 
    }
    arc =  DB.insert(DB.archive ,plates)
    DB.delete_exact_one(DB.active,"plate",plate)
    return arc

if name == "main":
        uvicorn.run("main:app", host="0.0.0.0", port=7788, reload=True, workers=4)


