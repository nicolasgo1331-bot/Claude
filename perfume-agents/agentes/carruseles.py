import json
from pathlib import Path

from .gemini import extraer_json
from .plantillas import cargar, RAIZ


def _leer(nombre):
    p = RAIZ / "datos" / nombre
    return p.read_text(encoding="utf-8") if p.exists() else "(sin datos todavía)"


def ideas(llm, tema="elige los temas con más potencial viral", n=5, nicho="perfumes árabes y de nicho"):
    prompt = cargar("06_carrusel_ideas", nicho=nicho, perfil=_leer("perfil.md"), tema=tema, n=n)
    return extraer_json(llm.texto(prompt, buscar=True))["ideas"]


def renderizar(llm, idea, carpeta):
    """Genera cada slide en 4:5; la portada sirve de referencia de estilo para las demás."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    estilo = (RAIZ / "prompts" / "estilo_marca.md").read_text(encoding="utf-8")
    slides, portada = idea["slides"], None
    for s in slides:
        cont = "Mantén exactamente la misma paleta, tipografías y estilo que la imagen de referencia adjunta." if portada else ""
        p = cargar("07_carrusel_slide", estilo=estilo, continuidad=cont, n=s["n"], total=len(slides),
                   titulo=s["titulo"], texto=s["texto"], visual=s["visual"])
        img = llm.imagen(p, referencias=[portada] if portada else [], aspecto="4:5")
        img.save(carpeta / f"slide{s['n']}.png")
        portada = portada or img
    (carpeta / "caption.md").write_text(idea["caption"], encoding="utf-8")
    (carpeta / "idea.json").write_text(json.dumps(idea, ensure_ascii=False, indent=2), encoding="utf-8")
