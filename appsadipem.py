import streamlit as st

# Configuración de la barra lateral para navegación
st.sidebar.title("Navegación")
pagina = st.sidebar.radio("Selecciona una página:", (
    "Origen de Financiamiento",
    "Plazos",
    "Ext-int por región",
    "Nicho de Mercado",
    "Montos"
))

# Página: Origen de Financiamiento
if pagina == "Origen de Financiamiento":
    st.title("Origen de Financiamiento")
    st.write("Esta es la página de Origen de Financiamiento.")
    # Aquí puedes agregar el contenido y lógica correspondiente

# Página: Plazos
elif pagina == "Plazos":
    st.title("Plazos")
    st.write("Esta es la página de Plazos.")
    # Aquí puedes agregar el contenido y lógica correspondiente

# Página: Ext-int por región
elif pagina == "Ext-int por región":
    st.title("Ext-int por región")
    st.write("Esta es la página de Ext-int por región.")
    # Aquí puedes agregar el contenido y lógica correspondiente

# Página: Nicho de Mercado
elif pagina == "Nicho de Mercado":
    st.title("Nicho de Mercado")
    st.write("Esta es la página de Nicho de Mercado.")
    # Aquí puedes agregar el contenido y lógica correspondiente

# Página: Montos
elif pagina == "Montos":
    st.title("Montos")
    st.write("Esta es la página de Montos.")
    # Aquí puedes agregar el contenido y lógica correspondiente
