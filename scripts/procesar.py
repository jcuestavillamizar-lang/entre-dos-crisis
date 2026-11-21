"""Limpieza y procesamiento de datos para el sitio "Entre dos crisis".

Entradas (data/raw):
  - wb_wdi.json: series del Banco Mundial (WDI) descargadas de su API.
  - censo2018_*.txt: tablas del Censo Nacional de Población y Vivienda 2018
    (DANE) generadas con el procesador REDATAM en línea.
Salidas (data/processed): CSV limpios que alimentan las gráficas.

Uso: python scripts/procesar.py
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

NIVELES = ["Preescolar", "Primaria", "Secundaria", "Media académica", "Media técnica",
           "Normalista", "Técnica o tecnológica", "Universitario", "Posgrado",
           "Ninguno", "No informa", "Total"]


def num(x: str) -> float:
    """'1 357 988' -> 1357988; '-' -> 0 (REDATAM usa '-' para celdas vacías)."""
    x = x.strip()
    return 0.0 if x in ("-", "") else float(x.replace(" ", "").replace(" ", ""))


def leer_tabla(path: Path, seccion: str | None = None) -> pd.DataFrame:
    """Lee filas 'etiqueta | n1 | ... | total' de un archivo exportado de REDATAM."""
    filas, activa = [], seccion is None
    for linea in path.read_text(encoding="utf-8").splitlines():
        if linea.startswith("##"):
            activa = seccion is not None and seccion in linea
            continue
        if not activa or linea.startswith("#") or "|" not in linea:
            continue
        partes = [p.strip() for p in linea.split("|")]
        if len(partes) != 13 or not re.search(r"\d", partes[-1]):
            continue  # encabezados
        filas.append([partes[0]] + [num(p) for p in partes[1:]])
    return pd.DataFrame(filas, columns=["grupo"] + NIVELES)


def tasas(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula tasas sobre la población que informa su nivel educativo."""
    base = df["Total"] - df["No informa"]
    df = df.copy()
    df["base"] = base
    df["pct_universitaria"] = 100 * (df["Universitario"] + df["Posgrado"]) / base
    df["pct_superior"] = 100 * (df["Técnica o tecnológica"] + df["Universitario"] + df["Posgrado"]) / base
    df["pct_solo_primaria_o_menos"] = 100 * (df["Preescolar"] + df["Primaria"] + df["Ninguno"]) / base
    return df


# ---------- 1. Series macro (Banco Mundial) ----------
wdi = json.loads((RAW / "wb_wdi.json").read_text())
serie = lambda k: pd.Series({int(a): v for a, v in wdi[k]}, name=k)
macro = pd.concat([
    serie("COL_NY.GDP.MKTP.KD.ZG").rename("pib_crec"),
    serie("COL_NV.IND.TOTL.KD.ZG").rename("industria_crec"),
    serie("COL_SL.UEM.TOTL.ZS").rename("desempleo"),
    serie("COL_PA.NUS.FCRF").rename("cop_por_usd"),
    serie("VEN_PA.NUS.FCRF").rename("ves_por_usd"),
], axis=1).loc[1980:2000]
# El Banco Mundial reporta el bolívar en unidades posteriores a la reconversión de 2008
# (1 bolívar fuerte = 1.000 bolívares). Se vuelve a bolívares de la época.
macro["bs_por_usd"] = macro["ves_por_usd"] * 1000
macro["cop_por_bolivar"] = macro["cop_por_usd"] / macro["bs_por_usd"]

# Pesos por bolívar para la gráfica de frontera:
#  - 1980-1986: serie de Fedesarrollo (1987) publicada en Barrera (1989), que refleja el mercado
#    de la frontera después del Viernes Negro (feb. 1983); desde 1983, valores de fin de año.
#  - 1987-1988: sin serie comparable (tasas múltiples en Venezuela, RECADI, hasta marzo de 1989).
#  - 1989-2000: tasa oficial del Banco Mundial. Desde marzo de 1989 la tasa venezolana se unificó
#    y se fijó en el mercado (salvo el control de cambios de mediados de 1994 a abril de 1996).
fed = pd.read_csv(RAW / "fedesarrollo_pesos_por_bolivar_1974_1986.csv", comment="#").set_index("anio")
macro["cop_por_bolivar_frontera"] = fed["cop_por_bolivar"].reindex(macro.index).where(macro.index <= 1986)
macro["tcr_peso_bolivar_1975_100"] = fed["tcr_peso_1975_100"].reindex(macro.index)
macro["cop_por_bolivar_oficial_unificada"] = macro["cop_por_bolivar"].where(macro.index >= 1989)
macro.index.name = "anio"
macro.round(3).to_csv(OUT / "macro_1980_2000.csv")

# Desempleo semestral de Cúcuta (ICER 2000)
icer = pd.read_csv(RAW / "icer_cucuta_desempleo.csv", comment="#")
icer.to_csv(OUT / "desempleo_cucuta_semestral.csv", index=False)

# ---------- 2. Censo 2018: cohorte nacida 1970-1978 ----------
dptos = tasas(leer_tabla(RAW / "censo2018_A_dptonac_x_nivel_40a48.txt"))
dptos.round(4).to_csv(OUT / "censo_cohorte_por_dpto_nacimiento.csv", index=False)

cata_mpio = tasas(leer_tabla(RAW / "censo2018_D1_catatumbo_40a48.txt", "T2"))
cata_mpio["grupo"] = cata_mpio["grupo"].str.split("_", n=1).str[1].str.title()
cata_mpio.round(4).to_csv(OUT / "censo_cohorte_catatumbo_por_mpio.csv", index=False)

cata_mig = tasas(leer_tabla(RAW / "censo2018_D1_catatumbo_40a48.txt", "T1"))
cata_cuc = tasas(leer_tabla(RAW / "censo2018_D1_catatumbo_40a48.txt", "T3"))
cucuta = tasas(leer_tabla(RAW / "censo2018_D2_cucuta_40a48.txt", "T1"))

g = lambda df, nombre: df.loc[df["grupo"].str.startswith(nombre)].iloc[0]
grupos = [
    ("Colombia (total)", g(dptos, "Total")),
    ("Nacidos en Bogotá", g(dptos, "11_")),
    ("Nacidos en Norte de Santander", g(dptos, "54_")),
    ("Nacidos y residentes en Cúcuta", g(cucuta, "Nacido en Cúcuta")),
    ("Catatumbo: migraron a otro municipio", g(cata_mig, "Migró")),
    ("Catatumbo: llegaron a Cúcuta", g(cata_cuc, "Catatumbo")),
    ("Catatumbo: se quedaron", g(cata_mig, "Se quedó")),
    ("Nacidos en San Calixto", g(cata_mpio, "San Calixto")),
]
cols = ["base", "pct_universitaria", "pct_superior", "pct_solo_primaria_o_menos"]
comparacion = pd.DataFrame([{"grupo": n, **{c: fila[c] for c in cols}} for n, fila in grupos])
comparacion.round(4).to_csv(OUT / "censo_cohorte_comparacion.csv", index=False)

# ---------- 3. Censo 2018: grupos de edad (cohortes) ----------
for nombre in ("B1_nacional", "B2_nortesantander"):
    p = RAW / f"censo2018_{nombre}_edad_x_nivel.txt"
    if p.exists():
        tasas(leer_tabla(p)).round(4).to_csv(OUT / f"censo_cohortes_{nombre}.csv", index=False)

print(macro.round(2).to_string())
print(comparacion.round(1).to_string())
print(cata_mpio[["grupo", "base", "pct_universitaria", "pct_superior"]].round(1).to_string())
