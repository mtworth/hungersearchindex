import json, requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timezone

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/searchtrends'])
if creds.expired: creds.refresh(Request())
headers = {'Authorization': 'Bearer ' + creds.token}

BASE = 'https://searchtrends.googleapis.com/v1alpha'
start_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
end_time = datetime(2026, 6, 1, tzinfo=timezone.utc)

combos = [
    ('GEO_TYPE_COUNTRY_OR_REGION', 'US', 'GEO_TYPE_ADMINISTRATIVE_AREA2'),
    ('GEO_TYPE_COUNTRY_OR_REGION', 'US', 'GEO_TYPE_DMA'),
    ('GEO_TYPE_COUNTRY_OR_REGION', 'US', 'GEO_TYPE_ADMINISTRATIVE_AREA1'),
]

for geo_type, geo_code, res in combos:
    body = {
        'spec': {
            'expression': {'terms': [{'value': 'food bank', 'type': 'BROAD'}]},
            'geo': {'type': geo_type, 'code': geo_code},
            'timeRange': {
                'startTime': {'seconds': int(start_time.timestamp())},
                'endTime': {'seconds': int(end_time.timestamp())},
            },
            'breakdownResolution': res,
            'zeroOutNoisyResults': False,
        }
    }
    r = requests.post(f'{BASE}:fetchGeoBreakdown', headers=headers, json=body)
    data = r.json()
    if r.status_code == 200:
        print(f'{geo_code} -> {res}: OK')
    else:
        print(f'{geo_code} -> {res}: {data["error"]["message"][:120]}')
