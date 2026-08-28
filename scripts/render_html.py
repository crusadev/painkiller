"""Render leads as a single self-contained HTML page.

No external assets: the jury laptop has no packages installed and the page must
open offline. Inline CSS, system fonts, no scripts.
"""
import html

CSS = '''
/* "Print job traveler" — a machine report interrupted by human voices.
   Machine values are monospace; buyer quotes are humanist sans, larger.
   System fonts only: this must render on a laptop with no network. */
:root{
  --sheet:#E9E5DC;      /* build plate */
  --sheet2:#F2EFE9;     /* card stock */
  --ink:#14161A;        /* machine ink */
  --ink2:#5C6169;       /* secondary */
  --rule:#C4BEB2;       /* hairline */
  --flag:#C63A16;       /* filament orange — the shortfall */
  --ok:#2A6152;         /* spruce — product quality */
  --stamp:#1C3D6E;      /* routing stamp */
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--sheet);color:var(--ink);font-family:var(--mono);
  font-size:14px;line-height:1.5;
  /* layer lines: the defining artifact of an FDM print */
  background-image:repeating-linear-gradient(to bottom,
    rgba(20,22,26,.035) 0 1px, transparent 1px 6px);}
.wrap{max-width:1000px;margin:0 auto;padding:0 28px 72px}

/* ---- job header: reads like a routing card ---- */
.head{border-bottom:2px solid var(--ink);padding:26px 0 12px;margin-bottom:0}
.head h1{font-family:var(--mono);font-size:15px;font-weight:700;letter-spacing:.16em;
  text-transform:uppercase;margin:0 0 14px}
.spec{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:2px 24px;
  font-size:11.5px;letter-spacing:.04em}
.spec div{border-top:1px solid var(--rule);padding:6px 0}
.spec b{display:block;color:var(--ink2);font-weight:400;text-transform:uppercase;
  letter-spacing:.1em;font-size:10px}

/* ---- thesis: the one idea, sized for a projector ---- */
.thesis{padding:44px 0 40px;border-bottom:1px solid var(--rule)}
.thesis p{font-family:var(--sans);font-size:clamp(24px,3.4vw,38px);line-height:1.22;
  font-weight:600;letter-spacing:-.02em;margin:0;max-width:22ch}
.thesis .num{font-family:var(--mono);font-weight:700;
  border-bottom:3px solid var(--flag);padding-bottom:1px}
.thesis .said{font-family:var(--sans);font-size:clamp(15px,1.6vw,18px);font-weight:400;
  color:var(--ink2);margin:20px 0 0;max-width:46ch;line-height:1.45}
.thesis .said em{font-style:normal;color:var(--ink);box-shadow:inset 0 -.5em 0 rgba(198,58,22,.14)}

/* ---- tally ---- */
.tally{display:flex;flex-wrap:wrap;gap:0 28px;padding:14px 0;border-bottom:2px solid var(--ink);
  font-size:12px;letter-spacing:.08em;text-transform:uppercase}
.tally span{color:var(--ink2)}
.tally b{color:var(--ink);font-size:15px;margin-right:5px}
.tally .hot b{color:var(--flag)}

/* ---- lead cards ---- */
h2{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink2);
  font-weight:400;margin:38px 0 14px}
.lead{background:var(--sheet2);border:1px solid var(--rule);border-left:3px solid var(--ink);
  padding:20px 22px;margin-bottom:12px}
.lead.hot{border-left-color:var(--flag)}
.ltop{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.rank{font-size:12px;color:var(--ink2);letter-spacing:.1em}
.lead h3{font-family:var(--mono);font-size:20px;font-weight:700;letter-spacing:-.01em;margin:0}
.tag{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  border:1px solid currentColor;padding:2px 7px;color:var(--ink2)}
.tag.hot{color:var(--flag)}
.sc{margin-left:auto;font-size:13px;color:var(--ink2);letter-spacing:.04em}
.route{font-size:11.5px;color:var(--ink2);letter-spacing:.06em;text-transform:uppercase;
  margin:9px 0 16px}
.route .o{color:var(--stamp);font-weight:700}

/* ---- signature: the gap drawn as two extruded layers ---- */
.gap{margin:0 0 16px}
.lay{display:flex;align-items:center;gap:12px;margin:4px 0;font-size:11px;
  letter-spacing:.08em;text-transform:uppercase}
.lay i{width:96px;flex:none;color:var(--ink2);font-style:normal}
.track{flex:1;height:12px;position:relative;background:
  repeating-linear-gradient(to bottom,rgba(20,22,26,.10) 0 1px,transparent 1px 3px);
  border-bottom:1px solid var(--rule)}
.fill{position:absolute;inset:0 auto 0 0;
  background:repeating-linear-gradient(to bottom,currentColor 0 2px,rgba(255,255,255,.35) 2px 3px)}
.lay.q{color:var(--ok)} .lay.s{color:var(--flag)}
.lay b{width:42px;text-align:right;flex:none;font-size:12.5px;color:var(--ink)}
.short{height:14px;position:relative;margin-left:108px;margin-right:54px}
.short span{position:absolute;top:0;bottom:0;border-left:1px solid var(--flag);
  border-right:1px solid var(--flag);
  background:repeating-linear-gradient(45deg,rgba(198,58,22,.16) 0 3px,transparent 3px 6px)}
.verdict{font-family:var(--sans);font-size:13.5px;color:var(--flag);margin:8px 0 0;font-weight:500}

/* ---- human voices ---- */
.said{font-family:var(--sans);font-size:15.5px;line-height:1.45;margin:14px 0 0;
  padding-left:14px;border-left:2px solid var(--rule)}
.said .attr{display:block;font-family:var(--mono);font-size:10.5px;color:var(--ink2);
  letter-spacing:.08em;text-transform:uppercase;margin-top:6px}
.said .attr a{color:var(--stamp)}
.none{font-family:var(--sans);font-size:14px;color:var(--ink2);margin:14px 0 0;
  padding-left:14px;border-left:2px dashed var(--rule)}
.opener{margin-top:16px;padding-top:12px;border-top:1px solid var(--rule)}
.opener i{display:block;font-style:normal;font-size:10px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink2);margin-bottom:6px}
.opener p{font-family:var(--sans);font-size:14px;line-height:1.45;margin:0}

/* ---- ranked table ---- */
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;font-weight:400;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink2);padding:7px 10px;border-bottom:1px solid var(--ink)}
td{padding:7px 10px;border-bottom:1px solid var(--rule)}
td a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}
.n{text-align:right;font-variant-numeric:tabular-nums}
tr.hot td:first-child{box-shadow:inset 2px 0 0 var(--flag)}
.foot{font-size:11.5px;color:var(--ink2);margin-top:16px;line-height:1.6;letter-spacing:.03em}
.foot a{color:var(--stamp)}
@media(max-width:640px){.wrap{padding:0 16px 48px}.lay i{width:70px}.short{margin-left:82px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
'''

def _layer(cls, label, value):
    pct = max(0.0, min((value - 4.15) / 0.85, 1.0)) * 100
    return (f'<div class="lay {cls}"><i>{label}</i>'
            f'<div class="track"><div class="fill" style="width:{pct:.1f}%"></div></div>'
            f'<b>{value:.2f}</b></div>')


def _shortfall(ship, qual):
    lo = max(0.0, min((ship - 4.15) / 0.85, 1.0)) * 100
    hi = max(0.0, min((qual - 4.15) / 0.85, 1.0)) * 100
    if hi <= lo:
        return ""
    return (f'<div class="short"><span style="left:{lo:.1f}%;width:{hi - lo:.1f}%"></span></div>')


def render(leads, meta, by_id):
    e = html.escape
    ranked = sorted(leads, key=lambda x: -x["score"])
    shown = [l for l in ranked if l["tier"] in ("hot", "watch")][:3]
    c = {t: sum(1 for l in leads if l["tier"] == t)
         for t in ("hot", "watch", "nurture", "pass")}

    P = ['<div class="wrap">']
    P.append('<div class="head"><h1>3DAPI &nbsp;·&nbsp; Fulfilment-pain lead qualification</h1>'
             '<div class="spec">'
             f'<div><b>Shops evaluated</b>{len(leads)}</div>'
             f'<div><b>Reviews read</b>{meta["reviews"]:,}</div>'
             f'<div><b>Evidence retrieved</b>{e(meta["date"])}</div>'
             f'<div><b>Data mode</b>{e(meta["mode"].split(",")[0])}</div>'
             f'<div><b>Storefronts found</b>{meta["links"]}</div>'
             '</div></div>')

    P.append('<div class="thesis"><p>All <span class="num">'
             f'{meta["signals"]}</span> fulfilment complaints across <span class="num">'
             f'{meta["reviews"]:,}</span> reviews sit in four- and five-star reviews.</p>'
             '<p class="said">Which is why this does not read star ratings. '
             '<em>&ldquo;It took about two months to arrive&rdquo;</em> &mdash; five stars, '
             'and the buyer recommends the shop. Filter on rating and you find nothing.</p></div>')

    P.append('<div class="tally">'
             f'<span class="hot"><b>{c["hot"]}</b>hot</span>'
             f'<span><b>{c["watch"]}</b>watch</span>'
             f'<span><b>{c["nurture"]}</b>tracked below floor</span>'
             f'<span><b>{c["pass"]}</b>rejected, with reasons</span></div>')

    P.append('<h2>Call these first</h2>')
    for i, l in enumerate(shown, 1):
        hot = " hot" if l["tier"] == "hot" else ""
        P.append(f'<div class="lead{hot}"><div class="ltop"><span class="rank">'
                 f'{i:02d}</span><h3>{e(l["shop"])}</h3>'
                 f'<span class="tag{hot}">{l["tier"]}</span>'
                 f'<span class="sc">{l["score"]}/100</span></div>')
        route = []
        if l.get("ships_from"):
            route.append(f'prints in <span class="o">{e(str(l["ships_from"]))}</span> '
                         f'&rarr; buyers largely US / UK')
        if l.get("sold_count"):
            route.append(f'{l["sold_count"]:,} sold')
        if l.get("ratio_per_year"):
            route.append(f'~{l["ratio_per_year"]:,} orders/yr')
        P.append(f'<div class="route">{" &nbsp;·&nbsp; ".join(route)}</div>')

        if l.get("shipping_rating") and l.get("quality_rating"):
            P.append('<div class="gap">')
            P.append(_layer("q", "item quality", l["quality_rating"]))
            P.append(_layer("s", "shipping", l["shipping_rating"]))
            P.append(_shortfall(l["shipping_rating"], l["quality_rating"]))
            P.append(f'<p class="verdict">Buyers rate the delivery '
                     f'{l["shipping_deficit"]:.2f} below the product. '
                     f'The print is fine. The distance is not.</p></div>')

        for ev in l["evidence"][:2]:
            txt = ev["text"].strip().replace("\n", " ")
            txt = txt[:200] + ("\u2026" if len(txt) > 200 else "")
            labels = ", ".join(by_id[s]["label"] for s in ev["signals"])
            src = f' &nbsp;·&nbsp; <a href="{e(ev["url"])}">listing</a>' if ev.get("url") else ""
            P.append(f'<p class="said">&ldquo;{e(txt)}&rdquo;<span class="attr">'
                     f'{ev.get("rating","?")}&#9733; &nbsp;·&nbsp; {e(str(ev.get("date","undated")))}'
                     f' &nbsp;·&nbsp; {e(labels)}{src}</span></p>')
        if not l["evidence"]:
            P.append('<p class="none">No buyer complaint quotes in the captured window. '
                     'This shop qualifies on shop-level evidence only, and the opener says so.</p>')
        P.append(f'<div class="opener"><i>drafted opener</i><p>{e(l["opener"])}</p></div></div>')

    P.append('<h2>Ranked</h2><table><tr><th class="n">#</th><th>Shop</th><th>Tier</th>'
             '<th class="n">Score</th><th>Prints in</th><th>Pain signals</th></tr>')
    for i, l in enumerate(ranked[:15], 1):
        sigs = ", ".join(by_id[s]["label"] for s in l["signals"]) or "&mdash;"
        cls = ' class="hot"' if l["tier"] == "hot" else ""
        P.append(f'<tr{cls}><td class="n">{i:02d}</td>'
                 f'<td><a href="{e(l["shop_url"])}">{e(l["shop"])}</a></td>'
                 f'<td>{l["tier"]}</td><td class="n">{l["score"]}</td>'
                 f'<td>{e(str(l.get("ships_from") or "&mdash;"))}</td><td>{sigs}</td></tr>')
    P.append('</table>')
    P.append(f'<p class="foot">{c["pass"]} shops rejected with a stated reason and '
             f'{c["nurture"]} tracked below the volume floor &mdash; all listed in '
             f'<a href="leads.md">leads.md</a>. Evidence is public Etsy review text with '
             f'source and retrieval date; reviewer and seller identity are never collected. '
             f'{e(meta["mode"])}.</p>')
    P.append('</div>')

    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>3DAPI \u2014 fulfilment-pain lead qualification</title><style>'
            + CSS + '</style></head><body>' + "".join(P) + '</body></html>')
