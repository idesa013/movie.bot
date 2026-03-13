# 🎬 SF Movie Bot

Telegram-бот для поиска информации о фильмах, актёрах и режиссёрах с использованием **TMDB API**.  
Бот позволяет искать фильмы, просматривать карточки актёров и режиссёров, сохранять их в избранное и получать рекомендации.

Проект разработан на **Python** с использованием библиотеки **pyTelegramBotAPI**.

## 📌 Основные возможности

### 🔎 Поиск
Бот поддерживает поиск:
- 🎬 фильмов
- 🎭 актёров
- 🎬 режиссёров

После поиска пользователь получает карточку с информацией:

**Фильм**
- название
- год выхода
- рейтинг
- описание
- актёры
- режиссёр

**Актёр / режиссёр**
- имя
- биография
- список фильмов

### ⭐ Избранное
Пользователь может добавлять в избранное:
- 🎬 фильмы
- 🎭 актёров
- 🎬 режиссёров

Лимиты задаются в базе `bot_config`:

| параметр | значение |
|---|---|
| `qty_movie_fav` | 30 |
| `qty_actor_fav` | 20 |
| `qty_director_fav` | 10 |

### ✨ Рекомендации
Бот формирует рекомендации на основе избранного пользователя:
- **Новинки**
- **По жанру**
- **Новинки по жанру**

Жанр определяется автоматически по наиболее часто встречающимся жанрам в избранных фильмах.

### 👨‍💻 Админ-панель
Администратор может:
- просматривать список пользователей
- открывать карточку пользователя
- блокировать / разблокировать пользователей
- просматривать сообщения от заблокированных пользователей
- просматривать избранное пользователя
- искать пользователя по username
- искать заблокированного пользователя по username

## 🌍 Поддержка языков
Все тексты проекта должны храниться в одном месте:

`utils/i18n.py`

Пример структуры:

```python
TEXT = {
    "movie_not_found": {
        "en": "Movie not found",
        "ru": "Фильм не найден"
    }
}
```

Использование в коде:

```python
bot.send_message(chat_id, t(lang, "movie_not_found"))
```

## 🧩 Структура проекта

```text
_movie_bot
│
├── api
│   ├── base.py
│   ├── tmdb_movie.py
│   ├── tmdb_actor.py
│   ├── tmdb_director.py
│
├── config_data
│   └── config.py
│
├── database
│   ├── models.py
│   ├── favorites.py
│   ├── actor_favorites.py
│   ├── director_favorites.py
│   ├── bot_config.py
│
├── handlers
│   ├── custom_handlers
│   └── default_handlers
│
├── keyboards
│   ├── inline
│   └── reply
│
├── states
├── utils
├── loader.py
├── main.py
├── .env.template
└── requirements.txt
```

## ⚙️ Установка и запуск

### 1. Клонировать проект
```bash
git clone <repository_url>
cd movie-bot
```

### 2. Установить зависимости
```bash
pip install -r requirements.txt
```

### 3. Создать `.env`
Пример переменных окружения:
```env
BOT_TOKEN=your_telegram_bot_token
TMBD_API_KEY=your_tmdb_api_key
ADMIN_ID=123456789
```

### 4. Запустить бота
```bash
python main.py
```

## 🌐 Использованные онлайн-сервисы

### TMDB API
Сервис: **The Movie Database (TMDB)**  
Документация: https://developer.themoviedb.org/docs  
Базовый URL API:

```text
https://api.themoviedb.org/3
```

### Используемые endpoints

#### 1. Поиск фильма
```text
GET /search/movie
```

Параметры:
- `api_key`
- `query`
- `language`

Пример ответа:

```json
{
  "page": 1,
  "results": [
    {
      "id": 550,
      "title": "Fight Club",
      "original_title": "Fight Club",
      "release_date": "1999-10-15",
      "overview": "A ticking-time-bomb insomniac...",
      "vote_average": 8.4,
      "genre_ids": [18]
    }
  ]
}
```

#### 2. Детали фильма
```text
GET /movie/{movie_id}
```

Возвращает:
- название
- описание
- рейтинг
- жанры
- дату выхода

#### 3. Актёры и съёмочная группа фильма
```text
GET /movie/{movie_id}/credits
```

Используется для получения:
- актёров
- режиссёра

#### 4. Поиск персоны
```text
GET /search/person
```

Пример ответа:

```json
{
  "results": [
    {
      "id": 287,
      "name": "Brad Pitt",
      "known_for_department": "Acting",
      "popularity": 45.2
    }
  ]
}
```

#### 5. Детали персоны
```text
GET /person/{person_id}
```

Возвращает:
- имя
- биографию
- дату рождения
- место рождения

#### 6. Фильмография персоны
```text
GET /person/{person_id}/movie_credits
```

Используется для получения:
- фильмов актёра
- фильмов режиссёра

#### 7. Переводы биографии
```text
GET /person/{person_id}/translations
```

## 🗄 База данных
Проект использует **SQLite**.

Основные таблицы:
- `user`
- `favorites`
- `actor_favorites`
- `director_favorites`
- `movie_search_log`
- `actor_search_log`
- `director_search_log`
- `msg_from_user`
- `user_block_log`
- `bot_config`

## 🚀 Возможные улучшения
- добавить больше языков
- улучшить алгоритм рекомендаций
- добавить поиск по году
- добавить фильтрацию по рейтингу
- сделать веб-панель администратора

## 📄 Назначение проекта
Проект создан в учебных целях.
