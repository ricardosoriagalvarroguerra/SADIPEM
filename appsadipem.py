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

# Filtro por millones_usd en la barra lateral
st.sidebar.title("Filtros")
min_val = df["millones_usd"].min()
max_val = df["millones_usd"].max()
valor_range = st.sidebar.slider("Valor de Contratación (millones USD)",
                                float(min_val), float(max_val),
                                (float(min_val), float(max_val)))
df = df[(df["millones_usd"] >= valor_range[0]) & (df["millones_usd"] <= valor_range[1])]

# Función para agrupar y calcular porcentajes por año y "Classificação no RGF" usando millones_usd
def prepare_data_rgf(data):
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

    # Primer gráfico: Todos los registros
    df_grouped = prepare_data_rgf(df)
    fig1 = px.bar(
        df_grouped,
        x="year",
        y="percentage",
        color="Classificação no RGF",
        title="Distribución por Año de Contratación (Todos los registros)",
        labels={"year": "Año de Contratación", "percentage": "Porcentaje"},
        color_discrete_map={"Externo": "#780000", "Interno": "#6c757d"}
    )
    fig1.update_layout(barmode='stack', yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig1, use_container_width=True)

    # Segundo gráfico: Filtrando registros con plazo > 14 y < 54
    df_filtered = df[(df["plazo"] > 14) & (df["plazo"] < 54)]
    if df_filtered.empty:
        st.write("No hay registros con plazo entre 14 y 54.")
    else:
        df_grouped2 = prepare_data_rgf(df_filtered)
        fig2 = px.bar(
            df_grouped2,
            x="year",
            y="percentage",
            color="Classificação no RGF",
            title="Distribución por Año de Contratación (Plazo > 14 y < 54)",
            labels={"year": "Año de Contratación", "percentage": "Porcentaje"},
            color_discrete_map={"Externo": "#780000", "Interno": "#6c757d"}
        )
        fig2.update_layout(barmode='stack', yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig2, use_container_width=True)

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
