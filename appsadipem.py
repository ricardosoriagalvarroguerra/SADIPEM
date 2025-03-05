import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------- Nueva paleta de colores -------------------------
# La paleta para los credores que NO sean FONPLATA (rojo) se define aquí:
other_palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                 "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

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
    # En Plazos se usa únicamente el filtro de Tipo de Ente (multiselect)
    tipo_ente_mult = st.sidebar.multiselect("Tipo de Ente", ["Estado", "Município"],
                                              default=["Estado", "Município"])
    df = df_all[df_all["Tipo de Ente"].isin(tipo_ente_mult)]
elif pagina == "Ext-int por región":
    # En Ext-int por región se agregan también filtros de Tipo de Ente, Plazo y Millones USD
    st.sidebar.title("Filtros para Ext-int por región")
    tipo_ente_mult = st.sidebar.multiselect("Tipo de Ente", ["Estado", "Município"],
                                              default=["Estado", "Município"])
    df = df_all[df_all["Tipo de Ente"].isin(tipo_ente_mult)]
    min_plazo = int(df["plazo"].min())
    max_plazo = int(df["plazo"].max())
    plazo_range = st.sidebar.slider("Plazo", min_plazo, max_plazo, (min_plazo, max_plazo))
    df = df[(df["plazo"] >= plazo_range[0]) & (df["plazo"] <= plazo_range[1])]
    min_mill = df["millones_usd"].min()
    max_mill = df["millones_usd"].max()
    mill_range = st.sidebar.slider("Millones USD", float(min_mill), float(max_mill),
                                   (float(min_mill), float(max_mill)))
    df = df[(df["millones_usd"] >= mill_range[0]) & (df["millones_usd"] <= mill_range[1])]
else:
    st.sidebar.title("Filtros")
    df = df_all.copy()
    min_val = df["millones_usd"].min()
    max_val = df["millones_usd"].max()
    valor_range = st.sidebar.slider(
        "Valor de Contratación (millones USD)",
        float(min_val), float(max_val),
        (float(min_val), float(max_val))
    )
    df = df[(df["millones_usd"] >= valor_range[0]) & (df["millones_usd"] <= valor_range[1])]
    min_plazo = int(df["plazo"].min())
    max_plazo = int(df["plazo"].max())
    plazo_range = st.sidebar.slider("Plazo", min_plazo, max_plazo, (min_plazo, max_plazo))
    df = df[(df["plazo"] >= plazo_range[0]) & (df["plazo"] <= plazo_range[1])]
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

    color_map = {"Externo": "#c1121f", "Interno": "#adb5bd"}

    df_grouped_montos = prepare_data_montos(df)
    df_grouped_percentage = prepare_data_percentage(df)

    fig1 = px.bar(
        df_grouped_montos,
        x="year",
        y="sum_value",
        color="Classificação no RGF",
        title="Montos por Año de Contratación (millones USD)",
        labels={"year": "Año de Contratación", "sum_value": "Montos (millones USD)"},
        color_discrete_map=color_map
    )
    fig1.update_layout(barmode='stack')
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        df_grouped_percentage,
        x="year",
        y="percentage",
        color="Classificação no RGF",
        title="Porcentajes por Año de Contratación",
        labels={"year": "Año de Contratación", "percentage": "Porcentaje (%)"},
        color_discrete_map=color_map
    )
    fig2.update_layout(barmode='stack', yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------- Página: Plazos -------------------------
elif pagina == "Plazos":
    st.title("Plazos")
    st.write("Porcentaje de operaciones por región y categoría de plazo.")
    
    df_grouped = df.groupby(["region", "class_plazo"]).size().reset_index(name="count")
    df_total = df.groupby("region").size().reset_index(name="total")
    df_grouped = df_grouped.merge(df_total, on="region")
    df_grouped["percentage"] = (df_grouped["count"] / df_grouped["total"]) * 100
    
    fig = px.bar(
        df_grouped,
        x="region",
        y="percentage",
        color="class_plazo",
        barmode="stack",
        labels={"region": "Región", "percentage": "Porcentaje (%)", "class_plazo": "Categoría de Plazo"},
        title="Porcentaje de operaciones por región y categoría de plazo"
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------- Página: Ext-int por región -------------------------
elif pagina == "Ext-int por región":
    st.title("Ext-int por región")
    st.write("Donut charts del top 4 'Nome do credor' por región basados en millones_usd.")
    
    # Primero, se crea una columna global para nombres truncados
    df['credor_short'] = df["Nome do credor"].apply(lambda x: x if len(x) <= 15 else x[:15] + "...")
    # Se obtiene el listado global de credores (truncados) para asignarles colores fijos
    unique_credors = sorted(df['credor_short'].unique())
    global_color_mapping = {}
    color_idx = 0
    # Asignar un color fijo a cada credor, forzando que si es FONPLATA se le asigne rojo (#FF0000)
    for cred in unique_credors:
        if cred.upper() == "FONPLATA":
            global_color_mapping[cred] = "#FF0000"
        else:
            global_color_mapping[cred] = other_palette[color_idx % len(other_palette)]
            color_idx += 1

    # Crear un gráfico único con subgráficos (tipo "domain") para cada región
    regiones = list(df["region"].unique())
    num_regions = len(regiones)
    num_cols = 3 if num_regions >= 3 else num_regions
    num_rows = math.ceil(num_regions / num_cols)
    
    specs = [[{"type": "domain"} for _ in range(num_cols)] for _ in range(num_rows)]
    subplot_titles = regiones  # Títulos: el nombre de cada región
    fig = make_subplots(rows=num_rows, cols=num_cols, specs=specs, subplot_titles=subplot_titles)
    
    for idx, reg in enumerate(regiones):
        row = idx // num_cols + 1
        col = idx % num_cols + 1
        df_reg = df[df["region"] == reg]
        df_group = df_reg.groupby("Nome do credor")["millones_usd"].sum().reset_index()
        df_group = df_group.sort_values(by="millones_usd", ascending=False)
        df_top4 = df_group.head(4)
        df_top4["credor_short"] = df_top4["Nome do credor"].apply(lambda x: x if len(x) <= 15 else x[:15] + "...")
        # Asignar colores usando el mapeo global (cada credor tendrá el mismo color en todos los gráficos)
        colors = [global_color_mapping[cred] for cred in df_top4["credor_short"]]
        trace = go.Pie(
            labels=df_top4["credor_short"],
            values=df_top4["millones_usd"],
            hole=0.4,
            textinfo="percent",
            marker=dict(colors=colors)
        )
        fig.add_trace(trace, row=row, col=col)
    
    fig.update_layout(
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
