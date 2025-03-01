import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la barra lateral para la navegación entre páginas
st.sidebar.title("Navegación")
pagina = st.sidebar.radio("Selecciona una página:", (
    "Origen de Financiamiento",
    "Plazos",
    "Ext-int por región",
    "Nicho de Mercado",
    "Montos"
))

# Función para cargar los datos desde el archivo Parquet
@st.cache_data
def load_data():
    # Se carga el dataset "sadipem.parquet"
    df = pd.read_parquet("sadipem.parquet")
    # Convertir la columna de fecha a formato datetime y extraer el año
    df['fecha_contratacion'] = pd.to_datetime(df['fecha_contratacion'], errors='coerce')
    df['year'] = df['fecha_contratacion'].dt.year
    return df

# Función para agrupar y calcular porcentajes por año y "Tipo de Ente"
def prepare_data(data):
    # Agrupar por año y "Tipo de Ente"
    df_grouped = data.groupby(['year', 'Tipo de Ente']).size().reset_index(name='count')
    # Calcular el total de registros por año
    total = data.groupby('year').size().reset_index(name='total')
    # Unir para calcular el porcentaje
    df_grouped = df_grouped.merge(total, on='year')
    df_grouped['percentage'] = (df_grouped['count'] / df_grouped['total']) * 100
    return df_grouped

# Página: Origen de Financiamiento
if pagina == "Origen de Financiamiento":
    st.title("Origen de Financiamiento")
    st.write("Análisis interactivo del origen de financiamiento a lo largo del tiempo (agrupado por año).")

    # Cargar los datos
    df = load_data()

    # Primer gráfico: Todos los registros (todos los plazos)
    df_grouped = prepare_data(df)
    fig1 = px.bar(
        df_grouped,
        x="year",
        y="percentage",
        color="Tipo de Ente",
        title="Distribución por Año de Contratación (Todos los plazos)",
        labels={"year": "Año de Contratación", "percentage": "Porcentaje"}
    )
    fig1.update_layout(barmode='stack', yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig1, use_container_width=True)

    # Segundo gráfico: Filtrando registros con plazo > 14
    df_filtered = df[df["plazo"] > 14]
    if df_filtered.empty:
        st.write("No hay registros con plazo > 14.")
    else:
        df_grouped2 = prepare_data(df_filtered)
        fig2 = px.bar(
            df_grouped2,
            x="year",
            y="percentage",
            color="Tipo de Ente",
            title="Distribución por Año de Contratación (Plazo > 14)",
            labels={"year": "Año de Contratación", "percentage": "Porcentaje"}
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
