"""Run the three evaluation cases and print a pass/fail table."""
import json, os, pathlib, subprocess, sys, time

os.environ["QUALIFY_TODAY"] = "2026-08-28"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from qualify import score_shop, today  # noqa: E402

FIX = ROOT / "tests" / "fixtures"
load = lambda n: json.loads((FIX / n).read_text())
META = lambda s, r: {"shop": s, "shop_url": "https://example.invalid", "category": "lamp", "ratio_per_year": r}
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))


hot = score_shop(META("SyntheticHot", 3880), load("SYNTHETIC_hot.json"), today())
check("case 1 · qualifies as hot", hot["tier"] == "hot", f"tier={hot['tier']} score={hot['score']}")
check("case 1 · ≥3 distinct signals", len(hot["signals"]) >= 3, f"{hot['signals']}")
check("case 1 · geo_blocked detected", "geo_blocked" in hot["signals"])
check("case 1 · evidence is dated", all(e.get("date") for e in hot["evidence"]))

cold = score_shop(META("SyntheticPass", 900), load("SYNTHETIC_pass.json"), today())
check("case 2 · rejected", cold["tier"] == "pass", f"tier={cold['tier']} score={cold['score']}")
check("case 2 · rejection explained", bool(cold["reasons"]), "; ".join(cold["reasons"]))
check("case 2 · rubric discriminates ≥30", hot["score"] - cold["score"] >= 30,
      f"{hot['score']} vs {cold['score']}")

env = {k: v for k, v in os.environ.items() if k not in ("APIFY_TOKEN", "APIFY_ETSY_ACTOR")}
t0 = time.time()
p = subprocess.run([sys.executable, str(ROOT / "scripts" / "qualify.py"), "--limit", "3"],
                   capture_output=True, text=True, env=env, cwd=ROOT)
elapsed = time.time() - t0
snaps = list((ROOT / "fallback" / "snapshot").glob("*.json"))
if snaps:
    out = (ROOT / "leads.md").read_text()
    check("case 3 · runs with no token", p.returncode == 0, p.stderr.strip()[:120])
    check("case 3 · declares data mode", "committed snapshot" in out)
    check("case 3 · under 75s", elapsed < 75, f"{elapsed:.1f}s")
else:
    check("case 3 · refuses rather than fabricating",
          p.returncode != 0 and "no snapshots" in (p.stdout + p.stderr),
          "no snapshot committed yet — capture before submitting")

w = max(len(n) for n, _, _ in results)
for n, ok, d in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {n.ljust(w)}  {d}")
failed = sum(1 for _, ok, _ in results if not ok)
print("\nall green" if not failed else f"\n{failed} failing")
sys.exit(1 if failed else 0)
