import streamlit as st
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Análisis de Partidos Internacionales", page_icon='⚽', layout='wide')

df = pd.read_csv('data/results.csv')
df2 = df.sample(n=1000, random_state=42)

df['date'] = pd.to_datetime(df['date'], errors='coerce')

    
def aplicar_estilos():
    st.markdown("""
        <style>
            /* Cambia color de fondo del sidebar */
            [data-testid="stSidebar"] {
                background-color: #277e31;
            }

            /* Cambia el fondo del main */
            .stApp {
                background-color: #277e31;
            }

            /* Estilo de los selectbox */
            .stSelectbox div {
                background-color: #277e31;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)

aplicar_estilos()
    

def main():
    st.title("⚽ Análisis histórico de partidos internacionales")
    st.write("Esta aplicación analiza los partidos internacionales por país a lo largo de la historia.")
    
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://cdn.dribbble.com/userupload/24357747/file/original-3e9bf95c056665e14225d1d53ac2de71.jpg?resize=752x&vertical=center");
        background-size: repeat;
        background-position: center;
    }
    </style>
    """, unsafe_allow_html=True)

    #Side bar

    st.sidebar.header("🏆 Navegación rápida")
    seccion = st.sidebar.radio("Ir a la sección:", ["Inicio", "Análisis por Países", "Local y visitante", "Gráficos, Mapas y más"])

    if seccion == "Inicio":
        columna1, columna2 = st.columns(2)
        with columna1:
            st.image('images/futbol.jpg', width=1000, use_container_width=True)
        with columna2:
            st.image('images/futbol2.jpg', width=1000, use_container_width=True)
        st.subheader("🏁 Bienvenido")
        st.write("Explorá datos de partidos entre selecciones nacionales.")
        st.dataframe(df.head(10))
    
    st.divider()
    
############ APARTADO PARA ANÁLISIS POR PAÍSES
    if seccion == 'Análisis por Países':
        st.subheader("🌎 Análisis por países")
        st.write("En este apartado, según el pais elégido, muestra 5 de sus últimos partidos.")
        
        paises = ["-- Selecciona un país --"] + list(sorted(df["country"].unique()))
        
        pais = st.selectbox(
            'Elige un país:',
            paises
        )
        
        if pais != "-- Selecciona un país --":
            df_paises_elegidos = df[df["country"] == pais].copy()
            
            st.write(df_paises_elegidos.sort_values(by='date', ascending=False).head(5))

            # Asignamos el resultado directamente en una sola columna
            df_paises_elegidos['Resultado'] = np.select(
                condlist=[
                    ((df_paises_elegidos['home_team'] == pais) & (df_paises_elegidos['home_score'] > df_paises_elegidos['away_score'])) |
                    ((df_paises_elegidos['away_team'] == pais) & (df_paises_elegidos['away_score'] > df_paises_elegidos['home_score'])),
                    
                    (df_paises_elegidos['home_score'] == df_paises_elegidos['away_score'])
                ],
                choicelist=['Ganados', 'Empatados'],
                default='Perdidos'
            )
            
            ganados = (df_paises_elegidos['Resultado'] == 'Ganados').sum()
            empatados = (df_paises_elegidos['Resultado'] == 'Empatados').sum()
            perdidos = (df_paises_elegidos['Resultado'] == 'Perdidos').sum()
            
            st.subheader(f'Históricamente,  *{pais}*  ha ganado {ganados} partidos, perdió {perdidos} y empató {empatados}')
        
        
            resultados = pd.DataFrame({
                'Resultado': ['Ganados', 'Perdidos', 'Empatados'],
                'Cantidad': [ganados, perdidos, empatados]
            })
            
            columna1, columna2 = st.columns(2)
            
            with columna1:
                fig = px.bar(
                    resultados, 
                    x="Resultado", 
                    y="Cantidad", 
                    color='Resultado',
                    color_discrete_map={
                        "Ganados": "green",
                        "Perdidos": "red",
                        "Empatados": "gray",
                        }, 
                    title=f'Resultados históricos de {pais}')
                st.plotly_chart(fig, use_container_width=True)
            
            with columna2: 
                fig2 = px.pie(
                    resultados, 
                    values='Cantidad', 
                    names="Resultado",
                    color="Resultado",
                    color_discrete_map={
                        "Ganados": "green",
                        "Perdidos": "red",
                        "Empatados": "gray",
                        },
                    title=f"Porcentaje de resultados de {pais}")
                st.plotly_chart(fig2, use_container_width=True)
            
            resultado_elegido = st.selectbox(
                'Elige el resultado:',
                ['Ganados', 'Perdidos', 'Empatados']
            )
            
            df_paises_histogram = df_paises_elegidos
            df_paises_histogram['año'] = pd.to_datetime(df_paises_histogram['date']).dt.year

            df_paises_histogram_filt = df_paises_histogram[df_paises_histogram['Resultado'] == resultado_elegido]
            
            fig3 = px.histogram(
                df_paises_histogram_filt, 
                x="año", 
                nbins=100,
                title=f"Partidos a lo largo de la historia de {pais}",
                color='Resultado',
                color_discrete_map={
                    "Ganados": "green",
                    "Perdidos": "red",
                    "Empatados": "gray",
                    },
                )
            
            fig3.update_layout(
                xaxis_title="Años",
                yaxis_title="Cantidad de partidos"
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
         st.warning("Selecciona un país para ver los resultados.")


############ APARTADO PARA LOCAL Y VISITANTE DE PAÍSES

        
    elif seccion == 'Local y visitante':
        st.subheader("🏟️ Rendimiento siendo local o visitante")
        st.write("En este apartado, según el país elegido, se muestra la comparación del rendimiento entre partidos de local y de visitante.")

        paises = ["-- Selecciona un país --"] + list(sorted(df["country"].unique()))
        pais = st.selectbox('Elige un país:', paises)

        if pais != "-- Selecciona un país --":
            df_filtrado = df[(df['home_team'] == pais) | (df['away_team'] == pais)].copy()

            df_filtrado['condicion'] = np.where(df_filtrado['home_team'] == pais, 'Local', 'Visitante')

            df_filtrado['Resultado'] = np.select(
                condlist=[
                    ((df_filtrado['home_team'] == pais) & (df_filtrado['home_score'] > df_filtrado['away_score'])) |
                    ((df_filtrado['away_team'] == pais) & (df_filtrado['away_score'] > df_filtrado['home_score'])),
                    
                    df_filtrado['home_score'] == df_filtrado['away_score']
                ],
                choicelist=['Ganado', 'Empatado'],
                default='Perdido'
            )

            resumen = df_filtrado.groupby(['condicion', 'Resultado']).size().reset_index(name='Cantidad')

            fig = px.bar(
                resumen,
                x='condicion',
                y='Cantidad',
                color='Resultado',
                barmode='group',
                color_discrete_map={
                    'Ganado': 'green',
                    'Perdido': 'red',
                    'Empatado': 'gray'
                },
                title=f'Rendimiento de {pais} como local y visitante'
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Selecciona un país para ver los resultados.")

############ APARTADO PARA GRÁFICOS y MAPAS
        
    elif seccion == 'Gráficos, Mapas y más':
        st.subheader("📌 Mapa mundial de partidos jugados por país")
        st.write("Visualizá la cantidad total de partidos jugados por cada país en el mapa. Solo se consideran países que hayan jugado al menos un partido internacional.")

        partidos_local = df.groupby('home_team').size()
        partidos_visitante = df.groupby('away_team').size()

        partidos_total = partidos_local.add(partidos_visitante, fill_value=0).reset_index()
        partidos_total.columns = ['country', 'total_matches']

        fig_map = px.choropleth(
            partidos_total,
            locations='country',
            locationmode='country names',
            color='total_matches',
            color_continuous_scale='greens',
            title="🌍 Total de partidos jugados por país",
        )
        fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")
        st.subheader("📅 Distribución de partidos a lo largo del tiempo")
        st.write("Este gráfico muestra cómo han evolucionado los partidos internacionales año a año.")

        df['año'] = df['date'].dt.year
        partidos_por_año = df.groupby('año').size().reset_index(name='cantidad')

        fig_line = px.line(
            partidos_por_año,
            x='año',
            y='cantidad',
            markers=True,
            title='📈 Evolución histórica de partidos internacionales por año',
        )
        fig_line.update_layout(xaxis_title='Año', yaxis_title='Cantidad de partidos')
        st.plotly_chart(fig_line, use_container_width=True)


if __name__ == '__main__':
    main()