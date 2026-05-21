# cms-fastapi-fastmcp

A metadata-driven CMS built with FastAPI, SQLAlchemy, PostgreSQL, and FastMCP.

## What It Does

Entity definitions live in the [entities](entities) folder as JSON files. On app startup, the project:

- loads each entity definition
- generates a SQLAlchemy model for it
- generates Pydantic request and response schemas
- registers CRUD routes automatically in FastAPI
- exposes those routes in the OpenAPI UI at `/docs`

For example, the entity in [entities/tasks.json](entities/tasks.json) produces:

- `POST /tasks/`
- `GET /tasks/`
- `GET /tasks/{item_id}`
- `PUT /tasks/{item_id}`
- `PATCH /tasks/{item_id}`
- `DELETE /tasks/{item_id}`

## Supported Field Types

- `string`
- `text`
- `integer`
- `float`
- `boolean`
- `datetime`

## Supported Validation Keys

- `required`
- `default`
- `min_length`
- `max_length`
- `pattern`
- `minimum`
- `maximum`
- `enum`

The sample entities in [entities/users.json](entities/users.json) and [entities/interviews.json](entities/interviews.json) demonstrate these rules in practice.

## Run The App

Activate virtual environment

````shell
python3 -m venv .venv
source .venv/bin/activate
````

Create and activate a virtual environment, then install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

OR 

```shell
pip install -r requirements.txt
```

Start the API:

```powershell
.\.venv\Scripts\uvicorn.exe main:create_app --factory --reload --reload-include "*.json"
```

Or 

```shell
uvicorn main:create_app --factory --reload --reload-include "*.json"
```

Open the docs UI at `http://127.0.0.1:8000/docs`.

Using `--reload-include "*.json"` means changes inside the [entities](entities) folder trigger a reload in development, so adding or editing an entity file updates the generated routes and OpenAPI UI automatically.

## Database Configuration

The app reads database settings from `.env`.

Supported variables:

- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DATABASE_URL`
- `AUTO_CREATE_DATABASE`
- `AUTO_CREATE_TABLES`

If `AUTO_CREATE_DATABASE=true`, the app will create the target PostgreSQL database automatically when the server is reachable but the database does not exist yet.

If `AUTO_CREATE_TABLES=true`, the app creates missing tables on startup. That is convenient for local development.

## Migrations

Alembic is configured against the same dynamic metadata used by the app.

Create a migration:

```powershell
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe your change"
```

Apply migrations:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

## Add A New Entity

Add a new JSON file under [entities](entities) using the same shape as [entities/tasks.json](entities/tasks.json). After restarting the app:

- the new CRUD routes appear in `/docs`
- the model is part of SQLAlchemy metadata
- Alembic can autogenerate a migration for the new table

If you run the development command above, JSON changes also trigger reload automatically and you do not need a manual restart.
