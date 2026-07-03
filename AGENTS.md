# AGENTS.md -- engine-revival

## Boundary

This is a public-facing archive tooling repo. Keep records public-safe and
machine-checkable.

## Never Commit

- proprietary SDK binaries
- leaked source
- game assets
- restricted media images
- private donor files
- private contact data
- credentials or `.env` files

## Verification

Run targeted tests before claiming changes are complete:

```powershell
python -m pytest
engine-revival validate
engine-revival audit-public
```
