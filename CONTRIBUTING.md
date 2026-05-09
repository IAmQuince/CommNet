# Contributing

CommNet is a local-first community networking prototype. Contributions should preserve the core goals: inspectable code, local usefulness, safe defaults, clear documentation, and no accidental internet exposure.

## Before opening an issue or pull request

- Do not post secrets, passwords, tokens, router credentials, private keys, user databases, session files, or private network maps.
- Do not post exploit details publicly. Use the security process in `SECURITY.md`.
- Check whether the repo root has drifted into a dated package-dump structure. New work should move toward a clean root layout.

## Development principles

- Keep public entry points easy to run and easy to inspect.
- Preserve existing features unless removal is explicitly discussed.
- Prefer simple, local-first behavior before adding network complexity.
- Keep admin-only functions clearly separated from normal user portal functions.
- Avoid hard-coded credentials, private paths, or machine-specific assumptions.
- Any default/demo credential must be clearly marked as prototype-only and must not be safe for public exposure.

## Pull request checklist

Before requesting review, confirm:

- The app still starts from the documented entry point.
- Normal user and admin flows are still separated.
- No secrets, real user data, local DB files, or logs were committed.
- New files follow the repo naming rules and avoid long path names.
- README or docs were updated for user-visible behavior changes.
- Security-sensitive changes are described without publishing exploit details.

## Testing

Run the available smoke tests or launch scripts before submitting. If a bug is hard to reproduce, add a small diagnostic note or harness output that another developer can copy and inspect.
