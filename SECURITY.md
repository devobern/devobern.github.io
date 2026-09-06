---
title: Security Policy
lang: en
permalink: /SECURITY/
---

This site is built with Jekyll and deployed via GitHub Pages. The goal is to keep the attack surface minimal and the content trustworthy.

## Report a vulnerability

- Preferred: Email security@nicolin-dora.ch (PGP: /assets/files/pgp_nicolin_dora.asc)
- Alternative: Open a GitHub security advisory (private) on this repository.
- Please include reproduction steps, impact, and scope. We aim to respond within 7 days.

## Supported versions

This is a static site. We support the state of `main`. Historical builds are not maintained.

## Hardening choices

- Dependencies:
  - Use the `github-pages` gem to pin the GitHub‑vetted Jekyll and plugin set.
  - Dependabot enabled for Bundler and GitHub Actions.
- Build Safety:
  - GitHub Actions CI builds the site and runs HTMLProofer checks (broken links, HTTPS enforcement, missing anchors).
  - CodeQL enabled for Ruby/JS code.
- Content Security & Privacy:
  - CSP via `<meta http-equiv>` with tight defaults. We only allow minimal external origins (GoatCounter analytics, Giscus comments). Inline scripts and inline styles are avoided entirely, so `script-src`/`style-src` stay at `'self'` without `'unsafe-inline'`; redirects use `<meta http-equiv="refresh">`.
  - Third-party scripts are pinned: GoatCounter is loaded with Subresource Integrity. Giscus (`client.js`) is intentionally not pinned because upstream ships a mutable URL; it is confined by CSP to `giscus.app` and rendered inside an iframe.
  - Caveat: `Strict-Transport-Security` and `X-Content-Type-Options` are HTTP-header-only controls. The `<meta http-equiv>` variants in `_includes/head.html` document the intent but are ignored by browsers. HSTS is delivered by GitHub Pages when "Enforce HTTPS" is on; `nosniff` needs the proxy described under "Going further".
  - External links use `rel="noopener"` (and `noreferrer` where appropriate) in templates.
  - Referrer policy: `strict-origin-when-cross-origin`.
  - Analytics: GoatCounter, production only, no cookies; respects DNT.
- Disclosure:
  - `/.well-known/security.txt` points here.
- Hygiene:
  - `.gitignore` prevents publishing build artifacts and environment files.

## Operational guidance

- Enforce HTTPS in the repository settings (GitHub Pages -> Enforce HTTPS).
- Enable branch protection on `main`: require PR review, passing CI, and up‑to‑date with base.
- Secrets: Secret scanning (GitHub Advanced Security) should be enabled; avoid secrets in this repo.
- Workflows run with `permissions: contents: read`; do not widen this without a reason stated in the PR.

## Going further (optional)

GitHub Pages does not support setting server headers. If you need strict headers (HSTS preload, server‑enforced CSP/Permissions‑Policy), consider a CDN like Cloudflare or a reverse proxy. Then set headers like:

- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `Content-Security-Policy: (server‑side version of the meta tag)`
- `Permissions-Policy: geolocation=(), camera=(), microphone=()`

Document any allow‑listed domains and the reason in PRs.
