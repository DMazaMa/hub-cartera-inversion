# Datos

Ficheros de datos que usa la aplicación.

| Fichero | Origen | Uso |
| --- | --- | --- |
| Extracto de operaciones (`.xls` / `.xlsx`) | MyInvestor, Consulta de operaciones | Compras, ventas y dividendos de la cartera |
| `operaciones_ejemplo.csv` | Cartera de ejemplo con precios reales de cierre | Probar la app sin datos personales |
| `activos.csv` | Hecho a mano | Ticker de Yahoo, clase, sector y región de cada ISIN |
| Ficheros limpios y resúmenes (`.csv` / `.json`) | Generados por `src/etl.py` | Datos que pinta la app |

Los extractos reales van en `data/privado/`, que está en el `.gitignore`, para no subir datos personales al repositorio.
