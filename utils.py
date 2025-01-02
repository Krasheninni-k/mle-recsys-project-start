import os
import io
import boto3
import logging
import requests
from dotenv import load_dotenv

import urls

load_dotenv()

S3_ENDPOINT_URL = "https://storage.yandexcloud.net"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


# Функция для загрузки данных из S3
def load_parquet_from_s3(s3_key):
    s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    buffer = io.BytesIO()
    s3_client.download_fileobj(Bucket=S3_BUCKET_NAME, Key=s3_key, Fileobj=buffer)
    buffer.seek(0)
    return buffer

# Функция для удаления дубликатов
def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Тест для холодных пользователей и пользователей с историей
def test_recs(user_id):
    logger.info("Starting test_recs for user_id: %s", user_id)
    params = {"user_id": user_id, 'k': 10}

    try:
        resp = requests.post(urls.recommendations_url + "/recommendations", headers=headers, params=params)
        
        if resp.status_code == 200:
            recs = resp.json()
            logger.info("Recommendations received: %s", recs)
        else:
            recs = []
            logger.warning("Failed to fetch recommendations. Status code: %s", resp.status_code)
            logger.debug("Response content: %s", resp.text)
    except Exception as e:
        recs = []
        logger.error("Error during test_recs execution: %s", e)

# Тест для онлайн рекомендаций
def test_online(user_id, event_item_ids):
    logger.info("Starting test_online for user_id: %s", user_id)
    try:
        for event_item_id in event_item_ids:
            logger.info("Sending event for user_id: %s with item_id: %s", user_id, event_item_id)
            resp = requests.post(urls.events_store_url + "/put", 
                                 headers=headers, 
                                 params={"user_id": user_id, "item_id": event_item_id})

            if resp.status_code != 200:
                logger.warning("Failed to send event. Status code: %s", resp.status_code)
                logger.debug("Response content: %s", resp.text)

        params = {"user_id": user_id, 'k': 10}
        resp = requests.post(urls.recommendations_url + "/recommendations", headers=headers, params=params)

        if resp.status_code == 200:
            online_recs = resp.json()
            logger.info("Online recommendations received: %s", online_recs)
        else:
            online_recs = []
            logger.warning("Failed to fetch online recommendations. Status code: %s", resp.status_code)
            logger.debug("Response content: %s", resp.text)

    except Exception as e:
        online_recs = []
        logger.error("Error during test_online execution: %s", e)

    print(online_recs)
