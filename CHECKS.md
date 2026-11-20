# Checks on snapshot 2026-11-20

Run on 20–21 Nov 2026 against the local build of tiersova.com that is live (`release-output/dist/`). Nothing in the
data was changed; the items under "Points worth knowing" are listed, not fixed.

## Copy and counts

| Check | Result |
|---|---|
| `data/tiersova-prices.json` vs live `data/tiersova-prices.json` | byte-identical (`cmp`), SHA-256 `4b0a982bc37949a31ae348973cc81e47bc226a3683559797ecb3aa3b72bcc217`, `"generated": "2026-11-20"` |
| `data/pricing-sources.json` vs live `pricing-sources.json` | byte-identical, SHA-256 `c0e0fa1b09a6fc3625933467ad45bcf98a6dff1357f933d3f44adb747cf63b1c` |
| `data/api-catalog.json` vs live `api-catalog.json` | byte-identical, SHA-256 `a3ddcde9d9dde4478998e3bca390af6d0c2198a73fadf92984c99af193fc549a` |
| Comparisons | 85 in `pricing-sources.json` and `api-catalog.json` (`comparison_count: 85`), 85 rows in `comparisons.csv`; 82 of them in `tiersova-prices.json` |
| Plan/fee calculators | 12 in `tiersova-prices.json` (102 tools, 164 rows in `calculator_plans.csv`) |
| Languages | 11 (`en, el, de, es, fr, it, zh, hi, pt, ja, pl`); every one of the 97 pages exists in all 11 (`<slug>.html` and `<lang>-<slug>.html`, 1,067 files) |
| Official pricing pages / vendors | 191 URLs / 169 vendors in `pricing_pages.csv`, the same numbers as the live Price watch page ("191 official pricing pages · 169 vendors · 97 calculators") |
| Rows in `price_points.csv` | 3,094 (ladder tiers 2,970; seat plans 36; seat plan options 33; linear rates 38; fx rates 5; fx plans 12) |
| Rows in `assumptions.csv` | 175 (169 for the 82 priced comparisons, 6 for the 3 illustrative ones) |
| The three JSON files agree | status, `checked_at`, sources and assumptions identical for all 82 shared comparisons; names identical (`tools/build_csv.py` stops if not) |
| Duplicate slugs | none |
| All five CSVs parse with pandas 3.0.5 | yes (85x18, 3094x14, 175x4, 164x16, 191x5) |
| Status counts | comparisons 48 `reference_checked`, 34 `partial_reference`, 3 `illustrative`; calculators 1 / 11 / 0. Together 49 / 45 / 3, as on the Price watch page. |
| Mighty Networks | `mighty-networks-skool-to-circle-community-migrator`, side `from`: 95 monthly / 79.17 annual per month, `$`, checked 2026-11-20 (`price_points.csv` and the JSON); assumptions: "$950 per year, which Mighty Networks shows as $79 a month". Status `reference_checked`. |
| Dates | comparisons 2026-10-24 to 2026-11-20; calculators 2026-11-08 to 2026-11-15; none later than `generated` |
| `LICENSE` | CC BY 4.0 legal code, unchanged from the draft package (SPDX licence-list text) |
| `CITATION.cff` | valid against schema 1.2.0 (`cffconvert --validate`) |
| `.zenodo.json` | parses as JSON |

## Why the draft said 82 comparisons

The draft package (built on 19 Nov 2026) counted the comparisons in `tiersova-prices.json` only. That file leaves
out, by design, the 3 comparisons whose status is `illustrative` (neither vendor publishes a price, so both sides
are editable estimates): `adp-to-rippling-hr-it-device-migration-calculator`,
`google-docs-sops-to-trainual-onboarding-calculator`, `manual-taxi-receipts-to-bolt-for-business-expense-calculator`.
This snapshot adds `pricing-sources.json` and `api-catalog.json`, which list all 85, so `comparisons.csv` and
`assumptions.csv` now cover every comparison; the 3 have `in_prices_json = false` and no price rows.

## URLs

- Every comparison `url` is `https://tiersova.com/<slug>` and the page exists: 85 of 85.
- Every calculator `url` is `https://tiersova.com/<slug>` and the page exists: 12 of 12.
- 191 unique source URLs: 132 on comparisons, 70 on calculator tools, 11 used by both. Without the 3 illustrative
  comparisons' pages (rippling.com, trainual.com, bolt.eu) the count is 188, which is what the draft could see.
- No source URL has a query string or tracking parameter. The URLs were not opened for this snapshot.

## Missing values

- No priced comparison lacks `sources`, `checked_at` or `assumptions`. The 3 illustrative ones have no `checked_at`
  (null in `pricing-sources.json`), so their 3 URLs have an empty `latest_checked_at` in `pricing_pages.csv`.
- Calculator tools with no readable price on one billing option carry `unread`, `m_unread` or `a_unread` flags and
  a null price; they are empty in the CSV.
- Seat plans with `seat_annual: null` and ladder tiers with a null annual price are empty in the CSV.

## Points worth knowing (not fixed)

1. **The automatic check is paused.** The site's automatic check of the pricing pages is paused until 1 Dec 2026.
   The live Price watch page still shows "Daily automatic check, last run 17 Nov 2026" and its JSON-LD says
   "Checked by a script daily and in a browser weekly". This package does not repeat the daily claim.
2. **Not every source is a pricing page.** 29 of the 191 URLs have no pricing-like word in them. Most are the
   vendor's product or buy pages that show prices (Autodesk, Foundry, SideFX, Maxon, Microsoft 365 plan pages,
   DaVinci Resolve, ...); a few are help, docs or blog pages (`zapier.com/blog/what-is-a-task-in-zapier/`,
   `airbnb.com/help/article/1857`, `docs.digitalocean.com/platform/billing/bandwidth/`) that may hold definitions
   or a single figure. The Price watch page says that in two comparisons one figure comes from the vendor's article.
3. **Calculator dates.** The 12 calculators carry `checked_at` 2026-11-08 to 2026-11-15, the last check by hand.
4. **Currency is a symbol, not an ISO code**: comparisons `$` 71, `€` 14 (of the 82 priced: 69 / 13); calculator
   tools `€` 62, `$` 40. `$` is not stated to be USD in the JSON.
5. **Converted prices.** Two ladder sides carry `converted_from: "EUR"` while the comparison currency is `$`:
   `zapier-to-n8n-cloud-workflow-cost-calculator` (to), `kajabi-to-thinkific-course-platform-migrator` (to). The
   conversion rate and date are not in the JSON.
6. **Annual price above monthly price** in one ladder row: `docusign-to-pandadoc-esignature-envelope-calculator`
   (from), limit 10, 45 monthly / 60 annual. The label explains it (1 user monthly vs 2 users annual).
7. **Sentinel limits.** `1000000000` and `1000000000000` are used as "no limit" tier limits.
8. **Tiers without labels or with equal limits.** `aws-ec2-to-digitalocean-vultr-bandwidth-calculator` (from): 4
   tiers, all with limit 500 and an empty label, separated only by `tier_rate`.
9. **Very long ladders** that list one row per unit count (repeated prices) make `price_points.csv` long; group by
   `plan_or_tier_label` to count plans.
10. **`from`/`to` vs page names.** In some comparisons the priced tool is one of several names in the page title
    (e.g. `heroku-to-railway-cost-and-env-migrator` prices Render while the page says "Railway / Render").
11. **`api-catalog.json` holds calculator defaults** (default usage, default monthly figures, default net result).
    These are the calculator's starting inputs, not price data and not a promise of savings.
