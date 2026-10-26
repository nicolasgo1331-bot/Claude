import json
import re
from pathlib import Path

from .gemini import extraer_json
from .plantillas import cargar


def slug(texto):
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def investigar(llm, perfume, notas_usuario=""):
    extra = f"Datos que el dueño ya confirmó (tienen prioridad): {notas_usuario}" if notas_usuario else ""
    ficha = extraer_json(llm.texto(cargar("00_investigador", perfume=perfume, notas_usuario=extra), buscar=True))
    ficha["notas_icono"] = ficha.get("notas_icono", [])[:6]
    return ficha


def guardar_ficha(carpeta, ficha):
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    (Path(carpeta) / "ficha.json").write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")


def cargar_ficha(carpeta):
    return json.loads((Path(carpeta) / "ficha.json").read_text(encoding="utf-8"))
