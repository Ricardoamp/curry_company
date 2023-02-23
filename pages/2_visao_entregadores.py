# Bibliotecas necessarias
import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='', layout = 'wide' )
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

def top_delivers( df1, top_asc ):
    df2 = df1.loc[:, ['Delivery_person_ID','City','Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat ( [df_aux01,df_aux02,df_aux03]).reset_index(drop=True)
                
    return df3


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
st.header('Marktplace - Visão Entregadores')

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
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4,gap='large')        
        
        with col1:
            df_aux_max = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric( 'Maior de idade', df_aux_max )

        with col2:
            df_aux_min = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor de idade', df_aux_min )
  
        with col3:
            df_veiculo_max = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição', df_veiculo_max )

        with col4:
            df_veiculo_min = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', df_veiculo_min )

            
    with st.container():
        st.markdown("""---""")
        st.title( 'Avaliações')
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            colunas = df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe ( colunas )
            
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            transito = df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density'] ].groupby('Road_traffic_density').aggregate(['mean','std']).reset_index()
            st.dataframe ( transito )
            
            
            st.markdown('##### Avaliação média por clima')
            avaliacao_media = df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']].groupby('Weatherconditions').agg( {'Delivery_person_Ratings' : ['mean','std']})

            avaliacao_media.columns = ['mean', 'std']
            clima = avaliacao_media.reset_index()
            st.dataframe ( clima )
    
    
    with st.container():
        st.markdown("""---""")
        st.title( 'Velocidade de Entregas')
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers( df1,top_asc = True )
            st.dataframe( df3 )
            
                        
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers( df1, top_asc= False )
            st.dataframe( df3)
