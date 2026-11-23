# Rassarpa · Changelog

[中文](CHANGELOG.md) · English

## Unreleased (2026-11-23)

External code review (GitHub Copilot CLI, read-only), 1 medium / 2 low:

- **Pure English text nodes no longer get a spacing element**: the leading group of `RE_BOUNDARY` was `[{ANS}]+`, so `<p>hello</p>` came back as `hell` + `o` with a `cjk-spacing` element inside the word. It now captures a single ideograph only.
- **README states what `.cjk` actually does**: it only disables the engine's automatic spacing; the quarter-em gap comes from `.mx` boxes or the `cjk-spacing` elements the script inserts.
- **`measure_pw.mjs` no longer passes on an unknown engine**: `--engine typo` used to skip every engine, leave `failed` empty and exit 0; it is now validated up front and exits 2.

## 0.1.1 (2026-11-20)

Fixes found the same day the first release went out, all in the "mangles the user's text" and "breaks on someone else's machine" categories.

- **Fixed**: `cjk_spacing.js` removed an existing ASCII space at the boundary (`中 a 中` → `中a中`), contradicting `cjk_spacing.py` and the rule book. Now an existing space is left alone: no box, no deleted characters.
- **Fixed**: the no-lookbehind fallback path wrapped the preceding ideograph inside the spacing box and advanced one character too far, swallowing the next character; punctuation squeezing had the same defect. It now slices the prefix and advances by the real match length.
- **Fixed**: `glyph_optical_correct.py` threw a full traceback when `fontTools` was missing; it now prints one line. That is the only tool here with an external dependency.
- **Tests**: added `tests/test_spacing_js.mjs` (jsdom, 14 checks), run in CI.
- **CI**: per-document checks switch to `git ls-files -z`, so filenames with spaces no longer break the loop.

## 0.1.0 (2026-11-20)

First public release. Directory, package and branch names are all `rassarpa`.

- **Default flipped**: the gap is now produced by `.mx` empty inline boxes at a quarter em; `text-autospace` is demoted to an opt-in class `.cjk--autospace`. Measured reasons: engines give 1/8 em, the spec offers no width parameter, and Safari adds on one side only.
- **Removed** the `@supports not (text-autospace: normal)` fallback: the property is recognized since Chrome 140, so the block never fired.
- **Added** the web-side hard rules (T01/T07/T08/T11/T11b/T13) and font-licensing rules (F03/F04/F06) to §9 of `SKILL.md`, keeping upstream rule IDs for later reconciliation.
- **Added three tools**: `cjk_spacing.js` (per-text-node wrapping, keeps `unicode-bidi: isolate`), `cjk_spacing.py` (same rules server-side), and `check_spacing_consistency.py` (numeral–measure-word consistency).
- **Added optical correction**: `glyph_optical_correct.py` aligns ink centres rather than advance boxes, fixing a `1` that floats and an `8` that sits left in a numeric grid.
- **Self-check**: `tools/selfcheck.py` runs five checks (API names, referenced files present, §9 IDs anchored, stylesheet red lines, consistency checker has teeth); CI runs it too.
- **Known gap**: Safari and Firefox are not measured locally. One-sided gaps and dropped gaps at element boundaries are cited from WebKit records and marked unverified.
