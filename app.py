import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Producción Industrial",
    layout="wide"
)

st.title("🏭 Dashboard de Producción Industrial")
st.write("Análisis basado en el dataset de ventas adaptado a indicadores de manufactura.")

@st.cache_data
def cargar_datos():
    # Carga del archivo específico proporcionado
    df = pd.read_csv("ventas_comerciales.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])
    
    # --- Adaptación de variables para el ejercicio industrial ---
    # Renombramos y creamos datos simulados para cumplir con los indicadores pedidos
    df = df.rename(columns={
        'unidades': 'unidades_producidas',
        'region': 'linea',
        'canal': 'turno'
    })
    
    # Simulamos unidades defectuosas (un pequeño porcentaje aleatorio de la producción)
    df["unidades_defectuosas"] = (df["unidades_producidas"] * 0.03).round().astype(int)
    
    # Simulamos tiempo de operación en minutos (ej: entre 400 y 500 min)
    df["tiempo_operacion_min"] = 480 
    
    # --- Construcción de indicadores (10.3) ---
    df["tasa_defectos"] = df["unidades_defectuosas"] / df["unidades_producidas"]
    df["productividad_min"] = df["unidades_producidas"] / df["tiempo_operacion_min"]
    
    return df

datos = cargar_datos()

# --- Sidebar: Filtros (10.4.2) ---
st.sidebar.header("Filtros de Planta")

lineas = ["Todas"] + sorted(datos["linea"].unique().tolist())
turnos = ["Todos"] + sorted(datos["turno"].unique().tolist())

linea_sel = st.sidebar.selectbox("Línea de Producción (Región)", lineas)
turno_sel = st.sidebar.selectbox("Turno Operativo (Canal)", turnos)

# Aplicar filtros
datos_filtrados = datos.copy()
if linea_sel != "Todas":
    datos_filtrados = datos_filtrados[datos_filtrados["linea"] == linea_sel]
if turno_sel != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["turno"] == turno_sel]

# --- Cálculos para Métricas (10.4.3) ---
prod_total = datos_filtrados["unidades_producidas"].sum()
defectos_totales = datos_filtrados["unidades_defectuosas"].sum()
tasa_promedio = defectos_totales / prod_total if prod_total > 0 else 0
tiempo_promedio = datos_filtrados["tiempo_operacion_min"].mean()
prod_por_min = prod_total / datos_filtrados["tiempo_operacion_min"].sum() if prod_total > 0 else 0

# Mostrar indicadores
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Producción Total", f"{prod_total:,.0f} und")
with col2:
    st.metric("Tasa de Defectos", f"{tasa_promedio:.2%}")
with col3:
    st.metric("Tiempo Prom. Operación", f"{tiempo_promedio:.0f} min")
with col4:
    st.metric("Productividad/Min", f"{prod_por_min:.2f} und")

# --- Visualizaciones ---
tab1, tab2, tab3 = st.tabs(["Línea de Tiempo", "Análisis de Calidad", "Tabla de Datos"])

with tab1:
    # 10.4.4 Visualización temporal
    st.subheader("Evolución Temporal de la Producción")
    df_temporal = datos_filtrados.groupby("fecha")["unidades_producidas"].sum().reset_index()
    fig_linea = px.line(
        df_temporal, 
        x="fecha", 
        y="unidades_producidas",
        title="Unidades Producidas por Día",
        line_shape="linear"
    )
    st.plotly_chart(fig_linea, use_container_width=True)

with tab2:
    # 10.4.5 Comparación de tasa de defectos
    st.subheader("Tasa de Defectos por Línea")
    defectos_por_linea = datos_filtrados.groupby("linea")["tasa_defectos"].mean().reset_index()
    
    fig_bar = px.bar(
        defectos_por_linea,
        x="linea",
        y="tasa_defectos",
        title="Tasa de Defectos Promedio por Línea",
        labels={'tasa_defectos': 'Tasa de Defectos (%)'},
        color="tasa_defectos",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    # 10.4.6 Tabla de datos filtrados
    st.subheader("Registros de Producción Filtrados")
    st.dataframe(datos_filtrados, use_container_width=True)