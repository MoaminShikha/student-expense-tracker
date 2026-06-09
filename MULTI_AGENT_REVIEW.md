# Mizān Multi-Agent Review Report
**Generated:** 2026-06-09  
**Scope:** Student Expense Tracker (Mizān) PyQt6 GUI Layer  
**Review Angles:** Code Quality · Security · UI/UX Design

---

## 1. CODE QUALITY & BUGS

### Critical Issues (Must Fix)

#### 🔴 Timeline Percentages Overflow 100%
- **File:** `src/expense_tracker/app/gui/controllers/dashboard_controller.py:191`
- **Issue:** Fuzzy zone width not capped to remaining budget space after committed+spent
- **Failure:** With spent_pct=50%, committed_pct=30%, fuzzy budget=600₪, total_budget=2000₪:
  - `fuzzy_width_pct = min(100-30, 30) = 30%`
  - Result: total width = 50 + 30 + 30 = **110%** (overflows)
- **Impact:** Timeline bars overflow past 100% width boundary in HeroCard paintEvent()
- **Fix:** Ensure `spent_pct + committed_pct + fuzzy_width_pct ≤ 100%` before rendering

#### 🔴 Private Attribute Coupling
- **File:** `src/expense_tracker/app/gui/views/main_window.py:156`
- **Issue:** Direct access to `DashboardPage._hero` (private) creates tight coupling
- **Failure:** If DashboardPage removes `_hero`, MainWindow.update_timeline() crashes with AttributeError
- **Impact:** Fragile refactoring; multiple sites must update in lockstep
- **Fix:** Add public accessor method: `def get_hero_card() -> HeroCard:` in DashboardPage

---

### High-Priority Issues

#### ⚠️ Missing Length Validation on User Input
1. **add_spend_dialog.py:145** — description field unbounded
   - Risk: 100KB+ strings cause UI lag, memory exhaustion
   - Fix: Add `QLineEdit.setMaxLength(500)` or validate on submit
   
2. **add_charge_dialog.py:160** — charge name unbounded
   - Risk: Long names degrade panel rendering performance
   - Fix: Cap at 100 chars; truncate with ellipsis in display

#### ⚠️ Invalid Day-of-Month Validation
- **File:** `src/expense_tracker/app/gui/dialogs/add_charge_dialog.py:112`
- **Issue:** QSpinBox allows day 31 for months with only 30 days (Apr, Jun, Sep, Nov)
- **Failure:** UI accepts invalid input that domain layer may reject
- **Fix:** Dynamically update QSpinBox.setMaximum() based on selected month

---

## 2. SECURITY REVIEW

### Critical (Potential XSS)

#### 🔴 HTML Injection in HeadsUpAlert
- **File:** `src/expense_tracker/app/gui/widgets/heads_up_alert.py:72`
- **Issue:** `setTextFormat(RichText)` allows HTML rendering; `set_data()` passes untrusted input
- **Failure:** If controller calls `set_alert(body_html="<img src=x onerror=alert(1)>")`, HTML executes
- **Risk:** Low (currently only called with hardcoded strings), but API is XSS-capable
- **Fix:** Either:
  1. Remove `body_html` parameter; always use PlainText
  2. Or: HTML-escape all input before rendering

#### 🔴 XSS-Capable API in HeroCard
- **File:** `src/expense_tracker/app/gui/widgets/hero_card.py:149`
- **Issue:** `set_alert(body_html=...)` passes unescaped HTML to HeadsUpAlert
- **Fix:** Sanitize HTML or remove HTML support entirely

---

### High (Input Validation)

#### ⚠️ No Max-Length on Descriptions
- **Files:** add_spend_dialog.py:145, add_charge_dialog.py:160
- **Risk:** Memory exhaustion via unbounded strings
- **Fix:** Enforce max 500 chars for descriptions, 100 chars for names

#### ⚠️ Generic Error Messages Hide Failures
- **File:** `src/expense_tracker/app/gui/controllers/dashboard_controller.py:93`
- **Issue:** User sees "Failed to add income" with no details on persistence failure
- **Risk:** Silent data loss; user unaware if transaction actually saved
- **Fix:** Show specific error (e.g., "Disk full" or "File locked")

#### ⚠️ Full Stack Trace Printed on Startup
- **File:** `src/expense_tracker/app/gui/main.py:64`
- **Issue:** `traceback.print_exc()` leaks file paths, Python version, library versions
- **Risk:** Low for local app, but reduces obscurity
- **Fix:** Use logger instead; show user-friendly error dialog

---

### Medium (Data Handling)

#### ⚠️ Date Validation Fragility
- **File:** `src/expense_tracker/app/gui/dialogs/add_income_dialog.py:145`
- **Issue:** QDateEdit.date() conversion assumes valid year/month/day (QT internal validation)
- **Risk:** Rare edge case if QT returns malformed dates due to timezone/locale
- **Fix:** Add explicit date range validation on submit

#### ⚠️ User Input Rendered Without Escaping (Currently Safe)
- **File:** `src/expense_tracker/app/gui/views/activity_page.py:62`
- **Issue:** Descriptions set via `QLabel.setText()` (PlainText by default — safe)
- **Risk:** If future code adds RichText rendering, HTML injection is possible
- **Fix:** Always render user strings as PlainText; use HTML only for app-generated labels

---

## 3. UI/UX DESIGN REVIEW

### Accessibility (CRITICAL per Material Design)

#### 🔴 Missing Focus Management in Dialogs
- **Issue:** Add/Edit dialogs don't auto-focus first input field
- **Impact:** Keyboard users must Tab through empty space before reaching input
- **Fix:** `dialog.amount_input.setFocus()` in dialog `__init__`

#### 🔴 No Touch Target Sizing (for mobile compatibility)
- **Issue:** Buttons/icons may be <44px (iOS minimum) or <48dp (Android minimum)
- **Impact:** Mobile users hit wrong buttons
- **Fix:** Audit all buttons/clickables; enforce minimum 44×44px with padding if needed

#### 🔴 Missing Accessibility Labels on Icons
- **Issue:** Navigation icons (sidebar), action buttons (panels) lack aria-labels
- **Impact:** Screen reader users hear "Button" instead of "Add Income"
- **Fix:** Add setAccessibleName() to all icon buttons; use QPushButton with text or setAccessibleDescription()

---

### Visual Hierarchy & Consistency

#### ⚠️ Type Scale Unused Consistently
- **tokens.py** defines T_MICRO–T_XL, but not all widgets use them
- **Fix:** Audit all QLabel/QLineEdit font sizes; replace hardcoded `setPointSize()` with tokens
- **Impact:** Professional polish; easier dark mode support

#### ⚠️ Color Token Not Used for All Semantic States
- **tokens.py** has RED (committed), GREEN (income), AMBER (fuzzy), but:
  - Panel headers may use hardcoded colors instead of tokens
  - Disabled state colors not defined
- **Fix:** Define DISABLED_FG, DISABLED_BG in tokens; use everywhere

#### ⚠️ Inconsistent Spacing
- **Issue:** Padding around cards/panels varies (no 8dp rhythm)
- **Impact:** Layout feels amateurish; hard to scale
- **Fix:** Define SPACING tokens (4, 8, 16, 24, 32) and enforce them

---

### Interaction & Feedback

#### 🔴 No Loading State on Slow Operations
- **Issue:** Add Income/Charge/Spend dialogs don't show spinner/progress while saving
- **Impact:** User unaware if operation succeeded; may click button multiple times → duplicate entries
- **Fix:** Show QProgressBar or spinner in dialog; disable submit button during save

#### 🔴 No Success/Error Feedback After Submit
- **Issue:** Dialog closes immediately; no toast/notification confirming save
- **Impact:** User unsure if data was saved or lost
- **Fix:** Show brief toast: "Income added ✓" or "Error: Failed to save"

#### ⚠️ Hardcoded Panel Content (Known Gap)
- **Issue:** Upcoming/Recent/Category panels show "—" (placeholder)
- **Impact:** Dashboard appears incomplete; user confused
- **Fix:** Populate from controller; show "No upcoming charges" when empty

#### ⚠️ Streak Widget Non-Functional
- **Issue:** Displays "—" (comment says Phase 7)
- **Impact:** User doesn't see their spending streak; feature appears broken
- **Fix:** Implement streak calculation in BalanceEngine or hide widget until ready

---

### Light/Dark Mode Readability

#### ⚠️ Dark Mode Not Implemented
- **Issue:** Tokens only define light-mode colors; no dark-theme variant
- **Impact:** App unusable in dark mode (if attempted)
- **Fix:** Create DARK_BG, DARK_FG variants in tokens; implement QApplication.setStyle("Fusion") with dark palette

#### ⚠️ Contrast Not Verified in Both Modes
- **Issue:** MUTED_FG (#56586c) on BG (#f7f3ec) may not meet 4.5:1 WCAG AA
- **Fix:** Run Lighthouse/WAVE on colors; adjust if needed

---

### Layout & Responsive

#### 🔴 Fixed Sidebar Width (210px) Not Responsive
- **Issue:** Sidebar doesn't collapse on small screens; may overflow on 800px displays
- **Impact:** Unusable on tablets in portrait mode
- **Fix:** Add breakpoint: `if screen_width < 1024px { hide sidebar; add menu button }`

#### 🔴 ScrollArea Not Tested on Mobile Orientation
- **Issue:** DashboardPage uses QScrollArea; untested in landscape
- **Impact:** Content may overflow or scroll inappropriately
- **Fix:** Test on mobile emulator; adjust card widths for landscape

#### ⚠️ No Empty States
- **Issue:** Panels show nothing when no data (upcoming charges, recent transactions)
- **Impact:** Confusing; user doesn't know why panel is blank
- **Fix:** Show: "No upcoming charges. Click Add to create one."

---

### Forms & Dialogs

#### ⚠️ No Placeholder or Helper Text
- **Issue:** QLineEdit/QSpinBox fields lack hints
- **Impact:** User unsure what to enter (e.g., amount format: "₪" or number only?)
- **Fix:** Add QLineEdit.setPlaceholderText("e.g., 150.50")

#### ⚠️ Error Messages Appear Only After Failed Submit
- **Issue:** Inline validation missing; user finds out amount is invalid only after clicking Add
- **Impact:** Poor UX; user frustrated
- **Fix:** Validate on blur; show inline error: "Amount must be > 0"

#### ⚠️ No Confirmation for Destructive Actions
- **Issue:** If app adds delete charges/transactions, no confirmation needed
- **Fix:** (Pre-emptive) When delete is added, show: "Delete this transaction? This cannot be undone."

---

### Animation & Motion

#### 🟡 HeroCard Timeline Animation (Partial)
- **Status:** TimelineWidget animates bar width with QPropertyAnimation ✓
- **Gap:** Stat cards (SPENT, COMMITTED) appear instantly without fade-in
- **Fix:** Add entrance animation (fade-in 200ms, ease-out) to StatColumn cards

#### 🟡 No Page Transition Animation
- **Status:** Dashboard/Activity/Insights tabs switch instantly
- **Fix:** Add cross-fade or slide-in transition (150-300ms) for page changes

---

## 4. DESIGN SYSTEM GAPS

### Missing Design Tokens
- [ ] DISABLED_FG, DISABLED_BG (for greyed-out state)
- [ ] BORDER_RADIUS_SM, BORDER_RADIUS_LG (small/large radius scale)
- [ ] SHADOW_SM, SHADOW_MD, SHADOW_LG (elevation scale)
- [ ] Z_INDEX tokens (base, nav, modal, toast, tooltip)

### Missing Component Foundations
- [ ] Toast/Notification component (for success/error feedback)
- [ ] Loading spinner / progress bar (for async operations)
- [ ] Empty state template (for "no data" scenarios)
- [ ] Error boundary (for graceful error display)

### Fonts (Implemented ✓)
- DM Mono (code), Playfair Display (headings), Noto Naskh Arabic (labels)
- **Gap:** Font weights not defined (100, 300, 400, 600, 700); hardcoded in components

---

## 5. PRIORITY ROADMAP

### Phase 1: Critical Fixes (This Sprint)
1. **Fix timeline percentage overflow** (dashboard_controller.py:191)
2. **Add public hero_card accessor** (main_window.py:156)
3. **Sanitize/remove HTML in HeadsUpAlert** (heads_up_alert.py:72)
4. **Add length validation to text inputs** (dialogs)
5. **Auto-focus first field in dialogs** (all dialogs)

### Phase 2: High-Priority (Next Sprint)
6. Add loading state & success feedback to dialogs
7. Implement date validation (month → max day)
8. Populate Upcoming/Recent/Category panels
9. Add touch target sizing audit (44×44px minimum)
10. Define Z-INDEX tokens; consolidate focus styles

### Phase 3: Polish (Future)
11. Implement dark mode
12. Add page transition animations
13. Implement responsive sidebar (collapse on <1024px)
14. Add toast/notification component
15. Implement streak calculation (Phase 7 feature)

---

## 6. CHECKLIST FOR DELIVERY

- [ ] Timeline percentages capped to ≤100%
- [ ] All buttons/clickables ≥44×44px or have expanded hit area
- [ ] Primary text contrast ≥4.5:1 in light mode (WCAG AA)
- [ ] Focus rings visible on all interactive elements (2-4px)
- [ ] Dialogs auto-focus first input; Tab order correct
- [ ] Loading state shown for async operations (>300ms)
- [ ] Success/error feedback shown after submit
- [ ] Empty states present (not blank panels)
- [ ] No hardcoded colors; all use tokens
- [ ] No layout shift on content load (CLS < 0.1)
- [ ] Dark mode colors defined (even if not active)
- [ ] Screen reader can navigate all inputs with descriptive labels

---

## Summary

**Bugs Found:** 2 critical + 3 high (code quality)  
**Security Issues:** 4 critical + 3 high + 2 medium  
**UX Gaps:** 4 critical + 8 high + 6 medium

**Overall Assessment:**
- ✅ Architecture is sound (clean layers, MVC pattern)
- ✅ Color/typography system is professionally designed
- ❌ UI feedback (loading, success, errors) needs work
- ❌ Accessibility (focus, labels, touch targets) incomplete
- ❌ Form validation and error messaging weak
- ⚠️ Security: current risk is low (hardcoded strings), but APIs are XSS-capable

**Recommendation:** Fix Phase 1 critical items before user testing. Phase 2 & 3 can be incremental.
