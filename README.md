# nicolin-dora.ch

Persönliche Website auf Basis von Jekyll (GitHub Pages kompatibel).

## Tech Stack

- Jekyll
- GitHub Pages Gems (`github-pages`)
- Liquid Templates (`_layouts`, `_includes`)
- Markdown Seiten und Posts (`_pages`, `_posts`)
- Zentrale CV-Datenquelle in JSON (`_data/cv.json`)

## Projektstruktur

- `_config.yml`: Jekyll-Konfiguration, Plugins, Site-Metadaten.
- `_pages/`: Statische Inhaltsseiten (z. B. About, CV, Projekte).
- `_posts/`: Blogposts.
- `_layouts/`: Seitenlayouts.
- `_includes/`: Wiederverwendbare Template-Teile.
- `_data/`: Strukturierte Inhalte (u. a. CV-Daten).
- `assets/`: CSS, Bilder, Downloads.

## Voraussetzungen

- Nix mit `nix-shell`

## Lokal testen

Im Repository-Root ausführen:

```bash
nix-shell -p ruby bundler --run 'bundle install && bundle exec jekyll serve --livereload --host 127.0.0.1 --port 4000'
```

Dann aufrufen:

- `http://127.0.0.1:4000/`
- `http://127.0.0.1:4000/cv/`

Server stoppen: `Ctrl + C`

## Build und Validierung

Lokaler Produktionsbuild:

```bash
nix-shell -p ruby bundler --run 'bundle install && bundle exec jekyll build --strict_front_matter'
```

Link- und HTML-Checks wie in CI:

```bash
nix-shell -p ruby bundler --run 'bundle install && bundle exec htmlproofer ./_site --assume-extension --enforce-https --check-internal-hash --disable-external'
```

## Inhaltspflege

- CV-Inhalte: `_data/cv.json`
- CV-Seite: `_pages/cv.md` + `_layouts/cv.html`
- About-Seite: `_pages/about.md`
- Navigation: `_data/navigation.yml`
- Styling: `assets/css/style.css`

## CI

Bei Pushes und Pull Requests auf `main` läuft ein Build inkl. HTMLProofer:

- `.github/workflows/ci.yml`
