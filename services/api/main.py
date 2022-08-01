from fastapi import FastAPI
import azure.cognitiveservices.speech as speechsdk
from fastapi.responses import FileResponse
import os
import boto3
from pymongo import MongoClient

class Database:
    def __init__(self):
        self.client = MongoClient('mongodb://database:27017/')
        self.db = self.client["azure"]
        self.check = self.db['check']
        if self.check.count_documents({}) == 0:
            self.initial_populate()
        # if self.video.count_documents({}) == 0:
        #     self.initial_populate1()


    def insert(self, table, data):
        if type(data) == list:
            result = table.insert_many(data)
            for d in data:
                d["_id"] = None
        else:
            result = table.insert_one(data)
            data["_id"] = None
        return result

    def get(self, table, key, data):
        try:
            result = table.find({key: data}, {'_id': False})
            result = list(result)
            return result
        except:
            return None

    def get_all(self, table):
        try:
            result = table.find({}, {'_id': False})
            return list(result)
        except:
            return None

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

    def delete(self, table, key, data):
        result = table.delete_one({key: data})
        return result

    def delete_all(self, table):
        result = table.delete_many({})
        return result

    def initial_populate(self):
        user = {
            "id": 1
        }
        self.insert(self.check, user)

DB = Database()

app = FastAPI()

@app.get("/text_to_mp3_and_keywords")
async def text_to_mp3_and_keywords(text:str):
        num=DB.get_only_one(DB.check)

        DB.check.find_one_and_update({"id": num['id']},{"$set":{"id":(num['id']+1)}})

        speech_config = speechsdk.SpeechConfig(subscription="1d1bbd3b0e1649ffa56c4c1b8b4cc507", region="eastus")

        audio_config = speechsdk.audio.AudioOutputConfig(filename=f"sound.wav")

        speech_config.speech_synthesis_voice_name='en-US-SaraNeural'

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        speech_synthesizer.speak_text_async(text).get()

        session = boto3.session.Session()

        client = session.client('s3',
                                endpoint_url='https://nyc3.digitaloceanspaces.com', # Find your endpoint in the control panel, under Settings. Prepend "https://".
                                region_name='nyc3', # Use the region in your endpoint.
                                aws_access_key_id='WZLBY4N42UCCD4BSXFWM', # Access key pair. You can create access key pairs using the control panel or API.
                                aws_secret_access_key = 'lX9Gm210qZsf4Lfkd1QN+bRcOYH84pKcG3hBPePcOz4')

        client.upload_file('sound.wav', 
                        'celesti.test',
                        'azure/sound%s.wav'%num['id'])

        url = client.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': 'celesti.test',
                                                'Key': 'azure/sound%s.wav'%num['id']})
        return url


    