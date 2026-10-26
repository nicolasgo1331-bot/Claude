from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def cargar(plantilla, /, **vars):
    """Lee prompts/<nombre>.md y reemplaza {{variable}}. Falla si queda alguna sin valor."""
    texto = (RAIZ / "prompts" / f"{plantilla}.md").read_text(encoding="utf-8")
    for k, v in vars.items():
        texto = texto.replace("{{" + k + "}}", str(v))
    if "{{" in texto:
        faltan = {p.split("}}")[0] for p in texto.split("{{")[1:]}
        raise KeyError(f"Variables sin valor en {plantilla}.md: {sorted(faltan)}")
    return texto
