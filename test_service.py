# Запустить сервер uvicorn recommendations_service:app
# Запуск сервиса uvicorn features_service:app --port 8010
# Запуск сервиса uvicorn events_service:app --port 8020
import requests
import random

recommendations_url = 'http://127.0.0.1:8000'
events_store_url = "http://127.0.0.1:8020"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# Тест для холодных пользователей и пользователей с историей
def test_recs(user_id):
    params = {"user_id": user_id, 'k': 10}

    resp = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)

    if resp.status_code == 200:
        recs = resp.json()
    else:
        recs = []
        print(f"status code: {resp.status_code}")
        
    print(recs)

# Тест для онлайн рекомендаций
def test_online(user_id, event_item_ids):
    for event_item_id in event_item_ids:
        resp = requests.post(events_store_url + "/put", 
                            headers=headers, 
                            params={"user_id": user_id, "item_id": event_item_id})
                
    params = {"user_id": user_id, 'k': 10}
    resp = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)
    online_recs = resp.json()
    print(online_recs)

print('Тест № 1. Даем рекомендации пользователям без персональных рекомендаций (холодным)')
test_users_1 = [random.randint(10 ** 12, 10 ** 13) for _ in range(5)]
for user in test_users_1:
    test_recs(user)

print('Тест № 2. Даем рекомендации пользователям, у которых есть история (персонализированные), но без онлайн')
test_users_2 = [4, 13, 14, 16, 19]
for user in test_users_2:
    test_recs(user)

print('Тест № 3. Даем рекомендации пользователям, у которых есть история (персонализированные), c учетом 3 их последних событий')
test_users_3 = test_users_2
new_items = [53404, 178529, 33311009]
for user in test_users_2:
    test_online(user, new_items)
