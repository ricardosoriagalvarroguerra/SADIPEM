import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
plazo_range = st.sidebar.slider("Plazo", min_plazo, max_plazo, (min_plazo, max_plazo))
df = df[(df["plazo"] >= plazo_range[0]) & (df["plazo"] <= plazo_range[1])]

# Filtro para Tipo de Ente (Município o Estado)
tipo_ente = st.sidebar.selectbox("Tipo de Ente", ("Município", "Estado"))
df = df[df["Tipo de Ente"] == tipo_ente]

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

# Asignación de colores para cada clasificación
color_map = {"Externo": "#c1121f", "Interno": "#adb5bd"}

# Página: Origen de Financiamiento
if pagina == "Origen de Financiamiento":
    st.title("Origen de Financiamiento")
    st.write("Análisis interactivo del origen de financiamiento según 'Classificação no RGF' (Interno y Externo) a lo largo del tiempo, basado en millones USD.")

    # Preparar datos para montos y porcentajes
    df_grouped_montos = prepare_data_montos(df)
    df_grouped_percentage = prepare_data_percentage(df)

    # Crear figura con subgráficos (2 filas, 1 columna) y eje x compartido.
    # Ajustamos vertical_spacing para reducir el espacio entre gráficos.
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            "Montos por Año de Contratación (millones USD)",
            "Porcentajes por Año de Contratación"
        )
    )

    # Agregar trazas para el gráfico de montos (fila 1)
    for clas in df_grouped_montos["Classificação no RGF"].unique():
        subset = df_grouped_montos[df_grouped_montos["Classificação no RGF"] == clas]
        fig.add_bar(
            x=subset["year"],
            y=subset["sum_value"],
            name=clas,
            marker_color=color_map[clas],
            row=1, col=1
        )

    # Agregar trazas para el gráfico de porcentajes (fila 2)
    for clas in df_grouped_percentage["Classificação no RGF"].unique():
        subset = df_grouped_percentage[df_grouped_percentage["Classificação no RGF"] == clas]
        # Se oculta la leyenda en la segunda fila para evitar duplicados
        fig.add_bar(
            x=subset["year"],
            y=subset["percentage"],
            name=clas,
            marker_color=color_map[clas],
            showlegend=False,
            row=2, col=1
        )

    # Actualizar la configuración de la figura
    fig.update_layout(
        barmode='stack',
        height=800,
        title_text="Origen de Financiamiento"
    )
    fig.update_yaxes(title_text="Montos (millones USD)", row=1, col=1)
    fig.update_yaxes(title_text="Porcentaje (%)", range=[0, 100], row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

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
