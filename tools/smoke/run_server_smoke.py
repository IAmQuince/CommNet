import json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
root = Path(__file__).resolve().parents[2]
main = root / 'src' / 'commnet' / 'main.py'
port = 8876
with tempfile.TemporaryDirectory() as td:
    env = os.environ.copy()
    env['PYTHONPATH'] = str(root / 'src')
    env['COMMNET_RUNTIME_DIR'] = td
    proc = subprocess.Popen([sys.executable, str(main), 'serve', '--port', str(port)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        ok = False
        for _ in range(40):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/status', timeout=1) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    ok = data.get('running') is True
                    break
            except Exception:
                time.sleep(0.15)
        assert ok, 'server did not respond'
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/loopback-test', timeout=2) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            assert data['result']['success'] is True
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/api/shutdown', timeout=2).read()
        except Exception:
            pass
        proc.wait(timeout=5)
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)
print('SERVER_SMOKE_PASS')
