# Bibliotecas necessarias
import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='', layout = 'wide' )
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


def order_metric( df1 ):
    # colunas
    cols = ['ID', 'Order_Date']
    # Seleção de linhas
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
            
    return fig


def traffic_order_share( df1 ):
    df_aux =  df1.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    linhas = df_aux['Road_traffic_density'] != 'NaN'
    df_aux = df_aux.loc[linhas, :]
    df_aux['entregas_porc'] = df_aux['ID']/df_aux['ID'].sum()
    fig = px.pie(df_aux, values = 'entregas_porc', names='Road_traffic_density')
                
    return fig


def traffic_Order_city( df1 ):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[ (df_aux['City'] != 'NaN') & (df_aux['Road_traffic_density'] != 'NaN'), :]
    fig = px.scatter( df_aux, x='City', y= 'Road_traffic_density', size = 'ID')
    
    return fig


def order_by_week( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x = 'week_of_year', y= 'ID')
            
    return fig


def order_share_by_week( df1 ):
    df_aux01 = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['Order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x = 'week_of_year', y= 'Order_by_deliver')
            
    return fig


def country_maps( df1 ):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ] ].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[ (df_aux['City'] != 'NaN') & (df_aux['Road_traffic_density'] != 'NaN'), :]

    map = folium.Map(zoom_start=11)
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    return folium_static( map )

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
st.header('Marktplace - Visão do cliente')

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','Visão tática','Visão Geografica'] )

with tab1:
    # Order Metric
    fig = order_metric( df1 )
    st.markdown('# Order by day')
    st.plotly_chart(fig, use_container_widht=True)     

    

    col1, col2 = st.columns(2)
        
    with col1:
        fig = traffic_order_share( df1 )
        st.markdown('##### Traffic Order Share')
        st.plotly_chart(fig, use_container_widht=True)                
                
    with col2:
        fig = traffic_Order_city( df1 )
        st.markdown('##### Traffic Order City')
        st.plotly_chart(fig, use_container_widht=True)
            
              
with tab2:
    with st.container():
        st.markdown( '# Order by Week' )
        fig = order_by_week (df1 )
        st.plotly_chart(fig, use_container_widht=True)
        

    with st.container():
        st.markdown( '# Order Share by Week' )
        fig = order_share_by_week (df1 )
        st.plotly_chart(fig, use_container_widht=True)        
        
        
with tab3:
    st.markdown('# Country maps')
    country_maps(df1)




