# Mortalidad no fetal en Colombia, 2019

Este proyecto se realizo para llevar a cabo una visualizacion de una Aplicación web interactiva para análizar las defunciones y  mortalidad no fetal en Colombia durante el año 2019, esta aplicacion fue construida con Python, Plotly y Dash a partir de las Estadísticas Vitales del DANE, dnde se sacaron datos reales para su realizacion. Con estas aplicaciones se genero un tablero donde se presentan diferentes tipos de graficos para msotrar bases de datos sobre la informacion recolectada.

- **Aplicación desplegada:** https://dashboar-mortalidad-colombia.onrender.com
- **Repositorio:** https://github.com/Sebasbarrioss/dashboar-mortalidad-colombia

## Introducción del proyecto

Este proyecto es un tablero web con visualizaciones interactivas sobre las defunciones no fetales registradas en Colombia en 2019. Integrando cuatro fuentes oficiales del DANE: los micro datos de mortalidad, el catálogo de causas de muerte CIE-10, la División Político-Administrativa (Divipola) y las proyecciones de población municipal. Todo esto en relación al mismo año y sacadas de hojas de Excel, el dashboard muestra el análisis de diferentes factores, como edad, sexo, mes, departamento, casusas y municipios, en el que por medio de gráficos construidos con Plotly, en el que sirven con Dash; está desplegada en un sitio público en Render y se puede consultar en línea de forma interactiva.
## Objetivo

Desarrollar un aplicación web interactiva que permita identificar y analizar patrones demográficos, temporales y territoriales de la mortalidad en Colombia, respondiendo preguntas como:

- ¿En qué departamentos se concentran las muertes?
- ¿Cómo cambia el número de muertes a lo largo del año?
- ¿Quiénes mueren, según sexo y etapa del ciclo de vida?
- ¿Cuáles son las principales causas de muerte?
- ¿En qué municipios se concentran los homicidios con arma de fuego y cuáles tienen la menor tasa de mortalidad?

## Estructura del proyecto

```
.
├── app.py                                  # Aplicación Dash: carga de datos, gráficos y diseño de la página
├── requirements.txt                        # Dependencias con versiones fijas
├── README.md
├── .gitignore
├── NoFetal2019_CE_15-03-23.xlsx            # Microdatos de mortalidad no fetal 2019 (DANE)
├── CodigosDeMuerte_CE_15-03-23.xlsx        # Catálogo de causas de muerte CIE-10 (DANE)
├── Divipola_CE_.xlsx                       # División político-administrativa (DANE)
├── PPED-AreaMun-2018-2042_VP.xlsx          # Proyecciones de población municipal (DANE)
└── col_departamentos.geojson               # Polígonos de los departamentos para el mapa
```
-  app.py  : Contiene el código principal y la construcción del dashboard
-  requirements.txt  : Están las bibliotecas instaladas de paython información
-  README.md  : Explicación de un archivo paso a paso e informe del proyecto
-  gitignore  : Código que se utilizaron tras activación de bibliotecas y confirmación
-  NoFetal2019_CE_15-03-23.xlsx  : Donde está la información se parada por sexo, género y demás variables 
-  CodigosDeMuerte_CE_15-03-23.xlsx  : Causas de Muerte y códigos por fallecimientos
-  PPED-AreaMun-2018-2042_VP.xlsx   : Departamentos y municipios
-  col_departamentos.geojson   : Es un archivo instalado para la construcción del mapa de Colombia
-  Divipola_CE_.xlsx   : Proyección municipal en Colombia de la población para el 2019

Cómo funciona `app.py`:

1. **Carga de datos:** lee los Excel de la raíz del repositorio con pandas (hoja `No_Fetales_2019` para las defunciones).
2. **Preparación:** une las defunciones con Divipola (nombre de departamento y municipio por `COD_DANE`) y con el catálogo CIE-10 (nombre de la causa por `COD_MUERTE`). Toma la población de 2019 (área geográfica "Total") para calcular tasas por municipio.
3. **Gráficos:** genera con Plotly Express las figuras de líneas, barras, barras apiladas, circular y mapa coroplético; la tabla de causas se arma con componentes HTML de Dash.
4. **Diseño:** define el encabezado, los indicadores generales y las tarjetas de gráficos en una cuadrícula adaptable a pantallas pequeñas.
5. **Servidor:** expone `server = app.server` para que gunicorn sirva la aplicación en Render.

## Requisitos

Para la realizacion del proyecto, se utilizaron Python y Visual Studio Code, ademas de la creacion de cuenta en Github y Render. Con las bibliotecas necesarias para el analiss de datos.

Versiones fijadas en `requirements.txt`:

| Librería | Versión |
|---|---|
| dash | 4.4.1 |
| plotly | 7.1.0 |
| pandas | 2.2.3 |
| openpyxl | 3.1.5 |
| gunicorn | 26.2.0 |

Además se requiere Python 3.11.6 de 64 o superior. `openpyxl` es necesaria porque los datos se leen directamente desde archivos Excel.

## Software

- Python como lenguaje de programación
- Dash (aplicación web y diseño de la página de forma interactiva)
- Plotly Express (gráficos interactivos)
- pandas y openpyxl (lectura de archivos de Excel, unión y agrupación de los datos)
- gunicorn (servidor de producción)
- Git y GitHub (control de versiones)
- Render (plataforma como servicio, PaaS)

## Instalación

Para ejecutar la aplicación localmente:
Se inicia con la intalacion de Python y Visual Studio Code, despues la intalacion de bibliotecas

python -m pip install pandas==2.2.3 dash==4.4.1 plotly openpyxl gunicorn

Despues comando para agregar información

```bash
git clone https://github.com/Sebasbarrioss/dashboar-mortalidad-colombia.git
cd dashboar-mortalidad-colombia
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Luego abrir en el navegador la dirección que muestra la terminal (por defecto `http://127.0.0.1:8050`). Los archivos de datos ya están en el repositorio, por lo que no hace falta descargar nada más.

## Despliegue en Render

1. Subir el proyecto a un repositorio público de GitHub, incluyendo los archivos de datos y `col_departamentos.geojson`.
2. Crear una cuenta en [Render](https://render.com) o conectar con la cuenta de GitHub.
3. Seleccionar **New > Web Service** y elegir el repositorio `dashboar-mortalidad-colombia`.
4. Configurar el servicio:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server`
5. Crear el servicio y esperar a que termine el despliegue. Render entrega la URL pública: https://dashboar-mortalidad-colombia.onrender.com

Notas:

- En el plan gratuito de Render el servicio se suspende por inactividad, por lo que la primera visita puede tardar un momento en cargar.
- La aplicación lee varios archivos Excel al iniciar, por lo que el arranque tarda más que en una aplicación con datos en CSV.
- Cada archivo que se modifique en Github se ve actualizado, pero si hay algun problema se ve en Logs para modificarlo

## Visualizaciones y explicación de resultados

En el dashboard se integran diferentes visualizaciones interactivas, mediante gráficos que al pasar el cursor se muestran los valores exactos. El tablero abre con tres indicadores: **244.355 defunciones** registradas, **33 departamentos** y **1.110 municipios** identificados. Estos son basados en archivos de Excel suministrados por docente o también por medio del sitio web oficial del DANE.

### 1. Mapa de defunciones por departamento


![Mapa de defunciones](Imagen/mapa_defunciones.png)

Se realiza un mapa coroplético, interactivo que colorea cada departamento según su número de defunciones. Bogotá D.C. (38.760), Antioquia (34.473) y Valle del Cauca (28.443) concentran más de 41 % de las muertes del país, en línea con su tamaño de población. En el extremo opuesto están Vaupés (87), Guainía (115) y Vichada (188).

### 2. Gráfico de líneas: defunciones por mes

![Defunciones por mes](img/defunciones_mensuales.png)

Se realiza un grafico de lineas que represente del total de muertes por mes en Colombia, donde la serie se mueve entre 18.000 y 21.700 muertes por mes. Febrero es el mínimo (17.974), en parte por ser el mes más corto, y diciembre el máximo (21.678). Enero (21.354) y julio (21.372) también son meses altos.

### 3. Gráfico de barras: cinco municipios con más homicidios por arma de fuego

![Municipios con más homicidios](Imagen/homicidios_arma_fuego.png)

Se lleva a cabo un gráfico de barras donde se visualice las 5 ciudades más violentas, se considera las defunciones de manera "homicidio" con códigos X93, X94 y X95 (agresión con disparo de armas de fuego y casos no especificados). Santiago de Cali encabeza con 971 casos, seguida de Bogotá D.C. (613), Medellín (429), Barranquilla (260) y San José de Cúcuta (206). Cada barra se colorea por departamento.

### 4. Gráfico circular: diez municipios con menor tasa de mortalidad

![Municipios con menor tasa de mortalidad](Imagen/menor_tasa_mortalidad.png)

Para medir la mortalidad de forma comparable entre municipios de distinto tamaño se toma un gráfico circular, que usa la **tasa de defunciones por cada 1.000 habitantes**. Se calcula dividiendo las defunciones de cada municipio entre su población de 2019 (proyecciones del DANE) y se muestran los diez municipios con la tasa más baja. Se tomó más información del cena como la proyección según municipio, para ser más exacto en cuanto a los resultados, ya que se necesitaba la variable de cantidad de población para tener resultados más óptimos en el análisis. 

Los diez municipios son Alto Baudó (0,04 por 1.000 habitantes), Nuquí (0,06), San Fernando (0,08), Margarita (0,09), Chimá (0,11), La Tola (0,13), Bajo Baudó (0,16), Nóvita (0,22), Unguía (0,23) y Carmen del Darién (0,26). Seis de ellos están en Chocó, dos en Bolívar, uno en Córdoba y uno en Nariño. Para comparar, la tasa promedio de los 1.110 municipios es de 3,0 por 1.000 habitantes. Valores tan bajos pueden reflejar subregistro de defunciones, por lo que conviene interpretarlos con cautela. Los porcentajes que se ven en cada porción indican su peso relativo dentro de estos diez municipios; el valor de la tasa aparece al pasar el cursor.

### 5. Tabla: diez principales causas de muerte

![Principales causas de muerte](Imagen/principales_causas.png)

| Código | Causa de muerte | Defunciones |
|---|---|---|
| I219 | Infarto agudo del miocardio, sin otra especificacion | 35.088 |
| J449 | Enfermedad pulmonar obstructiva cronica, no especificada | 7.210 |
| J440 | Enfermedad pulmonar obstructiva cronica con infeccion aguda de las vias respiratorias inferiores | 6.445 |
| J189 | Neumonia, no especificada | 5.798 |
| C169 | Tumor maligno del estomago, parte no especificada | 5.125 |
| C349 | Tumor maligno de los bronquios o del pulmon, parte no especificada | 4.438 |
| X954 | Agresion con disparo de otras armas de fuego, y las no especificadas, calles y carreteras | 4.396 |
| C509 | Tumor maligno de la mama, parte no especificada | 3.619 |
| C61 | Sin descripción | 3.437 |
| I10 | Sin descripción | 3.317 |

Se realizo una tabla sobre las 10 principales causas de muerte, en el que sus resultado arrojaron, que el infarto agudo del miocardio domina con una diferencia amplia: tiene casi cinco veces las muertes de la segunda causa. Predominan las enfermedades cardiovasculares, las respiratorias y los tumores malignos, y la agresión con arma de fuego aparece en el séptimo lugar. Las causas se agrupan por el código tal como viene en los microdatos. Los códigos C61 y I10 aparecen como "Sin descripción" porque el catálogo CIE-10 solo los registra con tres caracteres, y la aplicación cruza únicamente por el código de cuatro caracteres.

### 6. Gráfico de barras apiladas: defunciones por sexo en cada departamento

![Defunciones por sexo y departamento](Imagen/sexo_departamento.png)

Del total, 134.573 defunciones corresponden a hombres (55,1 %), 109.689 a mujeres (44,9 %) y 93 no tienen sexo determinado. Los hombres superan a las mujeres en los 33 departamentos. Los departamentos más poblados, como Bogotá D.C., Antioquia y Valle del Cauca, tienen las barras más altas.

### 7. Histograma: defunciones por etapa del ciclo de vida

![Grupos de edad](Imagen/defunciones_etapa_vida.png)

Este grafico agrupa el campo `GRUPO_EDAD1` en las categorías de la actividad. En la aplicación, la categoría de mortalidad neonatal considera el código 4; los códigos 0 a 3 aparecen en la categoría "Sin clasificar".

| Categoría | Códigos DANE | Defunciones |
|---|---|---|
| Mortalidad neonatal | 4 | 68 |
| Mortalidad infantil | 5 y 6 | 2.771 |
| Primera infancia | 7 y 8 | 1.518 |
| Niñez | 9 y 10 | 1.993 |
| Adolescencia | 11 | 3.795 |
| Juventud | 12 y 13 | 11.840 |
| Adultez temprana | 14 a 16 | 17.276 |
| Adultez intermedia | 17 a 19 | 29.105 |
| Vejez | 20 a 24 | 115.453 |
| Longevidad / Centenarios | 25 a 28 | 56.061 |
| Edad desconocida | 29 | 23 |
| Sin clasificar | 0 a 3 | 4.452 |

La vejez (60 a 84 años) y la longevidad (85 años o más) suman 171.514 muertes, cerca de 70 % del total. Entre las edades tempranas, la mayor parte de las muertes ocurre en el primer mes de vida (los códigos 0 a 4 suman 4.520), seguida de la mortalidad infantil (2.771).

### Otras visualizaciones del tablero

- **Gráfico de dona por sexo:** muestra la proporción de hombres (55,1 %) y mujeres (44,9 %) sobre el total de defunciones. En el tablero aparece en la tarjeta titulada "Defunciones por etapa de vida".
- **Defunciones por departamento (barras horizontales):** compara el total de registros entre los 33 departamentos, ordenados de menor a mayor.

## Autores

- Juan Sebastian Chavez Barrios


## Fuente de datos

Departamento Administrativo Nacional de Estadística (DANE): Estadísticas Vitales (EEVV) 2019, Divipola y proyecciones de población municipal. https://www.dane.gov.co
