from pathlib import Path

from PIL import Image


def poner_logo(img, logo_path, ancho=0.2, margen=0.03):
    """Pega tu logo abajo al centro, de forma determinista (la IA no lo toca)."""
    if not Path(logo_path).exists():
        return img
    logo = Image.open(logo_path).convert("RGBA")
    w = int(img.width * ancho)
    logo = logo.resize((w, int(logo.height * w / logo.width)))
    base = img.convert("RGBA")
    base.alpha_composite(logo, ((img.width - w) // 2, img.height - logo.height - int(img.height * margen)))
    return base.convert("RGB")
