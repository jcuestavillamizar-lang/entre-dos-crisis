"""Arma el sitio: inserta gráficas y citas de la entrevista en la plantilla.

Salidas:
  - docs/index.html  (documento completo, listo para GitHub Pages)
  - sitio/preview.html (cuerpo sin <html>/<head>, para vista previa)

Uso: python scripts/construir_sitio.py
"""
import json
import re
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITIO = ROOT / "sitio"
# Dirección del repositorio en GitHub (se llena al publicar).
REPO_URL = ""
plantilla = (SITIO / "plantilla.html").read_text(encoding="utf-8")


# ---------- mapa esquemático (lat/lon aproximadas) ----------
def mapa():
    lon0, lon1, lat0, lat1 = -73.75, -72.15, 7.65, 8.95
    W, H = 560, 460
    X = lambda lon: 20 + (lon - lon0) / (lon1 - lon0) * (W - 40)
    Y = lambda lat: 20 + (lat1 - lat) / (lat1 - lat0) * (H - 40)
    pt = lambda lat, lon: f"{X(lon):.1f},{Y(lat):.1f}"
    frontera = [(8.95, -72.98), (8.80, -72.70), (8.62, -72.42), (8.35, -72.36), (8.10, -72.38),
                (7.90, -72.47), (7.80, -72.44), (7.65, -72.40)]
    ven = " ".join(pt(a, o) for a, o in frontera) + f" {X(lon1):.1f},{Y(lat0):.1f} {X(lon1):.1f},{Y(lat1):.1f}"
    cata = [(8.95, -73.45), (8.80, -73.10), (8.85, -72.80), (8.62, -72.45), (8.30, -72.60),
            (7.98, -72.80), (7.98, -73.25), (8.10, -73.48), (8.45, -73.60)]
    ruta = [(8.402, -73.208), (8.330, -73.300), (8.237, -73.356), (8.081, -73.221), (8.010, -73.000),
            (8.083, -72.800), (7.980, -72.640), (7.894, -72.508)]
    pueblos = [("Ocaña", 8.237, -73.356, "end", -9, 4), ("Ábrego", 8.081, -73.221, "end", -9, 12),
               ("El Carmen", 8.510, -73.447, "end", -8, -8), ("La Playa", 8.217, -73.238, "start", 8, 10),
               ("Convención", 8.470, -73.337, "end", -8, 4), ("Teorama", 8.437, -73.286, "start", 6, -8),
               ("El Tarra", 8.575, -73.094, "start", 8, 4), ("Tibú", 8.639, -72.735, "start", 8, 4),
               ("Hacarí", 8.322, -73.149, "start", 8, 4), ("Sardinata", 8.083, -72.800, "start", 8, -6)]
    b = [f'<rect class="land" x="0" y="0" width="{W}" height="{H}"/>',
         f'<polygon class="ven" points="{ven}"/>',
         f'<polygon class="cata" points="{" ".join(pt(a, o) for a, o in cata)}"/>',
         f'<polyline class="border" points="{" ".join(pt(a, o) for a, o in frontera)}"/>',
         f'<text class="region" x="{W-14}" y="{Y(8.85):.1f}" text-anchor="end">VENEZUELA</text>',
         f'<text class="region" x="{X(-73.62):.1f}" y="{Y(8.88):.1f}">CATATUMBO</text>',
         f'<polyline class="route" points="{" ".join(pt(a, o) for a, o in ruta)}"/>']
    for n, a, o, anc, dx, dy in pueblos:
        b.append(f'<circle class="town" cx="{X(o):.1f}" cy="{Y(a):.1f}" r="3.5"/>')
        b.append(f'<text class="tname c-ax" x="{X(o)+dx:.1f}" y="{Y(a)+dy:.1f}" text-anchor="{anc}">{n}</text>')
    for n, a, o, anc, dx, dy in [("San Calixto", 8.402, -73.208, "start", 11, 5), ("Cúcuta", 7.894, -72.508, "end", -12, 5)]:
        b.append(f'<circle class="town-hi" cx="{X(o):.1f}" cy="{Y(a):.1f}" r="8"/>')
        b.append(f'<text class="tname-hi" x="{X(o)+dx:.1f}" y="{Y(a)+dy:.1f}" text-anchor="{anc}">{n}</text>')
    return (f'<svg class="chart map" viewBox="0 0 {W} {H}" role="img" aria-label="Mapa esquemático del recorrido de San Calixto a Cúcuta" '
            f'xmlns="http://www.w3.org/2000/svg" style="min-width:0">{"".join(b)}</svg>')


# ---------- citas de la entrevista ----------
voces_path = ROOT / "data" / "familia" / "voces.json"
voces = json.loads(voces_path.read_text(encoding="utf-8")) if voces_path.exists() else {}
PENDIENTE = {
    "1": "La vida en San Calixto antes de 1986",
    "2": "Cómo se instaló la familia en Cúcuta y de qué vivían",
    "3": "El año como vendedor ambulante",
    "4": "Cómo pagó la universidad y por qué ingeniería civil",
    "5": "Buscar trabajo en 1999",
    "6": "Mirando hacia atrás",
    "7": "El primer empleo",
}


def voz(n):
    citas = voces.get(n)
    if not citas:
        return (f'<blockquote class="pendiente"><p>[Fragmento de la entrevista: {PENDIENTE[n]}]</p>'
                f'<cite>Entrevista con mi papá</cite></blockquote>')
    return "".join(f'<blockquote><p>{escape(c)}</p><cite>Mi papá, entrevista de noviembre de 2026</cite></blockquote>'
                   for c in citas)


def tabla_comparacion():
    df = pd.read_csv(ROOT / "data" / "processed" / "censo_cohorte_comparacion.csv")
    f = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    filas = "".join(
        f"<tr><td>{escape(r.grupo)}</td><td class='n'>{f(r.base, 0)}</td><td class='n'>{f(r.pct_universitaria)} %</td>"
        f"<td class='n'>{f(r.pct_superior)} %</td><td class='n'>{f(r.pct_solo_primaria_o_menos)} %</td></tr>"
        for r in df.itertuples())
    return ("<details class='data'><summary>Ver los datos de la gráfica</summary><div class='tbl'><table>"
            "<thead><tr><th>Grupo (nacidos ~1970–1978)</th><th class='n'>Personas</th><th class='n'>Universidad o posgrado</th>"
            "<th class='n'>Cualquier educación superior</th><th class='n'>Primaria o menos</th></tr></thead>"
            f"<tbody>{filas}</tbody></table></div>"
            "<p class='how'>«Cualquier educación superior» suma técnica, tecnológica, universitaria y posgrado. "
            "Los porcentajes se calculan sobre quienes informaron su nivel educativo. Fuente: DANE, CNPV 2018; cálculo propio.</p></details>")


html = plantilla
html = html.replace("{{tabla:comparacion}}", tabla_comparacion())

# Fotos del archivo familiar (opcionales): sitio/fotos/fotos.json = [{"archivo": "x.jpg", "capitulo": 1, "pie": "..."}]
fotos_json = SITIO / "fotos" / "fotos.json"
fotos = json.loads(fotos_json.read_text(encoding="utf-8")) if fotos_json.exists() else []
def bloque_fotos(cap):
    items = [f for f in fotos if str(f["capitulo"]) == cap]
    if not items:
        return ""
    figs = "".join(f'<figure class="foto"><img src="fotos/{escape(f["archivo"])}" alt="{escape(f["pie"])}" loading="lazy">'
                   f'<figcaption>{escape(f["pie"])}</figcaption></figure>' for f in items)
    return f'<div class="fotos">{figs}</div>'
html = re.sub(r"\{\{fotos:(\d)\}\}", lambda m: bloque_fotos(m.group(1)), html)
# En GitHub Pages (usuario.github.io/repo) el enlace al repositorio se arma solo en el navegador.
html = html.replace("{{repo}}", (f'El código, los datos y las consultas están en <a id="repo-link" href="{REPO_URL}">{REPO_URL.replace("https://", "")}</a>.'
                                 if REPO_URL else 'El código, los datos y las consultas están en <a id="repo-link" href="#datos">el repositorio del proyecto</a>.'))
for nombre in re.findall(r"\{\{fig:(\w+)\}\}", html):
    contenido = mapa() if nombre == "mapa" else (SITIO / "figs" / f"{nombre}.svg").read_text(encoding="utf-8")
    html = html.replace(f"{{{{fig:{nombre}}}}}", contenido)
html = re.sub(r"\{\{voz:(\d)\}\}", lambda m: voz(m.group(1)), html)

# Espacio no separable antes de «%» en el texto (evita «9,5» al final de una línea y «%» al inicio de la siguiente).
html = re.sub(r"(\d) %", "\\1\u00a0%", html)

(SITIO / "preview.html").write_text(html, encoding="utf-8")

head_end = html.index("</style>") + len("</style>")
cabeza = html[:head_end].replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
cuerpo = html[head_end:]
doc = ("<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
       "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
       f"{cabeza}\n</head>\n<body>\n{cuerpo}\n</body>\n</html>\n")
(ROOT / "docs").mkdir(exist_ok=True)
if fotos:
    import shutil
    (ROOT / "docs" / "fotos").mkdir(exist_ok=True)
    for f in fotos:
        shutil.copy(SITIO / "fotos" / f["archivo"], ROOT / "docs" / "fotos" / f["archivo"])
(ROOT / "docs" / "index.html").write_text(doc, encoding="utf-8")
print("ok", len(doc), "bytes")
