# Seed prompt

> I sell into a distributed 3D-printing manufacturing network. Sellers list
> products, we route each order to the print farm nearest the customer, produce
> it locally under a QC pipeline, and ship domestically — which cuts delivery
> time, removes customs, and lets a seller sell into countries they cannot
> currently post to.
>
> Given `inputs/shops.csv` — Etsy shops selling 3D-printed products — find the
> shops whose **public buyer reviews** show they are hitting the limits of
> printing everything in one place.
>
> For each shop: gather public review evidence, match it against the pain
> taxonomy in `scripts/taxonomy.py`, score it with the rubric in the skill, and
> write `leads.md` containing a ranked table, a card for each top lead with
> quoted evidence (URL + retrieval date) and a drafted opener, and every
> rejected shop with the reason it was rejected.
>
> Never collect reviewer identity. Never invent evidence: if there is none, the
> shop scores low and the report says so. Run with `--limit 3` so a pass
> completes in under 75 seconds.
