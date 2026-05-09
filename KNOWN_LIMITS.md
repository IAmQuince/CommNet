# Known Limits — 20260508_10_CommNetPortalPolish

- This remains a local-first/LAN-first demonstrator, not an internet-hardened production portal.
- A fresh runtime seeds `admin` / `password`; the HUD warns until this is changed.
- `/admin/*` now requires admin capability, but this is still prototype-local authentication.
- User profile icon upload is deferred; blank and generated icons are supported.
- Display settings are persisted at the local node level rather than as fully isolated per-user preferences.
- Some older WIP docs may still lack the strictest doc-control metadata used by newer governance checks.
- Meshtastic live validation requires physical hardware, optional Python packages, and local serial drivers.
- True Windows tray-icon packaging is deferred; the persistent controller window remains the reliable baseline.
- RetroWeb retains profiles/icons/social interaction, but full media import/playback remains a later integration pass.
- BBS moderation/search/pagination remains basic.

## Explicit unfinished transport disclaimers

- Meshtastic hardware messaging is not validated without the user's physical node, drivers, and optional dependencies.
- Reticulum/RNS or LXMF messaging remains declared/deferred and is not a working transport in this package.
- Bluetooth messaging remains declared/deferred and is not a working transport in this package.
