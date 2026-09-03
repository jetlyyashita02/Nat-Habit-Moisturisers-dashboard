# 🧴 Dashboard changelog — what changed, exactly

Compare bases: **v1** = original GitHub file (142,015 B, had "FORMULA-DRIVEN CONCLUSIONS") · **current** = 201,261 B.
Exact line diff: `changes.diff` (+1,076 / −232). Side-by-side live: open `/original.html` vs `/` on the preview.

## v1 → v2 (rebuild)
**Removed**
- ❌ Entire **FORMULA-DRIVEN CONCLUSIONS** section (6 prose blocks) + its computation engine.

**Data layer (new)**
- ➕ File picker now reads your **raw order dump**: streamed chunk-by-chunk parsing (tab stays responsive on 100k+ rows), quote-aware parser across chunk boundaries, `,`/`;` sniffing, auto-detected headers (customer / date / SKU / code / name / city / order-id), flexible dates (`Mon D, YYYY`, `15-Jan-2026`, ISO+time, `DD/MM/YYYY`, Excel serials).
- ➕ Accepts **two shapes**: order-level rows (journeys rebuilt: same-day items merged, sorted, first 6) *and* the old journey-wide export; journeys keep only FC-* moisturiser SKUs; header chip reports raw rows / kept / skipped.
- ➕ Progress % in the busy overlay; graceful alert listing headers when a file can't be mapped.

**Layout & presentation (new)**
- ➕ New design system: card grid, sticky glass filter bar, section headers with subtitles, tabular numerals, KPI cards with context sub-lines, scope line ("Showing X of Y loaded customers…").
- ➕ **No more wall of tiles** — proper sections: Demand over time · Seasonality · Portfolio & cohort shape · Loyalty & repurchase · Switching behaviour · Variant summary · Journey explorer.

**Interactivity (new)**
- ➕ Every chart clickable → sets its filter (month bar, donut slice, variant/depth/region bars, city & transition rows → search); click again clears.
- ➕ New **Variant filter** dimension; removable **filter chips** + clear-all.
- ➕ Hover tooltips with counts + % everywhere; 3-month trend toggle on the month chart.
- ➕ Sortable tables; journey rows **expand into timelines** (dates, seasons, +N-day gap chips).

## v2 → v3 (deeper cuts)
- ➕ **⚡ Deep-cut insights strip**: auto-detected one-line findings (regional season concentration, gel affinity, on-season lift champion + mismatch, best-repeating region, entry-season→repeat effect, city concentration, downsize pressure), each with its own numbers, click-to-apply, sample-size guarded. *This replaced conclusion prose with data-grounded conclusions, per your request.*
- ➕ **Geography × seasonality section**: region × purchase-timing heat matrix + region × season-line heat matrix (with All-India reference row), affinity-index bars (1.00× = average), region loyalty table (Repeat / V2V / V2C per region).
- ➕ On-season **lift column** (× baseline) added to the variant table.

## v3 → v4 (your sheet format)
- ➕ Variant summary rebuilt as the **Variant Key** table with your exact columns: Cold Winter (Dec–Feb) · Hot Dry (March–May) · Hot Humid (June–Sept) · Non Seasonal/Concern · Gels (Active/Aloe) · Total · Peak Season · Intended Season · V2V Loyalty · V2C Loyalty · Avg Purchase Days V2V · Most Common 2nd order V2V · Avg Order Count V2V · Avg Purchase Days V2C · Most Common 2nd order V2C · Avg Order Count V2C.
- ➕ Per-variant loyalty engine (per-SKU V2V/V2C %, gaps, most-common 2nd order, avg order counts).
- ➕ **⬇ Export variant table CSV** button (drops straight into Excel).
- ➕ Definitions panel documents the column semantics (Post-Monsoon stays inside Total).

## What did NOT change
- Analysis semantics of kept sections (cohort filters apply to entry order; V2V/V2C definitions; season windows).
- Bundled 655-customer sample still boots the page; numbers on it are identical to v1's (regression-tested).
- Single self-contained file; still GitHub-Pages ready; still no libraries, no tracking.

## How to verify yourself
1. **Read this file** (structured) and **`changes.diff`** (exact).
2. **Side-by-side live**: preview → `/original.html` (v1) vs `/` (current).
3. Spot greps on the new file: `grep -c "FORMULA-DRIVEN" index.html` → **0** (removed); `grep -c "Deep-cut insights\|geoHeat\|Variant Key" index.html` → present.
4. Numbers regression: bundled sample still yields 655 / 835 / 107 / 16.3% (tested, unchanged from v1).

## v4 → v5 (SKU-master category linkage fix)
- 🐞 **Fixed: clicking Active Gel showed Face Malai products.** Root cause: the Category filter scoped only the *cohort* (entry order) while product views listed every product those customers bought. Now, with a category selected, the variant table, top-variants chart, transitions and insights show **only that category's products**, and the Variant/Size pickers are restricted to it (journey rows intentionally still show the full journey, per cohort semantics — documented in Definitions).
- ✅ Linkage verified against your SKU master: CWDM/HDDM/HHDM/DM → Fresh Whipped All Day Malai · AC → Active Face Gel (5 SKUs) · HG → Aloe vera gel (40 g/80 g). Sizes 30/50 (aloe 40/80) all match.
- Note: Blinkit (`BL-FC-…`) and Offline (`RL-FC-…`) channel codes and `BC-` lotions remain **excluded** (D2C FC- codes only), same as before — say the word if you want those channels in.
