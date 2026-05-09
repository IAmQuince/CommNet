from __future__ import annotations

from commnet.hardware.catena_protocol import PREFIX, parse_line


class FakeCatenaSerial:
    def __init__(self):
        self.tx_count = 0
        self.rx_count = 0
        self.last_write = ''
        self.profile = 'serial_only'

    def transact(self, line: str, timeout: float = 1.0) -> str:
        self.last_write = line.strip()
        parsed = parse_line(self.last_write)
        t = parsed['type']
        if t == 'PING':
            nonce = parsed['fields'].get('nonce', '')
            return f'{PREFIX}|PONG|nonce={nonce}|uptime_ms=123456'
        if t == 'ID?':
            return f'{PREFIX}|ID|device=catena4610|fw=commnet-catena-bridge|ver=0.1.0|adapter=catena_serial_lora|rf_mode=disabled|mode=fake'
        if t == 'STATUS?':
            return f'{PREFIX}|STATUS|uptime_ms=123456|tx={self.tx_count}|rx={self.rx_count}|err=0|last_error=none|profile={self.profile}|rf_mode=disabled|mode=fake'
        if t == 'CFG':
            self.profile = parsed['fields'].get('profile', self.profile)
            return f'{PREFIX}|ACK|id=cfg|status=accepted|profile={self.profile}|rf_mode=disabled|mode=fake'
        if t == 'TX':
            self.tx_count += 1
            mid = parsed['fields'].get('id', 'unknown')
            return f'{PREFIX}|ACK|id={mid}|status=accepted|detail=local_hardware_ack_only|class={parsed["fields"].get("class","text_message")}|to={parsed["fields"].get("to","broadcast")}|bytes=5|mode=fake'
        return f'{PREFIX}|ERR|code=unknown_command|detail={t}'
