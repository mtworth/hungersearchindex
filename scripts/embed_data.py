"""
Rebuilds the DATA = {...} block in index.html with both weekly and monthly datasets.
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

# ── Load weekly ───────────────────────────────────────────────
weekly_vals  = defaultdict(list)
weekly_dates = defaultdict(list)
for r in csv.DictReader(open('data/food_bank_trends_california_dma.csv')):
    weekly_vals[r['dma_code']].append(int(r['search_interest']))
    weekly_dates[r['dma_code']].append(r['week_start'][:10])

weeks_list = weekly_dates['807']

# ── Load monthly ──────────────────────────────────────────────
monthly_vals  = defaultdict(list)
monthly_dates = defaultdict(list)
for r in csv.DictReader(open('data/food_bank_trends_california_dma_monthly.csv')):
    monthly_vals[r['dma_code']].append(int(r['search_interest']))
    monthly_dates[r['dma_code']].append(r['period_start'][:10])

months_list = monthly_dates['807']

# ── Build per-DMA stats from monthly (primary) ────────────────
def monthly_stats(code):
    vals = monthly_vals[code]
    total = sum(vals)
    mx = max(vals) if vals else 0
    peak_i = vals.index(mx) if mx else 0
    recent = sum(vals[-6:])
    prior  = sum(vals[-12:-6])
    yoy = round((recent - prior) / prior * 100, 1) if prior > 0 else 0
    return {'total': total, 'max': mx, 'peak': months_list[peak_i], 'yoy': yoy}

# ── Aggregate (monthly) ───────────────────────────────────────
monthly_agg = [0] * len(months_list)
for _, code, *__ in DMAS:
    for i, v in enumerate(monthly_vals[code][:len(months_list)]):
        monthly_agg[i] += v

weekly_agg = [0] * len(weeks_list)
for _, code, *__ in DMAS:
    for i, v in enumerate(weekly_vals[code]):
        weekly_agg[i] += v

# ── Assemble DMA objects ──────────────────────────────────────
dma_data = []
for csv_name, code, label, lat, lon in DMAS:
    s = monthly_stats(code)
    dma_data.append({
        'code':   code,
        'label':  label,
        'cx':     cx(lon),
        'cy':     cy(lat),
        'sparse': code in SPARSE_CODES,
        'total':  s['total'],
        'max':    s['max'],
        'peak':   s['peak'],
        'yoy':    s['yoy'],
        'monthly': monthly_vals[code],
        'weekly':  weekly_vals[code],
    })

grand_total = sum(monthly_agg)
avg_yoy     = round(sum(d['yoy'] for d in dma_data) / len(dma_data), 1)
peak_idx_m  = monthly_agg.index(max(monthly_agg))
peak_idx_w  = weekly_agg.index(max(weekly_agg))

DATA = {
    'weeks':      weeks_list,
    'months':     months_list,
    'dmas':       dma_data,
    'weeklyAgg':  weekly_agg,
    'monthlyAgg': monthly_agg,
    'grandTotal': grand_total,
    'avgYoy':     avg_yoy,
    'peakWeek':   weeks_list[peak_idx_w],
    'peakWeekIdx':peak_idx_w,
    'peakMonth':  months_list[peak_idx_m],
    'peakMonthIdx':peak_idx_m,
}

DATA_JS = 'const DATA = ' + json.dumps(DATA, separators=(',', ':')) + ';'

# ── Patch index.html ──────────────────────────────────────────
html = open('index.html', encoding='utf-8').read()
html = re.sub(r'const DATA = \{.*?\};', lambda _: DATA_JS, html, flags=re.DOTALL)
open('index.html', 'w', encoding='utf-8').write(html)
print(f'Patched index.html — {len(dma_data)} DMAs, {len(weeks_list)} weeks, {len(months_list)} months')
print(f'Grand total (monthly): {grand_total:,}  Avg YoY: {avg_yoy:+.1f}%')
