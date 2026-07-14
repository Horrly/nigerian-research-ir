# Nigerian Research IR

An information retrieval system for searching Nigerian university
research papers (undergraduate/masters/PhD theses and published
papers). Built as a CSC 522 course project to demonstrate a working
end-to-end search pipeline: a curated dataset, a Django + DRF backend
with TF-IDF ranked search, a React frontend, and a script for
quantitatively evaluating retrieval quality.

The dataset (`data/papers_dataset.csv`) contains 43 real research
records — titles, authors, university, department, degree type, year,
abstract, keywords, supervisor, and source URL — drawn from Nigerian
university repositories and academic profile pages.

## Tech stack

- **Backend:** Django 5, Django REST Framework, SQLite (dev database,
  deliberate choice for a short academic project — no external DB
  dependency), scikit-learn (TF-IDF + cosine similarity)
- **Frontend:** React 18, Vite, plain CSS (no framework)
- **Testing:** pytest, pytest-django
- **Tooling:** Python venv, npm

## Project layout

```
nigerian-research-ir/
├── backend/                    Django project ("irsystem")
│   ├── irsystem/                settings, URL routing
│   └── papers/                  the one app: models, admin, search, tests
│       ├── management/commands/ import_papers, evaluate_search
│       └── tests/
├── frontend/                   Vite + React search UI
├── data/
│   ├── papers_dataset.csv       43 seed records
│   └── test_queries.json        evaluation queries + ground truth
├── requirements.txt
└── README.md
```

## Setup

### Backend

```bash
python -m venv venv
venv\Scripts\activate          # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

cd backend
python manage.py migrate
python manage.py import_papers data/papers_dataset.csv
python manage.py createsuperuser
```

Run the dev server:

```bash
python manage.py runserver 0.0.0.0:8000
```

Binding to `0.0.0.0` (instead of the default `127.0.0.1`) makes the
backend reachable from other devices on the same LAN, not just this
machine — useful for demoing from a phone. `http://localhost:8000/api/health/`
and `http://localhost:8000/admin/` should both respond once it's up.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

`vite.config.js` sets `server.host = true`, so the terminal prints
both a **Local** URL (`http://localhost:5173`) and a **Network** URL
(e.g. `http://192.168.x.x:5173`). Open the Local URL on this machine,
or the Network URL from another device on the same Wi-Fi/LAN, to reach
the same running instance.

The frontend derives the backend's address from `window.location.hostname`
(see `frontend/src/config.js`) rather than hardcoding `localhost`, so
API calls automatically target whichever host served the page —
`localhost:8000` when opened locally, or `<LAN-IP>:8000` when opened
via the Network URL. Both dev servers must be running for search to
work.

### ⚠️ Local/LAN demo only — not production settings

To make the LAN setup above work, the backend runs with:

- `ALLOWED_HOSTS = ['*']` in `backend/irsystem/settings.py`
- `CORS_ALLOW_ALL_ORIGINS = True` in `backend/irsystem/settings.py`

Both are intentionally wide open for this short-lived local academic
demo. **Do not deploy this configuration as-is** — a real deployment
should set `ALLOWED_HOSTS` to specific hostnames and restrict CORS to
known frontend origins.

## Running tests

```bash
cd backend
python -m pytest -v
```

Covers: ranked search ordering and no-match handling, the basic search
endpoint, and the import command's duplicate-skipping and
validation-failure handling.

## Running the evaluation script

```bash
cd backend
python manage.py evaluate_search
```

This loads `data/test_queries.json` — 8 hand-picked queries, each with
a manually curated list of `relevant_ids` (the paper IDs a human judged
as actually relevant to that query) — and runs every query through
three search modes, printing **Precision@10**, **Recall**, and **F1**
per query plus an averaged row for each:

1. **Ranked search** — the TF-IDF + cosine similarity search used by
   the app.
2. **Basic search, phrase match** — the same `icontains` logic behind
   `/api/search-basic/`: the whole query must appear as one literal
   substring.
3. **Basic search, OR terms** — evaluation-only baseline that splits
   the query into words and matches if *any* word appears; not wired
   into the API, added to give phrase-match a fairer competitor.

Precision@10 divides by 10 regardless of how many results were
actually returned (the standard IR convention — missing slots count as
non-relevant), Recall divides by the size of the full `relevant_ids`
set, and F1 is their harmonic mean.

## Design notes: how the ranking works

Every paper's `title + abstract + keywords` is concatenated into one
text blob. Scikit-learn's `TfidfVectorizer` turns the whole collection
of blobs into vectors, where each word gets a weight that's high if it
appears often in *that* paper but rare across the *other* papers —
so distinctive terms ("bioinformatics", "gamification") count for more
than common ones ("research", "study", which are also stripped as
English stop words). A search query gets turned into a vector the same
way, and each paper is scored by the cosine similarity between its
vector and the query's — effectively, "how much does the angle between
this paper's word-weight profile and the query's word-weight profile
line up." Results are sorted by that score, and anything scoring
exactly zero (no shared vocabulary at all) is dropped.

The index (vectorizer + document vectors) is built once and cached in
memory, and only rebuilt if the row count or max ID in the database
changes — good enough for a small, mostly-static dataset, though it
won't notice an in-place edit to an existing paper's text without an
accompanying add/delete.

## Evaluation results

Run against 8 queries with hand-labeled ground truth
(`data/test_queries.json`):

```
RANKED SEARCH (TF-IDF cosine similarity)
Query                                        P@10   Recall       F1
-------------------------------------------------------------------
machine learning classification             0.500    0.833    0.625
intrusion detection network security        0.300    1.000    0.462
bioinformatics DNA sequence                  0.600    1.000    0.750
cybersecurity threat detection               0.400    1.000    0.571
information retrieval search ranking         0.300    0.750    0.429
healthcare medical diagnosis                 0.500    0.833    0.625
web application development                  0.300    1.000    0.462
text mining natural language processing      0.500    1.000    0.667
-------------------------------------------------------------------
AVERAGE                                      0.425    0.927    0.574

BASIC SEARCH - PHRASE MATCH (existing icontains behavior)
Query                                        P@10   Recall       F1
-------------------------------------------------------------------
machine learning classification             0.000    0.000    0.000
intrusion detection network security         0.000    0.000    0.000
bioinformatics DNA sequence                   0.000    0.000    0.000
cybersecurity threat detection                0.000    0.000    0.000
information retrieval search ranking          0.000    0.000    0.000
healthcare medical diagnosis                  0.000    0.000    0.000
web application development                   0.000    0.000    0.000
text mining natural language processing       0.000    0.000    0.000
-------------------------------------------------------------------
AVERAGE                                       0.000    0.000    0.000

BASIC SEARCH - OR TERMS (matches if any query word appears)
Query                                        P@10   Recall       F1
-------------------------------------------------------------------
machine learning classification             0.500    0.833    0.625
intrusion detection network security         0.300    1.000    0.462
bioinformatics DNA sequence                   0.600    1.000    0.750
cybersecurity threat detection                0.300    0.750    0.429
information retrieval search ranking          0.300    0.750    0.429
healthcare medical diagnosis                  0.500    0.833    0.625
web application development                   0.300    1.000    0.462
text mining natural language processing       0.500    1.000    0.667
-------------------------------------------------------------------
AVERAGE                                       0.412    0.896    0.556
```

**Interpretation:** phrase-match basic search scores 0 across the
board because none of these multi-word natural-language queries appear
verbatim as a single substring anywhere in the dataset — it's not a
bug, it's the actual failure mode of naive substring search on
realistic queries, and it's the reason `/api/search-basic/` isn't the
default experience in the frontend. OR-terms search, once given credit
for matching on individual words, closes almost all of that gap with
ranked TF-IDF (0.412 vs. 0.425 average precision, 0.896 vs. 0.927
recall) and even ties or matches it on 6 of the 8 queries. The one
query where ranked search pulls clearly ahead is "cybersecurity threat
detection" (F1 0.571 vs. 0.429), where TF-IDF's term weighting favors
papers that are substantively *about* those specific terms over ones
that merely mention a word in passing. That's the real, if modest,
value TF-IDF ranking adds here: retrieving roughly the same papers as
simple keyword matching, but ordering them by relevance instead of
leaving them unordered by database ID — the win is in ranking quality
metrics like these can't fully capture, not in raw recall.
