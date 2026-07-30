# app2-microservices-docker

**SE-II Week 7 Tuesday TaskFlow microservices, fully containerized.**

Same two services as `app2-microservices`. Now each runs in its own
container, wired together by docker-compose. One command starts everything.

---

## Run it

```bash
docker compose up --build
```

Wait for both services to show as healthy, then open:
http://localhost:5001

To stop everything:
```bash
docker compose down
```

---

## What is different from app2-microservices

| Difference in                 | app2-microservices            | app2-microservices-docker |

| How to run                    | Two separate terminals        | One command |
| How services find each other  | `localhost:5002`              | `task-validator:5002` (Docker DNS) |
| Validator URL                 | Hardcoded                     | Environment variable |
| Startup order                 | Manual                        | docker-compose guarantees validator starts first |
| Health check                  | None                          | Docker checks `/health` before starting intake |

---

## The one line that changed in services.py

```python
# Before (plain Python):
VALIDATOR_URL = "http://localhost:5002/validate"

# After (docker-compose):
VALIDATOR_URL = os.environ.get("VALIDATOR_URL", "http://localhost:5002/validate")
```

Inside docker-compose, `VALIDATOR_URL` is injected as:
```
http://task-validator:5002/validate
```

`task-validator` is the service name in `docker-compose.yml`.
Docker's internal DNS resolves it to the right container automatically.

---

## Useful commands

```bash
# See both containers running
docker compose ps

# Watch live logs from both services
docker compose logs -f

# Watch logs from one service only
docker compose logs -f task-validator

# Rebuild after a code change
docker compose up --build

# Stop and remove containers
docker compose down

# Stop and remove containers AND images
docker compose down --rmi all
```

---

## File structure

```
app2-microservices-docker/
├── docker-compose.yml          ← orchestrates both services
├── task-validator/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── task-intake/
    ├── Dockerfile
    ├── app.py
    ├── services.py             ← reads VALIDATOR_URL from environment
    ├── models.py
    ├── repository.py
    ├── strategies_and_observers.py
    └── requirements.txt
```
