#!/usr/bin/env python3
"""
Galerie-Build-Script für GitHub Pages.

Verarbeitet Bilder aus photos/ und generiert:
- Thumbnails (max 400px Breite, WebP Q80) in assets/gallery/thumbs/
- Vollbilder (max 1200px Breite, WebP Q85) in assets/gallery/full/
- Metadaten (EXIF) in assets/gallery/gallery.json

Abhängigkeiten:
- Python 3.8+
- Pillow: pip install Pillow
  oder: nix-shell -p python3 python3Packages.pillow

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
    from PIL import Image, ImageDraw, ImageFont
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("Fehler: Pillow nicht installiert.")
    print("Installation: pip install Pillow")
    print("Oder mit Nix: nix-shell -p python3 python3Packages.pillow")
    sys.exit(1)

# Konfiguration
PHOTOS_DIR = Path("photos")
THUMBS_DIR = Path("assets/gallery/thumbs")
FULL_DIR = Path("assets/gallery/full")
JSON_PATH = Path("assets/gallery/gallery.json")

THUMB_MAX_WIDTH = 400
FULL_MAX_WIDTH = 1200
THUMB_QUALITY = 80
FULL_QUALITY = 85

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

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


def get_exif_data(image: Image.Image) -> dict:
    """Extrahiert relevante EXIF-Daten aus einem Bild."""
    exif_data = {}

    try:
        exif = image._getexif()
        if not exif:
            return exif_data

        # EXIF-Tags in lesbare Namen umwandeln
        exif_readable = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_readable[tag] = value

        # Kamera
        make = exif_readable.get("Make", "").strip()
        model = exif_readable.get("Model", "").strip()
        if make and model:
            # Vermeidet Duplikate wie "Canon Canon EOS R5"
            if model.startswith(make):
                exif_data["camera"] = model
            else:
                exif_data["camera"] = f"{make} {model}"
        elif model:
            exif_data["camera"] = model

        # Objektiv
        lens = exif_readable.get("LensModel", "")
        if lens:
            exif_data["lens"] = format_lens_name(str(lens).strip())

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

        # ISO
        iso = exif_readable.get("ISOSpeedRatings")
        if iso:
            if isinstance(iso, tuple):
                iso = iso[0]
            exif_data["iso"] = f"ISO {iso}"

        # Brennweite
        focal = exif_readable.get("FocalLength")
        if focal:
            try:
                if hasattr(focal, "numerator"):
                    mm = focal.numerator / focal.denominator
                else:
                    mm = float(focal)
                exif_data["focal_length"] = f"{int(mm)}mm"
            except (TypeError, ZeroDivisionError):
                pass

    except Exception as e:
        print(f"  Warnung: EXIF-Extraktion fehlgeschlagen: {e}")

    return exif_data


def get_image_date(image: Image.Image, filepath: Path) -> datetime:
    """Ermittelt das Aufnahmedatum für die Sortierung."""
    try:
        exif = image._getexif()
        if exif:
            exif_readable = {TAGS.get(k, k): v for k, v in exif.items()}
            date_str = exif_readable.get("DateTimeOriginal") or exif_readable.get("DateTime")
            if date_str:
                return datetime.strptime(str(date_str), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    # Fallback: Datei-Änderungszeit
    return datetime.fromtimestamp(filepath.stat().st_mtime)


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
    images = []
    for ext in SUPPORTED_EXTENSIONS:
        images.extend(PHOTOS_DIR.glob(f"*{ext}"))
        images.extend(PHOTOS_DIR.glob(f"*{ext.upper()}"))

    # Duplikate entfernen (falls .jpg und .JPG)
    images = list(set(images))

    if not images:
        print(f"Keine Bilder in '{PHOTOS_DIR}' gefunden.")
        print(f"Unterstützte Formate: {', '.join(SUPPORTED_EXTENSIONS)}")
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


if __name__ == "__main__":
    main()
