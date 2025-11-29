# Docker Setup

Единый контейнер для развертывания всех сервисов: нейросеть, FastAPI и Streamlit.

## Структура

- `src/Dockerfile` - контейнер для нейросети (YOLO detection)
- `web/api/Dockerfile` - контейнер для FastAPI
- `web/streamlit/Dockerfile` - контейнер для Streamlit
- `docker-compose.yml` - оркестрация всех сервисов
- `nginx/nginx.conf` - конфигурация Nginx для проксирования

## Быстрый старт

### Запуск всех сервисов

```bash
docker-compose up --build
```

### Запуск в фоновом режиме

```bash
docker-compose up -d --build
```

### Остановка

```bash
docker-compose down
```

## Доступ к сервисам

После запуска доступны:

- **Streamlit Dashboard**: http://localhost:80 или http://localhost:8501
- **FastAPI**: http://localhost:80/api или http://localhost:8000
- **API Docs**: http://localhost:80/api/docs

## Nginx

Nginx проксирует запросы:
- `/` → Streamlit (порт 8501)
- `/api/` → FastAPI (порт 8000)

## Volumes

- `./data` → данные и база данных
- `./output` → результаты обработки
- `./models` → модели YOLO

## Переменные окружения

Все сервисы используют `PYTHONUNBUFFERED=1` для корректного логирования.

## Пересборка

```bash
docker-compose build --no-cache
docker-compose up
```

## Логи

```bash
docker-compose logs -f
docker-compose logs -f streamlit
docker-compose logs -f api
docker-compose logs -f neural-network
```

