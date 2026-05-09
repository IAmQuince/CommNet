from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
files = [p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in {'.md','.py','.json','.html','.txt'} and p.name != 'check_catena_claims.py']
text = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in files)
forbidden = ['Catena' + ' is ' + 'Meshtastic', 'Catena remote delivery complete', 'LoRaWAN' + ' is local peer mesh']
found = [f for f in forbidden if f.lower() in text.lower()]
if found:
    raise SystemExit('Forbidden Catena claim(s): ' + ', '.join(found))
print('Catena claims audit: PASS')
