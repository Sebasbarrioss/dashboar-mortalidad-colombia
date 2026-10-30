 
import json

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# ============================================================
# 1. Archivos de datos (están en la raíz del repositorio)
# ============================================================
ARCHIVO_DEFUNCIONES = "NoFetal2019_CE_15-03-23.xlsx"
ARCHIVO_DIVIPOLA = "Divipola_CE_.xlsx"
ARCHIVO_CIE10 = "CodigosDeMuerte_CE_15-03-23.xlsx"
ARCHIVO_GEOJSON = "col_departamentos.geojson"
ARCHIVO_POBLACION = "PPED-AreaMun-2018-2042_VP.xlsx"

# ============================================================
# 2. Carga y preparación de datos
# ============================================================
df = pd.read_excel(ARCHIVO_DEFUNCIONES, sheet_name="No_Fetales_2019")
poblacion = pd.read_excel(
    ARCHIVO_POBLACION,
    sheet_name="PobMunicipalxÁrea",
    header=7
)

print("PRIMERAS FILAS COMPLETAS DE POBLACIÓN:", poblacion.head(12).to_dict("records"))

# Limpiar nombres de columnas
poblacion.columns = (
    poblacion.columns.astype(str)
    .str.strip()
    .str.replace("\n", " ", regex=False)
)

print("ENCABEZADOS POBLACION:", poblacion.columns.tolist())
# Preparar los datos
poblacion["AÑO"] = pd.to_numeric(poblacion["AÑO"], errors="coerce")
poblacion["TOTAL"] = pd.to_numeric(poblacion["TOTAL"], errors="coerce")
print("AÑOS DISPONIBLES:", sorted(poblacion["AÑO"].dropna().unique().tolist()))
print("ÁREAS DISPONIBLES:", poblacion["ÁREA GEOGRÁFICA"].astype(str).str.strip().unique().tolist())
print("PRIMERAS FILAS:", poblacion[["DPMP", "AÑO", "ÁREA GEOGRÁFICA", "TOTAL"]].head(10).to_dict("records"))

poblacion_2019 = poblacion[
    (poblacion["AÑO"] == 2019)
    & (
        poblacion["ÁREA GEOGRÁFICA"]
        .astype(str)
        .str.strip()
        .str.upper()
        == "TOTAL"
    )
].copy()

poblacion_2019["COD_DANE"] = pd.to_numeric(
    poblacion_2019["DPMP"], errors="coerce"
)

poblacion_2019 = poblacion_2019[
    ["COD_DANE", "TOTAL"]
].rename(columns={"TOTAL": "POBLACION"})

poblacion_2019 = poblacion_2019.dropna(
    subset=["COD_DANE", "POBLACION"]
).drop_duplicates(subset=["COD_DANE"])
print("Municipios en defunciones:", df["COD_DANE"].nunique())
print("Municipios en población:", poblacion_2019["COD_DANE"].nunique())
print("Ejemplos códigos defunciones:", df["COD_DANE"].dropna().head(10).tolist())
print("Ejemplos códigos población:", poblacion_2019["COD_DANE"].head(10).tolist())
divipola = pd.read_excel(ARCHIVO_DIVIPOLA, sheet_name="Hoja1")
cie10 = pd.read_excel(ARCHIVO_CIE10, sheet_name="Final", header=8)

df["COD_MUERTE"] = df["COD_MUERTE"].astype("string").str.strip().str.upper()
cie10["Código de la CIE-10 cuatro caracteres"] = (
    cie10["Código de la CIE-10 cuatro caracteres"]
    .astype("string").str.strip().str.upper()
)

df["COD_DANE"] = pd.to_numeric(df["COD_DANE"], errors="coerce")
divipola["COD_DANE"] = pd.to_numeric(divipola["COD_DANE"], errors="coerce")

df = df.merge(
    divipola[["COD_DANE", "DEPARTAMENTO", "MUNICIPIO"]].drop_duplicates(),
    on="COD_DANE",
    how="left",
)

cie10 = cie10.rename(
    columns={
        "Código de la CIE-10 cuatro caracteres": "COD_MUERTE",
        "Descripcion  de códigos mortalidad a cuatro caracteres": "CAUSA_MUERTE",
    }
)

df = df.merge(
    cie10[["COD_MUERTE", "CAUSA_MUERTE"]].drop_duplicates(),
    on="COD_MUERTE",
    how="left",
)

df = df[df["AÑO"] == 2019].copy()

# ============================================================
# 3. Indicadores generales
# ============================================================
total_defunciones = len(df)
total_departamentos = df["DEPARTAMENTO"].nunique()
total_municipios = df["COD_DANE"].nunique()

# ============================================================
# 4. Gráficas
# ============================================================
nombres_meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

defunciones_mes = (
    df.groupby("MES").size()
    .reindex(range(1, 13), fill_value=0)
    .rename_axis("MES")
    .reset_index(name="DEFUNCIONES")
)
defunciones_mes["NOMBRE_MES"] = defunciones_mes["MES"].map(
    dict(enumerate(nombres_meses, start=1))
)

fig_mes = px.line(
    defunciones_mes,
    x="NOMBRE_MES",
    y="DEFUNCIONES",
    markers=True,
    labels={"NOMBRE_MES": "Mes", "DEFUNCIONES": "Defunciones"},
)
fig_mes.update_traces(
    line={"color": "#167D9A", "width": 3},
    marker={"size": 8, "color": "#167D9A"},
    hovertemplate="%{x}<br>Defunciones: %{y:,}<extra></extra>",
)

defunciones_sexo = (
    df["SEXO"].map({1: "Hombres", 2: "Mujeres"})
    .fillna("Sin clasificar")
    .value_counts()
    .rename_axis("SEXO")
    .reset_index(name="DEFUNCIONES")
)
fig_sexo = px.pie(
    defunciones_sexo,
    names="SEXO",
    values="DEFUNCIONES",
    hole=0.58,
    color="SEXO",
    color_discrete_map={
        "Hombres": "#167D9A",
        "Mujeres": "#43B9A8",
        "Sin clasificar": "#A8B4C4",
    },
)
fig_sexo.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate="%{label}<br>Defunciones: %{value:,}<br>Porcentaje: %{percent}<extra></extra>",
)

defunciones_edad = (
    df["GRUPO_EDAD1"].value_counts().sort_index()
    .rename_axis("GRUPO_EDAD1")
    .reset_index(name="DEFUNCIONES")
)

rangos_edad = {
    "Mortalidad neonatal": [4],
    "Mortalidad infantil": [5, 6],
    "Primera infancia": [7, 8],
    "Niñez": [9, 10],
    "Adolescencia": [11],
    "Juventud": [12, 13],
    "Adultez temprana": [14, 15, 16],
    "Adultez intermedia": [17, 18, 19],
    "Vejez": [20, 21, 22, 23, 24],
    "Longevidad / Centenarios": [25, 26, 27, 28],
    "Edad desconocida": [29],
}


codigo_a_etapa = {
    codigo: etapa
    for etapa, codigos in rangos_edad.items()
    for codigo in codigos
}

df_edades = df.copy()

df_edades["CODIGO_EDAD"] = pd.to_numeric(
    df_edades["GRUPO_EDAD1"], errors="coerce"
)

df_edades["ETAPA_VIDA"] = (
    df_edades["CODIGO_EDAD"]
    .map(codigo_a_etapa)
    .fillna("Sin clasificar")
)

orden_etapas = list(rangos_edad.keys()) + ["Sin clasificar"]

defunciones_edad = (
    df_edades.groupby("ETAPA_VIDA")
    .size()
    .reindex(orden_etapas, fill_value=0)
    .rename("DEFUNCIONES")
    .reset_index()
)

fig_edad = px.bar(
    defunciones_edad,
    x="ETAPA_VIDA",
    y="DEFUNCIONES",
    category_orders={"ETAPA_VIDA": orden_etapas},
    labels={
        "ETAPA_VIDA": "Etapa de vida",
        "DEFUNCIONES": "Total de defunciones",
    },
    text="DEFUNCIONES",
    color_discrete_sequence=["#2471A3"],
)

fig_edad.update_traces(
    hovertemplate="Etapa: %{x}<br>Defunciones: %{y:,}<extra></extra>",
    textposition="outside",
)

fig_edad.update_layout(
    xaxis_tickangle=-35,
    showlegend=False,
)

principales_causas = (
    df.groupby(["COD_MUERTE", "CAUSA_MUERTE"], dropna=False)
    .size()
    .reset_index(name="DEFUNCIONES")
    .sort_values("DEFUNCIONES", ascending=False)
    .head(10)
)

defunciones_departamento = (
    df.groupby("DEPARTAMENTO", dropna=False)
    .size()
    .reset_index(name="DEFUNCIONES")
    .sort_values("DEFUNCIONES", ascending=False)
)

defunciones_sexo_departamento = (
    df.assign(
        SEXO_NOMBRE=df["SEXO"].map({1: "Hombres", 2: "Mujeres"}).fillna("Sin clasificar")
    )
    .groupby(["DEPARTAMENTO", "SEXO_NOMBRE"])
    .size()
    .reset_index(name="DEFUNCIONES")
)
fig_sexo_departamento = px.bar(
    defunciones_sexo_departamento,
    x="DEPARTAMENTO",
    y="DEFUNCIONES",
    color="SEXO_NOMBRE",
    labels={
        "DEPARTAMENTO": "Departamento",
        "DEFUNCIONES": "Defunciones",
        "SEXO_NOMBRE": "Sexo",
    },
    barmode="stack",
    color_discrete_map={
        "Hombres": "#167D9A",
        "Mujeres": "#43B9A8",
        "Sin clasificar": "#A8B4C4",
    },
)
fig_sexo_departamento.update_layout(xaxis_tickangle=-45)


codigos_armas_fuego = ["X93", "X94", "X95"]

df_homicidios = df[
    (
        df["MANERA_MUERTE"]
        .astype("string")
        .str.strip()
        .str.upper()
        == "HOMICIDIO"
    )
    &
    (
        df["COD_MUERTE"]
        .astype("string")
        .str.strip()
        .str.upper()
        .str[:3]
        .isin(codigos_armas_fuego)
    )
].copy()

homicidios_municipio = (
    df_homicidios.groupby(["DEPARTAMENTO", "MUNICIPIO"])
    .size()
    .reset_index(name="HOMICIDIOS")
    .sort_values("HOMICIDIOS", ascending=False)
    .head(5)
    .sort_values("HOMICIDIOS", ascending=True)
)

fig_homicidios = px.bar(
    homicidios_municipio,
    x="HOMICIDIOS",
    y="MUNICIPIO",
    color="DEPARTAMENTO",
    orientation="h",
    labels={
        "MUNICIPIO": "Municipio",
        "HOMICIDIOS": "Homicidios por arma de fuego",
        "DEPARTAMENTO": "Departamento",
    },
    color_discrete_sequence=[
        "#167D9A",
        "#43B9A8",
        "#F0A35E",
        "#7A8CC7",
        "#D46A6A",
    ],
)

fig_homicidios.update_layout(showlegend=True)
with open(ARCHIVO_GEOJSON, encoding="utf-8") as archivo:
    mapa_colombia = json.load(archivo)

defunciones_mapa = (
    df.assign(
        DEPARTAMENTO=df["DEPARTAMENTO"].astype("string").str.strip().str.upper()
    )
    .groupby("DEPARTAMENTO")
    .size()
    .reset_index(name="DEFUNCIONES")
)
fig_mapa = px.choropleth(
    defunciones_mapa,
    geojson=mapa_colombia,
    locations="DEPARTAMENTO",
    featureidkey="properties.dpto_nombre",
    color="DEFUNCIONES",
    color_continuous_scale=["#E6F4F5", "#80C9C5", "#167D9A", "#12304A"],
    labels={"DEFUNCIONES": "Defunciones", "DEPARTAMENTO": "Departamento"},
)
fig_mapa.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")

defunciones_municipio = (
    df.groupby(["COD_DANE", "DEPARTAMENTO", "MUNICIPIO"])
    .size()
    .reset_index(name="DEFUNCIONES")
)

# Unir las defunciones con la población de 2019
defunciones_municipio = defunciones_municipio.merge(
    poblacion_2019,
    on="COD_DANE",
    how="inner",
)

# Calcular tasa por cada 1.000 habitantes
defunciones_municipio["TASA_MORTALIDAD"] = (
    defunciones_municipio["DEFUNCIONES"]
    / defunciones_municipio["POBLACION"]
    * 1000
)

# Seleccionar los 10 municipios con menor tasa
defunciones_municipio = (
    defunciones_municipio[
        defunciones_municipio["POBLACION"] > 0
    ]
    .sort_values("TASA_MORTALIDAD", ascending=True)
    .head(10)
)

defunciones_municipio["MUNICIPIO_ETIQUETA"] = (
    defunciones_municipio["MUNICIPIO"].astype(str)
    + " - "
    + defunciones_municipio["DEPARTAMENTO"].astype(str)
)

fig_menor_mortalidad = px.pie(
    defunciones_municipio,
    names="MUNICIPIO_ETIQUETA",
    values="TASA_MORTALIDAD",
    hole=0.48,
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={
        "MUNICIPIO_ETIQUETA": "Municipio",
        "TASA_MORTALIDAD": "Tasa por 1.000 habitantes",
    },
)

fig_menor_mortalidad.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "%{label}<br>"
        "Tasa: %{value:.3f} por 1.000 habitantes"
        "<extra></extra>"
    ),
)
# Apariencia común para las gráficas
for figura in [
    fig_mes,
    fig_sexo,
    fig_edad,
    fig_sexo_departamento,
    fig_homicidios,
    fig_menor_mortalidad,
]:
    figura.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": "#243447", "size": 12},
        margin={"l": 24, "r": 24, "t": 30, "b": 35},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        hoverlabel={"bgcolor": "#12304A", "font_color": "white"},
    )
    figura.update_xaxes(showgrid=True, gridcolor="#E8EEF3", zeroline=False, linecolor="#DCE4EB")
    figura.update_yaxes(showgrid=True, gridcolor="#E8EEF3", zeroline=False, linecolor="#DCE4EB")

fig_mapa.update_layout(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    font={"family": "Arial, sans-serif", "color": "#243447", "size": 12},
    margin={"l": 8, "r": 8, "t": 8, "b": 8},
    coloraxis_colorbar={"title": "Defunciones", "thickness": 14, "len": 0.75},
)

# ============================================================
# 5. Componentes de diseño
# ============================================================
app = Dash(__name__)
server = app.server
app.title = "Mortalidad en Colombia | 2019"

COLOR_TEXTO = "#183247"
COLOR_SECUNDARIO = "#607486"
COLOR_ACENTO = "#167D9A"

ESTILO_TARJETA = {
    "backgroundColor": "#FFFFFF",
    "border": "1px solid #E5ECF2",
    "borderRadius": "16px",
    "padding": "22px",
    "boxShadow": "0 5px 18px rgba(23, 54, 78, 0.06)",
    "minWidth": "0",
}

def tarjeta_grafica(titulo, subtitulo, grafica, min_height=None):
    estilo = dict(ESTILO_TARJETA)
    estilo["overflow"] = "hidden"
    contenido = [
        html.H3(
            titulo,
            style={"margin": "0 0 6px", "fontSize": "17px", "fontWeight": "700", "color": COLOR_TEXTO},
        ),
        html.P(
            subtitulo,
            style={"margin": "0 0 12px", "fontSize": "12px", "lineHeight": "1.5", "color": COLOR_SECUNDARIO},
        ),
        dcc.Graph(
            figure=grafica,
            config={"displayModeBar": False, "responsive": True},
            style={"height": min_height or "350px"},
        ),
    ]
    return html.Div(contenido, style=estilo)

def tarjeta_kpi(etiqueta, valor, detalle, color):
    return html.Div(
        [
            html.Div(
                style={
                    "width": "42px",
                    "height": "5px",
                    "borderRadius": "10px",
                    "backgroundColor": color,
                    "marginBottom": "18px",
                }
            ),
            html.P(
                etiqueta,
                style={"margin": "0 0 9px", "fontSize": "13px", "fontWeight": "600", "color": COLOR_SECUNDARIO},
            ),
            html.Div(
                valor,
                style={"fontSize": "clamp(25px, 3vw, 34px)", "fontWeight": "800", "letterSpacing": "-1px", "color": COLOR_TEXTO},
            ),
            html.P(
                detalle,
                style={"margin": "8px 0 0", "fontSize": "12px", "color": COLOR_SECUNDARIO},
            ),
        ],
        style={**ESTILO_TARJETA, "padding": "22px 24px"},
    )

# ============================================================
# 6. Página del dashboard
# ============================================================
app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#F3F6FA",
        "minHeight": "100vh",
        "padding": "0",
        "color": COLOR_TEXTO,
    },
    children=[
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "ESTADÍSTICAS VITALES · COLOMBIA",
                            style={
                                "margin": "0 0 12px",
                                "fontSize": "11px",
                                "fontWeight": "700",
                                "letterSpacing": "2px",
                                "color": "#8EDBD2",
                            },
                        ),
                        html.H1(
                            "Mortalidad no fetal",
                            style={
                                "margin": "0",
                                "fontSize": "clamp(30px, 4vw, 44px)",
                                "fontWeight": "800",
                                "letterSpacing": "-1.5px",
                                "lineHeight": "1.1",
                                "color": "#FFFFFF",
                            },
                        ),
                        html.P(
                            "Panorama nacional de las defunciones registradas durante 2019",
                            style={
                                "margin": "14px 0 0",
                                "maxWidth": "720px",
                                "fontSize": "15px",
                                "lineHeight": "1.7",
                                "color": "#D5E5EF",
                            },
                        ),
                    ],
                    style={"maxWidth": "1200px", "margin": "0 auto", "padding": "42px 28px 48px"},
                )
            ],
            style={
                "background": "linear-gradient(120deg, #102B43 0%, #164B66 62%, #167D9A 100%)",
                "borderBottom": "4px solid #43B9A8",
            },
        ),
        html.Main(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2(
                                    "Resumen nacional",
                                    style={"margin": "0", "fontSize": "22px", "fontWeight": "750", "color": COLOR_TEXTO},
                                ),
                                html.P(
                                    "Indicadores generales del conjunto de datos analizado.",
                                    style={"margin": "7px 0 0", "fontSize": "13px", "color": COLOR_SECUNDARIO},
                                ),
                            ],
                            style={"marginBottom": "18px"},
                        ),
                        html.Div(
                            [
                                tarjeta_kpi(
                                    "Defunciones registradas",
                                    f"{total_defunciones:,}",
                                    "Registros del año 2019",
                                    "#167D9A",
                                ),
                                tarjeta_kpi(
                                    "Departamentos",
                                    f"{total_departamentos:,}",
                                    "Con registros identificados",
                                    "#43B9A8",
                                ),
                                tarjeta_kpi(
                                    "Municipios identificados",
                                    f"{total_municipios:,}",
                                    "Códigos DANE únicos",
                                    "#E6A15A",
                                ),
                            ],
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 220px), 1fr))",
                                "gap": "16px",
                            },
                        ),
                        html.Div(
                            [
                                html.H2(
                                    "Comportamiento y perfil demográfico",
                                    style={"margin": "0 0 16px", "fontSize": "22px", "fontWeight": "750"},
                                ),
                                html.Div(
                                    [
                                        tarjeta_grafica(
                                            "Defunciones por mes",
                                            "Conteo mensual de registros durante 2019.",
                                            fig_mes,
                                            "330px",
                                        ),
                                        tarjeta_grafica(
                                            "Defunciones por etapa de vida",
                                            "Distribución de las defunciones registradas en Colombia durante 2019 según la etapa de vida.",
                                            fig_sexo,
                                            "330px",
                                        ),
                                        tarjeta_grafica(
                                            "Grupos de edad",
                                            "Conteo por código de grupo de edad disponible en los datos.",
                                            fig_edad,
                                            "350px",
                                        ),
                                        tarjeta_grafica(
                                            "Sexo por departamento",
                                            "Comparación de los conteos por departamento y sexo.",
                                            fig_sexo_departamento,
                                            "430px",
                                        ),
                                    ],
                                    style={
                                        "display": "grid",
                                        "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 420px), 1fr))",
                                        "gap": "18px",
                                    },
                                ),
                            ],
                            style={"marginTop": "34px"},
                        ),
                        html.Div(
                            [
                                html.H2(
                                    "Causas y distribución territorial",
                                    style={"margin": "0 0 16px", "fontSize": "22px", "fontWeight": "750"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H3(
                                                    "Diez principales causas de muerte",
                                                    style={"margin": "0 0 6px", "fontSize": "17px", "fontWeight": "700"},
                                                ),
                                                html.P(
                                                    "Clasificación por código y descripción CIE-10.",
                                                    style={"margin": "0 0 16px", "fontSize": "12px", "color": COLOR_SECUNDARIO},
                                                ),
                                                html.Div(
                                                    html.Table(
                                                        [
                                                            html.Thead(
                                                                html.Tr(
                                                                    [
                                                                        html.Th("Código", style={"width": "90px"}),
                                                                        html.Th("Causa de muerte"),
                                                                        html.Th("Defunciones", style={"textAlign": "right", "width": "120px"}),
                                                                    ]
                                                                )
                                                            ),
                                                            html.Tbody(
                                                                [
                                                                    html.Tr(
                                                                        [
                                                                            html.Td(str(fila["COD_MUERTE"])),
                                                                            html.Td(
                                                                                str(fila["CAUSA_MUERTE"])
                                                                                if pd.notna(fila["CAUSA_MUERTE"])
                                                                                else "Sin descripción"
                                                                            ),
                                                                            html.Td(
                                                                                f"{fila['DEFUNCIONES']:,}",
                                                                                style={"textAlign": "right", "fontWeight": "700"},
                                                                            ),
                                                                        ],
                                                                        style={
                                                                            "backgroundColor": "#F6F9FC" if i % 2 == 0 else "#FFFFFF",
                                                                            "borderBottom": "1px solid #E8EEF3",
                                                                        },
                                                                    )
                                                                    for i, (_, fila) in enumerate(principales_causas.iterrows())
                                                                ]
                                                            ),
                                                        ],
                                                        style={
                                                            "width": "100%",
                                                            "borderCollapse": "collapse",
                                                            "fontSize": "12px",
                                                            "lineHeight": "1.5",
                                                        },
                                                    ),
                                                    style={"overflowX": "auto"},
                                                ),
                                            ],
                                            style=ESTILO_TARJETA,
                                        ),
                                        tarjeta_grafica(
                                            "Mapa de defunciones por departamento",
                                            "Conteo de registros por departamento; use el cursor para consultar valores.",
                                            fig_mapa,
                                            "430px",
                                        ),
                                        tarjeta_grafica(
                                            "Defunciones por departamento",
                                            "Comparación del número de registros entre departamentos.",
                                            px.bar(
                                                defunciones_departamento.sort_values("DEFUNCIONES", ascending=True),
                                                x="DEFUNCIONES",
                                                y="DEPARTAMENTO",
                                                orientation="h",
                                                labels={"DEPARTAMENTO": "Departamento", "DEFUNCIONES": "Defunciones"},
                                            ).update_traces(
                                                marker_color="#167D9A",
                                                hovertemplate="%{y}<br>Defunciones: %{x:,}<extra></extra>",
                                            ),
                                            "620px",
                                        ),
                                        tarjeta_grafica(
                                            "Cinco municipios con más homicidios",
                                            "Conteo de registros clasificados como homicidio.",
                                            fig_homicidios,
                                            "350px",
                                        ),
                                        tarjeta_grafica(
                                            "Diez municipios con menos defunciones registradas",
                                            "Distribución de los diez municipios con menor conteo observado.",
                                            fig_menor_mortalidad,
                                            "350px",
                                        ),
                                    ],
                                    style={
                                        "display": "grid",
                                        "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 420px), 1fr))",
                                        "gap": "18px",
                                    },
                                ),
                            ],
                            style={"marginTop": "34px"},
                        ),
                        html.Div(
                            [
                                html.P(
                                    "Fuente: archivos Excel proporcionados para el análisis.",
                                    style={"margin": "0 0 6px", "fontWeight": "700", "fontSize": "12px"},
                                ),
                                html.P(
                                    "Nota metodológica: los resultados representan conteos de registros; no son tasas ajustadas por población. "
                                    "Las categorías y resultados dependen de la calidad y cobertura de los archivos de origen.",
                                    style={"margin": "0", "fontSize": "12px", "lineHeight": "1.6"},
                                ),
                            ],
                            style={
                                "marginTop": "30px",
                                "padding": "20px 22px",
                                "borderTop": "1px solid #DCE5EC",
                                "color": COLOR_SECUNDARIO,
                            },
                        ),
                    ],
                    style={"maxWidth": "1280px", "margin": "0 auto", "padding": "30px 24px 18px"},
                )
            ],
            style={"width": "100%"},
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=False)
