# Запуск сервиса uvicorn features_service:app --port 8010
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

import urls
from utils import load_parquet_from_s3
from classes import SimilarItems

logger = logging.getLogger("uvicorn.error")

sim_items_store = SimilarItems()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    sim_items_store.load(
        load_parquet_from_s3(urls.similar_path),
        columns=["item_id_1", "item_id_2", "score"],
    )
    logger.info("Ready!")
    # код ниже выполнится только один раз при остановке сервиса
    yield

# создаём приложение FastAPI
app = FastAPI(title="features", lifespan=lifespan)

@app.post("/similar_items")
async def recommendations(item_id: int, k: int = 10):
    """
    Возвращает список похожих объектов длиной k для item_id
    """
    print(item_id)
    print(k)
    i2i = sim_items_store.get(item_id, k)

    return i2i 