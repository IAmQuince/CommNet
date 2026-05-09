
from __future__ import annotations
import os, string
from pathlib import Path

def detect_drives() -> list[dict]:
    drives = []
    if os.name == 'nt':
        for letter in string.ascii_uppercase:
            path = f'{letter}:\\'
            if os.path.exists(path):
                drives.append({'path': path, 'label': letter + ':', 'readable': os.access(path, os.R_OK)})
    else:
        drives.append({'path': '/', 'label': 'root', 'readable': os.access('/', os.R_OK)})
        home = str(Path.home())
        if home != '/':
            drives.append({'path': home, 'label': 'home', 'readable': os.access(home, os.R_OK)})
    return drives

def detect_common_folders() -> list[dict]:
    home = Path.home()
    names = ['Desktop', 'Documents', 'Downloads', 'Pictures', 'Music', 'Videos']
    out = []
    for name in names:
        p = home / name
        out.append({'name': name, 'path': str(p), 'exists': p.exists(), 'recommended': name == 'Documents'})
    public = home / 'Documents' / 'CommNet_Public'
    out.append({'name': 'Recommended CommNet Public Folder', 'path': str(public), 'exists': public.exists(), 'recommended': True})
    return out

def recommended_public_folder() -> Path:
    return Path.home() / 'Documents' / 'CommNet_Public'
