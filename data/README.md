# Datos

Ficheros de datos que usa la aplicación.

| Fichero | Origen | Uso |
| --- | --- | --- |
| Extracto de operaciones (`.xls` / `.xlsx`) | MyInvestor, Consulta de operaciones | Compras, ventas y dividendos de la cartera |
| Ficheros limpios y resúmenes (`.csv` / `.json`) | Generados por `src/etl.py` | Datos que pinta la app |

Los extractos reales van en `data/privado/`, que está en el `.gitignore`, para no subir datos personales al repositorio.
