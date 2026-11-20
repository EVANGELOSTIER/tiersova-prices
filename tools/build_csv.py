#!/usr/bin/env python3
"""Regenerate the CSV files in data/ from the three live JSON files in data/.

Usage (from the repository root):  python3 tools/build_csv.py
Standard library only. The JSON files are the source; the CSVs are derived views of them.
Values are copied as they appear in the JSON. A field that a model type does not have is left empty.

- data/tiersova-prices.json: price models of the 82 comparisons that have at least one published price, and the
  12 plan/fee calculators.
- data/pricing-sources.json: status, date, sources and assumptions of all 85 comparisons (including the 3
  "illustrative" ones, which tiersova-prices.json leaves out because neither side has a published price).
- data/api-catalog.json: names, category and the 11 language URLs of all 85 comparisons.
"""
import csv
import json
import os
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SRC = os.path.join(DATA, "tiersova-prices.json")
SOURCES = os.path.join(DATA, "pricing-sources.json")
CATALOG = os.path.join(DATA, "api-catalog.json")


def val(v):
    """CSV cell for a JSON scalar: empty for null/missing, numbers as written in JSON."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return str(v)


def extra(d):
    """JSON object of the remaining fields, or empty when there are none."""
    d = {k: v for k, v in d.items() if v is not None}
    return json.dumps(d, ensure_ascii=False, sort_keys=True) if d else ""


# side-level fields that are written out as rows (not as model parameters)
ROW_FIELDS = {"type", "tiers", "options", "plans", "unit_caps", "tier_rate",
              "plan", "seat_monthly", "seat_annual", "min_seats", "max_seats", "seat_unit"}


def model_params(m):
    """Side-level parameters of a model that are not one row of price_points.csv."""
    t = m["type"]
    p = {}
    for k, v in m.items():
        if k in ROW_FIELDS:
            continue
        if t == "linear" and k in ("base", "unit", "annual_factor"):
            continue
        if t == "fx" and not m.get("plans") and k in ("base", "rate", "weekend_surcharge", "wire_size", "wire_fee"):
            continue
        if t == "seat" and k == "base":
            continue
        p[k] = v
    return json.dumps(p, ensure_ascii=False, sort_keys=True) if p else ""


def price_rows(c, side_name, m):
    common = {"slug": c["slug"], "side": side_name, "model_type": m["type"],
              "currency": c["currency"], "checked_at": c["checked_at"]}
    t = m["type"]
    rows = []
    if t == "ladder":
        caps = m.get("unit_caps")
        rates = m.get("tier_rate")
        for i, tier in enumerate(m["tiers"]):
            limit, monthly, annual, label = tier
            ex = {}
            if caps is not None:
                ex["unit_cap"] = caps[i]
            rows.append(dict(common, row_kind="tier", row_index=i, plan_or_tier_label=label,
                             limit_or_unit=val(limit), monthly_price=val(monthly),
                             annual_price_per_month=val(annual), base_fee_monthly="",
                             unit_price=val(rates[i]) if rates is not None else "", extra=extra(ex)))
    elif t == "seat":
        opts = m.get("options") or [m]
        unit = "per " + m["seat_unit"] if m.get("seat_unit") else "per seat"
        for i, o in enumerate(opts):
            ex = {"min_seats": o.get("min_seats"), "max_seats": o.get("max_seats")}
            rows.append(dict(common, row_kind="plan_option" if m.get("options") else "plan", row_index=i,
                             plan_or_tier_label=o.get("plan", ""), limit_or_unit=unit,
                             monthly_price=val(o.get("seat_monthly")),
                             annual_price_per_month=val(o.get("seat_annual")),
                             base_fee_monthly=val(m.get("base")), unit_price="", extra=extra(ex)))
    elif t == "linear":
        rows.append(dict(common, row_kind="rate", row_index=0, plan_or_tier_label="", limit_or_unit="per unit",
                         monthly_price="", annual_price_per_month="", base_fee_monthly=val(m.get("base")),
                         unit_price=val(m.get("unit")), extra=extra({"annual_factor": m.get("annual_factor")})))
    elif t == "fx":
        if m.get("plans"):
            for i, p in enumerate(m["plans"]):
                rest = {k: v for k, v in p.items() if k not in ("name", "fee", "over_rate")}
                rows.append(dict(common, row_kind="plan_option", row_index=i, plan_or_tier_label=p.get("name", ""),
                                 limit_or_unit="per unit of volume above allowance", monthly_price=val(p.get("fee")),
                                 annual_price_per_month="", base_fee_monthly="", unit_price=val(p.get("over_rate")),
                                 extra=extra(rest)))
        else:
            rest = {k: m.get(k) for k in ("weekend_surcharge", "wire_size", "wire_fee")}
            rows.append(dict(common, row_kind="rate", row_index=0, plan_or_tier_label="",
                             limit_or_unit="per unit of volume", monthly_price="", annual_price_per_month="",
                             base_fee_monthly=val(m.get("base")), unit_price=val(m.get("rate")), extra=extra(rest)))
    else:
        raise SystemExit("unknown model type %r in %s %s" % (t, c["slug"], side_name))
    return rows


def calculator_rows(calc):
    rows = []
    known = {"id", "name", "cur", "url", "plans", "m", "a", "y", "price", "vat_removed"}
    for tool in calc["tools"]:
        tool_rest = {k: v for k, v in tool.items() if k not in known}
        plans = tool.get("plans")
        entries = [(p.get("n", ""), p) for p in plans] if plans else [("", tool)]
        for i, (name, p) in enumerate(entries):
            rest = {k: v for k, v in p.items() if k not in ("n", "m", "a", "y", "price")} if plans else {}
            rows.append({
                "calculator_slug": calc["slug"], "status": calc["status"], "checked_at": calc["checked_at"],
                "tool_id": tool["id"], "tool_name": tool["name"], "plan": name, "row_index": i,
                "currency": tool.get("cur", ""), "monthly_price": val(p.get("m")),
                "annual_price_per_month": val(p.get("a")), "yearly_price": val(p.get("y")),
                "one_time_price": val(p.get("price")), "vat_removed": val(tool.get("vat_removed")),
                "source_url": tool.get("url", ""), "plan_other_fields": extra(rest), "tool_other_fields": extra(tool_rest),
            })
    return rows


def write(name, fields, rows):
    path = os.path.join(DATA, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def vendor_key(u):
    """Vendor of a pricing-page URL, counted the way the site's Price watch page counts it:
    host name without "www.", first label (e.g. https://www.deel.com/pricing/ -> deel)."""
    return urlsplit(u).netloc.replace("www.", "").split(".")[0]


def main():
    with open(SRC, encoding="utf-8") as f:
        d = json.load(f)
    with open(SOURCES, encoding="utf-8") as f:
        ps = json.load(f)["comparison_sources"]
    with open(CATALOG, encoding="utf-8") as f:
        cat = json.load(f)
    catc = {c["slug"]: c for c in cat["comparisons"]}
    priced = {c["slug"]: c for c in d["comparisons"]}
    for slug, c in priced.items():  # the three files must agree on every comparison they share
        p = ps[slug]
        if (p["status"], p["checked_at"], p["sources"], p["assumptions"]) != (c["status"], c["checked_at"], c["sources"], c["assumptions"]):
            raise SystemExit("pricing-sources.json and tiersova-prices.json disagree on %s" % slug)
        if (catc[slug]["from_software"], catc[slug]["to_software"]) != (c["from"], c["to"]):
            raise SystemExit("api-catalog.json and tiersova-prices.json disagree on names of %s" % slug)
    if set(ps) != set(catc):
        raise SystemExit("pricing-sources.json and api-catalog.json list different comparisons")

    comps, points, assumptions = [], [], []
    for slug in sorted(catc):
        a, p, c = catc[slug], ps[slug], priced.get(slug)
        comps.append({
            "slug": slug, "url": a["urls"]["en"], "from": a["from_software"], "to": a["to_software"],
            "page_from_name": a["page_from_name"], "page_to_name": a["page_to_name"], "category": a.get("category", ""),
            "unit_metric": a.get("unit_metric", ""),
            "status": p["status"], "checked_at": p["checked_at"] or "", "currency": p["currency"],
            "source_urls": "|".join(p.get("sources") or []),
            "in_prices_json": "true" if c else "false",
            "from_model_type": c["from_model"]["type"] if c else "", "to_model_type": c["to_model"]["type"] if c else "",
            "from_model_params": model_params(c["from_model"]) if c else "", "to_model_params": model_params(c["to_model"]) if c else "",
            "assumption_count": len(p.get("assumptions") or []),
        })
        if c:
            for side_name, key in (("from", "from_model"), ("to", "to_model")):
                points.extend(price_rows(c, side_name, c[key]))
        for i, t in enumerate(p.get("assumptions") or []):
            assumptions.append({"slug": slug, "status": p["status"], "index": i, "text": t})
    calc = []
    for k in d["calculators"]:
        calc.extend(calculator_rows(k))

    # one row per official pricing-page URL, as the Price watch page counts them
    used = {}
    for slug in catc:
        for u in ps[slug].get("sources") or []:
            used.setdefault(u, []).append((slug, ps[slug]["checked_at"]))
    for k in d["calculators"]:
        for t in k["tools"]:
            if t.get("url"):
                used.setdefault(t["url"], []).append((k["slug"], k["checked_at"]))
    pages = []
    for u in sorted(used):
        slugs = sorted({s for s, _ in used[u]})
        dates = [x for _, x in used[u] if x]
        pages.append({"url": u, "vendor_key": vendor_key(u), "used_by_count": len(slugs), "used_by_slugs": "|".join(slugs),
                      "latest_checked_at": max(dates) if dates else ""})

    n1 = write("comparisons.csv", ["slug", "url", "from", "to", "page_from_name", "page_to_name", "category", "unit_metric",
                                   "status", "checked_at", "currency", "source_urls", "in_prices_json", "from_model_type",
                                   "to_model_type", "from_model_params", "to_model_params", "assumption_count"], comps)
    n2 = write("price_points.csv", ["slug", "side", "model_type", "row_kind", "row_index", "plan_or_tier_label",
                                    "limit_or_unit", "monthly_price", "annual_price_per_month", "base_fee_monthly",
                                    "unit_price", "currency", "checked_at", "extra"], points)
    n3 = write("assumptions.csv", ["slug", "status", "index", "text"], assumptions)
    n4 = write("calculator_plans.csv", ["calculator_slug", "status", "checked_at", "tool_id", "tool_name", "plan",
                                        "row_index", "currency", "monthly_price", "annual_price_per_month",
                                        "yearly_price", "one_time_price", "vat_removed", "source_url",
                                        "plan_other_fields", "tool_other_fields"], calc)
    n5 = write("pricing_pages.csv", ["url", "vendor_key", "used_by_count", "used_by_slugs", "latest_checked_at"], pages)
    print("comparisons.csv: %d rows (all comparisons; %d with price models in tiersova-prices.json)" % (n1, len(priced)))
    print("price_points.csv: %d rows" % n2)
    print("assumptions.csv: %d rows" % n3)
    print("calculator_plans.csv: %d rows (calculators: %d)" % (n4, len(d["calculators"])))
    print("pricing_pages.csv: %d rows (official pricing-page URLs), %d vendors" % (n5, len({r["vendor_key"] for r in pages})))
    print("languages: %d" % len(cat["languages"]))


if __name__ == "__main__":
    main()
