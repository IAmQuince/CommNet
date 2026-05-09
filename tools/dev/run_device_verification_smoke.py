from __future__ import annotations

from _smoke_common import result, runtime
from commnet.core.config import ConfigManager
from commnet.hardware.serial_ports import list_serial_ports
from commnet.demos.catena_demo import make_adapter_from_config

paths=runtime(); cfg=ConfigManager(paths).ensure_default(); adapter=make_adapter_from_config(cfg); status=adapter.status(); ports=list_serial_ports()
mode=cfg.get('catena_demo_mode')
state='simulated' if mode != 'real_only' and not cfg.get('catena_com_port') else ('connected' if status.get('available') else 'unverified')
checks={'status_dict': isinstance(status, dict), 'serial_ports_list': isinstance(ports, list), 'explicit_state': state in {'simulated','connected','unverified'}}
raise SystemExit(result('device_verification_report.json', checks, {'state': state, 'catena_status': status, 'port_count': len(ports)}))
