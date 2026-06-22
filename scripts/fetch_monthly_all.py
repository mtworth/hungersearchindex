import csv, time, requests, os
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

env = dict(line.split("=", 1) for line in open(".env").read().splitlines() if "=" in line)
SCOPES   = ["https://www.googleapis.com/auth/searchtrends"]
BASE_URL = "https://searchtrends.googleapis.com/v1alpha"

creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
headers = {"Authorization": f"Bearer {creds.token}"}

CA_DMAS = {
    "800": "Bakersfield",
    "803": "Los Angeles",
    "807": "San Francisco-Oakland-San Jose",
    "813": "Chico-Redding",
    "825": "San Diego",
    "828": "Monterey-Salinas",
    "855": "Eureka",
    "862": "Sacramento-Stockton-Modesto",
    "866": "Fresno-Visalia",
    "868": "Santa Barbara-Santa Maria-San Luis Obispo",
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

all_rows = []
for code, name in CA_DMAS.items():
    print(f"Fetching {name} (MONTH)...")
    body = {"spec": {
        "expression": {"terms": [{"value": "food bank", "type": "BROAD"}]},
        "geo": {"type": "GEO_TYPE_DESIGNATED_MARKET_AREA", "code": code},
        "timeRange": {
            "startTime": {"seconds": int(start_time.timestamp())},
            "endTime":   {"seconds": int(end_time.timestamp())},
        },
        "timeResolution": "MONTH",
    }}
    r = requests.post(f"{BASE_URL}:fetchTimeSeries", headers=headers, json=body)
    r.raise_for_status()
    data = poll(r.json()["name"])
    pts  = data["response"]["timeSeries"]["points"]
    nonzero = sum(1 for p in pts if p["searchInterest"] > 0)
    print(f"  {len(pts)} months, {nonzero} non-zero ({nonzero/len(pts)*100:.0f}%)")
    for pt in pts:
        all_rows.append({
            "dma_code": code,
            "dma_name": name,
            "period_start": pt["timeRange"]["startTime"],
            "period_end":   pt["timeRange"]["endTime"],
            "search_interest": pt["searchInterest"],
            "scaled_search_interest": pt["scaledSearchInterest"],
            "is_partial": pt.get("isPartial", False),
        })
    time.sleep(0.5)

out = "data/food_bank_trends_california_dma_monthly.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
    w.writeheader()
    w.writerows(all_rows)
print(f"\nDone. {len(all_rows)} rows written to {out}")
