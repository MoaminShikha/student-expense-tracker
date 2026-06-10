# Mizān — Issues & Improvement Backlog

Generated from a multi-agent review (architecture, UX/design, product) on 2026-06-10.
Ordered by leverage. Checkboxes track fix progress.

---

## 🏗️ Architecture & Code

- [x] **A1. Duplicated composition root.** ✅ FIXED — extracted `app/composition.py` with a `build_services(data_dir, logger)` factory returning a frozen `Services` container. Both `app/main.py` (CLI) and `app/gui/main.py` (GUI) now call it; the GUI's missing-logger drift is gone.
- [~] **A2. `sys.path.insert` hack** in `app/gui/main.py`. NOTE: a `mizaan` console-script entry-point already exists in `pyproject.toml`; the hack only supports running the file directly during dev. Low priority — left in place intentionally.
- [~] **A3. O(n) full-file load + rewrite per operation.** ✅ PARTIAL — added an mtime-keyed in-memory cache in the new `JsonStore` base (`infrastructure/json/repositories/base.py`): repeated reads in a process no longer re-parse the file, and a cross-process write is still observed via the on-disk mtime key. Full indexing / SQLite migration still open (writes remain full-file rewrites).
- [x] **A4. No file locking.** ✅ FIXED (in-process) — `safe_file_io.save_json_safely` now serializes the read-modify-write cycle under a process-wide per-path `threading.Lock`, so GUI worker threads + main thread can't clobber the same file. Cross-*process* safety (CLI + GUI simultaneously) would still need an OS file lock — noted in code.
- [x] **A5. Hand-rolled (de)serialization** ✅ FIXED — centralized into `infrastructure/json/mappers.py` (one `Mapper` per model) + a generic `JsonStore[T]` base. The 6 repos dropped their duplicated `_deserialize`/`_load_all`/`_save_all` and inline dict literals; each is now ~30–55 lines of pure queries. Serialization can no longer drift between read and write paths.
- [x] **A6. Log noise.** ✅ FIXED — demoted the 9 read-path "Retrieved…/retrieved…" logs to `logger.debug` across all repos; write/create events stay at `info` as an audit trail.
- [x] **A7. Weak CI quality gates.** ✅ FIXED — mypy split: **strict & blocking** on the core (`domain/application/ports/infrastructure`, now 0 errors), advisory on the Qt GUI. Tests now run under `--cov --cov-fail-under=35`. Fixing the core to type-clean surfaced a real bug: `Decimal('NaN')`/`Infinity` passed validation → now rejected in `_parse_decimal` (+ regression tests). New `test_domain_behavior.py` covers domain transitions, the NaN fix, and cache freshness.

- [x] **A8. Anemic domain model.** ✅ FIXED — state transitions moved onto the model: `CommittedCharge.mark_paid()` / `is_paid` (replaces the repo's dict-poking; the charge repo now calls the domain method). Fuzzy updates also go through immutable `replace()`.

## 🎨 UX & Visual Design

- [x] **U1. Broken / duplicated theming.** ✅ FIXED (core inconsistency) — the stale purple `DARK_*` base constants (`#1a1a2e`…) now derive from the canonical slate `_DARK` palette (`#020617`…). All three color paths (stylesheet_manager's `DARK_PALETTE`, the 180+ direct `tokens.*` refs, and `theme_manager.get_color`) now resolve to ONE palette, so the hero card no longer renders purple while the rest is slate. (Remaining: full light/dark runtime reactivity for the 180+ direct token refs is a larger refactor — still open.)
- [x] **U2. Hardcoded light-mode colors inside dark UI.** ✅ FIXED — hero money symbol `rgba(24,26,44,0.38)` (near-invisible navy on dark) → `tokens.MUTED`; Arabic label `rgba(168,124,36,0.65)` → `tokens.GOLD`. Base gradient already theme-aware. The subtle warm radial-glow overlays left intentionally (low-alpha warmth on slate).
- [x] **U3. Contrast risk (WCAG AA).** ✅ PARTIAL — bumped `T_MICRO` 8→10 and `T_MINI` 9→11 (raised the smallest type floor). Full contrast audit of muted-on-surface pairs still open.
- [ ] **U4. Limited responsiveness.** Fixed widths (`SIDEBAR_W`, `STAT_COL_W=290`) and `setFixedSize` across 14 files; min window 1280×720; no reflow. → Replace with min/max + stretch; add a breakpoint to collapse the sidebar.
- [ ] **U5. Accessibility gaps.** Only 4 files set tooltips; no `setAccessibleName`/screen-reader labels; active nav relies on color/dot only. → Add accessible names + a non-color active cue.
- [ ] **U6. 221 hardcoded `px` values** bypass the type scale (e.g. money `52px`/`54px` literals). → Route through tokens.

## 💡 Product / Idea

- [ ] **P1. Headline feature is vaporware.** The marketed "automatic pattern awareness" / spike-detection insight (PatternDetector) isn't implemented — insights page shows only deterministic burn/runway/encumbrance bars. → Ship at least one rule-based "spike" insight sentence.
- [ ] **P2. No real reminders/notifications.** The pre-charge reminder pillar reduces to a static "due within 7 days" strip; no scheduler/push.
- [ ] **P3. Manual entry only + desktop-only.** Competes on the friction that kills manual trackers; students are mobile-first (web is a stub). → Strategic: plan mobile/web + import.
- [ ] **P4. No shared/flatmate cost splitting** despite being in the user definition.
- [ ] **P5. No monetization thesis; ₪ hardcoded (no multi-currency).**

---

## Fixed this session ✅
- **A1** — unified composition root (`app/composition.py` factory)
- **A6** — repo read-path logs demoted to `debug`
- **U1** — dark palettes unified onto one slate source of truth
- **U2** — hero card hardcoded text colors routed through tokens
- **U3** — smallest type-scale floor raised (8→10, 9→11)
- **B1 (CRITICAL)** — *GUI never created a session*, so every add (income/spend/charge) silently no-op'd and `data/` stayed empty. Added a first-run **onboarding dialog** (`dialogs/onboarding_dialog.py`) wired into `gui/main.py`; if no active session exists it collects an opening balance and calls `init_session()`. Also replaced the **silent error swallows** in all add handlers with user-facing `ErrorDialog`s so failures can never be invisible again.
- **B2** — *Charges could never be marked paid in the GUI* (they stayed "upcoming" forever). Added a ✓ **mark-paid button** to each upcoming-charge row, plumbed `charge_id` through `ChargeRowVM` and a new `mark_charge_paid_requested(str)` signal (panel → page → window → controller → `charge_service.mark_paid`). Verified end-to-end.
- **U-theme** — per the dark-first decision, **removed the non-functional light/dark toggle** from Settings (a dead control hurts a portfolio); replaced with a static "uses a dark theme; light coming later" note. Theme-manager infra kept for future light mode.

All 253 tests pass; CLI + GUI both import and wire cleanly. GUI verified via offscreen screenshots.

### Edit/Delete — deliberately deferred (would be higher risk)
There are **no delete/edit methods** anywhere (ports, repos, or services). Adding them means new port interface methods + repo implementations + edit dialogs + delete confirmations — a much larger, riskier surface than mark-paid. Left as a scoped follow-up given the low-risk constraint.

## Still open (recommended next)
- **A3/A4** — caching + `filelock` JSON store (perf + CLI/GUI race safety)
- **A5** — centralize serialization
- **A7** — tighten CI gates (mypy non-advisory, coverage threshold)
- **U1 (remainder)** — make the 180+ direct `tokens.*` refs theme-reactive for a working light/dark toggle
- **U3 (remainder)** — full WCAG contrast audit
- **U4/U5/U6** — responsiveness, accessible names, px→token cleanup
- **P1–P5** — product/strategic (ship spike insight, reminders, mobile/web, cost-splitting, monetization)
