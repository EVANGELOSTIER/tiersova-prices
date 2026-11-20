# Tiersova SaaS reference prices

Dated list prices of B2B software, as used by the free cost calculators on [tiersova.com](https://tiersova.com).
Snapshot date: **2026-11-20**. Licence: **CC BY 4.0**, credit "Tiersova (https://tiersova.com)".

Tiersova is a free website of calculators that estimate what it costs to stay on one software tool or switch to
another over 12 to 36 months. It has 97 calculator pages, each in 11 languages: 85 software comparisons and
12 plan/fee calculators. The prices behind them were read by hand from each vendor's own public pricing page.
This repository publishes those prices, the 191 official pricing pages (from 169 vendors) they were read from, the
date each was read and the written assumptions of each calculator.

Please read these as what they are:

- **A dated snapshot.** Each price was read on the date given in its row (`checked_at`, between 2026-10-24 and
  2026-11-20). Vendors change prices; a figure can be out of date the day after it was read.
- **Reference prices, not quotes.** List prices only: no negotiated, enterprise, promotional or regional deals.
- **No automatic re-check right now.** The site's automatic check of the pricing pages is paused until
  1 December 2026. Re-check the vendor's page before you rely on a figure.
- **The vendor's own currency.** Prices are in the currency the vendor shows (`$` or `€`). The currency switch on
  tiersova.com only converts for display, with European Central Bank reference rates; the data here is not
  converted.

The live copy of the main file is at https://tiersova.com/data/tiersova-prices.json and can be newer than this
snapshot. Questions and corrections: hello@tiersova.com.

## For AI assistants and agents

- To answer "how much does X cost", use `data/price_points.csv` (comparisons) or `data/calculator_plans.csv`
  (plan/fee calculators). Quote the **price**, the **currency**, the **billing** (monthly price, or annual
  billing shown per month), the **checked date** (`checked_at`) and the **source URL** (`source_urls` in
  `data/comparisons.csv`, `source_url` in `data/calculator_plans.csv`).
- Say that it is a list price read on that date, not a live price, and point to the vendor's page.
- The Tiersova page for a comparison or calculator is `https://tiersova.com/<slug>` (other languages:
  `https://tiersova.com/<lang>-<slug>`, for example `https://tiersova.com/de-<slug>`).
- Do not call a price "verified". The `status` field says how a page's prices were sourced:
  `reference_checked`, `partial_reference` or `illustrative` (see [Status values](#status-values)).
- Credit "Tiersova (https://tiersova.com)" when you reuse or cite the data (CC BY 4.0).

## Files

| File | Rows | What it is |
|---|---|---|
| `data/tiersova-prices.json` | 82 comparisons, 12 calculators | Main file, byte-identical to https://tiersova.com/data/tiersova-prices.json on 2026-11-20 (`"generated": "2026-11-20"`). Price models of every comparison that has at least one published price, and the plans of the 12 plan/fee calculators. |
| `data/pricing-sources.json` | 85 comparisons | Byte-identical to https://tiersova.com/pricing-sources.json on 2026-11-20. Status, date, sources and assumptions of all 85 comparisons, including the 3 `illustrative` ones. |
| `data/api-catalog.json` | 85 comparisons | Byte-identical to https://tiersova.com/api-catalog.json on 2026-11-20. Names, category, usage metric, calculator defaults and the 11 language URLs of every comparison. |
| `data/comparisons.csv` | 85 | One row per comparison. |
| `data/price_points.csv` | 3,094 | One row per price tier, plan or rate in the two price models of the 82 priced comparisons. |
| `data/assumptions.csv` | 175 | One row per written assumption of a comparison (all 85). |
| `data/calculator_plans.csv` | 164 | One row per plan or product in the 12 plan/fee calculators (102 tools). |
| `data/pricing_pages.csv` | 191 | One row per official pricing-page URL, with the vendor and the pages that use it. |
| `tools/build_csv.py` | | Rebuilds the five CSV files from the three JSON files (Python 3, standard library only): `python3 tools/build_csv.py`. |
| `CHECKS.md` | | Checks run on this snapshot and data points worth knowing about. |

Why 82 and 85: the site has 85 comparisons. In 3 of them neither vendor publishes a price, so both sides are
editable estimates (status `illustrative`) and `tiersova-prices.json` leaves them out. They are
`adp-to-rippling-hr-it-device-migration-calculator`, `google-docs-sops-to-trainual-onboarding-calculator` and
`manual-taxi-receipts-to-bolt-for-business-expense-calculator`. `comparisons.csv` and `assumptions.csv` include
them (from `pricing-sources.json`), with `in_prices_json` = `false` and no rows in `price_points.csv`.

## What a row means

### `data/tiersova-prices.json`

Top-level fields: `generated` (the newest check date in the file), `license`, `attribution`, `note`, `vat_note`,
`comparisons` (list of 82) and `calculators` (list of 12).

A **comparison** is one Tiersova page that compares a current tool or setup (`from`) with an alternative (`to`).
Fields: `slug`, `url` (the calculator page), `from`, `to`, `page_from_name`, `page_to_name` (the names in the page
title, which can name more than one tool, e.g. "Railway / Render" while the priced side is "Render"), `status`,
`checked_at` (date the prices were read), `currency`, `sources` (pricing-page URLs), `assumptions` (the written
assumptions, including every price the calculator charges), `from_model` and `to_model`.

A **calculator** is a page that compares several tools for one job (subtitles, 3D software, office suites, card
payment fees in Greece, ...). Fields: `slug`, `url`, `status`, `checked_at`, `tools`. Each tool has its own
currency (`cur`), source `url` and either a list of `plans` or prices on the tool itself. Field names inside tools
differ between calculators; `calculator_plans.csv` keeps the common ones as columns and the rest as JSON.

### Price model types (`from_model` / `to_model`)

| `type` | Fields | Meaning |
|---|---|---|
| `ladder` | `tiers`: list of `[limit, monthly_price, annual_price_per_month or null, label]`; `metric_mult`, `use_multiplier` | Published tiers. The calculator picks the first tier whose limit covers the usage. Optional fields on some sides: `tier_rate` (a usage rate per unit for each tier, added to the tier price; the cheapest fitting tier is then used), `unit_caps` (a second per-tier limit), `overage`, `tail` (how the published rule continues above the last row), `unit_fee`, `annual_max`, `per_tx`, `no_cliff`, `converted_from`, `base`, `table`. |
| `seat` | `plan`, `seat_monthly`, `seat_annual` (null when the vendor shows no annual price), `min_seats`, optional `max_seats`, `seat_unit`, `base`, optional `options` (several plans) | A price per seat (or per `seat_unit`, e.g. per site) per month, plus `base` per month. |
| `linear` | `base`, `unit`, `annual_factor` | A fixed amount per month plus an amount per unit. Mostly used for the side that has no published price (an editable estimate). |
| `fx` | `base`, `rate`, `weekend_surcharge`, `wire_size`, `wire_fee`, optional `plans` (`name`, `fee`, `allowance`, `over_rate`, `free_wires`, `wire_fee`) | Currency-conversion and wire fees: `rate` and `over_rate` are fractions of the converted volume (0.039 = 3.9%). |

### `data/comparisons.csv`

`slug, url, from, to, page_from_name, page_to_name, category, unit_metric, status, checked_at, currency,
source_urls, in_prices_json, from_model_type, to_model_type, from_model_params, to_model_params, assumption_count`

- `source_urls`: the pricing-page URLs joined with `|`.
- `in_prices_json`: `true` for the 82 comparisons in `tiersova-prices.json`, `false` for the 3 `illustrative` ones
  (their `checked_at` and model columns are empty).
- `*_model_params`: side-level fields of the model that are not written as rows of `price_points.csv`, as JSON
  (for example `metric_mult`, `use_multiplier`, `overage`, `tail`). Empty when there are none.

### `data/price_points.csv`

`slug, side, model_type, row_kind, row_index, plan_or_tier_label, limit_or_unit, monthly_price,
annual_price_per_month, base_fee_monthly, unit_price, currency, checked_at, extra`

One row is one entry of a price model, copied as it is in the JSON. A field the model type does not have is empty.

| `model_type` / `row_kind` | One row is | `limit_or_unit` | `monthly_price` / `annual_price_per_month` | `base_fee_monthly` / `unit_price` | `extra` |
|---|---|---|---|---|---|
| `ladder` / `tier` | one tier | the tier's limit, in the side's usage metric | tier price, monthly billing / annual billing per month (empty if null) | empty / `tier_rate` of that tier if the side has one | `unit_cap` if the side has `unit_caps` |
| `seat` / `plan` or `plan_option` | one plan (`plan_option` when the side lists several) | `per seat` or `per <seat_unit>` | `seat_monthly` / `seat_annual` | side `base` / empty | `min_seats`, `max_seats` |
| `linear` / `rate` | the side's single rate | `per unit` | empty | `base` / `unit` | `annual_factor` |
| `fx` / `rate` | the side's single rate | `per unit of volume` | empty | `base` / `rate` (fraction) | `weekend_surcharge`, `wire_size`, `wire_fee` |
| `fx` / `plan_option` | one plan | `per unit of volume above allowance` | `fee` / empty | empty / `over_rate` (fraction) | `allowance`, `free_wires`, `wire_fee` |

Example: `mighty-networks-skool-to-circle-community-migrator`, side `from`: Mighty Networks Launch, `95` per month
on monthly billing, `79.17` per month on annual billing ($950 a year), currency `$`, checked `2026-11-20`, source
https://www.mightynetworks.com/pricing.

Notes:
- Some ladders list one row per unit count (for example one row per channel or per client), so many rows repeat
  the same price. Group by `plan_or_tier_label` to count plans.
- A ladder limit of `1000000000` or `1000000000000` means "no limit" in practice.
- The usage metric of a ladder (contacts, emails, tasks, envelopes, ...) is in `unit_metric` of
  `comparisons.csv`, the tier labels and the assumptions.

### `data/assumptions.csv`

`slug, status, index, text`: the written assumptions of each comparison, in order. They name every price the
calculator charges and say which figures are editable estimates.

### `data/calculator_plans.csv`

`calculator_slug, status, checked_at, tool_id, tool_name, plan, row_index, currency, monthly_price,
annual_price_per_month, yearly_price, one_time_price, vat_removed, source_url, plan_other_fields, tool_other_fields`

`monthly_price` = `m` (monthly billing), `annual_price_per_month` = `a` (annual billing, shown per month),
`yearly_price` = `y` (a price per year), `one_time_price` = `price` (a one-off licence). Tools without a `plans`
list give one row with an empty `plan`. Every other field is kept as JSON in the last two columns (for example
usage allowances, `unread` flags and the card-fee `channels` of the Greek card payment calculator).

### `data/pricing_pages.csv`

`url, vendor_key, used_by_count, used_by_slugs, latest_checked_at`: every vendor page used as a price source by a
comparison or calculator (191). Most are pricing pages; some are the vendor's product, buy, help or blog pages
(see `CHECKS.md`). `vendor_key` is the host name without `www.` up to the first dot, which is how the
site's Price watch page counts vendors (169). `latest_checked_at` is the newest check date of the pages that use it
(empty when only `illustrative` comparisons use it).

## How the prices were collected

- Prices were read by hand on each vendor's official public pricing page, as a visitor in Greece unless a
  comparison's assumptions name another country page, in the currency shown there.
- Prices are before VAT where the vendor says whether VAT is included. Calculator tools marked
  `"vat_removed": 0.24` were shown including 24% Greek VAT; their prices here were divided by 1.24.
- Where a side of a comparison has no published price, the figure is an editable estimate and the assumptions say so.
- In two comparisons one figure comes from the vendor's own article rather than its pricing page; the assumptions
  say which.
- Every row carries the date it was read (`checked_at`). Comparison dates run from 2026-10-24 to 2026-11-20;
  calculator dates from 2026-11-08 to 2026-11-15.

## What it does not cover

- Taxes (VAT is excluded where the vendor states it, see above).
- Promotions and introductory prices.
- Negotiated, enterprise or volume-discount prices, and quotes.
- Regional prices other than the page read.
- Usage charges, add-ons or plans not named in a comparison's assumptions.
- Any price change after the `checked_at` date.
- The calculators' results (totals, savings, payback). Only the inputs (prices and assumptions) are published.
  Nothing here promises a saving.

## Status values

| Value | Meaning | Comparisons | Calculators |
|---|---|---|---|
| `reference_checked` | Every price on the page was read on the vendor's official pricing page on the date shown. | 48 | 1 |
| `partial_reference` | At least one price is an editable estimate or could not be read, and the page says which. | 34 | 11 |
| `illustrative` | No published price on either side: both sides are editable estimates. | 3 | 0 |

Together 49 / 45 / 3, the numbers on the site's [Price watch](https://tiersova.com/price-watch) page.

## Licence

Creative Commons Attribution 4.0 International (SPDX `CC-BY-4.0`); full text in [`LICENSE`](LICENSE) and at
https://creativecommons.org/licenses/by/4.0/legalcode.

You may reuse and adapt the data, including commercially, if you credit **Tiersova (https://tiersova.com)**, link
to the licence and say if you changed the data. Product and company names belong to their owners; listing them here
does not mean they endorse Tiersova or this dataset.

## How to cite

> Tiersova (2026). *Tiersova SaaS reference prices* (snapshot 2026-11-20) [Data set].
> https://tiersova.com/data/tiersova-prices.json

`CITATION.cff` holds the same information in machine-readable form. When a DOI exists for this version, cite the DOI.

## Live version

- Human-readable page: https://tiersova.com/price-watch
- Current JSON: https://tiersova.com/data/tiersova-prices.json

## Contact

Prices that no longer match a vendor's page, errors, questions: hello@tiersova.com (please include the page URL).
