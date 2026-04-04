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

## Fotogalerie

Die Galerie zeigt Fotos unter `/gallery/`. Bilder werden als WebP komprimiert und mit EXIF-Metadaten angezeigt. Die Galerie unterstützt Kategorien und Filter-Tabs.

### Abhängigkeiten

- Python 3.8+
- Pillow
- PyYAML

Installation:
```bash
pip install Pillow pyyaml
# oder mit Nix:
nix-shell -p python3 python3Packages.pillow python3Packages.pyyaml
```

### Workflow: Neue Fotos hinzufügen

```bash
# 1. Bilder in photos/ ablegen
cp ~/Bilder/*.jpg photos/

# 2. Build-Script ausführen
nix-shell -p python3 python3Packages.pillow python3Packages.pyyaml --run 'python scripts/build-gallery.py'

# 3. Kategorien und Alt-Texte in _data/gallery.yml anpassen
#    (neue Bilder werden automatisch unter "Unkategorisiert" eingetragen)

# 4. Generierte Dateien committen
git add assets/gallery/ _data/gallery.yml
git commit -m "feat(gallery): add new photos"
git push
```

Das Script generiert:
- Thumbnails (400px, WebP) → `assets/gallery/thumbs/`
- Vollbilder (1200px, WebP) → `assets/gallery/full/`
- Metadaten → `assets/gallery/gallery.json`
- Kategorien → `_data/gallery.yml` (neue Bilder als "Unkategorisiert")

### Kategorien verwalten

Bilder werden in `_data/gallery.yml` kategorisiert:

```yaml
categories:
  - id: landschaften
    label:
      de: Landschaften
      en: Landscapes
    images:
      - file: DSF3502.webp
        alt:
          de: Bergpanorama im Schnee
          en: Mountain panorama in snow
```

Um ein Bild zu kategorisieren, verschiebe es von der "unkategorisiert"-Kategorie
in die gewünschte Kategorie und passe den Alt-Text an.

**Hinweis:** Die Originale in `photos/` werden nicht committed (siehe `.gitignore`).

## CI

Bei Pushes und Pull Requests auf `main` läuft ein Build inkl. HTMLProofer:

- `.github/workflows/ci.yml`
