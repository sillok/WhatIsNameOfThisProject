import uuid
import json
import time
import multiprocessing
from threading import Thread
from fastapi import FastAPI, HTTPException
from chatgpt import ChatGPT
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

class Item(BaseModel):
    item: str

@app.post("/name")
def request_item(item: Item):
    gpt_key = str(uuid.uuid4())
    with open("gpt.json", "r", encoding="utf-8") as f:
        gpt = json.load(f)
    if len(gpt.keys()) == 0:
        gpt[gpt_key] = ""
        with open("gpt.json", "w", encoding="utf-8") as f:
            json.dump(gpt, f)
        # Thread(target=ask2bot, args=(gpt_key, item.item)).start()
        pool = multiprocessing.Pool(processes=1)
        pool.apply_async(ask2bot, (gpt_key, item.item+"의 이름을 정해주세요."))
        return {"key": gpt_key}
    else:
        raise HTTPException(status_code=400, detail="waiting")

def ask2bot(gpt_key, item):
    with open("gpt.json", "r", encoding="utf-8") as f:
        gpt = json.load(f)
    bot = ChatGPT()
    v = bot.ask(item)
    # time.sleep(5)
    # v = "djfkds"
    print(v)
    gpt[gpt_key] = v
    with open("gpt.json", "w", encoding="utf-8") as f:
        json.dump(gpt, f)

@app.get("/answer")
def get_answer(gpt_key: str):
    with open("gpt.json", "r", encoding="utf-8") as f:
        gpt = json.load(f)
    if gpt_key in gpt.keys():
        if gpt.get(gpt_key) != "":
            answer = gpt[gpt_key]
            del(gpt[gpt_key])
            with open("gpt.json", "w", encoding="utf-8") as f:
                json.dump(gpt, f)
            return {"answer": answer}
        else:
            raise HTTPException(status_code=400, detail="waiting")
    else:
        raise HTTPException(status_code=400, detail="error")

@app.post("/fastname")
def fastname(item: Item):
    key = "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"
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    data = {
        "prompt": f"{item.item}의 이름을 정해주세요.",
        "max_tokens": 4000,
        "temperature": 1.0,
        "model": "text-davinci-003",
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        print(resp)
        return {"answer": resp["choices"][0]["text"].strip().strip('"')}
    except:
        raise HTTPException(status_code=400, detail="error")


