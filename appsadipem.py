import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuración de la barra lateral para la navegación entre páginas usando menú desplegable
st.sidebar.title("Navegación")
pagina = st.sidebar.selectbox("Selecciona una página:", (
    "Origen de Financiamiento",
    "Plazos",
    "Ext-int por región",
    "Nicho de Mercado",
    "Montos"
))

# Función para cargar los datos desde el archivo Parquet
@st.cache_data
def load_data():
    df = pd.read_parquet("sadipem.parquet")
    df['fecha_contratacion'] = pd.to_datetime(df['fecha_contratacion'], errors='coerce')
    df['year'] = df['fecha_contratacion'].dt.year
    # Crear la columna 'millones_usd' a partir de 'Valor_contratacion_USD'
    df['millones_usd'] = df["Valor_contratacion_USD"] / 1e6
    return df

# Cargar los datos y eliminar registros con Valor_contratacion_USD negativo
df = load_data()
df = df[df["Valor_contratacion_USD"] >= 0]

# Filtros en la barra lateral (aplican para todas las páginas)
st.sidebar.title("Filtros")

# Filtro para Valor de Contratación en millones USD
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

# Filtro para Tipo de Ente (Município o Estado)
tipo_ente = st.sidebar.selectbox("Tipo de Ente", ("Município", "Estado"))
df = df[df["Tipo de Ente"] == tipo_ente]

# ------------------------- Página: Plazos -------------------------
if pagina == "Plazos":
    st.title("Plazos")
    st.write("Porcentaje de operaciones por rango de plazo y región.")

    # Crear la columna categórica de plazo
    # Definimos los intervalos: menor a 5, 5 a 8, 9 a 13, 14 a 20 y mayor a 20 años.
    bins = [0, 5, 9, 14, 21, np.inf]
    labels = ["Menor a 5 años", "5 a 8 años", "9 a 13 años", "14 a 20 años", "Mayor a 20 años"]
    df["plazo_category"] = pd.cut(df["plazo"], bins=bins, labels=labels, right=False)

    # Agrupar por región y categoría de plazo para contar el número de operaciones
    df_grouped = df.groupby(["region", "plazo_category"]).size().reset_index(name="count")
    # Calcular el total de operaciones por región
    df_total = df.groupby("region").size().reset_index(name="total")
    df_grouped = df_grouped.merge(df_total, on="region")
    df_grouped["percentage"] = (df_grouped["count"] / df_grouped["total"]) * 100

    # Crear el gráfico de barras apiladas
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

# ------------------------- Página: Origen de Financiamiento -------------------------
elif pagina == "Origen de Financiamiento":
    # (Aquí iría el código existente para la página "Origen de Financiamiento")
    st.title("Origen de Financiamiento")
    st.write("Análisis interactivo del origen de financiamiento según 'Classificação no RGF' a lo largo del tiempo, basado en millones USD.")
    # ... (resto del código para esta página)

# ------------------------- Página: Ext-int por región -------------------------
elif pagina == "Ext-int por región":
    st.title("Ext-int por región")
    st.write("Esta es la página de Ext-int por región.")
    # Aquí puedes agregar el contenido y la lógica correspondiente

# ------------------------- Página: Nicho de Mercado -------------------------
elif pagina == "Nicho de Mercado":
    st.title("Nicho de Mercado")
    st.write("Esta es la página de Nicho de Mercado.")
    # Aquí puedes agregar el contenido y la lógica correspondiente

# ------------------------- Página: Montos -------------------------
elif pagina == "Montos":
    st.title("Montos")
    st.write("Esta es la página de Montos.")
    # Aquí puedes agregar el contenido y la lógica correspondiente
