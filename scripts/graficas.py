"""Genera las gráficas del sitio como SVG en línea (data/processed -> sitio/figs/*.svg).

Las gráficas usan clases CSS (c-*) que el sitio define, para que respeten el
tema claro/oscuro. Cada marca lleva un <title> que el navegador muestra al pasar
el cursor.

Uso: python scripts/graficas.py
"""
from pathlib import Path
from html import escape

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
FIGS = ROOT / "sitio" / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

fmt = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def svg(w, h, body, label):
    return (f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}" '
            f'xmlns="http://www.w3.org/2000/svg">{body}</svg>')


def guardar(nombre, contenido):
    (FIGS / f"{nombre}.svg").write_text(contenido, encoding="utf-8")


macro = pd.read_csv(P / "macro_1980_2000.csv").set_index("anio")

# ---------------- 1. Línea de tiempo: PIB + hitos ----------------
W, H = 860, 362
x0, x1 = 78, 846
yr = lambda a: x0 + (a - 1979.5) * (x1 - x0) / 21   # cada año ocupa una franja; las barras quedan centradas
ymin, ymax = -5, 7
plot_top, plot_bot = 90, 280
yv = lambda v: plot_top + (ymax - v) * (plot_bot - plot_top) / (ymax - ymin)
b = []
for a, c, lab, anc in [(1982, 1985, "CRISIS DE LOS OCHENTA", "start"), (1998, 1999, "CRISIS 1998–99", "end")]:
    b.append(f'<rect class="c-crisis" x="{yr(a)-16:.1f}" y="{plot_top-10}" width="{yr(c)-yr(a)+32:.1f}" height="{plot_bot-plot_top+10}">'
             f'<title>{lab.capitalize()}: {a}–{c}</title></rect>')
for v in (-4, -2, 0, 2, 4, 6):
    b.append(f'<line class="{"c-zero" if v == 0 else "c-grid"}" x1="{x0}" x2="{x1}" y1="{yv(v):.1f}" y2="{yv(v):.1f}"/>')
    b.append(f'<text class="c-ax" x="{x0-10}" y="{yv(v)+4:.1f}" text-anchor="end">{v}%</text>')
# hitos: las líneas van detrás de las barras
hitos = [(1984, "1984 · Llega a Cúcuta", "start"), (1993, "1993 · Vende en la calle", "middle"),
         (2000, "Dic. 2000 · Se gradúa", "end")]
for a, t, anc in hitos:
    b.append(f'<line class="c-hito-l" x1="{yr(a):.1f}" x2="{yr(a):.1f}" y1="38" y2="{plot_bot}"/>')
bw = 22
for a, v in macro["pib_crec"].items():
    y = min(yv(v), yv(0)); h = abs(yv(v) - yv(0))
    cls = "c-neg" if v < 0 else "c-bar"
    b.append(f'<rect class="{cls}" x="{yr(a)-bw/2:.1f}" y="{y:.1f}" width="{bw}" height="{max(h,1):.1f}" rx="2">'
             f'<title>{a}: PIB {fmt(v)} %</title></rect>')
    if a % 5 == 0:
        b.append(f'<text class="c-ax c-mono" x="{yr(a):.1f}" y="{plot_bot+38}" text-anchor="middle">{a}</text>')
for a, c, lab, anc in [(1982, 1985, "CRISIS DE LOS OCHENTA", "start"), (1998, 1999, "CRISIS 1998–99", "end")]:
    tx = yr(a) - 12 if anc == "start" else yr(c) + 12
    b.append(f'<text class="c-crisis-t" x="{tx:.1f}" y="{plot_top+6}" text-anchor="{anc}">{lab}</text>')
b.append(f'<text class="c-val" x="{yr(1999):.1f}" y="{yv(-4.2)+16:.1f}" text-anchor="middle">−4,2 %</text>')
b.append(f'<rect class="c-life" x="{yr(1994)-bw/2:.1f}" y="{plot_bot+10}" width="{yr(2000)-yr(1994)+bw:.1f}" height="9" rx="2"><title>Universidad: 1994–2000</title></rect>')
b.append(f'<text class="c-life-t" x="{(yr(1994)+yr(2000))/2:.1f}" y="{plot_bot+52}" text-anchor="middle">Universidad 1994–2000</text>')
for a, t, anc in hitos:
    b.append(f'<circle class="c-hito" cx="{yr(a):.1f}" cy="38" r="7"/>')
    b.append(f'<text class="c-hito-t" x="{yr(a)+(10 if anc=="start" else -10 if anc=="end" else 0):.1f}" y="24" text-anchor="{anc}">{t}</text>')
b.append(f'<text class="c-ax" x="{x0-40}" y="{H-4}">Crecimiento anual del PIB real de Colombia (%). Fuente: Banco Mundial, WDI.</text>')
guardar("linea_tiempo", svg(W, H, "".join(b), "Crecimiento anual del PIB de Colombia 1980-2000 con las crisis y los hitos de la vida de mi papá"))

# ---------------- 2. Pesos por bolívar ----------------
W, H = 720, 350
x0, x1, pt, pb = 56, 690, 34, 262
xa = lambda a: x0 + (a - 1980) * (x1 - x0) / 20
ya = lambda v: pb - v * (pb - pt) / 16
fr = macro["cop_por_bolivar_frontera"].dropna()
of = macro["cop_por_bolivar_oficial_unificada"].dropna()
b = []
# años sin serie comparable y años con control de cambios
b.append(f'<rect class="c-gap" x="{xa(1986.5):.1f}" y="{pt-6}" width="{xa(1988.5)-xa(1986.5):.1f}" height="{pb-pt+6}">'
         f'<title>1987–1988: tasas múltiples en Venezuela (RECADI); no hay serie comparable</title></rect>')
b.append(f'<text class="c-ax" x="{xa(1987.5):.1f}" y="{pb-26}" text-anchor="middle">Sin serie</text>')
b.append(f'<text class="c-ax" x="{xa(1987.5):.1f}" y="{pb-11}" text-anchor="middle">comparable</text>')
b.append(f'<rect class="c-gap" x="{xa(1993.5):.1f}" y="{pt-6}" width="{xa(1995.5)-xa(1993.5):.1f}" height="{pb-pt+6}">'
         f'<title>1994–1995: control de cambios en Venezuela; la tasa oficial sobrevalora el bolívar</title></rect>')
b.append(f'<text class="c-ax" x="{xa(1994.5):.1f}" y="{pt+8}" text-anchor="middle">Control de</text>')
b.append(f'<text class="c-ax" x="{xa(1994.5):.1f}" y="{pt+23}" text-anchor="middle">cambios</text>')
for v in (0, 4, 8, 12, 16):
    b.append(f'<line class="{"c-zero" if v == 0 else "c-grid"}" x1="{x0}" x2="{x1}" y1="{ya(v):.1f}" y2="{ya(v):.1f}"/>')
    b.append(f'<text class="c-ax" x="{x0-8}" y="{ya(v)+4:.1f}" text-anchor="end">{v}</text>')
for a in range(1980, 2001, 5):
    b.append(f'<text class="c-ax c-mono" x="{xa(a):.1f}" y="{pb+22}" text-anchor="middle">{a}</text>')
b.append(f'<line class="c-hito-l" x1="{xa(1983.13):.1f}" x2="{xa(1983.13):.1f}" y1="{ya(15.2):.1f}" y2="{pb}"/>')
for serie_, cls, fuente in [(fr, "c-line-b", "mercado de frontera, Fedesarrollo"), (of, "c-line", "tasa oficial unificada, Banco Mundial")]:
    pts = " ".join(f"{xa(a):.1f},{ya(v):.1f}" for a, v in serie_.items())
    b.append(f'<polyline class="{cls}" points="{pts}"/>')
    for a, v in serie_.items():
        b.append(f'<circle class="c-dot-hit" cx="{xa(a):.1f}" cy="{ya(v):.1f}" r="9"><title>{a}: 1 bolívar = {fmt(v)} pesos ({fuente})</title></circle>')
b.append(f'<text class="c-ax" x="{xa(1983.13)+5:.1f}" y="{ya(15.2)+4:.1f}">Viernes Negro (feb. 1983)</text>')
for a, t, anc, dx, dy, s_ in [(1982, "1982: 14,1", "end", -8, -6, fr), (1984, "1984, la llegada: 8,8", "start", 6, -12, fr),
                              (1986, "1986: 5,7", "middle", 0, 22, fr), (1999, "1999: 2,9", "middle", 0, -12, of)]:
    v = s_[a]
    b.append(f'<circle class="c-dot{"-b" if s_ is fr else ""}" cx="{xa(a):.1f}" cy="{ya(v):.1f}" r="5"/>')
    b.append(f'<text class="c-val" x="{xa(a)+dx:.1f}" y="{ya(v)+dy:.1f}" text-anchor="{anc}">{t}</text>')
b.append(f'<text class="c-lab" x="{xa(1980)+2:.1f}" y="{ya(4.2):.1f}">Mercado de frontera</text>')
b.append(f'<text class="c-lab c-lab-hi" x="{xa(1989)+6:.1f}" y="{ya(of[1989])-12:.1f}">Tasa oficial unificada</text>')
b.append(f'<text class="c-ax" x="{x0}" y="{H-22}">Pesos corrientes por bolívar. 1980–86: Fedesarrollo (1987), en Barrera (1989); 1983–86, fin de año.</text>')
b.append(f'<text class="c-ax" x="{x0}" y="{H-6}">1989–2000: tasas oficiales, promedio anual. Banco Mundial (WDI); cálculo propio.</text>')
guardar("bolivar", svg(W, H, "".join(b), "Cuántos pesos colombianos valía un bolívar venezolano, 1980-2000"))

# ---------------- 3. Desempleo: Colombia (anual) y Cúcuta (semestral) ----------------
W, H = 720, 320
x0, x1, pt, pb = 56, 690, 30, 250
d = macro["desempleo"].dropna()
cuc = pd.read_csv(P / "desempleo_cucuta_semestral.csv")
xa = lambda a: x0 + (a - 1991) * (x1 - x0) / 10   # la serie anual se ubica a mitad de año (a + 0,5)
ya = lambda v: pb - v * (pb - pt) / 22
b = []
for v in (0, 5, 10, 15, 20):
    b.append(f'<line class="{"c-zero" if v == 0 else "c-grid"}" x1="{x0}" x2="{x1}" y1="{ya(v):.1f}" y2="{ya(v):.1f}"/>')
    b.append(f'<text class="c-ax" x="{x0-8}" y="{ya(v)+4:.1f}" text-anchor="end">{v}%</text>')
for a in range(1991, 2001):
    b.append(f'<text class="c-ax c-mono" x="{xa(a+0.5):.1f}" y="{pb+22}" text-anchor="middle">{"’"+str(a)[2:] if a not in (1991, 2000) else a}</text>')
b.append(f'<rect class="c-life" x="{xa(1994):.1f}" y="{pb-4}" width="{xa(2001)-xa(1994):.1f}" height="4"><title>Años en la universidad</title></rect>')
pts = " ".join(f"{xa(a+0.5):.1f},{ya(v):.1f}" for a, v in d.items())
b.append(f'<polyline class="c-line" points="{pts}"/>')
for a, v in d.items():
    b.append(f'<circle class="c-dot-hit" cx="{xa(a+0.5):.1f}" cy="{ya(v):.1f}" r="9"><title>Colombia, {a}: {fmt(v)} %</title></circle>')
cpts = " ".join(f"{xa(r.anio_decimal):.1f},{ya(r.desempleo):.1f}" for r in cuc.itertuples())
b.append(f'<polyline class="c-dash" points="{cpts}"/>')
for r in cuc.itertuples():
    b.append(f'<circle class="c-dot-b" cx="{xa(r.anio_decimal):.1f}" cy="{ya(r.desempleo):.1f}" r="4.5"><title>Cúcuta, {r.periodo}: {fmt(r.desempleo)} %</title></circle>')
b.append(f'<text class="c-lab" x="{xa(1998.5)-8:.1f}" y="{ya(13.7)+4:.1f}" text-anchor="end">Cúcuta</text>')
b.append(f'<text class="c-lab c-lab-hi" x="{xa(1996.5)-6:.1f}" y="{ya(d[1996])-12:.1f}" text-anchor="end">Colombia</text>')
for a, t, anc, dx, dy in [(1993, "1993: 7,8 %", "start", 10, 18), (2000, "2000: 20,5 %", "end", -12, -10)]:
    v = d[a]
    b.append(f'<circle class="c-dot" cx="{xa(a+0.5):.1f}" cy="{ya(v):.1f}" r="5"/>')
    b.append(f'<text class="c-val" x="{xa(a+0.5)+dx:.1f}" y="{ya(v)+dy:.1f}" text-anchor="{anc}">{t}</text>')
b.append(f'<text class="c-ax" x="{x0}" y="{H-22}">Colombia: tasa anual, estimación de la OIT (Banco Mundial, WDI).</text>')
b.append(f'<text class="c-ax" x="{x0}" y="{H-6}">Cúcuta: área metropolitana, junio y diciembre; jun. 2000 provisional (DANE y Banco de la República, ICER).</text>')
guardar("desempleo", svg(W, H, "".join(b), "Tasa de desempleo en Colombia 1991-2000 y en Cúcuta 1998-2000"))

# ---------------- 4. Comparación central (barras horizontales) ----------------
comp = pd.read_csv(P / "censo_cohorte_comparacion.csv")
W = 760; row = 46; top = 20; H = top + row * len(comp) + 50
lab_w = 300; x0, x1 = lab_w, 700
xs = lambda v: x0 + v * (x1 - x0) / 40
nac = comp.loc[comp.grupo == "Colombia (total)", "pct_universitaria"].iloc[0]
b = []
for v in (0, 10, 20, 30, 40):
    b.append(f'<line class="c-grid" x1="{xs(v):.1f}" x2="{xs(v):.1f}" y1="{top-6}" y2="{top+row*len(comp)}"/>')
    b.append(f'<text class="c-ax c-mono" x="{xs(v):.1f}" y="{top+row*len(comp)+18}" text-anchor="middle">{v}%</text>')
b.append(f'<line class="c-ref" x1="{xs(nac):.1f}" x2="{xs(nac):.1f}" y1="{top-6}" y2="{top+row*len(comp)}"/>')
for i, r in comp.iterrows():
    y = top + i * row
    cls = "c-hi" if "San Calixto" in r.grupo else ("c-bar2" if "Catatumbo" in r.grupo else "c-bar")
    b.append(f'<text class="c-lab{" c-lab-hi" if "San Calixto" in r.grupo else ""}" x="{lab_w-12}" y="{y+row/2+4:.1f}" text-anchor="end">{escape(r.grupo)}</text>')
    b.append(f'<rect class="{cls}" x="{x0}" y="{y+9}" width="{xs(r.pct_universitaria)-x0:.1f}" height="{row-18}" rx="3">'
             f'<title>{escape(r.grupo)}: {fmt(r.pct_universitaria)} % con universidad o posgrado (base: {fmt(r.base, 0)} personas)</title></rect>')
    b.append(f'<text class="c-val" x="{xs(r.pct_universitaria)+8:.1f}" y="{y+row/2+5:.1f}">{fmt(r.pct_universitaria)} %</text>')
b.append(f'<text class="c-ref-t" x="{xs(nac)+6:.1f}" y="{top+row*len(comp)-6}">Promedio nacional: {fmt(nac)} %</text>')
b.append(f'<text class="c-ax" x="{x0-290}" y="{H-6}">% de la cohorte de 40 a 48 años (nacidos ~1970–1978) con universidad o posgrado. Fuente: DANE, CNPV 2018; cálculo propio.</text>')
guardar("comparacion", svg(W, H, "".join(b), "Porcentaje de la generación de mi papá con educación universitaria según origen"))

# ---------------- 5. Municipios del Catatumbo ----------------
cm = pd.read_csv(P / "censo_cohorte_catatumbo_por_mpio.csv").sort_values("pct_universitaria", ascending=False).reset_index(drop=True)
nds = comp.loc[comp.grupo == "Nacidos en Norte de Santander", "pct_universitaria"].iloc[0]
W = 720; row = 32; top = 16; H = top + row * len(cm) + 50
x0, x1 = 120, 640
xs = lambda v: x0 + v * (x1 - x0) / 25
b = []
for v in (0, 5, 10, 15, 20, 25):
    b.append(f'<line class="c-grid" x1="{xs(v):.1f}" x2="{xs(v):.1f}" y1="{top-4}" y2="{top+row*len(cm)}"/>')
    b.append(f'<text class="c-ax c-mono" x="{xs(v):.1f}" y="{top+row*len(cm)+18}" text-anchor="middle">{v}%</text>')
b.append(f'<line class="c-ref" x1="{xs(nds):.1f}" x2="{xs(nds):.1f}" y1="{top-4}" y2="{top+row*len(cm)}"/>')
for i, r in cm.iterrows():
    y = top + i * row; hi = r.grupo == "San Calixto"
    b.append(f'<text class="c-lab{" c-lab-hi" if hi else ""}" x="{x0-10}" y="{y+row/2+4:.1f}" text-anchor="end">{escape(r.grupo)}</text>')
    b.append(f'<rect class="{"c-hi" if hi else "c-bar2"}" x="{x0}" y="{y+6}" width="{xs(r.pct_universitaria)-x0:.1f}" height="{row-12}" rx="3">'
             f'<title>{escape(r.grupo)}: {fmt(r.pct_universitaria)} % (base: {int(r.base)} personas)</title></rect>')
    b.append(f'<text class="c-val" x="{xs(r.pct_universitaria)+6:.1f}" y="{y+row/2+4:.1f}">{fmt(r.pct_universitaria)} %</text>')
b.append(f'<text class="c-ref-t" x="{xs(nds)+5:.1f}" y="{top+row*len(cm)-6}">Norte de Santander: {fmt(nds)} %</text>')
b.append(f'<text class="c-ax" x="{10}" y="{H-6}">% con universidad o posgrado, nacidos ~1970–1978 en cada municipio. Fuente: DANE, CNPV 2018; cálculo propio.</text>')
guardar("catatumbo", svg(W, H, "".join(b), "Educación universitaria de la generación de mi papá en los municipios del Catatumbo"))

# ---------------- 6. Cohortes: nacional vs Norte de Santander ----------------
n1 = pd.read_csv(P / "censo_cohortes_B1_nacional.csv")
n2 = pd.read_csv(P / "censo_cohortes_B2_nortesantander.csv")
edades = list(n1.grupo)[::-1]  # de mayor a menor edad = de cohortes viejas a jóvenes
nacim = {g: f"{2018-int(g.split('-')[1])}–{str(2018-int(g.split('-')[0]))[2:]}" for g in edades}
W, H = 720, 320
x0, x1, pt, pb = 56, 600, 24, 250
xa = lambda i: x0 + i * (x1 - x0) / (len(edades) - 1)
ya = lambda v: pb - v * (pb - pt) / 25
b = []
i40 = edades.index("40-44")
paso = (x1 - x0) / (len(edades) - 1)
b.append(f'<rect class="c-crisis" x="{xa(i40)-paso/2:.1f}" y="{pt}" width="{paso:.1f}" height="{pb-pt}"><title>Grupo de mi papá: nacidos 1974–1978</title></rect>')
b.append(f'<text class="c-crisis-t" x="{xa(i40):.1f}" y="{pt+14}" text-anchor="middle">Su grupo</text>')
for v in (0, 5, 10, 15, 20, 25):
    b.append(f'<line class="{"c-zero" if v == 0 else "c-grid"}" x1="{x0}" x2="{x1}" y1="{ya(v):.1f}" y2="{ya(v):.1f}"/>')
    b.append(f'<text class="c-ax" x="{x0-8}" y="{ya(v)+4:.1f}" text-anchor="end">{v}%</text>')
for i, g in enumerate(edades):
    if i % 2 == 0:
        b.append(f'<text class="c-ax c-mono" x="{xa(i):.1f}" y="{pb+20}" text-anchor="middle">{nacim[g]}</text>')
for df, cls, nombre in [(n1, "c-line-b", "Colombia"), (n2, "c-line", "Nacidos en Norte de Santander")]:
    vals = [df.set_index("grupo").loc[g, "pct_universitaria"] for g in edades]
    pts = " ".join(f"{xa(i):.1f},{ya(v):.1f}" for i, v in enumerate(vals))
    b.append(f'<polyline class="{cls}" points="{pts}"/>')
    for i, v in enumerate(vals):
        b.append(f'<circle class="c-dot-hit" cx="{xa(i):.1f}" cy="{ya(v):.1f}" r="8"><title>{nombre}, nacidos {nacim[edades[i]]}: {fmt(v)} %</title></circle>')
    b.append(f'<text class="c-lab" x="{xa(len(edades)-1)+8:.1f}" y="{ya(vals[-1])+(-4 if cls=="c-line-b" else 14):.1f}">{"Colombia" if cls=="c-line-b" else "Norte de S."}</text>')
b.append(f'<text class="c-ax" x="{x0}" y="{pb+40}">Año de nacimiento →</text>')
b.append(f'<text class="c-ax" x="{x0}" y="{H-6}">% con universidad o posgrado, por año de nacimiento. Fuente: DANE, CNPV 2018; cálculo propio.</text>')
guardar("cohortes", svg(W, H, "".join(b), "Porcentaje con universidad por generación en Colombia y en Norte de Santander"))

print("ok:", sorted(p.name for p in FIGS.iterdir()))
