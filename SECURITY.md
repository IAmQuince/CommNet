# Security Policy

## Security status

CommNet is an early-stage local-first community portal and mesh-network demonstrator. It is not yet hardened for public internet exposure.

Do not deploy CommNet on a public-facing server without reviewing authentication, authorization, session handling, secret storage, file serving, upload handling, firewall rules, and runtime configuration.

## Supported versions

Only the latest public default branch is currently supported for security review.

| Version or branch | Supported |
| --- | --- |
| Latest default branch | Yes |
| Older dated package drops | No |

## Reporting a vulnerability

Do not open a public GitHub issue for a security vulnerability.

Preferred path:

1. Use GitHub private vulnerability reporting from the repository Security page.
2. Include the affected repository, commit or release folder, reproduction steps, expected impact, and whether the issue may expose credentials, files, user data, admin functions, node identities, network routes, or local machine paths.
3. If private reporting is not available, open a public issue titled `Security contact request` without exploit details.

## CommNet-specific security concerns

Please report issues involving:

- Default, demo, weak, or reusable credentials.
- Authentication bypass or privilege escalation between normal users and admin functions.
- Session, cookie, CSRF, XSS, or local-site scripting problems.
- Path traversal, arbitrary file reads, unsafe uploads, or media-library exposure.
- LAN/Wi-Fi/router exposure that unintentionally makes the service reachable outside the intended local network.
- Leaked node identity, invite tokens, mesh-network configuration, SSIDs, passwords, private keys, API tokens, or user profile data.
- Unsafe assumptions around Meshtastic, Reticulum, Bluetooth, Wi-Fi, serial bridges, or future transport adapters.

## Default credentials and first-use behavior

Prototype or demo credentials must never be used on a public or shared network.

A production-ready CommNet release should require first-run admin account creation or forced password rotation before accepting non-local users.

## Secrets and runtime data

Do not commit real secrets or runtime state, including:

- `.env` files
- Private keys or certificates
- User databases
- Session keys
- Invite tokens
- Router, Wi-Fi, or mesh credentials
- Logs containing personal data or network topology
- Local filesystem paths that reveal private workstation structure

## Disclosure expectations

Please allow reasonable time for investigation and remediation before public disclosure. This project is maintained as a prototype, so response time may vary.
