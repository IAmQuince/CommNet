---
document_id: CMN-GOV-STD-003
title: Active Archive and Package Structure Standard
revision: r0
status: WIP
document_class: controlled_doc
package_class: PRECODE_BASELINE
classification:
  domain: GOV
  type: STD
  sequence: 001
effective_date: 2026-05-08
authoring_context: CommNet
depends_on:
- CMN-GOV-STD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Active Archive and Package Structure Standard

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-05-08 | WIP | Initial package layout standard for CommNet pre-code and later implementation packages. |

## 1. Purpose [SEC:CMN-GOV-STD-003::1]

This standard defines the required package structure for CommNet packages extracted under `C:\Users\iaq16\Documents\Code\CommNet`.

## 2. Required Root Structure [SEC:CMN-GOV-STD-003::2]

The pre-code package shall contain:

```text
.github/
audit_reports/
docs/
proof/
registries/
runtime/
src/
tests/
tools/
.gitignore
.pre-commit-config.yaml
CODEOWNERS
CONTRIBUTING.md
pyproject.toml
README.md
```

## 3. Runtime Boundary [SEC:CMN-GOV-STD-003::3]

`runtime/` is reserved for local state after installation. It shall not contain private identities, user registries, logs, databases, or generated runtime data in a source package. The source package may include only `.gitkeep` and boundary documentation in that folder.

## 4. Short Path Rule [SEC:CMN-GOV-STD-003::4]

Package folder and filenames shall be kept short. Human-readable titles belong inside document metadata, not in long filenames. The audit path threshold for this package is 180 characters relative to the intended Windows extraction path.
