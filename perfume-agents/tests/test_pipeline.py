"""Prueba todo el flujo con un Gemini falso (sin red ni API key): python -m unittest"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run
from agentes import fotografo

FICHA = {
    "marca": "Armaf", "nombre": "Odyssey Limoni", "genero": "Unisex", "concentracion": "Eau de Parfum",
    "notas": {"salida": ["Limón"], "corazon": ["Té"], "fondo": ["Azahar"]},
    "acordes_principales": ["cítrico", "verde"], "notas_icono": ["Limón", "Té", "Naranja", "Bergamota", "Mandarina", "Azahar"],
    "duracion_horas": 5, "duracion_texto": "Moderada", "ocasion": "Diario / Casual",
    "iconos_ocasion": ["sol", "copas", "coctel"], "inspirado_en": "Louis Vuitton Afternoon Swim",
    "direccion_arte": {"superficie": "roca húmeda con musgo", "fondo": "jardín de cítricos", "paleta": "verdes y amarillos",
                       "luz": "luz suave de mañana", "elementos": ["limones", "azahar"]},
    "dudas": [],
}


class Falso:
    def __init__(self, qa):
        self.qa, self.prompts = list(qa), []

    def texto(self, prompt, imagenes=(), buscar=False):
        if "control de calidad" in prompt:
            return "```json\n" + json.dumps(self.qa.pop(0)) + "\n```"
        if "Responde SOLO con JSON válido" in prompt:
            return "```json\n" + json.dumps(FICHA) + "\n```"
        return "1. Copy de prueba"

    def imagen(self, prompt, referencias=(), aspecto="1:1", tamano="2K"):
        self.prompts.append(prompt)
        return Image.new("RGB", (64, 64), "green")


OK = {"aprobado": True, "puntaje": 9, "problemas": [], "correccion": ""}
MAL = {"aprobado": False, "puntaje": 5, "problemas": ["logo cambiado"], "correccion": "respeta el logo LIMONI"}


class Pipeline(unittest.TestCase):
    def test_flujo_completo_con_reintento(self):
        with tempfile.TemporaryDirectory() as d:
            run.SALIDA = Path(d)
            foto = Path(d) / "base.png"
            Image.new("RGB", (64, 64), "white").save(foto)
            llm = Falso([MAL, OK, OK, OK])  # la imagen 1 falla una vez
            run.main(["ficha", "Armaf Odyssey Limoni"], llm)
            run.main(["imagenes", str(foto), "Armaf Odyssey Limoni"], llm)
            carpeta = Path(d) / "armaf-odyssey-limoni"
            for n in ("1_frasco_y_caja", "2_solo_frasco", "3_info"):
                self.assertTrue((carpeta / f"{n}.png").exists())
            self.assertEqual(len(llm.prompts), 4)
            self.assertIn("respeta el logo LIMONI", llm.prompts[1])
            self.assertIn("INSPIRADO EN", llm.prompts[3])
            with self.assertRaises(SystemExit):
                run.main(["copy", "Armaf Odyssey Limoni"], llm)
            run.main(["aprobar", "Armaf Odyssey Limoni"], llm)
            run.main(["copy", "Armaf Odyssey Limoni"], llm)
            self.assertTrue((carpeta / "copy.md").exists())

    def test_sin_inspiracion_no_agrega_bloque(self):
        v = fotografo._vars_info({**FICHA, "inspirado_en": None})
        self.assertEqual(v["bloque_inspirado"], "")
        self.assertEqual(v["pct"], 50)


if __name__ == "__main__":
    unittest.main()
