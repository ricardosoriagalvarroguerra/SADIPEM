import streamlit as st
import pandas as pd
import numpy as np
import math
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
# Para "Plazos" y "Ext-int por región" se utiliza solo el filtro de Tipo de Ente (multiselect)
if pagina in ["Plazos", "Ext-int por región"]:
    tipo_ente_mult = st.sidebar.multiselect("Tipo de Ente", ["Estado", "Município"],
                                              default=["Estado", "Município"])
    df = df_all[df_all["Tipo de Ente"].isin(tipo_ente_mult)]
else:
    st.sidebar.title("Filtros")
    df = df_all.copy()
    # Filtro para Valor de Contratación (millones USD)
    min_val = df["millones_usd"].min()
    max_val = df["millones_usd"].max()
    valor_range = st.sidebar.slider(
        "Valor de Contratación (millones USD)",
        float(min_val), float(max_val),
        (float(min_val), float(max_val))
    )
    df = df[(df["millones_usd"] >= valor_range[0]) & (df["millones_usd"] <= valor_range[1])]

    # Filtro para Plazo
    min_plazo = int(df["plazo"].min())
    max_plazo = int(df["plazo"].max())
    plazo_range = st.sidebar.slider("Plazo", min_plazo, max_plazo, (min_plazo, max_plazo))
    df = df[(df["plazo"] >= plazo_range[0]) & (df["plazo"] <= plazo_range[1])]

    # Filtro para Tipo de Ente (selectbox para escoger una única opción)
    tipo_ente = st.sidebar.selectbox("Tipo de Ente", ("Município", "Estado"))
    df = df[df["Tipo de Ente"] == tipo_ente]

# ------------------------- Página: Origen de Financiamiento -------------------------
if pagina == "Origen de Financiamiento":
    st.title("Origen de Financiamiento")
    st.write("Análisis interactivo del origen de financiamiento según 'Classificação no RGF' (Interno y Externo) a lo largo del tiempo, basado en millones USD.")

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

    # Asignación de colores para "Externo" e "Interno"
    color_map = {"Externo": "#c1121f", "Interno": "#adb5bd"}

    df_grouped_montos = prepare_data_montos(df)
    df_grouped_percentage = prepare_data_percentage(df)

    # Crear figura con subgráficos: 2 filas (montos y porcentajes) y 1 columna, eje x compartido
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            "Montos por Año de Contratación (millones USD)",
            "Porcentajes por Año de Contratación"
        ),
        row_heights=[0.5, 0.5]
    )

    for clas in df_grouped_montos["Classificação no RGF"].unique():
        subset = df_grouped_montos[df_grouped_montos["Classificação no RGF"] == clas]
        fig.add_bar(
            x=subset["year"],
            y=subset["sum_value"],
            name=clas,
            marker_color=color_map[clas],
            row=1, col=1
        )

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
    st.write("Porcentaje de operaciones por región y categoría de plazo.")
    
    # Agrupar por "region" y la variable existente "class_plazo"
    df_grouped = df.groupby(["region", "class_plazo"]).size().reset_index(name="count")
    df_total = df.groupby("region").size().reset_index(name="total")
    df_grouped = df_grouped.merge(df_total, on="region")
    df_grouped["percentage"] = (df_grouped["count"] / df_grouped["total"]) * 100
    
    # Gráfico de barras apiladas: eje horizontal = region, segmentado por "class_plazo"
    fig = px.bar(
        df_grouped,
        x="region",
        y="percentage",
        color="class_plazo",
        barmode="stack",
        labels={
            "region": "Región",
            "percentage": "Porcentaje (%)",
            "class_plazo": "Categoría de Plazo"
        },
        title="Porcentaje de operaciones por región y categoría de plazo"
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------- Página: Ext-int por región -------------------------
elif pagina == "Ext-int por región":
    st.title("Ext-int por región")
    st.write("Donut charts del top 4 'Nome do credor' por región basados en millones_usd.")

    # Obtener la lista de regiones
    regiones = list(df["region"].unique())
    cols = 3
    rows = math.ceil(len(regiones) / cols)
    # Crear la figura de subgráficos con tipo "domain" para los pie charts
    specs = [[{"type": "domain"} for _ in range(cols)] for _ in range(rows)]
    subplot_titles = [f"Top 4 Credores en {reg}" for reg in regiones]
    fig = make_subplots(rows=rows, cols=cols, specs=specs, subplot_titles=subplot_titles)

    # Iterar sobre las regiones y agregar cada donut chart
    for idx, reg in enumerate(regiones):
        df_reg = df[df["region"] == reg]
        # Agrupar por "Nome do credor" y sumar "millones_usd"
        df_group = df_reg.groupby("Nome do credor")["millones_usd"].sum().reset_index()
        df_group = df_group.sort_values(by="millones_usd", ascending=False)
        df_top4 = df_group.head(4)
        # Crear traza para el donut chart
        trace = go.Pie(
            labels=df_top4["Nome do credor"],
            values=df_top4["millones_usd"],
            hole=0.4,
            textinfo="percent+label",
            marker=dict(line=dict(color='white', width=2)),
            showlegend=True
        )
        # Determinar la fila y columna en el grid
        r = (idx // cols) + 1
        c = (idx % cols) + 1
        fig.add_trace(trace, row=r, col=c)

    fig.update_layout(
        height=rows * 350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(font=dict(size=10))
    )

    st.plotly_chart(fig, use_container_width=True)

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
