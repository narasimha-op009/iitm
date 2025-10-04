from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

class MetricsRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

# Load data from JSON file
def load_data():
    data_path = Path(__file__).parent / "q-vercel-latency.json"
    with open(data_path, 'r') as f:
        return json.load(f)

@app.post("/metrics")
async def calculate_metrics(request: MetricsRequest):
    data = load_data()
    result = {}

    for region in request.regions:
        # Filter records for the region
        region_records = [r for r in data if r["region"] == region]

        if not region_records:
            continue

        latencies = [r["latency_ms"] for r in region_records]
        uptimes = [r["uptime_pct"] for r in region_records]

        # Calculate metrics
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        avg_uptime = np.mean(uptimes)
        breaches = sum(1 for lat in latencies if lat > request.threshold_ms)

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }

    return result
