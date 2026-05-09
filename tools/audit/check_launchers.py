from pathlib import Path
root = Path(__file__).resolve().parents[2]
required = ['Start_Config.bat','Start_CommNet.bat','Stop_CommNet.bat','Run_Diagnostics.bat','Export_Support_Bundle.bat']
missing = [x for x in required if not (root/x).exists()]
body = '# Launcher Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: ' + ', '.join(missing) + '\n')
(root/'audit_reports'/'active'/'launcher_report.md').write_text(body, encoding='utf-8')
print('LAUNCHER_CHECK_' + ('PASS' if not missing else 'FAIL'))
raise SystemExit(1 if missing else 0)
