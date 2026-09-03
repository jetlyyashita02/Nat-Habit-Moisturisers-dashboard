# 🧴 Moisturisers — Final Findings (live dump: 160,696 customers · 204,851 orders)

Source: `query_result_2026-09-02…csv` (journey file) — 160,738 raw rows loaded, 42 skipped · Jan '24 → Aug '26.
All figures below come straight from the dashboard's computed views.

## 1. Scale & repeat behaviour
- **160,696** moisturiser customers, **204,851** orders — avg **1.27** orders/customer.
- **26,074 repeat buyers (16.2%)** — 134,622 customers (84%) bought once. Acquisition engine is strong; the leak is order-2.
- **Median repurchase gap 79 days** (p25 = 37 d, p75 = 153 d). Gap histogram peaks at 0–30 d (9,328 gaps) and decays — the reorder window to win is the first ~3 months.
- **V2V 42.3% vs V2C 73.8%** — people stay in *moisturisers* (74%) but happily switch *SKU* (only 42% repeat the exact variant). Category habit > variant habit.
- Avg orders per repeater ≈ 2.7 (both V2V and V2C); avg 1st→2nd gap ≈ 116–118 days.

## 2. Seasonality
- Purchase timing is **broad, not spiky**: Hot Humid 30% · Hot Dry 29% · Cold Winter 24% · Post-Monsoon 17% — moisturiser is a year-round need with a mild monsoon tilt.
- Intent lines: **concern-led dominates — 77,052 orders (53%)** vs Cold Winter 24,498 · Hot Humid 22,681 · Hot Dry 21,080. Pigmentation/concern formulas, not weather formulas, drive the portfolio.
- **Flax Walnut is the standout seasonal SKU**: 45.9% of its orders land in its intended Cold Winter window (1.9× baseline) — the one variant with true winter seasonality to plan stock/promos around.
- **December spike** (~13.3k orders, highest month on the chart) — festive/gifting demand cutting across seasons.

## 3. Portfolio concentration
- **Aloe Vera gel (47,248, 23%) + Turmeric Nutmeg (42,427, 21%) = ~44% of all orders** — a two-hero portfolio; the next five variants share 8–5% each.
- Top transitions are **same-SKU repeats** (TN30→TN30 8.0% · AV80→AV80 5.6% · AV40→AV40 3.2%) — heroes restock themselves.
- **Size flows: upsize beats downsize** — same-product 31.8% · lateral 29.6% · **upsized 21.8% vs downsized 16.8%**. Net size trajectory is upward (AV40→AV80 is the #1 cross-SKU move at 396).

## 4. Geography × seasonality
- **Rest of India is the largest bloc (52,422 customers, 33%)**, ahead of North 23% · South 22% · West 18% · East 5% — this is a national brand, not a metro brand. Bengaluru (18,324) is the single biggest city, ahead of New Delhi (11,850) and Mumbai (9,805).
- **North over-indexes on winter lines (1.27×)** and under-buys its "concern" share relatively; **South (0.88×) and West (0.89×) under-index on winter** — geographically sensible seasonality, and a reason to vary the promo mix by zone.
- **West (1.06×) and South (1.03×) tilt to gels**; East leans Hot Humid (15% vs 11% national line share).
- Regional timing matrices are otherwise flat (24–32% per season everywhere) — season is a *variant* property more than a *region* property.

## 5. Loyalty by region
- **South repeats best (18.0%)**, East 17.1%, West 16.3%, North 15.6%, Rest-of-India lowest (15.3%) — metro/South customers are the retention core; RoI volume is more one-and-done.
- V2V/V2C are even across regions (42–43% / 73–75%) — switching culture is national, not regional.

## 6. So-what (compact)
1. **Win order-2 inside 90 days** — median gap 79 d, 84% one-timers; trigger reorder nudges at day 30–45 (usage cycle of a 30–50 g jar).
2. **Merchandise the category, not the SKU**: V2C 74% ≫ V2V 42% — recommend "next moisturiser for your skin/season" rather than only same-SKU replenishment.
3. **Protect and stock the two heroes** (Aloe Vera gel, Turmeric Nutmeg) and use them as the default 2nd-order recommendation (they already are the most common 2nd orders).
4. **Promote size-up paths** (AV40→AV80, 30 g → 50 g): upsizes outpace downsizes 21.8% → 16.8%.
5. **Run winter only where winter sells**: Flax Walnut / Tomato Patchouli promos weighted to North & East (1.27×/1.05×), concern-led evergreen messaging elsewhere.
6. **December is the gifting spike** — plan stock and kits for it independently of season lines.
7. **Retention push in Rest of India** (33% of base, lowest repeat) — free-shipping thresholds or sachet-to-jar conversion offers aimed at that bloc.
