# Security Policy

## Security status

CommNet is an early-stage local-first community portal and mesh-network demonstrator. It is not yet hardened for unreviewed public internet exposure.

Do not deploy this software in a public, shared, or safety-critical environment without reviewing authentication, authorization, secret storage, runtime configuration, logging, firewall exposure, and safe-state behavior.

## Supported versions

Only the latest public default branch is currently supported for security review.

| Version or branch | Supported |
| --- | --- |
| Latest default branch | Yes |
| Older dated package drops | No |

## Reporting a vulnerability

Do not open a public GitHub issue containing exploit details, private paths, credentials, tokens, screenshots with secrets, or private network information.

Preferred path:

1. Use GitHub private vulnerability reporting from the repository Security page, when available.
2. Include the affected repository, commit or release folder, reproduction steps, expected impact, and whether the issue may expose credentials, files, user data, admin functions, node identities, hardware outputs, local machine paths, or network routes.
3. If private vulnerability reporting is not available, open a public issue titled `Security contact request` without technical exploit details or private information.

## Project-specific security concerns

Please report issues involving:

- Default, demo, weak, or reusable credentials.
- Authentication bypass or privilege escalation between normal users and admin functions.
- Session, cookie, CSRF, XSS, or local-site scripting problems.
- Path traversal, arbitrary file reads, unsafe uploads, or media-library exposure.
- LAN, Wi-Fi, router, or firewall exposure that unintentionally makes the service reachable outside the intended local network.
- Leaked node identity, invite tokens, mesh-network configuration, SSIDs, passwords, private keys, API tokens, or user profile data.
- Unsafe assumptions around Meshtastic, Reticulum, Bluetooth, Wi-Fi, serial bridges, or future transport adapters.

## Email privacy

This policy intentionally does not publish a personal maintainer email address. Use GitHub's private vulnerability reporting workflow when available, or open a non-sensitive `Security contact request` issue.

## Default credentials and first-use behavior

Prototype or demo credentials must never be used on a public or shared network. Fresh deployments should require first-use credential rotation before accepting non-local users.

## Disclosure

Please give the maintainer reasonable time to investigate and correct the issue before public disclosure.
