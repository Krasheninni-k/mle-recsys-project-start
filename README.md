# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Используйте то же самое виртуальное окружение, что и созданное для работы с уроками. Если его не существует, то его следует создать.

Создать новое виртуальное окружение можно командой:

```
python3 -m venv env_recsys_start
```

После его инициализации следующей командой

```
. env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`.

Запустите сервисы рекомендаций следующими командами:
uvicorn recommendations_service:app
uvicorn features_service:app --port 8010
uvicorn events_service:app --port 8020

Сервис вовзращает три типа рекомендаций:
1. Если нет истории взаимодействий - то топ популярных треков
2. Если история есть - то персональные рекомендации
3. Если есть последние взаимодейстивя - то персональные рекомендации чередуются с онлайн рекомендациями

# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.

Запустите файл для тестирования в командной строке
python test_service.py

Будут выполнены тесты в трех вариациях:
- Тест № 1. Даем рекомендации пользователям без персональных рекомендаций (холодным)
- Тест № 2. Даем рекомендации пользователям, у которых есть история (персонализированные), но без онлайн
- Тест № 3. Даем рекомендации пользователям, у которых есть история (персонализированные), c учетом 3 их последних событий
