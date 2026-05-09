import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from commnet.ux.site_map import SITE_MAP
required = ['/admin/network-wizard','/admin/share-links','/admin/site-map','/admin/catena','/demo/catena','/sitemap']
flat = [href for items in SITE_MAP.values() for href, _ in items]
missing = [r for r in required if r not in flat]
if missing: raise SystemExit('Missing routes in site map: '+repr(missing))
print('Navigation map audit: PASS')
