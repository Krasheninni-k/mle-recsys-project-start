# Запустить сервер: uvicorn recommendations_service:app
import requests

from fastapi import FastAPI
from contextlib import asynccontextmanager

import logging as logger
import pandas as pd

import urls
from utils import load_parquet_from_s3, dedup_ids
from classes import Recommendations

rec_store = Recommendations()

popular = load_parquet_from_s3(urls.popular_path)
final = load_parquet_from_s3(urls.personal_path)
rec_store.load("default", popular, columns=["item_id"])
rec_store.load("personal", final, columns=["user_id", "item_id"])

# Запускаем серсис
logger = logger.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")
    yield
    # этот код выполнится только один раз при остановке сервиса
    logger.info("Stopping")
    
# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

# ОФЛАЙН РЕКОМЕНДАЦИИ
@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 20):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs = rec_store.get(user_id, k)

    return {"recs": recs}

# ОНЛАЙН рекомендации (отсортированные объекты по последним трем взаимодействиям)
@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 20):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 3}
    resp = requests.post(urls.events_store_url + "/get", headers=headers, params=params)
    events = resp.json()
    events = events["events"]

    # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
    items = []
    scores = []
    for item_id in events:
        params = {"item_id": item_id, "k": k}
        resp = requests.post(urls.features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp.json()
        items += item_similar_items["item_id_2"]
        scores += item_similar_items["score"]

    # сортируем похожие объекты по scores в убывающем порядке
    # для старта это приемлемый подход
    combined = list(zip(items, scores))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    combined = [item for item, _ in combined]

    # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
    recs = dedup_ids(combined)
    recs = recs[:5]

    return {"recs": recs} 

# Смешиваем онлайн и офлайн рекомендации
@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 20):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs_offline = await recommendations_offline(user_id, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])

    # добавляем оставшиеся элементы в конец
    if len(recs_offline) > min_length:
        recs_blended.extend(recs_offline[min_length:])

    if len(recs_online) > min_length:
        recs_blended.extend(recs_online[min_length:])

    # удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)

    # оставляем только первые k рекомендаций
    recs_blended = recs_blended[:k]

    return {"recs": recs_blended}
