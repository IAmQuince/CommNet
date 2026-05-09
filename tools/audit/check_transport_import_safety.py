from pathlib import Path
import ast, sys
root=Path(__file__).resolve().parents[2]
transport=root/'src/commnet/transport'
blocked={'meshtastic','serial','RNS','LXMF','bleak','zeroconf','paho','psutil'}
violations=[]
for path in transport.glob('*.py'):
    tree=ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in blocked:
                    violations.append(f'{path.name}: top-level import {alias.name}')
        elif isinstance(node, ast.ImportFrom):
            mod=(node.module or '').split('.')[0]
            if mod in blocked:
                violations.append(f'{path.name}: top-level from {node.module}')
report=root/'audit_reports/active/transport_import_safety_report.md'
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# Transport Import Safety Report\n\n' + ('PASS\n' if not violations else 'FAIL\n'+'\n'.join('- '+v for v in violations)), encoding='utf-8')
if violations:
    print('\n'.join(violations)); sys.exit(1)
print('TRANSPORT_IMPORT_SAFETY_PASS')
