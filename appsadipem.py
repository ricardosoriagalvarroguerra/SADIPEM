import streamlit as st
import pandas as pd
import plotly.express as px

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

# Filtros en la barra lateral
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
plazo_range = st.sidebar.slider("Plazo",
                                min_plazo, max_plazo,
                                (min_plazo, max_plazo))
df = df[(df["plazo"] >= plazo_range[0]) & (df["plazo"] <= plazo_range[1])]

# Funciones para preparar datos para los gráficos

def prepare_data_montos(data):
    # Filtrar solo los registros con "Interno" y "Externo"
    data = data[data["Classificação no RGF"].isin(["Interno", "Externo"])]
    df_grouped = data.groupby(['year', 'Classificação no RGF'])['millones_usd'].sum().reset_index(name='sum_value')
    return df_grouped

def prepare_data_percentage(data):
    # Filtrar solo los registros con "Interno" y "Externo"
    data = data[data["Classificação no RGF"].isin(["Interno", "Externo"])]
    df_grouped = data.groupby(['year', 'Classificação no RGF'])['millones_usd'].sum().reset_index(name='sum_value')
    total = data.groupby('year')['millones_usd'].sum().reset_index(name='total_value')
    df_grouped = df_grouped.merge(total, on='year')
    df_grouped['percentage'] = (df_grouped['sum_value'] / df_grouped['total_value']) * 100
    return df_grouped

# Página: Origen de Financiamiento
if pagina == "Origen de Financiamiento":
    st.title("Origen de Financiamiento")
    st.write("Análisis interactivo del origen de financiamiento según la variable 'Classificação no RGF' (Interno y Externo) a lo largo del tiempo, basado en millones USD.")

    # Gráfico 1: Montos Stacked
    df_grouped_montos = prepare_data_montos(df)
    fig_montos = px.bar(
        df_grouped_montos,
        x="year",
        y="sum_value",
        color="Classificação no RGF",
        title="Montos por Año de Contratación (millones USD)",
        labels={"year": "Año de Contratación", "sum_value": "Montos (millones USD)"}
    )
    fig_montos.update_layout(barmode='stack')
    st.plotly_chart(fig_montos, use_container_width=True)

    # Gráfico 2: Porcentajes Stacked
    df_grouped_percentage = prepare_data_percentage(df)
    fig_percentage = px.bar(
        df_grouped_percentage,
        x="year",
        y="percentage",
        color="Classificação no RGF",
        title="Porcentajes por Año de Contratación",
        labels={"year": "Año de Contratación", "percentage": "Porcentaje (%)"}
    )
    fig_percentage.update_layout(barmode='stack', yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_percentage, use_container_width=True)

# Página: Plazos
elif pagina == "Plazos":
    st.title("Plazos")
    st.write("Esta es la página de Plazos.")
    # Aquí puedes agregar el contenido y la lógica correspondiente

# Página: Ext-int por región
elif pagina == "Ext-int por región":
    st.title("Ext-int por región")
    st.write("Esta es la página de Ext-int por región.")
    # Aquí puedes agregar el contenido y la lógica correspondiente

# Página: Nicho de Mercado
elif pagina == "Nicho de Mercado":
    st.title("Nicho de Mercado")
    st.write("Esta es la página de Nicho de Mercado.")
    # Aquí puedes agregar el contenido y la lógica correspondiente

# Página: Montos
elif pagina == "Montos":
    st.title("Montos")
    st.write("Esta es la página de Montos.")
    # Aquí puedes agregar el contenido y la lógica correspondiente
