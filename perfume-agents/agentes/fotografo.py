import json
from pathlib import Path

from PIL import Image

from . import control_calidad
from .marca import poner_logo
from .plantillas import cargar, RAIZ

MAX_INTENTOS = 3
UMBRAL = 8


def _vars_escena(f):
    d = f["direccion_arte"]
    return dict(marca=f["marca"], nombre=f["nombre"], superficie=d["superficie"], fondo=d["fondo"],
                paleta=d["paleta"], luz=d["luz"], elementos=", ".join(d["elementos"]),
                acordes=", ".join(f["acordes_principales"]))


def _vars_info(f):
    notas = f["notas_icono"]
    inspirado = cargar("03b_bloque_inspirado", inspirado_en=f["inspirado_en"].upper()) if f.get("inspirado_en") else ""
    dur = f"{f['duracion_texto'].upper()} (UNAS {f['duracion_horas']} HS)"
    return dict(n_notas=len(notas), lista_notas="\n".join(f"{i}. {n.upper()}" for i, n in enumerate(notas, 1)),
                genero=f["genero"].upper(), duracion=dur, pct=min(100, f["duracion_horas"] * 10),
                ocasion=f["ocasion"].upper(), iconos_ocasion=", ".join(f["iconos_ocasion"]),
                bloque_inspirado=inspirado)


def _generar_con_qa(llm, prompt, referencias, foto_base, ficha, tipo, carpeta, nombre):
    """Genera, revisa y regenera con la corrección del QA. Guarda todos los intentos."""
    mejor, mejor_puntaje, informe = None, -1, []
    correccion = ""
    for i in range(1, MAX_INTENTOS + 1):
        p = prompt + (f"\n\nCORRECCIONES OBLIGATORIAS respecto al intento anterior: {correccion}" if correccion else "")
        img = llm.imagen(p, referencias=[*referencias])
        img.save(carpeta / f"{nombre}_intento{i}.png")
        r = control_calidad.revisar(llm, img, foto_base, ficha, tipo)
        informe.append({"intento": i, **r})
        if r["puntaje"] > mejor_puntaje:
            mejor, mejor_puntaje = img, r["puntaje"]
        if r["aprobado"] and r["puntaje"] >= UMBRAL:
            break
        correccion = r["correccion"]
    (carpeta / f"{nombre}_qa.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    return mejor


def generar_set(llm, foto_base_path, ficha, carpeta, logo=RAIZ / "assets" / "logo.png"):
    carpeta = Path(carpeta)
    base = Image.open(foto_base_path).convert("RGB")
    producto = ["Imagen de referencia del producto (fiel al original):", base]

    escena = _generar_con_qa(llm, cargar("01_escena_caja", **_vars_escena(ficha)), producto, base, ficha,
                             "caja", carpeta, "1_frasco_y_caja")
    solo = _generar_con_qa(llm, cargar("02_solo_frasco"), [*producto, "Escena a conservar:", escena], base,
                           ficha, "frasco", carpeta, "2_solo_frasco")
    info = _generar_con_qa(llm, cargar("03_info", **_vars_info(ficha)), [*producto, "Foto base de la escena:", solo],
                           base, ficha, "info", carpeta, "3_info")

    finales = {"1_frasco_y_caja": escena, "2_solo_frasco": solo, "3_info": info}
    for nombre, img in finales.items():
        poner_logo(img, logo).save(carpeta / f"{nombre}.png")
    return finales
