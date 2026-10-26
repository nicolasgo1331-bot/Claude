# Modo manual (Gemini app, sin API)

Por cada perfume:
1. Le pasás a Claude el **nombre del perfume** y la **foto base** (fondo blanco).
2. Claude investiga y te devuelve la **ficha** (notas, género, duración, ocasión, inspirado en) para que la confirmes, y los **3 prompts ya rellenados**.
3. En Gemini: subí la foto base + pegá el prompt 1. Luego, en el MISMO chat, pegá el prompt 2 y después el 3 (así mantiene fondo y base).
4. Controlá a mano (checklist): logo y textos del frasco/caja idénticos al original · sin estelas/aros de luz · texto del panel sin errores · notas en el orden de la ficha. Si algo falla, pedile solo esa corrección en el mismo chat.
5. Pegá el logo MP Fragance abajo al centro (o pedime que lo pegue: me pasás la imagen y la guardo con `agentes/marca.py`).
6. Pasale a Claude la imagen 3 aprobada → te devuelve 3 versiones de copy.

Ejemplo ya hecho: `manual/armaf-odyssey-limoni/ficha.json`.
Comando equivalente local: `python run.py prompts "<perfume>"` (usa salida/<perfume>/ficha.json).
