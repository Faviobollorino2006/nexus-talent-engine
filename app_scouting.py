import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración general
st.set_page_config(page_title="Nexus Talent Engine", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🔒 SISTEMA DE SEGURIDAD
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Acceso Restringido")
        st.markdown("**Nexus Talent Engine** - Módulo de uso exclusivo para personal autorizado.")
        password = st.text_input("Ingrese la contraseña corporativa", type="password")
        if st.button("Desbloquear Sistema"):
            if password == "Scout2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas. Acceso denegado.")
    st.stop() 

# ==========================================
# ⚡ APLICACIÓN PRINCIPAL
# ==========================================
st.title("⚡ Nexus Talent Engine: Módulo Formativo")
st.markdown("Plataforma independiente para la proyección de talento y corrección del Efecto de la Edad Relativa (RAE).")
st.markdown("---")

@st.cache_data 
def cargar_datos():
    conexion = sqlite3.connect("scouting_formativas.db")
    df = pd.read_sql_query("SELECT * FROM proyecciones_scouting", conexion)
    conexion.close()
    return df

df_jugadores = cargar_datos()

# --- SISTEMA DE TRES PESTAÑAS ---
tab_dashboard, tab_scouting, tab_masiva = st.tabs([
    "📊 Dashboard General", 
    "➕ Evaluación en Vivo (Scouting)", 
    "📁 Carga Masiva de Plantillas"
])

# ==========================================
# PESTAÑA 1: DASHBOARD HISTÓRICO
# ==========================================
with tab_dashboard:
    st.sidebar.header("⚙️ Filtros (Dashboard)")
    clubes = ["Todos"] + df_jugadores['Club_Actual'].unique().tolist()
    club_seleccionado = st.sidebar.selectbox("Seleccionar Club", clubes)

    categorias = ["Todas"] + df_jugadores['Categoria'].unique().tolist()
    categoria_seleccionada = st.sidebar.selectbox("Seleccionar Categoría", categorias)

    df_filtrado = df_jugadores.copy()
    if club_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Club_Actual'] == club_seleccionado]
    if categoria_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_seleccionada]

    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Exportar Datos")
    csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Descargar Reporte (CSV)",
        data=csv_export,
        file_name=f'reporte_nexus_{club_seleccionado}_{categoria_seleccionada}.csv',
        mime='text/csv',
        help="Exporta la tabla actual para reportes ejecutivos o uso en Excel."
    )

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Jugadores en Base", len(df_filtrado))
    with col2: st.metric("Listos para Primer Equipo", len(df_filtrado[df_filtrado['Decision_Directiva'] == 'Promover al Primer Equipo']))
    with col3: st.metric("Valor Promedio Proyectado", f"${df_filtrado['Valor_Mercado_Proyectado_USD'].mean():,.0f}" if not df_filtrado.empty else "$0")

    st.markdown("---")
    col_grafico1, col_grafico2 = st.columns(2)
    colores_decision = {'Promover al Primer Equipo': '#00FF7F', 'Proyección a Futura Venta': '#FFD700', 'Mantener en Desarrollo': '#00FFFF', 'Alerta de Rendimiento': '#FF4040'}

    with col_grafico1:
        st.subheader("🎯 Talentos Ocultos vs Espejismos Físicos")
        if not df_filtrado.empty:
            fig_scatter = px.scatter(df_filtrado, x="Edad_Biologica", y="Valor_Mercado_Proyectado_USD", color="Decision_Directiva", color_discrete_map=colores_decision, hover_name="Nombre")
            fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_scatter, use_container_width=True)

    with col_grafico2:
        st.subheader("🕸️ Perfil 360° del Jugador")
        if not df_filtrado.empty:
            jugador_seleccionado = st.selectbox("Selecciona un jugador:", df_filtrado['Nombre'].tolist())
            datos_jugador = df_filtrado[df_filtrado['Nombre'] == jugador_seleccionado].iloc[0]
            categorias_radar = ['Veloc_Max_kmh', 'xG', 'xA', 'Pases_Progresivos', 'Puntaje_Resiliencia']
            valores_radar = [datos_jugador['Veloc_Max_kmh']/35*100, datos_jugador['xG']/15*100, datos_jugador['xA']/15*100, datos_jugador['Pases_Progresivos']/150*100, datos_jugador['Puntaje_Resiliencia']/10*100]
            fig_radar = go.Figure(data=go.Scatterpolar(r=valores_radar, theta=categorias_radar, fill='toself', line_color='#00FFFF'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Base de Datos Activa")
    st.dataframe(df_filtrado, use_container_width=True)

# ==========================================
# PESTAÑA 2: EVALUACIÓN EN VIVO (Con Accesibilidad)
# ==========================================
with tab_scouting:
    st.subheader("➕ Ingreso de Nuevo Talento")
    
    with st.form("formulario_scouting"):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            st.markdown("**Datos Generales y Biométricos**")
            nombre_nuevo = st.text_input("Nombre del Jugador", help="Ingresa el nombre completo o identificador.")
            club_nuevo = st.selectbox("Club Actual", ["Barcelona SC", "Independiente del Valle", "LDU Quito", "Emelec", "Aucas", "Otro"])
            categoria_nueva = st.selectbox("Categoría", ["Sub-17", "Sub-19"])
            edad_crono_nueva = st.number_input("Edad Cronológica (Años)", 14.0, 20.0, 16.0, 0.1, help="Edad exacta basada en la fecha de nacimiento.")
            edad_bio_nueva = st.number_input("Edad Biológica (Años)", 13.0, 21.0, 16.0, 0.1, help="Edad de desarrollo físico estimada mediante radiografía carpal o pico de velocidad de crecimiento.")
            velocidad_nueva = st.number_input("Velocidad Máxima (km/h)", 20.0, 38.0, 28.0, 0.1)
            
        with col_form2:
            st.markdown("**Métricas Técnicas y Psicológicas**")
            posicion_nueva = st.selectbox("Posición Principal", ["Delantero", "Mediocampista", "Defensa", "Portero"])
            pases_nuevos = st.number_input("Pases Progresivos", 0, 300, 50, help="Pases exitosos que acercan el balón un 25% más a la portería rival.")
            xg_nuevo = st.number_input("Goles Esperados (xG)", 0.0, 30.0, 2.5, 0.1)
            xa_nuevo = st.number_input("Asistencias Esperadas (xA)", 0.0, 30.0, 2.5, 0.1)
            resiliencia_nueva = st.number_input("Resiliencia Mental (1-10)", 1.0, 10.0, 7.0, 0.5, help="Puntuación psicológica evaluada por el cuerpo técnico.")
            minutos_nuevos = st.number_input("Minutos Jugados", 0, 3000, 900)
            
        boton_evaluar = st.form_submit_button("🧠 Ejecutar Motor Predictivo y Guardar")
        
    if boton_evaluar and nombre_nuevo != "":
        coef_rae_nuevo = edad_crono_nueva / edad_bio_nueva
        puntaje_nuevo = min(((pases_nuevos / 150) * 20) + ((xg_nuevo + xa_nuevo) * 20) + ((velocidad_nueva / 35) * 30 * coef_rae_nuevo) + ((resiliencia_nueva / 10) * 30), 100)
        valor_nuevo = (puntaje_nuevo * 15000) + (minutos_nuevos * 100)
        
        if puntaje_nuevo >= 85: decision_nueva = "Promover al Primer Equipo"
        elif puntaje_nuevo >= 70: decision_nueva = "Proyección a Futura Venta"
        elif puntaje_nuevo >= 50: decision_nueva = "Mantener en Desarrollo"
        else: decision_nueva = "Alerta de Rendimiento"
            
        try:
            conexion = sqlite3.connect("scouting_formativas.db")
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO proyecciones_scouting (Nombre, Categoria, Club_Actual, Posicion, Edad_Cronologica, Edad_Biologica, Minutos_Jugados, Pases_Progresivos, xG, xA, Veloc_Max_kmh, Puntaje_Resiliencia, Coeficiente_RAE, Puntaje_Consolidacion, Valor_Mercado_Proyectado_USD, Decision_Directiva) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (nombre_nuevo, categoria_nueva, club_nuevo, posicion_nueva, edad_crono_nueva, edad_bio_nueva, minutos_nuevos, pases_nuevos, xg_nuevo, xa_nuevo, velocidad_nueva, resiliencia_nueva, coef_rae_nuevo, puntaje_nuevo, valor_nuevo, decision_nueva))
            conexion.commit()
            conexion.close()
            st.cache_data.clear()
            st.success(f"💾 {nombre_nuevo} evaluado como '{decision_nueva}' y guardado con éxito.")
        except Exception as e:
            st.error(f"❌ Error en base de datos: {e}")

# ==========================================
# PESTAÑA 3: CARGA MASIVA DE DATOS (CSV)
# ==========================================
with tab_masiva:
    st.subheader("📁 Procesamiento de Plantillas Completas")
    st.markdown("Sube un archivo `.csv` para evaluar a múltiples jugadores simultáneamente. El sistema calculará el coeficiente RAE, el valor de mercado y la decisión directiva para cada fila, y los anexará a la base de datos segura.")
    
    archivo_subido = st.file_uploader("Arrastra tu archivo CSV aquí", type=["csv"], help="Asegúrate de que las columnas coincidan con las métricas requeridas.")
    
    if archivo_subido is not None:
        try:
            # Leemos el archivo masivo
            df_masivo = pd.read_csv(archivo_subido)
            st.write("Vista previa de los datos a procesar:", df_masivo.head(3))
            
            if st.button("🚀 Procesar e Insertar Lote Completo"):
                # 1. El motor procesa toda la plantilla a la vez
                df_masivo['Coeficiente_RAE'] = df_masivo['Edad_Cronologica'] / df_masivo['Edad_Biologica']
                
                df_masivo['Puntaje_Consolidacion'] = (
                    ((df_masivo['Pases_Progresivos'] / 150) * 20) + 
                    ((df_masivo['xG'] + df_masivo['xA']) * 20) +
                    ((df_masivo['Veloc_Max_kmh'] / 35) * 30 * df_masivo['Coeficiente_RAE']) + 
                    ((df_masivo['Puntaje_Resiliencia'] / 10) * 30)
                ).round(1).clip(upper=100)
                
                df_masivo['Valor_Mercado_Proyectado_USD'] = ((df_masivo['Puntaje_Consolidacion'] * 15000) + (df_masivo['Minutos_Jugados'] * 100)).round(0)
                
                def clasificar_lote(puntaje):
                    if puntaje >= 85: return "Promover al Primer Equipo"
                    elif puntaje >= 70: return "Proyección a Futura Venta"
                    elif puntaje >= 50: return "Mantener en Desarrollo"
                    else: return "Alerta de Rendimiento"
                    
                df_masivo['Decision_Directiva'] = df_masivo['Puntaje_Consolidacion'].apply(clasificar_lote)
                
                # 2. Inserción masiva segura en SQLite
                conexion = sqlite3.connect("scouting_formativas.db")
                df_masivo.to_sql("proyecciones_scouting", conexion, if_exists='append', index=False)
                conexion.close()
                
                st.cache_data.clear()
                st.success(f"✅ ¡Éxito! Se han procesado y guardado {len(df_masivo)} jugadores en el sistema.")
                st.balloons() # Pequeño detalle de UX para celebrar la carga masiva
                
        except Exception as e:
            st.error("❌ Error procesando el archivo. Revisa que el CSV tenga las columnas correctas (Ej: Edad_Cronologica, Edad_Biologica, xG, etc).")
st.dataframe(df_filtrado, use_container_width=True)
