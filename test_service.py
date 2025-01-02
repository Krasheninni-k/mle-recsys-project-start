# Запустить сервер uvicorn recommendations_service:app
# Запуск сервиса uvicorn features_service:app --port 8010
# Запуск сервиса uvicorn events_service:app --port 8020
import random

import utils

print('Тест № 1. Даем рекомендации пользователям без персональных рекомендаций (холодным)')
test_users_1 = [random.randint(10 ** 12, 10 ** 13) for _ in range(5)]
for user in test_users_1:
    utils.test_recs(user)

print('Тест № 2. Даем рекомендации пользователям, у которых есть история (персонализированные), но без онлайн')
test_users_2 = [4, 13, 14, 16, 19]
for user in test_users_2:
    utils.test_recs(user)

print('Тест № 3. Даем рекомендации пользователям, у которых есть история (персонализированные), c учетом 3 их последних событий')
test_users_3 = test_users_2
new_items = [53404, 178529, 33311009]
for user in test_users_2:
    utils.test_online(user, new_items)
