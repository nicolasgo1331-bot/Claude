from .gemini import extraer_json
from .plantillas import cargar


def textos_panel(ficha):
    t = ["PERFIL DE LA FRAGANCIA", "GÉNERO", ficha["genero"].upper(), "DURACIÓN", "OCASIÓN",
         *[n.upper() for n in ficha["notas_icono"]]]
    if ficha.get("inspirado_en"):
        t += ["INSPIRADO EN", ficha["inspirado_en"].upper()]
    return t


def revisar(llm, imagen, foto_base, ficha, tipo):
    """tipo: 'caja' | 'frasco' | 'info'. Devuelve dict con aprobado/problemas/correccion."""
    chequeo = ""
    if tipo == "info":
        chequeo = cargar("05b_chequeo_texto", textos="; ".join(textos_panel(ficha)),
                         lista_notas=", ".join(n.upper() for n in ficha["notas_icono"]))
    prompt = cargar("05_qa", tipo=tipo, y_caja="y caja" if tipo == "caja" else "", chequeo_texto=chequeo)
    return extraer_json(llm.texto(prompt, imagenes=[foto_base, imagen]))
