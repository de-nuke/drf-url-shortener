# drf-url-shortener
Recruitment task for "Szkoła w Chmurze"

Original text:

> Projekt "API w DRF to skracania urli"- coś w rodzaju https://tinyurl.com/app tylko samo API.
> Funkcjonalność ma być ekstremalnie minimalistyczna, nie chodzi o dodawanie super features (potraktuj to jako podpowiedź :slightly_smiling_face: tu nie trzeba wiele kodować).
>
> Projekt powinien umożliwiać:
>
> 1. Stworzenie skróconego urla, czyli np. wkładamy `http://example.com/very-very/long/url/even-longer` w zamian dostajemy krótki url wygenerowany przez API, np. `http://localhost:8000/shrt/`
> 2. Rozwinięcie skróconego urla do oryginalnego, czyli odwrotność poprzedniej operacji.
>
> Jak coś nie jest zrozumiałe to improwizuj i krótko opisz co było niejasne i jaka decyzja została podjęta.

## How to run

Application works in virtual env. For simplicity, it uses sqlite3 as a database
so there's no need to set up any other service.

Environment: **Python 3.11** / **Django 4.2**

Run inside the project root:
1. `python -m venv venv` – to create virtual env
1. `source venv/bin/activate` – to activate the virtual env
1. `python -m pip install -r requirements.txt -r requirements-dev.txt` – to install dependencies. You can skip `requirements-dev.txt` if you don't need to run tests.
1. `cp env.example .env` – to prepare basic environment variables
1. `python -m pytest` – to test that everything works. Installing dev requirements is required to run `pytest`.

## Usage:
1. Send long url to the API via `POST /urls/` (see [API Documentation](#api-documentation)).
2. You shortened link will be returned as `shortened_url` in the response. It should have a form of: `http://<domain>/<shortcut>`.
3. Paste the shortened URL into the browser. You should be redirected to the original, long URL.
4. Server counts how many times the shortcut has been used and when was the last usage.
5. Use API endpoint `GET /urls/<shortcut>/` (see [API Documentation](#api-documentation)) to see all the details of the shortcut.

## API Documentation

### Send URL to shorten

An endpoint which allows to upload a long url and get a generated shortcut.

`POST /urls/`
```json
{
  "url": "http://example.com"
}
```

**Returns:**
```json
{
  "url": "http://example.com",
  "shortcut": "u5Ga4",
  "created": "2023-09-06T11:19:05.496782Z",
  "last_accessed": null,
  "use_count": 0,
  "shortened_url": "http://localhost:8000/u5Ga4/"
}
```

**Errors:**

400 – Invalid data
```json
{
  "url": ["Enter a valid URL."]
}
```

### Get shortened URL detail by shortcut

Returns details about shortened url along with simple usage information.

`GET /urls/<shortcut>/`

**Returns:**
```json
{
  "url": "http://example.com",
  "shortcut": "u5Ga4",
  "created": "2023-09-06T11:19:05.496782Z",
  "last_accessed": "2023-09-07T20:09:05.566632Z" | null,
  "use_count": 3,
  "shortened_url": "http://localhost:8000/u5Ga4/"
}
```

**Errors:**

404 – Shortcut does not exist
```json
{
    "detail": "Not found."
}
```
