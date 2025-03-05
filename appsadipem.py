import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.express as px
import plotly.graph_objects as go

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
# Para las páginas "Plazos" y "Ext-int por región" se utiliza únicamente el filtro de Tipo de Ente (multiselect)
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
    
    # Gráfico de montos
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
    
    # Gráfico de porcentajes
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
        labels={"region": "Región", "percentage": "Porcentaje (%)", "class_plazo": "Categoría de Plazo"},
        title="Porcentaje de operaciones por región y categoría de plazo"
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------- Página: Ext-int por región -------------------------
elif pagina == "Ext-int por región":
    st.title("Ext-int por región")
    st.write("Donut charts del top 4 'Nome do credor' por región basados en millones_usd.")
    
    # Obtener la lista de regiones
    regiones = list(df["region"].unique())
    # Usar número fijo de columnas (3) o la cantidad de regiones disponibles, lo que sea menor
    ncols = 3 if len(regiones) >= 3 else len(regiones)
    for i in range(0, len(regiones), ncols):
        cols = st.columns(ncols)
        for j in range(ncols):
            if i + j < len(regiones):
                reg = regiones[i + j]
                df_reg = df[df["region"] == reg]
                # Agrupar por "Nome do credor" y sumar "millones_usd"
                df_group = df_reg.groupby("Nome do credor")["millones_usd"].sum().reset_index()
                df_group = df_group.sort_values(by="millones_usd", ascending=False)
                df_top4 = df_group.head(4)
                # Crear una nueva columna con nombres truncados a 15 caracteres
                df_top4["credor_short"] = df_top4["Nome do credor"].apply(
                    lambda x: x if len(x) <= 15 else x[:15] + "..."
                )
                # Crear donut chart individual con dimensiones fijas (300x300)
                fig = px.pie(
                    df_top4,
                    names="credor_short",
                    values="millones_usd",
                    title=f"Top 4 Credores en {reg}",
                    hole=0.4,
                    width=300,
                    height=300
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(font=dict(size=10))
                )
                cols[j].plotly_chart(fig, use_container_width=False)

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
