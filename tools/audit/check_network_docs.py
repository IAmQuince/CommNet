from pathlib import Path
import sys, os
root=Path(__file__).resolve().parents[2]
required=['CMN-NET-SPEC-009_LanPeerHandshake_r0_WIP.md','CMN-NET-SPEC-010_PeerRegistry_r0_WIP.md','CMN-TRANS-SPEC-006_TransportManager_r0_WIP.md','CMN-TRANS-SPEC-010_LanHttpAdapter_r0_WIP.md','CMN-DIAG-SPEC-003_NetworkDiagnostics_r0_WIP.md']
missing=[f for f in required if not (root/'docs/active'/f).exists()]
report=root/'audit_reports/active/network_docs_report.md'; report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# Network Docs Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: '+', '.join(missing)+'\n'), encoding='utf-8')
if missing: sys.exit(1)
print('NETWORK_DOCS_PASS', flush=True)
os._exit(0)
