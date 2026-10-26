# Agentes de publicaciones para perfumes

Flujo: **ficha → 3 imágenes (con control de calidad) → tu aprobación → copy**, más carruseles virales.

## Instalación
```
pip install -r requirements.txt
cp .env.example .env   # pega tu GEMINI_API_KEY (https://aistudio.google.com/apikey)
```

## Uso
```
python run.py ficha "Armaf Odyssey Limoni"                   # investiga y crea salida/<perfume>/ficha.json
#   -> abre ficha.json, corrige lo que haga falta (notas, duración, inspirado_en)
python run.py imagenes foto_base.png "Armaf Odyssey Limoni"  # 1) frasco+caja 2) solo frasco 3) con info
python run.py aprobar "Armaf Odyssey Limoni"                 # cuando las imágenes te gusten
python run.py copy "Armaf Odyssey Limoni"                    # 3 versiones de copy a partir de la imagen 3
python run.py carrusel "tips para que dure el perfume"       # ideas virales; --render N genera las slides
```

## Qué hace cada agente
| Agente | Archivo | Función |
|---|---|---|
| Investigador | `agentes/investigador.py` | Busca notas, género, duración, ocasión, inspiración y diseña la escena |
| Fotógrafo | `agentes/fotografo.py` | Genera las 3 imágenes encadenadas (misma escena y base) |
| Control de calidad | `agentes/control_calidad.py` | Compara con tu foto: logo, textos, realismo; ordena regenerar |
| Copywriter | `agentes/copywriter.py` | 3 versiones de copy desde la imagen + ficha |
| Estratega | `agentes/carruseles.py` | Ideas de carruseles, guion por slide, caption |

## Personalizar
- Todos los prompts están en `prompts/*.md` (variables `{{así}}`). Edítalos sin tocar código.
- Voz de marca: `prompts/voz.md`. Estilo visual de carruseles: `prompts/estilo_marca.md`.
- Tu logo: guarda un PNG transparente en `assets/logo.png` y se pega por código abajo al centro.
- Contexto de tu perfil para los carruseles: `datos/perfil.md`.

## Tests (sin API key)
`python -m unittest discover -s tests`
