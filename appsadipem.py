import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------- Navegación -------------------------
st.sidebar.title("Navegación")
pagina = st.sidebar.selectbox("Selecciona una página:", (
    "Origen de Financiamiento",
    "Plazos",
    "Ext-int por región",
    "Nicho de Mercado",
    "Montos"
))

# ------------------------- Carga de datos -------------------------
@st.cache_data
def load_data():
    df = pd.read_parquet("sadipem.parquet")
    df['fecha_contratacion'] = pd.to_datetime(df['fecha_contratacion'], errors='coerce')
    df['year'] = df['fecha_contratacion'].dt.year
    # Crear la columna 'millones_usd' a partir de 'Valor_contratacion_USD'
    df['millones_usd'] = df["Valor_contratacion_USD"] / 1e6
    return df

df_all = load_data()
df_all = df_all[df_all["Valor_contratacion_USD"] >= 0]

# ------------------------- Filtros según la página -------------------------
if pagina == "Plazos":
    # Para la página Plazos solo se deja el filtro de Tipo de Ente,
    # permitiendo escoger simultáneamente ambas opciones.
    tipo_ente_plazos = st.sidebar.multiselect("Tipo de Ente", ["Estado", "Município"],
                                               default=["Estado", "Município"])
    df = df_all[df_all["Tipo de Ente"].isin(tipo_ente_plazos)]
else:
    st.sidebar.title("Filtros")
    df = df_all.copy()
    # Filtro para Valor de Contratación (millones USD)
    min_val = df["millones_usd"].min()
    max_val = df["millones_usd"].max()
    valor_range = st.sidebar.slider("Valor de Contratación (millones USD)",
                                    float(min_val), float(max_val),
                                    (float(min_val), float(max_val)))
    df = df[(df["millones_usd"] >= valor_range[0]) & (df["millones_usd"] <= valor_range[1])]
    
    # Filtro para Plazo
    min_plazo = int(df["plazo"].min())
    max_plazo = int(df["plazo"].max())
    plazo_range = st.sidebar.slider("Plazo", min_plazo, max_plazo, (min_plazo, max_plazo))
    df = df[(df["plazo"] >= plazo_range[0]) & (df["plazo"] <= plazo_range[1])]
    
    # Filtro para Tipo de Ente (se usa selectbox, por lo que se escoge una sola opción)
    tipo_ente = st.sidebar.selectbox("Tipo de Ente", ("Município", "Estado"))
    df = df[df["Tipo de Ente"] == tipo_ente]

# ------------------------- Página: Origen de Financiamiento -------------------------
if pagina == "Origen de Financiamiento":
    st.title("Origen de Financiamiento")
    st.write("Análisis interactivo del origen de financiamiento según 'Classificação no RGF' (Interno y Externo) a lo largo del tiempo, basado en millones USD.")
    
    # Funciones para preparar datos
    def prepare_data_montos(data):
        data = data[data["Classificação no RGF"].isin(["Interno", "Externo"])]
        df_grouped = data.groupby(['year', 'Classificação no RGF'])['millones_usd'].sum().reset_index(name='sum_value')
        return df_grouped

    def prepare_data_percentage(data):
        data = data[data["Classificação no RGF"].isin(["Interno", "Externo"])]
        df_grouped = data.groupby(['year', 'Classificação no RGF'])['millones_usd'].sum().reset_index(name='sum_value')
        total = data.groupby('year')['millones_usd'].sum().reset_index(name='total_value')
        df_grouped = df_grouped.merge(total, on='year')
        df_grouped['percentage'] = (df_grouped['sum_value'] / df_grouped['total_value']) * 100
        return df_grouped

    # Asignación de colores
    color_map = {"Externo": "#c1121f", "Interno": "#adb5bd"}
    
    df_grouped_montos = prepare_data_montos(df)
    df_grouped_percentage = prepare_data_percentage(df)
    
    # Crear figura con subgráficos: 2 filas (montos y porcentajes) y 1 columna, eje x compartido.
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,  # Espacio entre subgráficos
        subplot_titles=(
            "Montos por Año de Contratación (millones USD)",
            "Porcentajes por Año de Contratación"
        ),
        row_heights=[0.5, 0.5]
    )
    
    # Trazas para montos (fila 1)
    for clas in df_grouped_montos["Classificação no RGF"].unique():
        subset = df_grouped_montos[df_grouped_montos["Classificação no RGF"] == clas]
        fig.add_bar(
            x=subset["year"],
            y=subset["sum_value"],
            name=clas,
            marker_color=color_map[clas],
            row=1, col=1
        )
    
    # Trazas para porcentajes (fila 2)
    for clas in df_grouped_percentage["Classificação no RGF"].unique():
        subset = df_grouped_percentage[df_grouped_percentage["Classificação no RGF"] == clas]
        fig.add_bar(
            x=subset["year"],
            y=subset["percentage"],
            name=clas,
            marker_color=color_map[clas],
            showlegend=False,  # Para evitar leyendas duplicadas
            row=2, col=1
        )
    
    fig.update_layout(
        barmode='stack',
        height=600,
        title_text="Origen de Financiamiento"
    )
    fig.update_yaxes(title_text="Montos (millones USD)", row=1, col=1)
    fig.update_yaxes(title_text="Porcentaje (%)", range=[0, 100], row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

# ------------------------- Página: Plazos -------------------------
elif pagina == "Plazos":
    st.title("Plazos")
    st.write("Porcentaje de operaciones por rango de plazo y región.")
    
    # Se usa el df filtrado únicamente por Tipo de Ente (según el multiselect)
    # Crear columna categórica para 'plazo' según los intervalos:
    bins = [0, 5, 9, 14, 21, np.inf]
    labels = ["Menor a 5 años", "5 a 8 años", "9 a 13 años", "14 a 20 años", "Mayor a 20 años"]
    df["plazo_category"] = pd.cut(df["plazo"], bins=bins, labels=labels, right=False)
    
    # Agrupar por 'region' y 'plazo_category' y calcular el porcentaje
    df_grouped = df.groupby(["region", "plazo_category"]).size().reset_index(name="count")
    df_total = df.groupby("region").size().reset_index(name="total")
    df_grouped = df_grouped.merge(df_total, on="region")
    df_grouped["percentage"] = (df_grouped["count"] / df_grouped["total"]) * 100
    
    # Gráfico de barras apiladas
    fig = px.bar(
        df_grouped,
        x="region",
        y="percentage",
        color="plazo_category",
        barmode="stack",
        labels={
            "region": "Región",
            "percentage": "Porcentaje (%)",
            "plazo_category": "Rango de Plazo"
        },
        title="Porcentaje de operaciones por rango de plazo y región"
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------- Página: Ext-int por región -------------------------
elif pagina == "Ext-int por región":
    st.title("Ext-int por región")
    st.write("Esta es la página de Ext-int por región.")
    # Aquí puedes agregar la lógica y visualizaciones correspondientes

# ------------------------- Página: Nicho de Mercado -------------------------
elif pagina == "Nicho de Mercado":
    st.title("Nicho de Mercado")
    st.write("Esta es la página de Nicho de Mercado.")
    # Aquí puedes agregar la lógica y visualizaciones correspondientes

# ------------------------- Página: Montos -------------------------
elif pagina == "Montos":
    st.title("Montos")
    st.write("Esta es la página de Montos.")
    # Aquí puedes agregar la lógica y visualizaciones correspondientes
