# Stage-3 Freshness Review — Archived-Sourced Rows

**Reviewed:** 2026-08-10 · **Scope:** `leads/leads.csv` rows with `source_url` containing `web.archive.org` (b8/b9 archived harvests). **Annotation only — no rows deleted.**

## Method

- MX record resolution + A/AAAA liveness per unique domain (`dns.resolver`).
- `current`: domain live + MX resolvable · `refresh-needed`: domain live but MX not resolvable · `stale`: domain not resolving.
- Every archived address carries a caveat: archived snapshot + re-verify against the live site before outreach (archived data may be years old).

## Summary

| Status | Rows |
|---|---|
| current | 16 |
| refresh-needed | 0 |
| stale | 0 |

## Per-domain verdicts

| Domain | Live | MX | Verdict |
|---|---|---|---|
| sterke.dk | True | True | current |
| willo.se | True | True | current |

## Per-row annotations

| Email | Company | Domain | Archive date | Status |
|---|---|---|---|---|
| lbo@sterke.dk | Sterke A/S | sterke.dk | 2023-12-02 | current |
| henrik.wolf@willo.se | Willo | willo.se | 2019-04-23 | current |
| jenny.kejder@willo.se | Willo | willo.se | 2019-04-23 | current |
| johan.backgard@willo.se | Willo | willo.se | 2019-04-23 | current |
| johan.blomster@willo.se | Willo | willo.se | 2019-04-23 | current |
| johan.skandevall@willo.se | Willo | willo.se | 2019-04-23 | current |
| marcus.johansson@willo.se | Willo | willo.se | 2019-04-23 | current |
| marcus.magnusson@willo.se | Willo | willo.se | 2019-04-23 | current |
| peter.grahn@willo.se | Willo | willo.se | 2019-04-23 | current |
| peter.hultkvist@willo.se | Willo | willo.se | 2019-04-23 | current |
| petra.kjellsson@willo.se | Willo | willo.se | 2019-04-23 | current |
| roland.engnell@willo.se | Willo | willo.se | 2019-04-23 | current |
| sofia.gustavsson@willo.se | Willo | willo.se | 2019-04-23 | current |
| svante.johansson@willo.se | Willo | willo.se | 2019-04-23 | current |
| mail@willo.se | Willo | willo.se | 2019-04-23 | current |
| hr@sterke.dk | Sterke A/S | sterke.dk | 2023-12-02 | current |

Full note field per row: `leads/freshness-annotations.csv`.
