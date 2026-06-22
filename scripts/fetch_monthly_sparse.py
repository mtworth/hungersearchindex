import csv, json, time, requests, os
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

env = dict(line.split("=", 1) for line in open(".env").read().splitlines() if "=" in line)
SCOPES    = ["https://www.googleapis.com/auth/searchtrends"]
BASE_URL  = "https://searchtrends.googleapis.com/v1alpha"

creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
headers = {"Authorization": f"Bearer {creds.token}"}

SPARSE_DMAS = {
    "800": "Bakersfield",
    "813": "Chico–Redding",
    "868": "Santa Barbara",
}

start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
end_time   = datetime.now(timezone.utc) - timedelta(days=3)

def poll(op_name):
    for _ in range(30):
        r = requests.get(f"{BASE_URL}/operations/{op_name}", headers=headers)
        r.raise_for_status()
        d = r.json()
        if d.get("done"):
            return d
        print("  waiting...")
        time.sleep(2)
    raise TimeoutError

results = {}
for code, name in SPARSE_DMAS.items():
    for res in ["WEEK", "MONTH"]:
        print(f"{name} ({res})...")
        body = {"spec": {
            "expression": {"terms": [{"value": "food bank", "type": "BROAD"}]},
            "geo": {"type": "GEO_TYPE_DESIGNATED_MARKET_AREA", "code": code},
            "timeRange": {
                "startTime": {"seconds": int(start_time.timestamp())},
                "endTime":   {"seconds": int(end_time.timestamp())},
            },
            "timeResolution": res,
        }}
        r = requests.post(f"{BASE_URL}:fetchTimeSeries", headers=headers, json=body)
        r.raise_for_status()
        data = poll(r.json()["name"])
        pts  = data["response"]["timeSeries"]["points"]
        nonzero = [p for p in pts if p["searchInterest"] > 0]
        print(f"  {len(pts)} periods, {len(nonzero)} non-zero ({len(nonzero)/len(pts)*100:.0f}%)")
        results[f"{name}_{res}"] = pts
        time.sleep(0.5)

# Write monthly CSV for the three sparse DMAs
rows = []
for code, name in SPARSE_DMAS.items():
    pts = results.get(f"{name}_MONTH", [])
    for pt in pts:
        rows.append({
            "dma_code": code,
            "dma_name": name,
            "period_start": pt["timeRange"]["startTime"],
            "period_end":   pt["timeRange"]["endTime"],
            "search_interest": pt["searchInterest"],
            "scaled_search_interest": pt["scaledSearchInterest"],
            "is_partial": pt.get("isPartial", False),
        })

out = "data/sparse_dmas_monthly.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nMonthly data written to {out}")
