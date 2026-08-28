# Seed prompt

Paste this into Codex, as-is.

> Use `$etsy-fulfillment-leads` to run its **periodic stage** over the watchlist
> in `demo/input/watchlist.json`, using the company profile in
> `demo/input/profile.json`.
>
> I run outbound for a distributed 3D-printing manufacturing network. Sellers
> list products; we route each order to the print farm nearest the customer,
> produce it locally under QC, and ship domestically — which cuts delivery time,
> removes customs, and lets a seller reach countries they cannot currently post
> to.
>
> The profile already holds my triggers and thresholds from setup. Sweep every
> prospect on the watchlist, work out which ones have become interesting *since
> the last run*, and write `demo/output/radar.md`.
>
> For each prospect give me a **ripeness likelihood, not a yes/no** — how close
> they are to the moment their fulfilment stops working — with the drivers that
> produced that number, the buyer evidence where it exists, and an explicit note
> where it does not. List the prospects that are not ripe with the reason. End
> with the limitations of the run.
>
> Never invent evidence: if a prospect qualifies on published numbers alone, say
> so and lead with the numbers. Never collect reviewer identity. Run with no
> credentials against the committed snapshot, and finish in under 75 seconds.
