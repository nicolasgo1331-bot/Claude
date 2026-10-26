import json

from .plantillas import cargar, RAIZ


def escribir_copy(llm, imagen_info, ficha):
    voz = (RAIZ / "prompts" / "voz.md").read_text(encoding="utf-8")
    prompt = cargar("04_copy", ficha=json.dumps(ficha, ensure_ascii=False, indent=2), voz=voz)
    return llm.texto(prompt, imagenes=[imagen_info])
