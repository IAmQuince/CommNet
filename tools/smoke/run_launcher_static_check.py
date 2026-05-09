from pathlib import Path
root = Path(__file__).resolve().parents[2]
for name in ['Start_Config.bat','Start_CommNet.bat','Stop_CommNet.bat','Run_Diagnostics.bat','Export_Support_Bundle.bat']:
    p = root / name
    assert p.exists(), f'missing {name}'
    txt = p.read_text(encoding='utf-8', errors='replace')
    assert '%~dp0' in txt, f'{name} does not use relative root'
    assert 'commnet\\main.py' in txt, f'{name} does not call commnet main'
print('LAUNCHER_STATIC_CHECK_PASS')
