"""
TidalBrix Dummy Backend
=======================
A "Hello World" mirror of the real TidalBrix FastAPI backend.
Same routes, same response shapes — but all data is hardcoded / mocked.
No DB, no NetCDF files, no Copernicus credentials needed.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import math

# ─────────────────────────────────────────────
# App setup (mirrors real app.py)
# ─────────────────────────────────────────────
app = FastAPI(
    debug=True,
    title="TidalBrix Dummy API",
    description="Hello-World mirror of the Ocean Data Processing API. "
                "All responses are mocked — safe for Docker/EC2 deployment practice.",
    version="0.0.1-dummy",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Fake JWT auth (mirrors real auth.py)
# ─────────────────────────────────────────────
DUMMY_TOKEN = "dummy-jwt-token-for-testing"
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Accepts any Bearer token (or the magic dummy token)."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user_id": 1, "email": "dummy@tidalbrix.com", "name": "Dummy User"}


# ─────────────────────────────────────────────
# Request / Response schemas (mirrors schemas/)
# ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class OceanRequest(BaseModel):
    lat: float = 13.0827
    lon: float = 80.2707
    start_date: str = "2024-01-01"
    end_date: str = "2024-01-07"


# ─────────────────────────────────────────────
# Root health-check (mirrors real root endpoint)
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "TidalBrix Dummy API is running",
        "version": "0.0.1-dummy",
        "note": "All data is mocked. Safe for deployment practice.",
        "container": os.environ.get("HOSTNAME", "unknown"),
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────
# Auth routes  (prefix: /auth)
# ─────────────────────────────────────────────
@app.post("/auth/login")
def login(body: LoginRequest):
    """Accepts any email/password — always returns a dummy token."""
    return {
        "access_token": DUMMY_TOKEN,
        "token_type": "bearer",
        "user": {"email": body.email, "name": "Dummy User"},
        "message": "Login successful (dummy mode)",
    }

@app.post("/auth/register")
def register(body: RegisterRequest):
    return {
        "message": "User registered successfully (dummy mode)",
        "user": {"email": body.email, "name": body.name},
    }

@app.get("/auth/me")
def me(user=Depends(get_current_user)):
    return user


# ─────────────────────────────────────────────
# Tide routes  (prefix: /tide)
# Mirrors: api/routes/tide.py
# ─────────────────────────────────────────────
def _mock_tide_series(lat: float, lon: float, days: int = 7):
    """Generate a sinusoidal fake tide timeseries."""
    base = datetime(2024, 1, 1)
    entries = []
    for h in range(days * 24):
        t = base + timedelta(hours=h)
        # Semidiurnal tide approximation
        height = round(1.5 * math.sin(2 * math.pi * h / 12.4) + 0.3 * math.sin(2 * math.pi * h / 24), 3)
        entries.append({"timestamp": t.isoformat(), "tide_height_m": height})
    return entries

@app.get("/tide/predict")
def tide_predict(lat: float = 13.08, lon: float = 80.27, days: int = 3,
                 user=Depends(get_current_user)):
    return {
        "location": {"lat": lat, "lon": lon},
        "unit": "metres",
        "source": "dummy-mock",
        "data": _mock_tide_series(lat, lon, days),
    }

@app.get("/tide/status")
def tide_status(user=Depends(get_current_user)):
    return {"cache_status": "ready", "last_run": datetime.utcnow().isoformat(), "source": "dummy"}


# ─────────────────────────────────────────────
# UKC routes  (prefix: /ukc)
# Mirrors: api/routes/ukc.py
# ─────────────────────────────────────────────
@app.get("/ukc/calculate")
def ukc_calculate(lat: float = 13.08, lon: float = 80.27,
                  draft: float = 8.5, ukc_required: float = 1.0,
                  user=Depends(get_current_user)):
    """Under Keel Clearance dummy calculation."""
    tide_data = _mock_tide_series(lat, lon, 1)
    results = []
    for entry in tide_data:
        charted_depth = 12.0           # fake chart datum depth
        tide_height = entry["tide_height_m"]
        available_depth = charted_depth + tide_height
        ukc = round(available_depth - draft, 3)
        results.append({
            "timestamp": entry["timestamp"],
            "tide_height_m": tide_height,
            "available_depth_m": round(available_depth, 3),
            "draft_m": draft,
            "ukc_m": ukc,
            "safe": ukc >= ukc_required,
        })
    return {
        "location": {"lat": lat, "lon": lon},
        "charted_depth_m": 12.0,
        "required_ukc_m": ukc_required,
        "results": results,
    }

@app.get("/ukc/status")
def ukc_status(user=Depends(get_current_user)):
    return {"cache_status": "ready", "last_run": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────
# Ocean routes  (prefix: /api/ocean)
# Mirrors: api/routes/ocean.py  (wind, waves, currents, sealevel)
# ─────────────────────────────────────────────
@app.post("/api/ocean/wind")
def ocean_wind(body: OceanRequest, user=Depends(get_current_user)):
    return {
        "dataset": "wind",
        "location": {"lat": body.lat, "lon": body.lon},
        "period": {"start": body.start_date, "end": body.end_date},
        "source": "dummy-mock",
        "data": [
            {"timestamp": "2024-01-01T00:00:00", "wind_speed_ms": 5.2, "wind_dir_deg": 225},
            {"timestamp": "2024-01-01T06:00:00", "wind_speed_ms": 6.8, "wind_dir_deg": 210},
            {"timestamp": "2024-01-01T12:00:00", "wind_speed_ms": 4.1, "wind_dir_deg": 240},
        ],
    }

@app.post("/api/ocean/waves")
def ocean_waves(body: OceanRequest, user=Depends(get_current_user)):
    return {
        "dataset": "waves",
        "location": {"lat": body.lat, "lon": body.lon},
        "source": "dummy-mock",
        "data": [
            {"timestamp": "2024-01-01T00:00:00", "sig_wave_height_m": 1.2, "peak_period_s": 8.4},
            {"timestamp": "2024-01-01T06:00:00", "sig_wave_height_m": 1.5, "peak_period_s": 9.1},
        ],
    }

@app.post("/api/ocean/currents")
def ocean_currents(body: OceanRequest, user=Depends(get_current_user)):
    return {
        "dataset": "currents",
        "location": {"lat": body.lat, "lon": body.lon},
        "source": "dummy-mock",
        "data": [
            {"timestamp": "2024-01-01T00:00:00", "u_ms": 0.3, "v_ms": -0.1, "speed_ms": 0.32},
            {"timestamp": "2024-01-01T06:00:00", "u_ms": 0.5, "v_ms": 0.2, "speed_ms": 0.54},
        ],
    }

@app.post("/api/ocean/sealevel")
def ocean_sealevel(body: OceanRequest, user=Depends(get_current_user)):
    return {
        "dataset": "sealevel",
        "location": {"lat": body.lat, "lon": body.lon},
        "source": "dummy-mock",
        "data": [
            {"timestamp": "2024-01-01T00:00:00", "sea_level_m": 0.12},
            {"timestamp": "2024-01-01T06:00:00", "sea_level_m": 0.18},
        ],
    }

@app.get("/api/ocean/cache-status")
def cache_status(user=Depends(get_current_user)):
    """Mirrors the real cache_checker.get_all_cache_status()"""
    return {
        "tide": True,
        "ukc": True,
        "wind": False,
        "waves": False,
        "currents": False,
        "sealevel": False,
        "note": "dummy mode — no real parquet/netcdf files",
    }
