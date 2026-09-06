# nicolin-dora.ch

Persönliche Website auf Basis von Jekyll (GitHub Pages kompatibel).

## Tech Stack

- Jekyll
- GitHub Pages Gems (`github-pages`)
- Liquid Templates (`_layouts`, `_includes`)
- Markdown Seiten und Posts (`_pages`, `_posts`)
- Zentrale CV-Datenquelle in JSON (`_data/cv/<lang>.json`)
- Mehrsprachigkeit (DE/EN) ohne Zusatz-Plugin, GitHub-Pages-kompatibel

## Projektstruktur

- `_config.yml`: Jekyll-Konfiguration, Plugins, Site-Metadaten.
- `_pages/`: Statische Inhaltsseiten (z. B. About, CV, Projekte).
- `_posts/`: Blogposts.
- `_layouts/`: Seitenlayouts.
- `_includes/`: Wiederverwendbare Template-Teile.
- `_data/`: Strukturierte Inhalte (CV-Daten, UI-Übersetzungen, Navigation).
- `assets/`: CSS, JavaScript, Bilder, Downloads.

## Mehrsprachigkeit (DE/EN)

Die Website ist zweisprachig. Deutsch liegt auf den bestehenden Root-URLs,
Englisch unter `/en/`. Es wird kein zusätzliches Plugin verwendet, damit der
Build GitHub-Pages-kompatibel bleibt.

### Wie es funktioniert

| Baustein | Zweck |
| --- | --- |
| `_config.yml` (`default_lang`, `languages`) | Registrierte Sprachen; `default_lang` liegt auf `/` |
| `_data/i18n.yml` | Alle UI-Texte pro Sprache |
| `_data/navigation.yml` | Navigationstitel und -URLs pro Sprache |
| `_includes/i18n.html` | Setzt `page_lang` und `t` (Übersetzungstabelle) |
| `_includes/lang-alternates.html` | Sprachumschalter (`mode="nav"`) und `hreflang`-Links (`mode="head"`) |
| Front Matter `lang:` / `ref:` | `lang` = Sprache der Seite, `ref` = sprachübergreifende ID |

Zwei Seiten gelten als Übersetzungen voneinander, wenn sie dasselbe `ref`
tragen. Daraus entstehen automatisch der Sprachumschalter im Header, die
`hreflang`-Angaben im `<head>` und die Gruppierung im Blog-Index.

### Neue Seite anlegen

```markdown
---
permalink: /neue-seite/
title: Neue Seite
lang: de
ref: neue-seite
---
```

```markdown
---
permalink: /en/new-page/
title: New page
lang: en
ref: neue-seite
---
```

Existiert eine Seite nur in einer Sprache, verlinkt der Umschalter auf die
Startseite der anderen Sprache; im Blog-Index wird der Beitrag mit einem
Sprach-Badge gekennzeichnet.

### Neuen Text im Template übersetzen

Keine Zeichenketten direkt ins Template schreiben. Stattdessen einen Key in
`_data/i18n.yml` für **alle** Sprachen ergänzen und im Template `{{ t.key }}`
verwenden. Für JavaScript werden die Texte als `data-*`-Attribute übergeben
(siehe `_includes/gallery.html`), weil die CSP keine Inline-Skripte erlaubt.

### URLs, die nicht gebrochen werden dürfen

Feeds: `/feed.de.xml` und `/feed.en.xml` enthalten nur die Beiträge der jeweiligen
Sprache und werden im `<head>` passend verlinkt. Der kombinierte Feed von
jekyll-feed bleibt für bestehende Abos unter `/feed.xml` erreichbar.

Bereits veröffentlichte englische URLs bleiben über kleine Weiterleitungsseiten
erreichbar (`_pages/*-legacy.md`, Front Matter `redirect:`). Bei Giscus sorgt
`giscus_term:` dafür, dass bestehende Kommentar-Threads erhalten bleiben, auch
wenn sich die URL ändert.

## Kopfzeile und Navigation

Ab dem Umbruchpunkt `--nav-breakpoint` (siehe `assets/css/style.css`, aktuell
48rem) klappt die Hauptnavigation in ein Hamburger-Menü. `assets/js/nav.js`
liest denselben Wert aus, damit CSS und JavaScript nicht auseinanderlaufen.

Das Menü ist Progressive Enhancement: der Knopf trägt im HTML `hidden` und
wird erst von `nav.js` aktiviert. Ohne JavaScript bleibt die Navigation eine
gewöhnliche, sichtbare Liste. Das Panel schliesst per Escape, per Klick
ausserhalb und beim Wechsel auf Desktop-Breite; der Fokus wandert beim Öffnen
in die Liste und beim Schliessen zurück auf den Knopf.

Sprachumschalter und Theme-Umschalter liegen zusammen in `.site-controls`
rechts in der Kopfzeile, damit beide Einstellungen an einem Ort stehen.
Wird ein Navigationspunkt ergänzt, ist zu prüfen, ob die Kopfzeile in der
längeren Sprache (Deutsch) noch einzeilig bleibt; sonst muss
`--nav-breakpoint` steigen.

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

- CV-Inhalte: `_data/cv/de.json` und `_data/cv/en.json` (gleiche Struktur, gleiche `id`s)
- CV-Seite: `_pages/cv.md` / `_pages/cv-en.md` + `_layouts/cv.html`
- About-Seite: `_pages/about.md` / `_pages/about-en.md`
- Projekt-Links: `_data/projects.yml` (verknüpft über die CV-Item-`id`)
- UI-Texte: `_data/i18n.yml`
- Navigation: `_data/navigation.yml`
- Styling: `assets/css/style.css`

## Fotogalerie

Die Galerie zeigt Fotos unter `/gallery/`. Bilder werden als WebP komprimiert und mit EXIF-Metadaten angezeigt. Die Galerie unterstützt Kategorien und Filter-Tabs.

### Abhängigkeiten

- Python 3.8+
- Pillow
- PyYAML
- pillow-heif (optional, nur für HEIC/HEIF vom iPhone)

Installation:
```bash
pip install Pillow pyyaml pillow-heif
# oder mit Nix:
nix-shell -p python3 python3Packages.pillow python3Packages.pyyaml python3Packages.pillow-heif
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

### Upload direkt vom Smartphone

Für den Weg ohne Rechner gibt es `photos/incoming/`. Dieser Ordner ist als
einziger unterhalb von `photos/` versioniert, damit Bilder über die
GitHub-Weboberfläche hochgeladen werden können.

1. In Lightroom exportieren (siehe unten) und die Datei in *Dateien* bzw.
   *Files* ablegen, nicht in der Fotos-App lassen.
2. Auf github.com im Browser: `photos/incoming/` öffnen, *Add file →
   Upload files*, Datei aus *Dateien* wählen, direkt auf `main` committen.
3. `.github/workflows/gallery.yml` verarbeitet den Upload: Thumbnail,
   Vollbild mit Wasserzeichen, Metadaten, Eintrag in `_data/gallery.yml`.
   Anschliessend löscht die Action das Original wieder aus `photos/incoming/`
   und committet das Ergebnis nach `main`.
4. In `_data/gallery.yml` noch Kategorie und Alt-Text setzen (der
   Web-Editor von GitHub funktioniert auf dem Handy).

Der Copyright-String entsteht dabei genau wie beim lokalen Lauf im
Build-Script, das Wasserzeichen ist also identisch mit dem der übrigen Bilder.

**Lightroom-Export:** Als Metadaten *Alle* wählen, nicht *Nur Copyright*.
Sonst werden Kamera, Objektiv, Blende und ISO aus der Datei entfernt und die
Specs-Zeile in der Galerie bleibt leer. Lightrooms eigenes Wasserzeichen wird
nicht gebraucht, das setzt das Build-Script. Als Grösse genügt die lange Kante
mit rund 2048 px: die Galerie skaliert ohnehin auf 1200 px herunter, und das
Original landet mit dem Upload für immer in der Git-History.

**Ohne Netz oder für viele Bilder** bleibt der lokale Weg über `photos/` und
`python scripts/build-gallery.py` der schnellere.

**Warum `--merge` im Workflow:** Auf dem Runner liegt nur das frisch
hochgeladene Original, alle übrigen liegen lokal. Ohne `--merge` würde
`gallery.json` auf dieses eine Bild zusammenschrumpfen. Mit `--merge` bleiben
die Einträge früherer Läufe erhalten, solange ihr WebP noch im Repository
liegt.

### Fotos vom Smartphone

Dieser Abschnitt gilt für Fotos, die mit dem Handy aufgenommen wurden,
unabhängig vom Upload-Weg.

Smartphone-Fotos laufen durch denselben Weg wie Fotos aus der Systemkamera:
ins `photos/`-Verzeichnis legen, `build-gallery.py` ausführen. Wasserzeichen
(`© <Aufnahmejahr> Nicolin Dora`) und Specs-Zeile entstehen automatisch, sofern
die EXIF-Daten im Original noch vorhanden sind.

**Übertragung, die EXIF erhält:** USB-Kabel, AirDrop, SD-Karte, Nextcloud/Syncthing,
Google Fotos (Download des Originals), iCloud Fotos. Bei iOS beim Teilen unter
"Optionen" *Alle Fotodaten* aktiviert lassen.

**Übertragung, die EXIF entfernt:** WhatsApp, Signal, Telegram (als "Bild" statt
"Datei"), Instagram, die meisten Web-Uploads. Danach fehlen Kameradaten
vollständig, und das Wasserzeichen nutzt das Datei-Datum statt des
Aufnahmedatums. Das Script weist beim Build darauf hin.

**HEIC vom iPhone:** wird nur mit installiertem `pillow-heif` verarbeitet, sonst
meldet das Script die übersprungenen Dateien. Alternativ am iPhone unter
*Einstellungen → Kamera → Formate* auf *Maximale Kompatibilität* stellen, dann
nimmt das Gerät JPEG auf.

**Kameraname:** Viele Android-Geräte schreiben nur den Modellcode ins EXIF
(z. B. `SM-S928B`). Für einen lesbaren Namen einen Eintrag in `CAMERA_NAMES`
in `scripts/build-gallery.py` ergänzen:

```python
CAMERA_NAMES = {
    "SM-S928B": "Samsung Galaxy S24 Ultra",
}
```

**Brennweite:** Handy-Objektive sind physikalisch sehr kurz. Steht das
Kleinbild-Äquivalent im EXIF, wird es ergänzt: `6.8mm (≙ 24mm)`. Das gilt auch
für die APS-C-Aufnahmen (`23mm (≙ 35mm)`); die Angaben aktualisieren sich beim
nächsten Build-Lauf.

## CI

Bei Pushes und Pull Requests auf `main` läuft ein Build inkl. HTMLProofer:

- `.github/workflows/ci.yml` (läuft mit `permissions: contents: read`)
- `.github/workflows/codeql.yml`

Dazu kommt `.github/workflows/gallery.yml`: Er läuft nur bei Änderungen unter
`photos/incoming/` und braucht als einziger Workflow `contents: write`, weil er
die generierten Galeriedateien nach `main` zurückschreibt.

## Sicherheit

Siehe [SECURITY.md](SECURITY.md) für Meldewege, die CSP und die bewusst
getroffenen Härtungsmassnahmen.
