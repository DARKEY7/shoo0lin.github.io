# shoo0lin.github.io

Field notes on web security — client/server policy mismatches, cross-origin bugs,
and the seams where two components disagree about the same value.

## Stack

Plain static HTML + one CSS file. No build step, no framework, no trackers,
no external fonts. Served directly by GitHub Pages.

```
.
├── index.html                              # home / post index
├── posts/
│   └── interactivity-accordion.html        # WordPress Interactivity API XSS
├── assets/
│   ├── css/style.css
│   └── img/                                # lab screenshots (redacted)
├── .nojekyll                               # serve files as-is
└── README.md
```

## Local preview

```sh
python3 -m http.server 8000
# → http://127.0.0.1:8000/
```

## Adding a post

1. Copy `posts/interactivity-accordion.html` as a starting point.
2. Add a `<a class="card">` entry to `index.html`.
3. Keep the byline, the scope note, and the separation between proven impact
   and inferred impact intact.

## Content policy

- Only lab-verified or genuinely disclosed findings are published.
- Severity is computed from proven facts, never inflated.
- Screenshots are redacted for credentials and PII before commit.
