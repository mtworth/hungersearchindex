"""
Rebuilds the DATA = {...} block in index.html with both weekly and monthly datasets.
Uses scaled_search_interest (0-100) throughout.
Run from the repo root: python scripts/embed_data.py
"""
import csv, json, re
from collections import defaultdict

SPARSE_CODES = {'800', '813', '868'}

DMAS = [
    ('San Francisco-Oakland-San Jose',               '807', 'SF Bay Area',       37.77, -122.42),
    ('Sacramento-Stockton-Modesto',                  '862', 'Sacramento',        38.58, -121.49),
    ('Los Angeles',                                  '803', 'Los Angeles',        34.05, -118.24),
    ('San Diego',                                    '825', 'San Diego',          32.72, -117.16),
    ('Fresno-Visalia',                               '866', 'Fresno–Visalia',     36.74, -119.77),
    ('Monterey-Salinas',                             '828', 'Monterey–Salinas',   36.60, -121.89),
    ('Eureka',                                       '855', 'Eureka',             40.80, -124.16),
    ('Chico-Redding',                                '813', 'Chico–Redding',      40.58, -122.39),
    ('Bakersfield',                                  '800', 'Bakersfield',        35.37, -119.02),
    ('Santa Barbara-Santa Maria-San Luis Obispo',    '868', 'Santa Barbara',      34.42, -119.70),
]

def cx(lon): return round((lon + 124.5) / 10.4 * 300, 1)
def cy(lat): return round((42.0 - lat) / 9.5  * 400, 1)

# ── Load weekly (scaled) ──────────────────────────────────────
weekly_vals  = defaultdict(list)
weekly_dates = defaultdict(list)
for r in csv.DictReader(open('data/food_bank_trends_california_dma.csv')):
    weekly_vals[r['dma_code']].append(int(r['scaled_search_interest']))
    weekly_dates[r['dma_code']].append(r['week_start'][:10])

weeks_list = weekly_dates['807']

# ── Load monthly (scaled) ─────────────────────────────────────
monthly_vals  = defaultdict(list)
monthly_dates = defaultdict(list)
for r in csv.DictReader(open('data/food_bank_trends_california_dma_monthly.csv')):
    monthly_vals[r['dma_code']].append(int(r['scaled_search_interest']))
    monthly_dates[r['dma_code']].append(r['period_start'][:10])

months_list = monthly_dates['807']

# ── Per-DMA stats (monthly scaled) ───────────────────────────
def monthly_stats(code):
    vals    = monthly_vals[code]
    nz      = [v for v in vals if v > 0]
    avg     = round(sum(nz) / len(nz)) if nz else 0
    recent  = round(sum(v for v in vals[-12:] if v > 0) / max(1, sum(1 for v in vals[-12:] if v > 0)))
    prior   = round(sum(v for v in vals[-24:-12] if v > 0) / max(1, sum(1 for v in vals[-24:-12] if v > 0)))
    yoy     = round((recent - prior) / prior * 100, 1) if prior > 0 else 0
    mx      = max(vals) if vals else 0
    peak_i  = vals.index(mx) if mx else 0
    current = next((v for v in reversed(vals) if v > 0), 0)
    return {'avg': avg, 'current': current, 'max': mx, 'peak': months_list[peak_i], 'yoy': yoy}

# ── Statewide aggregate (avg across DMAs per period) ─────────
n_months = len(months_list)
n_weeks  = len(weeks_list)

monthly_agg = []
for i in range(n_months):
    period_vals = [monthly_vals[code][i] for _, code, *__ in DMAS if i < len(monthly_vals[code])]
    nz = [v for v in period_vals if v > 0]
    monthly_agg.append(round(sum(nz) / len(nz)) if nz else 0)

weekly_agg = []
for i in range(n_weeks):
    period_vals = [weekly_vals[code][i] for _, code, *__ in DMAS if i < len(weekly_vals[code])]
    nz = [v for v in period_vals if v > 0]
    weekly_agg.append(round(sum(nz) / len(nz)) if nz else 0)

# ── Assemble DMA objects ──────────────────────────────────────
dma_data = []
for csv_name, code, label, lat, lon in DMAS:
    s = monthly_stats(code)
    dma_data.append({
        'code':    code,
        'label':   label,
        'cx':      cx(lon),
        'cy':      cy(lat),
        'sparse':  code in SPARSE_CODES,
        'avg':     s['avg'],
        'current': s['current'],
        'max':     s['max'],
        'peak':    s['peak'],
        'yoy':     s['yoy'],
        'monthly': monthly_vals[code],
        'weekly':  weekly_vals[code],
    })

avg_yoy      = round(sum(d['yoy'] for d in dma_data) / len(dma_data), 1)
peak_idx_m   = monthly_agg.index(max(monthly_agg))
peak_idx_w   = weekly_agg.index(max(weekly_agg))
# statewide current = avg of most recent non-zero monthly values
state_current = round(sum(d['current'] for d in dma_data) / len(dma_data))

DATA = {
    'weeks':        weeks_list,
    'months':       months_list,
    'dmas':         dma_data,
    'weeklyAgg':    weekly_agg,
    'monthlyAgg':   monthly_agg,
    'avgYoy':       avg_yoy,
    'stateCurrent': state_current,
    'peakWeek':     weeks_list[peak_idx_w],
    'peakWeekIdx':  peak_idx_w,
    'peakMonth':    months_list[peak_idx_m],
    'peakMonthIdx': peak_idx_m,
}

DATA_JS = 'const DATA = ' + json.dumps(DATA, separators=(',', ':')) + ';'

html = open('index.html', encoding='utf-8').read()
html = re.sub(r'const DATA = \{.*?\};', lambda _: DATA_JS, html, flags=re.DOTALL)
open('index.html', 'w', encoding='utf-8').write(html)

print(f'Patched index.html — {len(dma_data)} DMAs, {len(weeks_list)} weeks, {len(months_list)} months')
print(f'Statewide current score: {state_current}/100  Avg YoY: {avg_yoy:+.1f}%')
for d in dma_data:
    print(f'  {d["label"]:<20} current={d["current"]:>3}/100  avg={d["avg"]:>3}/100  yoy={d["yoy"]:+.1f}%')
