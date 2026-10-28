#!/usr/bin/env python3
"""druginfo.py -- drug reference info from the FDA's openFDA API.

Free public API, no key: https://api.fda.gov/drug/...
Endpoints used:
  drug/label.json       -- approved label: indications, warnings, dosage
  drug/ndc.json         -- product NDC directory (brand, strengths, packages)
  drug/enforcement.json -- recalls and enforcement actions

REFERENCE ONLY. Nothing this script prints is medical advice.
READ-ONLY. Prints plain-language human-readable text.

Anonymous openFDA requests are limited to roughly 1,000 per day
(the count resets daily and the script uses one request per command).
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request

API = "https://api.fda.gov/drug"
UA = {"User-Agent": "muse-druginfo-skill/1.0"}
DISCLAIMER = ("Reference only: this is FDA label and recall text, "
              "not medical advice. Check anything consequential "
              "with a doctor or pharmacist.")


def fail(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def get(endpoint, search):
    # Keep literal "+OR+" separators unencoded (openFDA's query parser
    # needs them); only the search value itself is percent-encoded.
    # Returns None when the endpoint has no matching records (404).
    url = f"{API}/{endpoint}.json?search={search}&limit=1"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 429:
            fail("openFDA rate-limited us (429). Wait a bit and try again.")
        fail(f"openFDA returned HTTP {e.code}")
    except urllib.error.URLError as e:
        fail(f"could not reach openFDA ({e})")
    except ValueError:
        fail("openFDA did not return JSON")


def first(results):
    if not results:
        return None
    return results[0]


def clean(text):
    """Squash SPL whitespace and trim; keep output readable."""
    t = re.sub(r"\s+", " ", text).strip()
    return t


def section(value, maxlen=1200):
    """Label fields come back as lists of strings; join and trim."""
    if not value:
        return None
    t = clean(" ".join(value))
    if len(t) > maxlen:
        t = t[:maxlen].rstrip() + " [truncated; see full label]"
    return t


def nameq(name):
    """Build an OR query across brand and generic names.

    Only the value is percent-encoded (spaces -> +). The quoted-phrase
    markers and the +OR+ separator stay in openFDA's own syntax.
    """
    v = urllib.parse.quote_plus(name).replace("+", "%20")
    return f"openfda.brand_name%3A%22{v}%22+OR+openfda.generic_name%3A%22{v}%22"


def noresults():
    fail("no results (the FDA has no record matching that search)")


def cmd_label(args):
    q = nameq(args.name)
    r = first((get("label", q) or {}).get("results", []))
    if r is None:
        noresults()
    of = r.get("openfda", {})

    brand = ", ".join(of.get("brand_name", ["?"]))
    generic = ", ".join(of.get("generic_name", ["?"]))
    mfr = ", ".join(of.get("manufacturer_name", ["?"]))
    route = ", ".join(of.get("route", ["?"]))

    print(f"{brand} ({generic})")
    print(f"  maker: {mfr} | route: {route} | "
          f"label effective: {r.get('effective_time', '?')}")
    print()
    print("What it is for (indications):")
    ind = section(r.get("indications_and_usage"))
    print(f"  {ind if ind else 'not listed on this label'}")
    print()
    print("Warnings and cautions:")
    # Rx labels use warnings_and_cautions; OTC labels use warnings.
    w = section(r.get("warnings_and_cautions")) or section(r.get("warnings"))
    w = w and w[:2000] + (" [truncated; see full label]" if len(w) > 2000 else "")
    print(f"  {w if w else 'not listed on this label'}")
    print()
    print("Dosage and administration:")
    dose = section(r.get("dosage_and_administration"), maxlen=1600)
    print(f"  {dose if dose else 'not listed on this label'}")
    print()
    print(f"Note: {DISCLAIMER}")


def cmd_ndc(args):
    term = args.query
    if re.fullmatch(r"[\d-]+", term):
        # Try product NDC first, then package NDC (the number printed
        # on a bottle box), which lives inside the packaging list.
        r = first((get("ndc", f'product_ndc%3A%22{term}%22') or {})
                  .get("results", []))
        if r is None:
            r = first((get("ndc", f'packaging.package_ndc%3A%22{term}%22') or {})
                      .get("results", []))
        if r is None:
            noresults()
    else:
        v = urllib.parse.quote_plus(term).replace("+", "%20")
        q = f'brand_name%3A%22{v}%22+OR+generic_name%3A%22{v}%22'
        r = first((get("ndc", q) or {}).get("results", []))
        if r is None:
            noresults()

    print(f"{r.get('brand_name', '?')} ({r.get('generic_name', '?')})")
    print(f"  product NDC: {r.get('product_ndc', '?')}")
    print(f"  dosage form: {r.get('dosage_form', '?')}")
    print(f"  labeler: {r.get('labeler_name', '?')}")
    print(f"  marketed since: {r.get('marketing_start_date', '?')} "
          f"| finished product: {'yes' if r.get('finished') else 'unknown'}")
    ais = r.get("active_ingredients", [])
    for ai in ais:
        print(f"  ingredient: {ai.get('name', '?')} "
              f"({ai.get('strength', '?')})")
    pkgs = r.get("packaging", [])
    for p in pkgs[:5]:
        print(f"  package: {p.get('package_ndc', '?')} "
              f"-- {clean(p.get('description', ''))}")
    if len(pkgs) > 5:
        print(f"  ... and {len(pkgs) - 5} more package sizes")
    print()
    print(f"Note: {DISCLAIMER}")


def cmd_recalls(args):
    v = urllib.parse.quote_plus(args.name).replace("+", "%20")
    q = f'product_description%3A%22{v}%22+OR+openfda.brand_name%3A%22{v}%22'
    d = get("enforcement", q) or {}
    r = first(d.get("results", []))
    if r is None:
        noresults()

    print(f"Most recent recall: {r.get('recall_number', '?')}")
    print(f"  product: {clean(r.get('product_description', '?'))}")
    print(f"  reason: {clean(r.get('reason_for_recall', '?'))}")
    print(f"  classification: {r.get('classification', '?')} "
          f"| status: {r.get('status', '?')}")
    print(f"  recalled by: {clean(r.get('recalling_firm', '?'))}")
    print(f"  initiation date: {r.get('recall_initiation_date', '?')} "
          f"| reported: {r.get('report_date', '?')}")
    dist = clean(r.get("distribution_pattern", ""))
    if dist:
        print(f"  distribution: {dist}")
    total = d.get("meta", {}).get("results", {}).get("total")
    if total and total > 1:
        print(f"  (this is the most recent of {total} matching recalls)")
    print()
    print(f"Note: {DISCLAIMER}")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="Drug reference info from the FDA's free openFDA API. "
                    "Reference only, not medical advice.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("label", help="FDA label: what it does, warnings, dosage")
    p.add_argument("name", help="brand or generic name, e.g. 'ibuprofen'")

    p = sub.add_parser("ndc", help="NDC directory lookup by name or product NDC")
    p.add_argument("query", help="drug name or product NDC, e.g. 'ibuprofen' or '55513-810'")

    p = sub.add_parser("recalls", help="recalls for a drug by product name")
    p.add_argument("name", help="brand or generic name, e.g. 'ibuprofen'")

    args = ap.parse_args()
    try:
        {"label": cmd_label, "ndc": cmd_ndc, "recalls": cmd_recalls}[args.cmd](args)
    except BrokenPipeError:
        sys.exit(0)


if __name__ == "__main__":
    main()
