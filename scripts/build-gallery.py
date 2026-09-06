#!/usr/bin/env python3
"""
Galerie-Build-Script für GitHub Pages.

Verarbeitet Bilder aus photos/ und generiert:
- Thumbnails (max 400px Breite, WebP Q80) in assets/gallery/thumbs/
- Vollbilder (max 1200px Breite, WebP Q85) in assets/gallery/full/
- Metadaten (EXIF) in assets/gallery/gallery.json
- Aktualisiert _data/gallery.yml mit neuen Bildern (Kategorie: Unkategorisiert)

Abhängigkeiten:
- Python 3.8+
- Pillow: pip install Pillow
  oder: nix-shell -p python3 python3Packages.pillow
- PyYAML: pip install pyyaml
  oder: nix-shell -p python3 python3Packages.pillow python3Packages.pyyaml
- pillow-heif (optional, nur für HEIC/HEIF vom iPhone):
  pip install pillow-heif
  oder: nix-shell -p python3 python3Packages.pillow python3Packages.pillow-heif

Verwendung:
    python scripts/build-gallery.py

Das Script ist idempotent: bereits verarbeitete Bilder werden übersprungen,
es sei denn, das Original ist neuer als die generierte Version.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("Fehler: Pillow nicht installiert.")
    print("Installation: pip install Pillow")
    print("Oder mit Nix: nix-shell -p python3 python3Packages.pillow")
    sys.exit(1)

# HEIC/HEIF (iPhone-Standardformat) nur, wenn pillow-heif vorhanden ist
try:
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False

# Konfiguration
PHOTOS_DIR = Path("photos")
THUMBS_DIR = Path("assets/gallery/thumbs")
FULL_DIR = Path("assets/gallery/full")
JSON_PATH = Path("assets/gallery/gallery.json")
YAML_PATH = Path("_data/gallery.yml")

THUMB_MAX_WIDTH = 400
FULL_MAX_WIDTH = 1200
THUMB_QUALITY = 80
FULL_QUALITY = 85

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
HEIF_EXTENSIONS = {".heic", ".heif"}

# Herstellernamen, wie sie im EXIF stehen, in eine lesbare Schreibweise bringen.
# Schlüssel immer kleingeschrieben.
MAKE_NAMES = {
    "apple": "Apple",
    "canon": "Canon",
    "fujifilm": "FUJIFILM",
    "google": "Google",
    "huawei": "Huawei",
    "nikon corporation": "Nikon",
    "olympus corporation": "Olympus",
    "olympus imaging corp.": "Olympus",
    "oneplus": "OnePlus",
    "panasonic": "Panasonic",
    "samsung": "Samsung",
    "sony": "Sony",
    "xiaomi": "Xiaomi",
}

# Smartphones schreiben oft nur den internen Modellcode ins EXIF
# (z. B. "SM-S928B"). Hier lässt sich ein Anzeigename hinterlegen:
#     "SM-S928B": "Samsung Galaxy S24 Ultra",
CAMERA_NAMES = {}

# Wasserzeichen-Konfiguration
WATERMARK_AUTHOR = "Nicolin Dora"
WATERMARK_OPACITY = 0.7  # 70%
WATERMARK_MARGIN = 20  # Pixel vom Rand
WATERMARK_FONT_RATIO = 0.012  # Schriftgrösse relativ zur Bilddiagonale


def sanitize_filename(name: str) -> str:
    """
    Entfernt führende Unterstriche aus Dateinamen.
    Jekyll ignoriert Dateien, die mit _ beginnen.
    """
    return name.lstrip("_")


def format_camera_name(make: str, model: str) -> str:
    """
    Baut einen lesbaren Kameranamen aus Hersteller und Modell.
    Smartphones schreiben den Hersteller oft klein ("samsung") und das
    Modell als Code; beides lässt sich über MAKE_NAMES/CAMERA_NAMES glätten.
    """
    model = CAMERA_NAMES.get(model, model)
    make = MAKE_NAMES.get(make.lower(), make)

    if not make:
        return model
    if not model:
        return make
    # Vermeidet Duplikate wie "Canon Canon EOS R5" oder "Apple Apple iPhone"
    if model.lower().startswith(make.lower()):
        return model
    return f"{make} {model}"


def clean_lens_name(lens: str, camera: str) -> str:
    """
    Räumt Objektivnamen von Smartphones auf.

    Diese wiederholen den Kameranamen und hängen die physikalischen Daten an,
    z. B. "iPhone 15 Pro back triple camera 6.765mm f/1.78". Beides steht
    ohnehin schon in der Specs-Zeile, deshalb bleibt nur "Back Triple Camera".
    Objektivnamen von Systemkameras ("XF23mmF2 R WR") bleiben unverändert.
    """
    # Angehängte Brennweite/Blende entfernen
    lens = re.sub(r"\s*\d+(\.\d+)?\s*mm\s*f/?\d+(\.\d+)?\s*$", "", lens, flags=re.IGNORECASE)
    # Vorangestellten Kameranamen entfernen (Modell und Modell ohne Hersteller),
    # längster Treffer zuerst
    prefixes = sorted({camera, camera.split(" ", 1)[-1]} - {""}, key=len, reverse=True)
    for prefix in prefixes:
        if lens.lower().startswith(prefix.lower()):
            lens = lens[len(prefix):]
            break
    lens = " ".join(lens.split())
    # Rein kleingeschriebene Beschreibungen ("back triple camera") aufwerten,
    # Produktnamen mit Grossbuchstaben aber unangetastet lassen
    if lens and not any(c.isupper() for c in lens):
        lens = lens.title()
    return lens


def format_lens_name(lens: str) -> str:
    """
    Formatiert Objektivnamen lesbarer.
    z.B. "XF18-55mmF2.8-4 R LM OIS" → "XF 18-55mm F2.8-4 R LM OIS"
    """
    # Abstand zwischen Buchstaben und Zahlen am Anfang (XF18 → XF 18)
    lens = re.sub(r'^([A-Za-z]+)(\d)', r'\1 \2', lens)
    # Abstand vor F-Zahl wenn direkt nach mm (55mmF2.8 → 55mm F2.8)
    lens = re.sub(r'(mm)(F\d)', r'\1 \2', lens)
    return lens


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Lädt eine passende Schriftart."""
    # Versuche gängige System-Schriften
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "C:/Windows/Fonts/arial.ttf",  # Windows
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # Fallback: Default-Schrift
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Ältere Pillow-Versionen
        return ImageFont.load_default()


def add_watermark(image: Image.Image, year: int) -> Image.Image:
    """
    Fügt ein Wasserzeichen unten rechts hinzu.
    Format: © {year} {author}
    """
    import math

    # Kopie erstellen
    watermarked = image.copy()

    # Text
    text = f"© {year} {WATERMARK_AUTHOR}"

    # Schriftgrösse relativ zur Diagonale (ergibt konsistente Grösse bei Darstellung)
    diagonal = math.sqrt(image.width ** 2 + image.height ** 2)
    font_size = max(12, int(diagonal * WATERMARK_FONT_RATIO))
    font = get_font(font_size)

    # Overlay für Transparenz erstellen
    txt_layer = Image.new("RGBA", watermarked.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Textgrösse ermitteln
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position: unten rechts mit Margin
    x = image.width - text_width - WATERMARK_MARGIN
    y = image.height - text_height - WATERMARK_MARGIN

    # Halbtransparenter Schatten für bessere Lesbarkeit
    shadow_opacity = int(255 * WATERMARK_OPACITY * 0.7)
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, shadow_opacity))

    # Weisser Text
    text_opacity = int(255 * WATERMARK_OPACITY)
    draw.text((x, y), text, font=font, fill=(255, 255, 255, text_opacity))

    # Overlay auf Bild anwenden
    if watermarked.mode != "RGBA":
        watermarked = watermarked.convert("RGBA")
    watermarked = Image.alpha_composite(watermarked, txt_layer)

    # Zurück zu RGB für WebP
    return watermarked.convert("RGB")


def read_exif(image: Image.Image) -> dict:
    """
    Liest die EXIF-Tags eines Bildes als {Tagname: Wert}.

    Nutzt bewusst die öffentliche getexif()-API statt des privaten
    _getexif(): HEIC/HEIF-Dateien (iPhone) kennen _getexif() nicht.
    Aufnahmedaten wie Blende oder Brennweite stehen in der Exif-Unter-IFD
    und werden hier mit der Haupt-IFD zusammengeführt.
    """
    try:
        exif = image.getexif()
    except Exception:
        return {}

    if not exif:
        return {}

    tags = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif.items()}

    try:
        # 0x8769 = ExifOffset, die Unter-IFD mit den Aufnahmeparametern
        for tag_id, value in exif.get_ifd(0x8769).items():
            tags[TAGS.get(tag_id, tag_id)] = value
    except Exception:
        pass

    return tags


def get_exif_data(image: Image.Image) -> dict:
    """Extrahiert relevante EXIF-Daten aus einem Bild."""
    exif_data = {}

    try:
        exif_readable = read_exif(image)
        if not exif_readable:
            return exif_data

        # Kamera
        make = str(exif_readable.get("Make", "")).strip()
        model = str(exif_readable.get("Model", "")).strip()
        camera = format_camera_name(make, model)
        if camera:
            exif_data["camera"] = camera

        # Objektiv
        lens = exif_readable.get("LensModel", "")
        if lens:
            lens = clean_lens_name(str(lens).strip(), camera)
            if lens:
                exif_data["lens"] = format_lens_name(lens)

        # Datum
        date_str = exif_readable.get("DateTimeOriginal") or exif_readable.get("DateTime")
        if date_str:
            try:
                dt = datetime.strptime(str(date_str), "%Y:%m:%d %H:%M:%S")
                exif_data["date"] = dt.isoformat()
                exif_data["date_display"] = dt.strftime("%d.%m.%Y")
            except ValueError:
                pass

        # Blende
        fnumber = exif_readable.get("FNumber")
        if fnumber:
            try:
                if hasattr(fnumber, "numerator"):
                    f = fnumber.numerator / fnumber.denominator
                else:
                    f = float(fnumber)
                exif_data["aperture"] = f"f/{f:.1f}"
            except (TypeError, ZeroDivisionError):
                pass

        # Belichtungszeit
        exposure = exif_readable.get("ExposureTime")
        if exposure:
            try:
                if hasattr(exposure, "numerator"):
                    num, den = exposure.numerator, exposure.denominator
                    if num >= den:
                        exif_data["shutter"] = f"{num/den:.1f}s"
                    else:
                        exif_data["shutter"] = f"1/{int(den/num)}s"
                else:
                    exif_data["shutter"] = f"{float(exposure)}s"
            except (TypeError, ZeroDivisionError):
                pass

        # ISO (je nach EXIF-Version unter verschiedenen Namen)
        iso = (
            exif_readable.get("ISOSpeedRatings")
            or exif_readable.get("PhotographicSensitivity")
            or exif_readable.get("RecommendedExposureIndex")
        )
        if iso:
            if isinstance(iso, tuple):
                iso = iso[0]
            exif_data["iso"] = f"ISO {iso}"

        # Brennweite. Smartphone-Objektive sind physikalisch sehr kurz
        # (z. B. 6.8mm), deshalb wird das Kleinbild-Äquivalent ergänzt,
        # sobald es im EXIF steht und nennenswert abweicht.
        focal = exif_readable.get("FocalLength")
        if focal:
            try:
                if hasattr(focal, "numerator"):
                    mm = focal.numerator / focal.denominator
                else:
                    mm = float(focal)
                display = f"{mm:.1f}mm".replace(".0mm", "mm")

                equivalent = exif_readable.get("FocalLengthIn35mmFilm")
                if equivalent:
                    if hasattr(equivalent, "numerator"):
                        equivalent = equivalent.numerator / equivalent.denominator
                    equivalent = float(equivalent)
                    if equivalent > 0 and abs(equivalent - mm) >= 1:
                        display = f"{display} (≙ {equivalent:.0f}mm)"

                exif_data["focal_length"] = display
            except (TypeError, ValueError, ZeroDivisionError):
                pass

    except Exception as e:
        print(f"  Warnung: EXIF-Extraktion fehlgeschlagen: {e}")

    return exif_data


def get_image_date(image: Image.Image, filepath: Path) -> datetime:
    """Ermittelt das Aufnahmedatum für die Sortierung."""
    try:
        exif_readable = read_exif(image)
        date_str = exif_readable.get("DateTimeOriginal") or exif_readable.get("DateTime")
        if date_str:
            return datetime.strptime(str(date_str), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    # Fallback: Datei-Änderungszeit
    return datetime.fromtimestamp(filepath.stat().st_mtime)


def warn_missing_exif(source: Path, exif: dict) -> None:
    """
    Weist darauf hin, wenn ein Bild ohne EXIF ankommt.

    Typisch für Fotos, die über Messenger oder soziale Netzwerke geschickt
    wurden: dort werden die Metadaten beim Upload entfernt. Ohne EXIF fehlen
    die Kameradaten in der Galerie, und das Jahr im Wasserzeichen stammt dann
    aus dem Datei-Änderungsdatum statt aus dem Aufnahmedatum.
    """
    if exif:
        if "date" not in exif:
            print(f"    Hinweis: kein Aufnahmedatum in {source.name}, "
                  f"Wasserzeichen nutzt das Datei-Datum")
        return

    print(f"    Hinweis: keine EXIF-Daten in {source.name} - keine Kameradaten "
          f"in der Galerie, Wasserzeichen nutzt das Datei-Datum")
    print("    (Original direkt vom Gerät kopieren, nicht über Messenger senden)")


def needs_processing(source: Path, target: Path) -> bool:
    """Prüft, ob das Bild (neu) verarbeitet werden muss."""
    if not target.exists():
        return True
    return source.stat().st_mtime > target.stat().st_mtime


def process_image(source: Path) -> dict | None:
    """
    Verarbeitet ein einzelnes Bild.
    Gibt die Metadaten zurück oder None bei Fehler.
    """
    # Führende Unterstriche entfernen (Jekyll ignoriert _-Dateien)
    safe_stem = sanitize_filename(source.stem)
    thumb_path = THUMBS_DIR / f"{safe_stem}.webp"
    full_path = FULL_DIR / f"{safe_stem}.webp"

    # Prüfen, ob Verarbeitung nötig ist
    needs_thumb = needs_processing(source, thumb_path)
    needs_full = needs_processing(source, full_path)

    if not needs_thumb and not needs_full:
        print(f"  Übersprungen (aktuell): {source.name}")
        # Trotzdem Metadaten laden für gallery.json
        try:
            with Image.open(source) as img:
                img_date = get_image_date(img, source)
                exif = get_exif_data(img)
                warn_missing_exif(source, exif)
                return {
                    "filename": safe_stem,
                    "thumb": f"/assets/gallery/thumbs/{safe_stem}.webp",
                    "full": f"/assets/gallery/full/{safe_stem}.webp",
                    "date_sort": img_date.isoformat(),
                    "exif": exif
                }
        except Exception as e:
            print(f"  Fehler beim Lesen: {source.name}: {e}")
            return None

    print(f"  Verarbeite: {source.name}")

    try:
        with Image.open(source) as img:
            # EXIF-Orientierung korrigieren
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # In RGB konvertieren (für WebP)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Metadaten extrahieren
            # Muss vor dem Resize passieren, da EXIF dabei verloren geht
            original_img = Image.open(source)
            exif_data = get_exif_data(original_img)
            img_date = get_image_date(original_img, source)
            original_img.close()
            warn_missing_exif(source, exif_data)

            # Thumbnail erstellen
            if needs_thumb:
                thumb = img.copy()
                thumb.thumbnail((THUMB_MAX_WIDTH, THUMB_MAX_WIDTH * 10), Image.Resampling.LANCZOS)
                thumb.save(thumb_path, "WEBP", quality=THUMB_QUALITY)
                print(f"    → Thumbnail: {thumb_path}")

            # Vollbild erstellen (mit Wasserzeichen)
            if needs_full:
                full = img.copy()
                if full.width > FULL_MAX_WIDTH:
                    ratio = FULL_MAX_WIDTH / full.width
                    new_height = int(full.height * ratio)
                    full = full.resize((FULL_MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                # Wasserzeichen hinzufügen
                photo_year = img_date.year
                full = add_watermark(full, photo_year)
                full.save(full_path, "WEBP", quality=FULL_QUALITY)
                print(f"    → Vollbild: {full_path} (mit Wasserzeichen)")

            return {
                "filename": safe_stem,
                "thumb": f"/assets/gallery/thumbs/{safe_stem}.webp",
                "full": f"/assets/gallery/full/{safe_stem}.webp",
                "date_sort": img_date.isoformat(),
                "exif": exif_data
            }

    except Exception as e:
        print(f"  Fehler: {source.name}: {e}")
        return None


def load_gallery_yaml() -> dict:
    """Lädt die bestehende gallery.yml oder gibt eine leere Struktur zurück."""
    if not YAML_PATH.exists():
        return {"categories": []}

    if yaml is None:
        print("  Warnung: PyYAML nicht installiert, gallery.yml wird nicht aktualisiert.")
        print("  Installation: pip install pyyaml")
        return None

    try:
        with open(YAML_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data else {"categories": []}
    except Exception as e:
        print(f"  Warnung: gallery.yml konnte nicht gelesen werden: {e}")
        return {"categories": []}


def get_categorized_files(gallery_data: dict) -> set:
    """Gibt alle bereits kategorisierten Dateinamen zurück."""
    files = set()
    for category in gallery_data.get("categories", []):
        for image in category.get("images", []):
            files.add(image.get("file", ""))
    return files


def update_gallery_yaml(processed_files: list[str]) -> int:
    """
    Aktualisiert gallery.yml mit neuen Bildern.
    Neue Bilder werden zur Kategorie 'Unkategorisiert' hinzugefügt.
    Gibt die Anzahl neuer Bilder zurück.
    """
    if yaml is None:
        return 0

    gallery_data = load_gallery_yaml()
    if gallery_data is None:
        return 0

    categorized = get_categorized_files(gallery_data)

    # Finde neue Bilder
    new_files = []
    for filename in processed_files:
        webp_name = f"{filename}.webp"
        if webp_name not in categorized:
            new_files.append(webp_name)

    if not new_files:
        return 0

    # Finde oder erstelle die "Unkategorisiert"-Kategorie
    uncategorized = None
    for category in gallery_data.get("categories", []):
        if category.get("id") == "unkategorisiert":
            uncategorized = category
            break

    if uncategorized is None:
        uncategorized = {
            "id": "unkategorisiert",
            "label": {
                "de": "Unkategorisiert",
                "en": "Uncategorized"
            },
            "images": []
        }
        gallery_data["categories"].append(uncategorized)

    # Neue Bilder hinzufügen
    for webp_name in new_files:
        uncategorized["images"].append({
            "file": webp_name,
            "alt": {
                "de": "Neues Bild - Beschreibung hinzufügen",
                "en": "New image - add description"
            }
        })

    # YAML schreiben
    try:
        # Custom representer für bessere Formatierung
        def str_representer(dumper, data):
            if '\n' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)

        yaml.add_representer(str, str_representer)

        with open(YAML_PATH, "w", encoding="utf-8") as f:
            f.write("# Gallery categories and images\n")
            f.write("# Used by _includes/gallery.html\n\n")
            yaml.dump(gallery_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return len(new_files)
    except Exception as e:
        print(f"  Fehler beim Schreiben von gallery.yml: {e}")
        return 0


def main():
    print("=== Galerie-Build-Script ===\n")

    # Prüfen, ob photos/ existiert
    if not PHOTOS_DIR.exists():
        print(f"Fehler: Ordner '{PHOTOS_DIR}' nicht gefunden.")
        print("Erstelle den Ordner und lege Bilder hinein.")
        sys.exit(1)

    # Output-Ordner erstellen
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    FULL_DIR.mkdir(parents=True, exist_ok=True)

    # Bilder finden
    extensions = set(SUPPORTED_EXTENSIONS)
    if HEIF_SUPPORT:
        extensions |= HEIF_EXTENSIONS

    images = []
    for ext in extensions:
        images.extend(PHOTOS_DIR.glob(f"*{ext}"))
        images.extend(PHOTOS_DIR.glob(f"*{ext.upper()}"))

    # Duplikate entfernen (falls .jpg und .JPG)
    images = list(set(images))

    # HEIC/HEIF vom iPhone nicht stillschweigend übergehen
    if not HEIF_SUPPORT:
        skipped_heif = [
            path for path in PHOTOS_DIR.iterdir()
            if path.suffix.lower() in HEIF_EXTENSIONS
        ]
        if skipped_heif:
            print(f"Warnung: {len(skipped_heif)} HEIC/HEIF-Datei(en) übersprungen "
                  f"(z. B. {skipped_heif[0].name}).")
            print("Für iPhone-Fotos in HEIC wird pillow-heif benötigt:")
            print("  pip install pillow-heif")
            print("  oder: nix-shell -p python3 python3Packages.pillow "
                  "python3Packages.pillow-heif")
            print("Alternative: am iPhone unter Einstellungen > Kamera > Formate")
            print("'Maximale Kompatibilität' wählen, dann wird JPEG aufgenommen.\n")

    if not images:
        print(f"Keine Bilder in '{PHOTOS_DIR}' gefunden.")
        print(f"Unterstützte Formate: {', '.join(sorted(extensions))}")
        # Leere gallery.json erstellen
        JSON_PATH.write_text("[]")
        sys.exit(0)

    print(f"Gefunden: {len(images)} Bild(er)\n")

    # Bilder verarbeiten
    gallery_data = []
    for img_path in sorted(images):
        result = process_image(img_path)
        if result:
            gallery_data.append(result)

    # Nach Datum sortieren (neueste zuerst)
    gallery_data.sort(key=lambda x: x.get("date_sort", ""), reverse=True)

    # JSON schreiben
    JSON_PATH.write_text(json.dumps(gallery_data, indent=2, ensure_ascii=False))
    print(f"\n✓ Metadaten gespeichert: {JSON_PATH}")
    print(f"✓ Verarbeitet: {len(gallery_data)} Bild(er)")

    # gallery.yml aktualisieren
    processed_filenames = [item["filename"] for item in gallery_data]
    new_count = update_gallery_yaml(processed_filenames)
    if new_count > 0:
        print(f"✓ {new_count} neue(s) Bild(er) zu '{YAML_PATH}' hinzugefügt (Kategorie: Unkategorisiert)")
        print(f"  → Bitte Kategorien und Alt-Texte in '{YAML_PATH}' anpassen")
    elif yaml is not None:
        print(f"✓ Keine neuen Bilder für '{YAML_PATH}'")


if __name__ == "__main__":
    main()
