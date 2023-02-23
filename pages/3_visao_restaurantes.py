# Bibliotecas necessarias
import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon='', layout = 'wide' )
#=========================================================================
# FUNÇÕES
#=========================================================================
def clean_code( df1 ):
    """ Esta função tem a responsabildade de limpar o dataframe.
    
    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Mudança de tipo da coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo
    
    
    Input: Dataframe
    Output: Dataframe 
    """
    
    # 1. Convertendo a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2. Convertendo a coluna Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. Convertendo a coluna Order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4. Convertendo multiple_deliveries de texto para numero inteiro
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5. Removendo os espaços dentro de strings/texto/object
    df1.loc[:,'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:, 'City'].str.strip()

    # 6. Limpando a coluna Time_take(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1]).astype(int)
    
    return df1



#===================Inicio da Estrutura lógica do código==================


#=========================================================================
# Importar dataset
#=========================================================================
df = pd.read_csv('dataset/train.csv')


#=========================================================================
# Limpando os dados
#=========================================================================
df1 = clean_code( df )


#=========================================================================
# BARRA LATERAL
#=========================================================================
st.header('Marktplace - Visão Restaurantes')

st.sidebar.markdown('# Curry company')
st.sidebar.markdown('## Fatest delivery in town')
st.sidebar.markdown( """---""")

st.sidebar.markdown( '## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered By Ricardo')


# filtro de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas,:]


# filtro de trafego
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas,:]



#=========================================================================
# LAYOUT DO STREAMLIT
#=========================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','',''] )

with tab1:
    with st.container():
        st.title('Overal Metrics')
        col1, col2, col3 = st.columns( 3 )
        with col1:
            delivery_unique = len( df1['Delivery_person_ID'].unique() )
            col1.metric('entregadores únicos', delivery_unique)
            
        with col2:            
            cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
            df1['distance'] = df1.loc[:,cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),                         (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis = 1)   
            a = round( df1['distance'].mean())
            col2.metric('Distância média', a)
            
            
        with col3:
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg(['mean','std']) )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = df_aux.loc[df_aux['Festival'] == 'Yes','avg_time']
            col3.metric('Tempo medio festival', df_aux)       
    
    with st.container():
        st.markdown("""---""")
        st.title('Tempo Medio de entrega por cidade')
        df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby(['City']).agg(['mean','std'])
        df_aux.columns = ['mean','std']
        cidade = df_aux.reset_index()
        st.dataframe( cidade )

    
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Tipo de pedido')
            df_aux = df1.loc[:, ['City','Type_of_order','Time_taken(min)']].groupby(['City', 'Type_of_order']).agg(['mean','std'])
            df_aux.columns = ['mean','std']
            trafego = df_aux.reset_index()
            st.dataframe (trafego )
            
        with col2:
            st.markdown( '##### Tipo de trafego')
            df_aux = df1.loc[:, ['City','Road_traffic_density','Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg(['mean','std'])
            df_aux.columns = ['mean','std']
            pedido = df_aux.reset_index()
            st.dataframe (pedido)
            


        