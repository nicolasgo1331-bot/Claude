"""Uso:
  python run.py ficha  "Armaf Odyssey Limoni"            -> investiga y crea salida/<perfume>/ficha.json (revísala)
  python run.py imagenes foto.png "Armaf Odyssey Limoni" -> genera las 3 imágenes con control de calidad
  python run.py aprobar  "Armaf Odyssey Limoni"          -> marca el set como aprobado
  python run.py copy     "Armaf Odyssey Limoni"          -> escribe el copy a partir de la imagen 3
  python run.py prompts  "Armaf Odyssey Limoni"          -> imprime los 3 prompts ya rellenados (para pegar en la app de Gemini)
  python run.py carrusel ["tema"] [--render N]           -> ideas virales (y render de la idea N)
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from agentes.plantillas import cargar
from agentes import carruseles, copywriter, fotografo, investigador

SALIDA = Path(__file__).parent / "salida"


def main(argv=None, llm=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("ficha", "aprobar", "copy", "prompts"):
        sub.add_parser(c).add_argument("perfume")
    sub.choices["ficha"].add_argument("--notas", default="", help="datos que ya confirmaste")
    p = sub.add_parser("imagenes"); p.add_argument("foto"); p.add_argument("perfume")
    p = sub.add_parser("carrusel"); p.add_argument("tema", nargs="?", default="elige los temas con más potencial viral")
    p.add_argument("--render", type=int, help="número de idea a renderizar")
    a = ap.parse_args(argv)

    if llm is None:
        from agentes.gemini import Gemini
        llm = Gemini()

    if a.cmd == "carrusel":
        lista = carruseles.ideas(llm, a.tema)
        base = SALIDA / "carruseles"
        base.mkdir(parents=True, exist_ok=True)
        (base / "ideas.json").write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")
        for i, idea in enumerate(lista, 1):
            print(f"{i}. {idea['titulo_interno']} — {idea['angulo']}")
        if a.render:
            carruseles.renderizar(llm, lista[a.render - 1], base / investigador.slug(lista[a.render - 1]["titulo_interno"]))
        return

    carpeta = SALIDA / investigador.slug(a.perfume)
    if a.cmd == "ficha":
        ficha = investigador.investigar(llm, a.perfume, a.notas)
        investigador.guardar_ficha(carpeta, ficha)
        print(f"Ficha en {carpeta/'ficha.json'}. Revisa 'dudas' y corrige antes de generar imágenes.")
        if ficha.get("dudas"):
            print("Dudas:", *ficha["dudas"], sep="\n - ")
    elif a.cmd == "prompts":
        ficha = investigador.cargar_ficha(carpeta)
        for n, p in (("1", cargar("01_escena_caja", **fotografo._vars_escena(ficha))), ("2", cargar("02_solo_frasco")),
                     ("3", cargar("03_info", **fotografo._vars_info(ficha)))):
            print(f"\n===== PROMPT {n} =====\n{p}")
    elif a.cmd == "imagenes":
        ficha = investigador.cargar_ficha(carpeta)
        fotografo.generar_set(llm, a.foto, ficha, carpeta)
        print(f"3 imágenes en {carpeta}. Revísalas y luego: python run.py aprobar \"{a.perfume}\"")
    elif a.cmd == "aprobar":
        (carpeta / "APROBADO").write_text("ok")
        print("Aprobado.")
    elif a.cmd == "copy":
        if not (carpeta / "APROBADO").exists():
            sys.exit("Primero aprueba las imágenes: python run.py aprobar ...")
        texto = copywriter.escribir_copy(llm, Image.open(carpeta / "3_info.png"), investigador.cargar_ficha(carpeta))
        (carpeta / "copy.md").write_text(texto, encoding="utf-8")
        print(texto)


if __name__ == "__main__":
    main()
