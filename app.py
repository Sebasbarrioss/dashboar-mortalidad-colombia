import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# 1. Configuracion de archivos
ARCHIVO_DEFUNCIONES = "NoFetal2019_CE_15-03-23.xlsx"
ARCHIVO_DIVIPOLA = "Divipola_CE_.xlsx"
ARCHIVO_CIE10 = "CodigosDeMuerte_CE_15-03-23.xlsx"

# 2. Carga de datos
df = pd.read_excel(ARCHIVO_DEFUNCIONES, sheet_name="No_Fetales_2019")
divipola = pd.read_excel(ARCHIVO_DIVIPOLA, sheet_name="Hoja1")
cie10 = pd.read_excel(ARCHIVO_CIE10, sheet_name="Final", header=8)

# 3. Normalizar codigos de causa de muerte
df["COD_MUERTE"] = df["COD_MUERTE"].astype("string").str.strip().str.upper()
cie10["Código de la CIE-10 cuatro caracteres"] = (
    cie10["Código de la CIE-10 cuatro caracteres"]
    .astype("string").str.strip().str.upper()
)

# 4. Asociar departamentos y municipios
df["COD_DANE"] = pd.to_numeric(df["COD_DANE"], errors="coerce")
divipola["COD_DANE"] = pd.to_numeric(divipola["COD_DANE"], errors="coerce")

df = df.merge(
    divipola[["COD_DANE", "DEPARTAMENTO", "MUNICIPIO"]].drop_duplicates(),
    on="COD_DANE",
    how="left"
)

# 5. Asociar descripcion de las causas de muerte
cie10 = cie10.rename(columns={
    "Código de la CIE-10 cuatro caracteres": "COD_MUERTE",
    "Descripcion  de códigos mortalidad a cuatro caracteres": "CAUSA_MUERTE"
})

df = df.merge(
    cie10[["COD_MUERTE", "CAUSA_MUERTE"]].drop_duplicates(),
    on="COD_MUERTE",
    how="left"
)

# 6. Filtrar el año 2019
df = df[df["AÑO"] == 2019].copy()

# 7. Resumen general
total_defunciones = len(df)
total_departamentos = df["DEPARTAMENTO"].nunique()
total_municipios = df["COD_DANE"].nunique()

# 8. Grafico de defunciones por mes
defunciones_mes = (
    df.groupby("MES").size()
    .reindex(range(1, 13), fill_value=0)
    .rename_axis("MES")
    .reset_index(name="DEFUNCIONES")
)

nombres_meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
defunciones_mes["NOMBRE_MES"] = defunciones_mes["MES"].map(
    dict(enumerate(nombres_meses, start=1))
)

fig_mes = px.line(
    defunciones_mes,
    x="NOMBRE_MES",
    y="DEFUNCIONES",
    markers=True,
    title="Defunciones por mes - Colombia, 2019",
    labels={"NOMBRE_MES": "Mes", "DEFUNCIONES": "Numero de defunciones"}
)

# 9. Grafico por sexo
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
    title="Distribucion de defunciones por sexo"
)

# 10. Grafico por grupo de edad
defunciones_edad = (
    df["GRUPO_EDAD1"].value_counts().sort_index()
    .rename_axis("GRUPO_EDAD1")
    .reset_index(name="DEFUNCIONES")
)

fig_edad = px.bar(
    defunciones_edad,
    x="GRUPO_EDAD1",
    y="DEFUNCIONES",
    title="Defunciones por codigo de grupo de edad",
    labels={"GRUPO_EDAD1": "Codigo de grupo de edad", "DEFUNCIONES": "Defunciones"}
)

# 11. Diez principales causas de muerte
principales_causas = (
    df.groupby(["COD_MUERTE", "CAUSA_MUERTE"], dropna=False)
    .size()
    .reset_index(name="DEFUNCIONES")
    .sort_values("DEFUNCIONES", ascending=False)
    .head(10)
)

# 12. Defunciones por departamento
defunciones_departamento = (
    df.groupby("DEPARTAMENTO", dropna=False)
    .size()
    .reset_index(name="DEFUNCIONES")
    .sort_values("DEFUNCIONES", ascending=False)
)# 12.1 Defunciones por sexo y departamento
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
    title="Defunciones por sexo y departamento - Colombia, 2019",
    labels={
        "DEPARTAMENTO": "Departamento",
        "DEFUNCIONES": "Número de defunciones",
        "SEXO_NOMBRE": "Sexo"
    },
    barmode="stack"
)# 12.2 Cinco municipios con mas homicidios
df_homicidios = df[
    df["MANERA_MUERTE"].astype("string").str.strip().str.upper() == "HOMICIDIO"
].copy()

homicidios_municipio = (
    df_homicidios.groupby(["DEPARTAMENTO", "MUNICIPIO"])
    .size()
    .reset_index(name="HOMICIDIOS")
    .sort_values("HOMICIDIOS", ascending=False)
    .head(5)
)

fig_homicidios = px.bar(
    homicidios_municipio,
    x="MUNICIPIO",
    y="HOMICIDIOS",
    color="DEPARTAMENTO",
    title="Cinco municipios con más homicidios - Colombia, 2019",
    labels={
        "MUNICIPIO": "Municipio",
        "HOMICIDIOS": "Número de homicidios",
        "DEPARTAMENTO": "Departamento"
    }
)# 12.3 Mapa de defunciones por departamento
import json

with open("col_departamentos.geojson", encoding="utf-8") as archivo:
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
    color_continuous_scale="Reds",
    title="Defunciones por departamento - Colombia, 2019",
    labels={
        "DEFUNCIONES": "Número de defunciones",
        "DEPARTAMENTO": "Departamento"
    }
)

fig_mapa.update_geos(
    fitbounds="locations",
    visible=False
)# 12.4 Diez municipios con menos defunciones registradas
defunciones_municipio = (
    df.groupby(["DEPARTAMENTO", "MUNICIPIO"])
    .size()
    .reset_index(name="DEFUNCIONES")
    .sort_values("DEFUNCIONES", ascending=True)
    .head(10)
)

defunciones_municipio["MUNICIPIO_ETIQUETA"] = (
    defunciones_municipio["MUNICIPIO"].astype("string")
    + " - "
    + defunciones_municipio["DEPARTAMENTO"].astype("string")
)

fig_menor_mortalidad = px.pie(
    defunciones_municipio,
    names="MUNICIPIO_ETIQUETA",
    values="DEFUNCIONES",
    title="Diez municipios con menos defunciones registradas - 2019",
    hole=0.3
)

# 13. Aplicacion Dash
app = Dash(__name__)
server = app.server 
app.title = "Mortalidad en Colombia 2019"

app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f4f6f9",
        "padding": "24px"
    },
    children=[
        html.H1(
            "Dashboard de Mortalidad en Colombia - 2019",
            style={"textAlign": "center", "color": "#17365d"}
        ),
        html.P(
            "Analisis de defunciones no fetales registradas en 2019.",
            style={"textAlign": "center", "fontSize": "17px"}
        ),
        html.Div(
            style={
                "display": "flex",
                "gap": "16px",
                "justifyContent": "center",
                "flexWrap": "wrap"
            },
            children=[
                html.Div(
                    [html.H3("Defunciones registradas"), html.H2(f"{total_defunciones:,}")],
                    style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "textAlign": "center", "minWidth": "220px"}
                ),
                html.Div(
                    [html.H3("Departamentos"), html.H2(str(total_departamentos))],
                    style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "textAlign": "center", "minWidth": "220px"}
                ),
                html.Div(
                    [html.H3("Municipios identificados"), html.H2(str(total_municipios))],
                    style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "textAlign": "center", "minWidth": "220px"}
                )
            ]
        ),
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))",
                "gap": "20px",
                "marginTop": "24px"
            },
            children=[
                html.Div(dcc.Graph(figure=fig_mes), style={"backgroundColor": "white", "padding": "12px"}),
                html.Div(dcc.Graph(figure=fig_sexo), style={"backgroundColor": "white", "padding": "12px"}),
                html.Div(dcc.Graph(figure=fig_edad), style={"backgroundColor": "white", "padding": "12px"})
            ]
        ),
        html.H2("Diez principales codigos de causa de muerte"),
        html.Table(
            [
                html.Thead(html.Tr([
                    html.Th("Codigo"),
                    html.Th("Causa de muerte"),
                    html.Th("Defunciones")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(str(fila["COD_MUERTE"])),
                        html.Td(str(fila["CAUSA_MUERTE"]) if pd.notna(fila["CAUSA_MUERTE"]) else "Sin descripcion"),
                        html.Td(f"{fila['DEFUNCIONES']:,}")
                    ])
                    for _, fila in principales_causas.iterrows()
                ])
            ],
            style={"width": "100%", "backgroundColor": "white", "borderCollapse": "collapse", "padding": "12px"}
        ),
   html.H2("Defunciones por sexo y departamento"),

dcc.Graph(figure=fig_sexo_departamento),     html.H2("Cinco municipios con más homicidios"),

dcc.Graph(figure=fig_homicidios),      html.H2("Diez municipios con menos defunciones registradas"),
        dcc.Graph(figure=fig_menor_mortalidad),      html.H2("Mapa de defunciones por departamento"),
        dcc.Graph(figure=fig_mapa),     html.H2("Defunciones por departamento"),
        dcc.Graph(
            figure=px.bar(
                defunciones_departamento,
                x="DEPARTAMENTO",
                y="DEFUNCIONES",
                title="Numero de defunciones por departamento",
                labels={"DEPARTAMENTO": "Departamento", "DEFUNCIONES": "Defunciones"}
            )
        ),
        html.P(
            "Fuente: archivos Excel proporcionados para el analisis. "
            "Los resultados representan conteos de registros, no tasas ajustadas por poblacion."
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
