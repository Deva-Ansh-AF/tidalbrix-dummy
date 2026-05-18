# 🌊 TidalBrix Dummy — Docker Deployment Practice App

A **"Hello World"** mirror of the real TidalBrix ocean-data platform.  
Same 4-container architecture, same ports, same dependency chain — **zero real data required**.

---

## What this is

| Real App | This Dummy |
|---|---|
| FastAPI + PostgreSQL + Parquet + NetCDF | FastAPI (mocked responses only) |
| FES2022 tide model (huge files) | Sine-wave math — no files |
| Copernicus Marine (CMEMS) credentials | No external API calls |
| React + Vite frontend (npm build) | Single HTML file served by nginx |
| Worker processes NetCDF data | Worker sleeps + prints, then exits |
| JWT auth with real DB validation | Any Bearer token accepted |

**Goal:** Practice building, pushing, and deploying Docker containers on EC2  
without risk of breaking your real app or spending time on data setup.

---

## Architecture

```
EC2 Instance
└── docker compose up
    ├── db        postgres:16          ← healthcheck gate (same as real)
    ├── backend   python:3.11-slim     ← FastAPI on :8000, waits for db
    ├── frontend  nginx:alpine         ← Static HTML on :5173 → :80
    └── worker    python:3.11-slim     ← Runs once, exits (same as real)
```

Port mapping (identical to real app):
- `5173` → Frontend UI
- `8000` → Backend API + Swagger docs
- `5432` → PostgreSQL

---

## Quick Start (Local)

```bash
# 1. Clone / unzip this folder
cd tidalbrix-dummy

# 2. Build and start all 4 containers
docker compose up --build

# 3. Open in browser
#    Frontend:  http://localhost:5173
#    API docs:  http://localhost:8000/docs
#    Health:    http://localhost:8000/health
```

To watch the worker logs separately:
```bash
docker compose logs -f worker
```

---

## EC2 Deployment — Step by Step

### Step 1: Launch EC2 Instance

- **AMI:** Ubuntu 22.04 LTS (free tier eligible)
- **Instance type:** t2.micro (enough for this dummy app)
- **Security group inbound rules:**

| Port | Source | Purpose |
|------|--------|---------|
| 22   | Your IP | SSH |
| 8000 | 0.0.0.0/0 | Backend API |
| 5173 | 0.0.0.0/0 | Frontend UI |
| 5432 | Your IP (optional) | Postgres direct access |

### Step 2: Install Docker on EC2

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Update and install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin

# Add ubuntu user to docker group (no sudo needed after this)
sudo usermod -aG docker ubuntu

# Re-login to apply group change
exit
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Verify
docker --version
docker compose version
```

### Step 3: Copy the App to EC2

**Option A — SCP (simplest):**
```bash
# From your local machine
scp -i your-key.pem -r ./tidalbrix-dummy ubuntu@<EC2_PUBLIC_IP>:~/
```

**Option B — Git (if you push this to GitHub):**
```bash
# On EC2
git clone https://github.com/your-org/tidalbrix-dummy.git
cd tidalbrix-dummy
```

**Option C — Use Docker Hub (most realistic practice):**
```bash
# On your local machine: build and push each image
docker build -t yourdockerhub/tidalbrix-backend:dummy ./backend
docker build -t yourdockerhub/tidalbrix-frontend:dummy ./frontend
docker build -t yourdockerhub/tidalbrix-worker:dummy ./worker

docker push yourdockerhub/tidalbrix-backend:dummy
docker push yourdockerhub/tidalbrix-frontend:dummy
docker push yourdockerhub/tidalbrix-worker:dummy

# Then on EC2: update docker-compose.yml to use image: instead of build:
# and run:
docker compose pull
docker compose up -d
```

### Step 4: Run the App on EC2

```bash
cd tidalbrix-dummy
docker compose up --build -d   # -d = detached (background)

# Check all containers are running
docker compose ps

# Check logs
docker compose logs backend
docker compose logs frontend
docker compose logs worker
docker compose logs db
```

### Step 5: Verify

```bash
# From EC2 (curl test)
curl http://localhost:8000/
curl http://localhost:8000/health

# From your browser (use EC2 public IP)
http://<EC2_PUBLIC_IP>:5173      # Frontend
http://<EC2_PUBLIC_IP>:8000/docs # Swagger UI
```

---

## Useful Docker Commands to Practice

```bash
# View running containers
docker ps

# View all containers (including stopped worker)
docker ps -a

# Inspect a container
docker inspect tidalbrix-backend

# View resource usage
docker stats

# Exec into a container
docker exec -it tidalbrix-backend bash
docker exec -it tidalbrix-db psql -U tidalbrix

# Stop everything
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v

# Rebuild a single service
docker compose up --build backend

# Scale (not needed here, but good to know)
docker compose up --scale backend=2
```

---

## API Endpoints (all return mock data)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health check |
| GET | `/health` | Container health |
| POST | `/auth/login` | Login (any credentials) |
| POST | `/auth/register` | Register |
| GET | `/auth/me` | Current user |
| GET | `/tide/predict` | Tide prediction (sine wave) |
| GET | `/tide/status` | Tide cache status |
| GET | `/ukc/calculate` | UKC calculation |
| GET | `/ukc/status` | UKC cache status |
| POST | `/api/ocean/wind` | Wind data |
| POST | `/api/ocean/waves` | Wave data |
| POST | `/api/ocean/currents` | Currents data |
| POST | `/api/ocean/sealevel` | Sea level data |
| GET | `/api/ocean/cache-status` | All cache status |

**Swagger UI:** `http://localhost:8000/docs`  
**Auth:** Use `Bearer dummy-jwt-token-for-testing` in the Authorization header.

---

## When You're Ready for the Real App

Things you'll need that this dummy skips:

1. **FES2022 tide model** — large `.nc` files, volume mount to `/app/fes2022`
2. **GEBCO bathymetry** — volume mount to `/app/gebco`
3. **Copernicus Marine credentials** — `COPERNICUS_USERNAME` + `COPERNICUS_PASSWORD`
4. **Real JWT secret** — replace `JWT_SECRET_KEY` in `.env`
5. **SMTP credentials** — for onboarding emails
6. **PostgreSQL migrations** — run Alembic or your migration scripts
7. **SSL/HTTPS** — add nginx + certbot for production

The deployment steps on EC2 are **identical** — only the `.env` and volume mounts change.

---

## File Structure

```
tidalbrix-dummy/
├── docker-compose.yml      ← 4-service orchestration
├── .env                    ← Safe dummy env vars
├── .dockerignore
├── backend/
│   ├── Dockerfile          ← python:3.11-slim
│   ├── requirements.txt    ← fastapi, uvicorn only
│   └── main.py             ← All routes with mocked responses
├── frontend/
│   ├── Dockerfile          ← nginx:alpine
│   ├── nginx.conf          ← Proxy pass to backend
│   └── index.html          ← Full UI (dashboard, tide, UKC, API tester)
└── worker/
    ├── Dockerfile          ← python:3.11-slim
    └── worker.py           ← Prints steps, exits cleanly
```
