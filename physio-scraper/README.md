# Swiss Physiotherapist Lead Scraper

Finds physiotherapy practices across German-speaking Switzerland, checks each
one's website, sorts them by web presence, drops the ones that already have a
modern site, and exports the rest to Excel for outreach.

Built it for my own web-design agency to find practices that need a new site.
Data comes from OpenStreetMap (free), with optional Google Places enrichment.

## Quick start

```bash
pip install -r requirements.txt
python physio_scraper.py
```

Output lands in `swiss_physio_leads.xlsx`. The run is resumable — it caches
progress in `physio_cache.sqlite`, so if it crashes or you stop it, just run it
again and it picks up where it left off. Use `--fresh` to ignore the cache.

## Options

```bash
python physio_scraper.py --help

  -o, --output FILE     Excel output file
  --cache FILE          SQLite cache file
  --fresh               ignore the cache, re-check every website
  --workers N           concurrent website checks (default 10)
  --cantons CH-ZH ...   ISO3166-2 canton codes to include
```

Example — just Zürich and Bern, fresh run:

```bash
python physio_scraper.py --cantons CH-ZH CH-BE --fresh -o zh_be.xlsx
```

## How it classifies

Each practice's site gets bucketed:

| Category         | Meaning                                                        | Kept?       |
|------------------|----------------------------------------------------------------|-------------|
| `no_website`     | no real site (social-only counts here) — **priority**          | yes         |
| `wix_wordpress`  | built on Wix / WordPress / Jimdo / Squarespace / Weebly / etc. | yes         |
| `outdated_basic` | has a site but old, thin, or unreachable                       | yes         |
| `full_website`   | modern and complete                                            | **dropped** |

The Excel file has a colour-coded **Leads** sheet (autofilter, frozen header)
and a **Summary** sheet with per-category counts.

## Honest expectations

- **Name, location, phone** — good coverage from OSM.
- **Email** — only scraped from a live site, so it's mostly empty for the
  no-website (priority) leads. Nothing online to pull from.
- **Owner** — best-effort from the site's Impressum, also sparse.
- **Coverage** — OSM won't have every practice. Enable Google Places to go wider.

## Google Places (optional, paid)

1. Create a project at https://console.cloud.google.com, enable **Places API**,
   create a key.
2. **Set a billing cap first** — a full sweep is a few thousand requests.
3. Provide the key via environment variable (never hardcode it):

```bash
export GOOGLE_API_KEY=your_key_here   # or copy .env.example to .env
python physio_scraper.py
```

Results merge and de-duplicate with the OSM ones.

## Tuning

In `physio_scraper.py`:

- `OUTDATED_THRESHOLD` — higher pushes borderline sites into `full_website`
  (dropped); lower keeps more as `outdated_basic`.
- `BUILDER_SIGNATURES` — add builders if you see ones being missed.
- `SOCIAL_DOMAINS` — what counts as "social only".

## A note on the data (Switzerland)

The scraped output contains real business contact data, so it's gitignored and
should stay private. B2B cold calling is allowed in Switzerland, but numbers
marked with `*` in the public directory must not be called for advertising, and
unsolicited cold emails are restricted under the UWG / revised FADP. Not legal
advice — verify before a campaign.
