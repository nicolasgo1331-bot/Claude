from pathlib import Path

from PIL import Image, ImageFilter


def poner_logo(img, logo_path, ancho=0.2, margen=0.03):
    """Pega tu logo abajo al centro, de forma determinista (la IA no lo toca)."""
    if not Path(logo_path).exists():
        return img
    logo = Image.open(logo_path).convert("RGBA")
    w = int(img.width * ancho)
    logo = logo.resize((w, int(logo.height * w / logo.width)))
    base = img.convert("RGBA")
    # sombra suave para que el logo blanco se lea también sobre fondos claros
    sombra = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    sombra.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.65)))
    pad = 12
    lienzo = Image.new("RGBA", (w + 2 * pad, logo.height + 2 * pad), (0, 0, 0, 0))
    lienzo.alpha_composite(sombra, (pad, pad))
    lienzo = lienzo.filter(ImageFilter.GaussianBlur(5))
    base.alpha_composite(lienzo, ((img.width - w) // 2 - pad, img.height - logo.height - int(img.height * margen) - pad))
    base.alpha_composite(logo, ((img.width - w) // 2, img.height - logo.height - int(img.height * margen)))
    return base.convert("RGB")
