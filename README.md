# Items API-FastAPI + PostgreSQL + Docker
*API REST para para consulta,modificación y creación de items de manera asincrónica exponiendolos como endpoints JSON*

### Tecnologías
- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- Docker
- PostgreSQL
- Uvicorn

### Endpoints
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/items ` | Lista todos los items |
| GET | `/items/{item_id}` | Filtra los items por un id |
| POST | `/items ` | Crea items |
| PATCH | `/items/{item_id} ` | Actualiza un item ya existente según su id |
| DELETE | `/items/{item_id} ` | Elimina un item según su id |

### cómo correrlo?
```bash
 git clone https://github.com/DamianPanero/fastapi_postgreSQL_docker

 pip install -r requirements.txt

 uvicorn main:app --reload
```

 ### Con Docker
```bash
docker-compose up --build
```
La API queda en http://localhost:8000/docs

 ### Estructura
 ```
 |-main.py
 |-docker-compose.yml
 |-dockerfile
 |-README.md
 |-requirements.txt
 ```