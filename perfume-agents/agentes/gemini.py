"""Cliente fino de Gemini. Los agentes solo dependen de `texto` e `imagen`,
así que en los tests se reemplaza por un falso."""
import io
import json
import os
import re
import time

from PIL import Image


def extraer_json(texto):
    m = re.search(r"```(?:json)?\s*(.*?)```", texto, re.S)
    crudo = m.group(1) if m else texto[texto.find("{"):texto.rfind("}") + 1]
    return json.loads(crudo)


def _reintentar(fn, intentos=4):
    for i in range(intentos):
        try:
            return fn()
        except Exception:
            if i == intentos - 1:
                raise
            time.sleep(2 ** (i + 1))


class Gemini:
    def __init__(self):
        from dotenv import load_dotenv
        from google import genai

        load_dotenv()
        self._genai = genai
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.modelo_texto = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-pro")
        self.modelo_imagen = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")

    def texto(self, prompt, imagenes=(), buscar=False):
        from google.genai import types

        cfg = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())] if buscar else None
        )
        r = _reintentar(lambda: self.client.models.generate_content(
            model=self.modelo_texto, contents=[prompt, *imagenes], config=cfg))
        return r.text

    def imagen(self, prompt, referencias=(), aspecto="1:1", tamano="2K"):
        from google.genai import types

        cfg = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspecto, image_size=tamano),
        )

        def llamar():
            r = self.client.models.generate_content(
                model=self.modelo_imagen, contents=[prompt, *referencias], config=cfg)
            for parte in r.candidates[0].content.parts:
                if parte.inline_data:
                    return Image.open(io.BytesIO(parte.inline_data.data)).convert("RGB")
            raise RuntimeError("Gemini no devolvió imagen: " + (r.text or "sin texto"))

        return _reintentar(llamar)
