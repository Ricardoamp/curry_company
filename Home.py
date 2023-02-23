import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon=""
)    



st.sidebar.markdown('# Curry company')
st.sidebar.markdown('## Fatest delivery in town')
st.sidebar.markdown( """---""")


st.write( "# Curry Company Growth Dashboard" )

st.markdown(
    """
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
""")
    