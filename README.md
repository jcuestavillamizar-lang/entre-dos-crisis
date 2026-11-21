# Entre dos crisis

Sitio web del trabajo individual de Historia Familiar, Historia Económica de Colombia (Universidad de los Andes, 2026-2).
Autor: Juan Pablo Coronel Villamizar.

La historia de mi papá, hijo de campesinos desplazado del Catatumbo que se volvió ingeniero civil entre dos crisis
económicas, contrastada con microdatos del censo de 2018, series macroeconómicas y fuentes de la época.

## Estructura

- `docs/index.html`: el sitio publicado (GitHub Pages: rama `main`, carpeta `/docs`).
- `data/raw/`: datos originales.
  - `censo2018_*.txt`: tablas del Censo Nacional de Población y Vivienda 2018 exportadas del procesador REDATAM del DANE.
  - `consultas_redatam.txt`: los programas REDATAM exactos con los que se generó cada tabla.
  - `wb_wdi.json`: series del Banco Mundial (World Development Indicators).
  - `fedesarrollo_pesos_por_bolivar_1974_1986.csv`: tasa de cambio en la frontera (Fedesarrollo, 1987, en Barrera, 1989).
  - `icer_cucuta_desempleo.csv`: desempleo semestral de Cúcuta (DANE y Banco de la República, ICER 2000).
- `data/processed/`: datos limpios que alimentan las gráficas.
- `data/familia/voces.json`: citas de la entrevista que aparecen en el sitio.
- `scripts/procesar.py`: limpieza y cálculo de tasas.
- `scripts/graficas.py`: genera las gráficas en SVG.
- `scripts/construir_sitio.py`: arma `docs/index.html` a partir de `sitio/plantilla.html`.

## Reproducir

```
pip install pandas
python scripts/procesar.py
python scripts/graficas.py
python scripts/construir_sitio.py
```
