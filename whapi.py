from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import requests
import os

load_dotenv() 

# Configuration
# file_path = ''
WHAPI_TOKEN = os.getenv('WHAPI_TOKEN')
WHAPI_BASE_URL = os.getenv('WHAPI_BASEURL')

app = FastAPI()

# Pydantic models
class TextMessage(BaseModel):
    phone_number: str
    message: str

class ImageMessage(BaseModel):
    phone_number: str
    image_url: str
    caption: str = ''

class BroadcastMessage(BaseModel):
    numbers: List[str]
    message: str
    message_type: str = 'text'
    image_url: str = ''

# Functions
def send_text_message(phone_number, message):
    """Send a text message via WhatsApp"""
    url = f'{WHAPI_BASE_URL}/messages/text'
    headers = {'Authorization': f'Bearer {WHAPI_TOKEN}'}
    payload = {'to': phone_number, 'body': message}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def send_image_message(phone_number, image_url, caption=''):
    """Send an image message via WhatsApp"""
    url = f'{WHAPI_BASE_URL}/messages/image'
    headers = {'Authorization': f'Bearer {WHAPI_TOKEN}'}
    payload = {'to': phone_number, 'image': image_url, 'caption': caption}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def broadcast_message(numbers, message, message_type='text', image_url=''):
    """Broadcast message to multiple numbers"""
    results = []
    for number in numbers:
        if message_type == 'text':
            result = send_text_message(number, message)
        elif message_type == 'image':
            result = send_image_message(number, image_url, message)
        results.append(result)
    return results

# Routes
@app.get('/')
def welcome():
    try:
        return "Whatapi is running"
    except Exception as e:
        raise HTTPException(status_code=000, detail=f'Server is not able to access routes, error:{e}')

@app.post('/send/text')
def send_text(payload: TextMessage):
    try:
        result = send_text_message(payload.phone_number, payload.message)
        return {'status': 'success', 'data': result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/send/image')
def send_image(payload: ImageMessage):
    try:
        result = send_image_message(payload.phone_number, payload.image_url, payload.caption)
        return {'status': 'success', 'data': result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/broadcast')
def broadcast(payload: BroadcastMessage):
    try:
        results = broadcast_message(payload.numbers, payload.message, payload.message_type, payload.image_url)
        return {'status': 'success', 'data': results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)