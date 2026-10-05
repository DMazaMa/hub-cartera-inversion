Hub de Cartera de Inversión

Trabajo final de la asignatura Desarrollo de Aplicaciones para la Visualización de Datos (DAVD).

Aplicación en Python para el seguimiento centralizado de la cartera personal de inversión. Reúne en un único cuadro de mando las posiciones, las operaciones, la diversificación, las rentabilidades históricas, el riesgo estimado y las noticias y resultados de las empresas en cartera.

Descripción

Invertir el capital personal es probablemente la decisión financiera más responsable que puede tomar alguien. Aun así, mucha gente no lo hace por la barrera de acceso. Le parece complicado, no sabe cómo seguir lo que tiene o la información está repartida en demasiados sitios.

Quien ya invierte tiene los movimientos en el bróker (por ejemplo, MyInvestor), los precios en Yahoo Finance, los resultados y hechos relevantes en la CNMV y en las webs de relación con inversores, y las noticias en otros medios. Las apps de los brókers enseñan el saldo y poco más.

Con este proyecto quiero construir un hub único donde cualquier persona pueda introducir sus inversiones y seguir su cartera en un solo sitio, con gráficas y tablas interactivas como las que hacemos en el curso. El usuario introduce o importa sus operaciones y la app calcula automáticamente posiciones, plusvalías y rentabilidades. Además añade noticias clasificadas por sentimiento y un modelo de predicción del riesgo. La idea es que sea una herramienta útil y también un incentivo para que más gente se anime a invertir.

Objetivos
Centralizar en un único hub toda la información de la cartera personal.
Calcular posiciones, precio medio, plusvalías, dividendos y rentabilidad por posición y de la cartera completa.
Analizar la diversificación por sector, geografía, divisa y clase de activo.
Mostrar la rentabilidad histórica frente a un índice de referencia y el histórico de aportaciones.
Mantener al usuario al día con noticias, resultados y hechos relevantes de sus posiciones.
Estimar el riesgo de la cartera y agrupar las posiciones por perfil con modelos de scikit-learn.
Desplegar la aplicación en Render para que sea accesible desde cualquier sitio.
Reducir la barrera de acceso a la inversión con una herramienta clara y visual.
(Ampliación) Añadir un chat de IA para conversar sobre la cartera.
Usuarios
Inversor particular que ya invierte y quiere seguir su cartera sin hojas de cálculo.
Persona que todavía no invierte y necesita una herramienta sencilla que le quite el miedo a empezar.
Páginas de la aplicación
Página	Contenido
Cartera	Títulos, precio medio, precio actual, valor de mercado, plusvalía en € y %, peso y rentabilidad por posición
Operaciones	Registro de compras, ventas, dividendos y comisiones con filtros por fecha, activo y tipo
Diversificación	Reparto por sector, geografía, divisa y clase de activo
Rentabilidades	Evolución del valor, rentabilidad mensual, anual y YTD, comparación con índice, volatilidad y drawdown
Histórico de inversión	Capital aportado frente a valor de la cartera
Noticias y resultados	Noticias, hechos relevantes de la CNMV y resultados con su sentimiento
Predicción y riesgo	Volatilidad estimada del mes siguiente y agrupación de activos por perfil rentabilidad-riesgo
Chat IA (opcional)	Asistente para preguntar sobre la cartera en lenguaje natural
Fuentes de datos
Operaciones del usuario. Entrada manual o importación de ficheros CSV o Excel. MyInvestor no ofrece una API pública, así que la conexión se hace importando el extracto de movimientos que permite descargar.
Precios de mercado. Yahoo Finance para precios históricos y actuales, dividendos y datos básicos de cada activo (sector, país y divisa). Fiscal AI como fuente complementaria de fundamentales y resultados, según el acceso a su API.
Resultados y hechos relevantes. Publicaciones de la CNMV y páginas oficiales de relación con inversores de las empresas.
Noticias. Noticias asociadas a cada ticker obtenidas desde Yahoo Finance.
Pipeline de procesamiento

Sigo el esquema visto en clase: datos → limpieza → KPIs → modelo → visualización.

Ingesta (src/etl.py). Lectura de operaciones con una función única de carga para CSV, JSON y Excel. Descarga de precios, metadatos, noticias y publicaciones con requests.
Validación y limpieza con pandas. Normalización de columnas, conversión de tipos con to_numeric(errors="coerce") y to_datetime, eliminación de duplicados, separación de filas válidas y erróneas y conversión de divisas a euros.
Cálculo de KPIs. Posiciones y precio medio, valor de mercado, plusvalías realizadas y latentes, dividendos y pesos. Uso groupby y agg para la diversificación y series temporales para la rentabilidad acumulada, la volatilidad y el drawdown.
Exportación. Los datos limpios y los resúmenes se guardan en CSV o JSON y se pueden regenerar en cualquier momento.
Visualización (src/graphics.py y app.py). Gráficas Plotly y tablas en Dash con callbacks y componentes core (dropdowns, date pickers y checklists) para filtrar por activo, periodo o tipo de operación.
API de sentimiento (api/app.py). API REST en Flask, basada en la API de sentimiento vista en clase, que clasifica el titular de cada noticia con un modelo de Hugging Face Transformers. La app Dash la consume con requests.
Modelo de predicción

El modelo está en src/model.py y sigue el patrón del curso: cargar datos → DataFrame → X/y → split → fit → métricas en test → guardar con joblib → servir en Dash.

Regresión de riesgo. Predigo la volatilidad del mes siguiente de la cartera y de cada posición a partir de rendimientos y volatilidades pasadas en ventanas móviles. Uso ElasticNet y lo evalúo con MSE, RMSE, MAE y R². El split respeta el orden temporal para evitar fuga de información.
Clustering de posiciones. Agrupo los activos según su perfil de rentabilidad y riesgo con K-Means, eligiendo el número de grupos con el método del codo y el silhouette score. Así se ve si la diversificación es real o solo aparente.

El modelo da una estimación de riesgo y no una recomendación de inversión.

Chat de IA (ampliación)

Si me da tiempo, añadiré un chat que use un LLM con acceso a los datos de la cartera mediante herramientas (function calling), aplicando lo que aprendí en Agentic AI en UIUC. El asistente podrá consultar posiciones, rentabilidades y noticias para responder preguntas como "¿cuál ha sido mi mejor posición este año?" o "¿qué peso tengo en tecnología?".

Tecnologías
Uso	Tecnología
Lenguaje	Python 3.12
Entorno	venv, Jupyter Notebook y Google Colab
Datos	pandas, NumPy, openpyxl y requests
Visualización	Plotly y Dash
Modelos	scikit-learn y joblib
API	Flask, Flask-RESTful y Hugging Face Transformers
Despliegue	Render con gunicorn
Versionado	Git y GitHub
Estructura del proyecto
plaintext
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
├── data/                # Datos de ejemplo (no se suben datos personales)
├── notebooks/           # Exploración y prototipos
├── app.py               # Aplicación Dash principal
├── requirements.txt     # Dependencias de Python
├── Procfile             # Comando de inicio en Render
├── render.yaml          # Configuración de Render
├── .gitignore
└── README.md
Instalación y ejecución en local
bash
git clone https://github.com/<usuario>/hub-cartera-inversion.git
cd hub-cartera-inversion

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

python app.py

La app queda disponible en http://127.0.0.1:8050/

Para arrancar la API de sentimiento:

bash
cd api
pip install -r requirements.txt
python app.py

La API queda disponible en http://127.0.0.1:5000/

Despliegue

La aplicación se despliega en Render conectando el repositorio de GitHub. Render instala las dependencias con pip install -r requirements.txt y arranca la app con gunicorn app:server, usando el objeto server que expone Dash.

Plan de trabajo inicial
Fase	Tareas
1. Preparación	Crear el repositorio, el entorno virtual, la estructura de carpetas y el .gitignore
2. Datos	Definir el formato de operaciones, la importación CSV/Excel y la conexión con Yahoo Finance
3. ETL y KPIs	Limpieza de datos y cálculo de posiciones, plusvalías, rentabilidades y diversificación
4. Dashboard	Páginas de cartera, operaciones, diversificación, rentabilidades e histórico con callbacks
5. Noticias y CNMV	Descarga de noticias y publicaciones y API Flask de sentimiento
6. Modelos	Regresión de volatilidad y clustering de posiciones integrados en Dash
7. Despliegue	Despliegue en Render y pruebas
8. Ampliación	Chat de IA sobre la cartera
9. Cierre	Documentación, limpieza del código y presentación final
Aviso

Esta aplicación es una herramienta de seguimiento y análisis. No constituye asesoramiento financiero.

Autor

Diego
