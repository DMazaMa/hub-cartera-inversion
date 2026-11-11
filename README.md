# Hub de Cartera de Inversión

Trabajo final de la asignatura **Desarrollo de Aplicaciones para la Visualización de Datos (DAVD)**.

Aplicación en Python para el seguimiento centralizado de la cartera personal de inversión. Reúne en un único cuadro de mando las posiciones, las operaciones, la composición y las rentabilidades de la cartera, y una ficha por cada activo con su histórico, sus noticias y su riesgo estimado.

## Descripción

Invertir el capital personal es probablemente la decisión financiera más responsable que puede tomar alguien. Aun así, mucha gente no lo hace por la barrera de acceso. Le parece complicado, no sabe cómo seguir lo que tiene o la información está repartida en demasiados sitios.

Quien ya invierte tiene los movimientos en el bróker (por ejemplo, MyInvestor), los precios en Yahoo Finance, los resultados y hechos relevantes en la CNMV y en las webs de relación con inversores, y las noticias en otros medios. Las apps de los brókers enseñan el saldo y poco más.

Con este proyecto quiero construir un hub único donde cualquier persona pueda cargar sus inversiones y seguir su cartera en un solo sitio, con gráficas y tablas interactivas como las que hacemos en el curso. El usuario importa el extracto de operaciones que descarga de su bróker y la app calcula automáticamente posiciones, plusvalías y rentabilidades. Además añade noticias clasificadas por sentimiento y un modelo de predicción del riesgo. La idea es que sea una herramienta útil y también un incentivo para que más gente se anime a invertir.

## Objetivos

- Centralizar en un único hub toda la información de la cartera personal.
- Importar las operaciones desde el extracto de MyInvestor y calcular posiciones, precio medio, plusvalías, dividendos y rentabilidad por posición y de la cartera completa.
- Analizar la composición de la cartera por sector, geografía, divisa y clase de activo.
- Mostrar la rentabilidad histórica frente a un índice de referencia y frente al capital aportado.
- Tener una ficha por activo con su histórico, sus datos principales y sus noticias.
- Estimar el riesgo de cada posición y agrupar las posiciones por perfil con modelos de scikit-learn.
- Desplegar la aplicación en Render para que sea accesible desde cualquier sitio, también desde el móvil.
- Reducir la barrera de acceso a la inversión con una herramienta clara y visual.

## Usuarios

- **Inversor particular** que ya invierte y quiere seguir su cartera sin hojas de cálculo.
- **Persona que todavía no invierte** y necesita una herramienta sencilla que le quite el miedo a empezar.

## Páginas de la aplicación

La página de inicio funciona como menú. Desde ella se entra a cada sección con botones.

| Página | Contenido |
| --- | --- |
| Inicio | Cinta con lo que sube o baja cada posición en el día, resumen de la cartera, botones a cada sección y últimas noticias |
| Cartera | Títulos, precio medio, precio actual, valor de mercado, plusvalía en € y %, peso de cada posición y noticias de la cartera |
| Composición | Reparto por sector, geografía, divisa y clase de activo, y agrupación de posiciones por perfil rentabilidad-riesgo |
| Rentabilidad | Evolución del valor frente al capital aportado, rentabilidad mensual, anual y YTD, comparación con índice, volatilidad y drawdown |
| Operaciones | Registro de compras, ventas, dividendos y comisiones con filtros por fecha, activo y tipo |
| Ficha de activo | Histórico de precio, datos de la empresa o del fondo, noticias con su sentimiento y volatilidad estimada del mes siguiente |

## Fuentes de datos

- **Operaciones del usuario.** MyInvestor no ofrece una API pública, así que la conexión se hace importando el extracto en Excel que se descarga desde su web, en la consulta de operaciones de cada tipo de producto (fondos, acciones y ETF).
- **Datos de mercado y de empresa.** API de Fiscal AI como fuente principal: perfil de la empresa, precios históricos, fundamentales, dividendos y noticias.
- **Fondos y ETF.** Como no son empresas, sus precios se completan con Yahoo Finance.

## Pipeline de procesamiento

Sigo el esquema visto en clase: datos → limpieza → KPIs → modelo → visualización.

1. **Ingesta** (`src/etl.py`). Lectura del extracto de MyInvestor con una función única de carga para CSV, JSON y Excel. Descarga de precios, datos de empresa y noticias desde la API de Fiscal AI con `requests`.
2. **Validación y limpieza** con pandas. Normalización de columnas, conversión de tipos con `to_numeric(errors="coerce")` y `to_datetime`, eliminación de duplicados, separación de filas válidas y erróneas y conversión de divisas a euros.
3. **Cálculo de KPIs.** Posiciones y precio medio, valor de mercado, plusvalías realizadas y latentes, dividendos y pesos. Uso `groupby` y `agg` para la composición y series temporales para la rentabilidad acumulada, la volatilidad y el drawdown.
4. **Exportación.** Los datos limpios y los resúmenes se guardan en CSV o JSON y se pueden regenerar en cualquier momento.
5. **Visualización** (`src/graphics.py` y `app.py`). Gráficas Plotly y tablas en Dash con callbacks y componentes core (botones, dropdowns, date pickers y checklists) para moverse entre secciones y filtrar por activo, periodo o tipo de operación.
6. **API de sentimiento** (`api/app.py`). API REST en Flask, basada en la API de sentimiento vista en clase, que clasifica el titular de cada noticia con un modelo de Hugging Face Transformers. La app Dash la consume con `requests`.

## Modelo de predicción

El modelo está en `src/model.py` y sigue el patrón del curso: cargar datos → DataFrame → X/y → split → fit → métricas en test → guardar con `joblib` → servir en Dash.

- **Regresión de riesgo.** Predigo la volatilidad del mes siguiente de cada posición a partir de rendimientos y volatilidades pasadas en ventanas móviles. Uso ElasticNet y lo evalúo con MSE, RMSE, MAE y R². El split respeta el orden temporal para evitar fuga de información. Se ve en la ficha de cada activo.
- **Clustering de posiciones.** Agrupo los activos según su perfil de rentabilidad y riesgo con K-Means, eligiendo el número de grupos con el método del codo y el silhouette score. Así se ve si la diversificación es real o solo aparente. Se ve en la página de composición.

El modelo da una estimación de riesgo y no una recomendación de inversión.

## Tecnologías

| Uso | Tecnología |
| --- | --- |
| Lenguaje | Python 3.12 |
| Entorno | venv, Jupyter Notebook y Google Colab |
| Datos | pandas, NumPy, openpyxl y requests |
| Fuentes externas | API de Fiscal AI y Yahoo Finance |
| Visualización | Plotly y Dash |
| Modelos | scikit-learn y joblib |
| API | Flask, Flask-RESTful y Hugging Face Transformers |
| Despliegue | Render con gunicorn |
| Versionado | Git y GitHub |

## Estructura del proyecto

```plaintext
hub-cartera-inversion/
│
├── src/
│   ├── __init__.py
│   ├── etl.py           # Carga, limpieza y cálculo de KPIs
│   ├── graphics.py      # Gráficas Plotly
│   └── model.py         # Entrenamiento e inferencia de modelos
│
├── api/
│   ├── app.py           # API Flask de sentimiento de noticias
│   └── requirements.txt
│
├── data/                # Datos de ejemplo (los extractos reales no se suben)
├── notebooks/           # Exploración y prototipos
├── app.py               # Aplicación Dash principal
├── requirements.txt     # Dependencias de Python
├── Procfile             # Comando de inicio en Render
├── render.yaml          # Configuración de Render
├── runtime.txt          # Versión de Python
├── .gitignore
└── README.md
```

## Instalación y ejecución en local

```bash
git clone https://github.com/DMazaMa/hub-cartera-inversion.git
cd hub-cartera-inversion

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

python app.py
```

La app queda disponible en http://127.0.0.1:8050/

La API de Fiscal AI necesita una clave. Se guarda como variable de entorno y nunca se sube al repositorio.

Para arrancar la API de sentimiento:

```bash
cd api
pip install -r requirements.txt
python app.py
```

La API queda disponible en http://127.0.0.1:5000/

## Despliegue

La aplicación se despliega en Render conectando el repositorio de GitHub. Render instala las dependencias con `pip install -r requirements.txt` y arranca la app con `gunicorn app:server`, usando el objeto `server` que expone Dash. La clave de Fiscal AI se añade como variable de entorno del servicio en Render.

## Plan de trabajo

| Fase | Tareas | Estado |
| --- | --- | --- |
| 1. Preparación | Repositorio, estructura de carpetas, `.gitignore` y plantilla de despliegue en Render | Hecho |
| 2. Datos | Exportación del extracto de MyInvestor, lectura y limpieza, y conexión con la API de Fiscal AI | Pendiente |
| 3. KPIs | Posiciones, plusvalías, rentabilidades y composición | Pendiente |
| 4. Dashboard | Inicio con menú y cinta de cotizaciones, Cartera, Composición, Rentabilidad y Operaciones | Pendiente |
| 5. Ficha de activo | Histórico, datos de la empresa o del fondo y noticias con su sentimiento | Pendiente |
| 6. Modelos | Volatilidad del mes siguiente y agrupación de posiciones con K-Means | Pendiente |
| 7. Despliegue | Despliegue en Render, adaptación al móvil y pruebas | Pendiente |
| 8. Ampliación | Chat de IA sobre la cartera, si da tiempo | Pendiente |
| 9. Cierre | Documentación, limpieza del código y presentación final | Pendiente |

## Aviso

Esta aplicación es una herramienta de seguimiento y análisis. No constituye asesoramiento financiero.

## Autor

Diego Luis de Mazarredo Martín
