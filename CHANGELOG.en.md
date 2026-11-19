# Rassarpa · Changelog

[中文](CHANGELOG.md) · English

## 0.1.0 (2026-11-20)

First public release. Directory, package and branch names are all `rassarpa`.

- **Default flipped**: the gap is now produced by `.mx` empty inline boxes at a quarter em; `text-autospace` is demoted to an opt-in class `.cjk--autospace`. Measured reasons: engines give 1/8 em, the spec offers no width parameter, and Safari adds on one side only.
- **Removed** the `@supports not (text-autospace: normal)` fallback: the property is recognized since Chrome 140, so the block never fired.
- **Added** the web-side hard rules (T01/T07/T08/T11/T11b/T13) and font-licensing rules (F03/F04/F06) to §9 of `SKILL.md`, keeping upstream rule IDs for later reconciliation.
- **Added three tools**: `cjk_spacing.js` (per-text-node wrapping, keeps `unicode-bidi: isolate`), `cjk_spacing.py` (same rules server-side), and `check_spacing_consistency.py` (numeral–measure-word consistency).
- **Added optical correction**: `glyph_optical_correct.py` aligns ink centres rather than advance boxes, fixing a `1` that floats and an `8` that sits left in a numeric grid.
- **Self-check**: `tools/selfcheck.py` runs five checks (API names, referenced files present, §9 IDs anchored, stylesheet red lines, consistency checker has teeth); CI runs it too.
- **Known gap**: Safari and Firefox are not measured locally. One-sided gaps and dropped gaps at element boundaries are cited from WebKit records and marked unverified.
