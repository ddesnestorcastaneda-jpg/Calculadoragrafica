import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

# Configuración de la página
st.set_page_config(page_title="Calculadora de Programación Lineal", layout="wide")

st.title("📊 Calculadora de Programación Lineal - EcoRider S.A.")
st.markdown("Utiliza esta herramienta para analizar las restricciones, la región factible y los vértices óptimos.")

# --- INICIALIZACIÓN DEL ESTADO (SESSION STATE) ---
if "restricciones" not in st.session_state:
    st.session_state.restricciones = [
        {'nombre': '1. Contrato Mínimo', 'a1': 1.0, 'a2': 0.0, 'signo': '>=', 'b': 15.0, 'color': 'red'},
        {'nombre': '2. Motores', 'a1': 0.0, 'a2': 1.0, 'signo': '<=', 'b': 40.0, 'color': 'green'},
        {'nombre': '3. Pintura Operativa', 'a1': 1.0, 'a2': 2.0, 'signo': '<=', 'b': 120.0, 'color': 'blue'},
        {'nombre': '4. Pintura Ampliada', 'a1': 1.0, 'a2': 2.0, 'signo': '<=', 'b': 180.0, 'color': 'orange'},
        {'nombre': '5. Capacidad Almacén', 'a1': 1.0, 'a2': 1.0, 'signo': '<=', 'b': 300.0, 'color': 'purple'},
        {'nombre': '6. Inspección Calidad', 'a1': 0.0, 'a2': 0.0, 'signo': '<=', 'b': 500.0, 'color': 'brown'},
        {'nombre': '7. Proporción', 'a1': -0.5, 'a2': 1.0, 'signo': '>=', 'b': 0.0, 'color': 'magenta'}
    ]

colores_disponibles = ['red', 'green', 'blue', 'orange', 'purple', 'brown', 'magenta', 'cyan', 'gray']

# --- BARRA LATERAL (SIDEBAR) PARA CONTROLES ---
st.sidebar.header("1. Función Objetivo (FO)")
c1 = st.sidebar.number_input("Coeficiente C1 (X1):", value=100.0, step=10.0)
c2 = st.sidebar.number_input("Coeficiente C2 (X2):", value=200.0, step=10.0)
graficar_fo = st.sidebar.checkbox("Graficar Línea de F.O.", value=False)
z_val = st.sidebar.number_input("Valor de Z para F.O.:", value=12000.0, step=500.0) if graficar_fo else 0

st.sidebar.header("2. Controles de Zoom")
lim_x = st.sidebar.slider("Zoom Eje X:", min_value=20, max_value=500, value=200, step=10)
lim_y = st.sidebar.slider("Zoom Eje Y:", min_value=20, max_value=500, value=150, step=10)

st.sidebar.header("3. Gestionar Restricciones")

# --- SECCIÓN PARA EDITAR / ELIMINAR RESTRICCIONES ---
if st.session_state.restricciones:
    opciones = [f"{i+1}. {r['nombre']}" for i, r in enumerate(st.session_state.restricciones)]
    seleccion = st.sidebar.selectbox("Seleccionar para Modificar / Eliminar:", opciones)
    idx_sel = opciones.index(seleccion)
    r_sel = st.session_state.restricciones[idx_sel]

    # Formulario desplegable para editar la restricción seleccionada
    with st.sidebar.expander("✏️ Editar Restricción Seleccionada", expanded=False):
        edit_nombre = st.text_input("Nombre:", value=r_sel['nombre'], key=f"nom_{idx_sel}")
        col_e1, col_e2 = st.columns(2)
        edit_a1 = col_e1.number_input("Coef. X1:", value=r_sel['a1'], key=f"a1_{idx_sel}")
        edit_a2 = col_e2.number_input("Coef. X2:", value=r_sel['a2'], key=f"a2_{idx_sel}")
        
        col_es, col_eb = st.columns(2)
        idx_signo = ["<=", ">=", "="].index(r_sel['signo'])
        edit_signo = col_es.selectbox("Signo:", ["<=", ">=", "="], index=idx_signo, key=f"sig_{idx_sel}")
        edit_b = col_eb.number_input("Límite (b):", value=r_sel['b'], key=f"b_{idx_sel}")
        
        if st.button("💾 Guardar Cambios"):
            st.session_state.restricciones[idx_sel] = {
                'nombre': edit_nombre,
                'a1': edit_a1,
                'a2': edit_a2,
                'signo': edit_signo,
                'b': edit_b,
                'color': r_sel['color']
            }
            st.rerun()

    col_del_one, col_del_all = st.sidebar.columns(2)
    
    if col_del_one.button("🗑️ Eliminar esta"):
        st.session_state.restricciones.pop(idx_sel)
        st.rerun()

    if col_del_all.button("⚠️ Borrar Todo"):
        st.session_state.restricciones = []
        st.rerun()
else:
    st.sidebar.info("No hay restricciones activas.")

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Agregar Nueva Restricción")
with st.sidebar.form("form_restriccion"):
    nombre_r = st.text_input("Nombre:", value=f"Restricción {len(st.session_state.restricciones)+1}")
    col_a1, col_a2 = st.columns(2)
    a1_r = col_a1.number_input("Coef. X1:", value=1.0)
    a2_r = col_a2.number_input("Coef. X2:", value=1.0)
    
    col_s, col_b = st.columns(2)
    signo_r = col_s.selectbox("Signo:", ["<=", ">=", "="])
    b_r = col_b.number_input("Límite (b):", value=50.0)
    
    btn_agregar = st.form_submit_button("➕ Agregar Restricción")
    if btn_agregar:
        color_nuevo = colores_disponibles[len(st.session_state.restricciones) % len(colores_disponibles)]
        st.session_state.restricciones.append({
            'nombre': nombre_r, 'a1': a1_r, 'a2': a2_r, 'signo': signo_r, 'b': b_r, 'color': color_nuevo
        })
        st.rerun()

# --- ÁREA PRINCIPAL: GRÁFICO Y TABLA ---
col_grafico, col_tabla = st.columns([1.3, 1])

with col_grafico:
    st.subheader("Plano Operativo")
    fig, ax = plt.subplots(figsize=(8, 6))
    x1_range = np.linspace(0, lim_x * 1.5, 500)

    # 1. Sombrear Región Factible
    if st.session_state.restricciones:
        grid_x1, grid_x2 = np.meshgrid(np.linspace(0, lim_x, 400), np.linspace(0, lim_y, 400))
        factible = (grid_x1 >= 0) & (grid_x2 >= 0)
        
        for r in st.session_state.restricciones:
            a1, a2, s, b = r['a1'], r['a2'], r['signo'], r['b']
            lhs = a1 * grid_x1 + a2 * grid_x2
            if s == '<=':
                factible &= (lhs <= b + 1e-5)
            elif s == '>=':
                factible &= (lhs >= b - 1e-5)
            elif s == '=':
                factible &= np.isclose(lhs, b, atol=1e-1)
        
        ax.imshow(factible.astype(int), extent=(0, lim_x, 0, lim_y), origin='lower', 
                  cmap='Greens', alpha=0.3, aspect='auto')

    # 2. Dibujar Restricciones
    for r in st.session_state.restricciones:
        c, a1, a2, s, b = r['color'], r['a1'], r['a2'], r['signo'], r['b']
        
        if a1 == 0 and a2 == 0:
            continue  # Restricción Basura (0X1 + 0X2 <= b): no genera línea
        elif a2 == 0 and a1 != 0:
            val_x = b / a1
            ax.axvline(val_x, color=c, linewidth=2, linestyle='--', label=f"{r['nombre']}")
        elif a1 == 0 and a2 != 0:
            val_y = b / a2
            ax.axhline(val_y, color=c, linewidth=2, linestyle='--', label=f"{r['nombre']}")
        elif a2 != 0:
            y_vals = (b - a1 * x1_range) / a2
            ax.plot(x1_range, y_vals, color=c, linewidth=2, linestyle='--', label=f"{r['nombre']}")

    # 3. Calcular Intersecciones
    puntos_interseccion = []
    for r1, r2 in combinations(st.session_state.restricciones, 2):
        A = np.array([[r1['a1'], r1['a2']], [r2['a1'], r2['a2']]])
        B = np.array([r1['b'], r2['b']])
        try:
            punto = np.linalg.solve(A, B)
            x1_p, x2_p = punto[0], punto[1]
            if 0 <= x1_p <= lim_x and 0 <= x2_p <= lim_y:
                ax.plot(x1_p, x2_p, 'ko', markersize=6)
                ax.annotate(f"({x1_p:.1f}, {x2_p:.1f})", (x1_p, x2_p), 
                            textcoords="offset points", xytext=(5, 5), fontsize=8, fontweight='bold')
                
                z_p = (c1 * x1_p) + (c2 * x2_p)
                puntos_interseccion.append({
                    'r1': r1['nombre'], 'r2': r2['nombre'],
                    'x1': x1_p, 'x2': x2_p, 'z': z_p
                })
        except np.linalg.LinAlgError:
            pass

    # 4. Graficar FO
    if graficar_fo and c2 != 0:
        y_fo = (z_val - c1 * x1_range) / c2
        ax.plot(x1_range, y_fo, color='black', linewidth=3, linestyle='-', label=f'F.O. Z = {z_val:.0f}')

    ax.set_xlim(0, lim_x)
    ax.set_ylim(0, lim_y)
    ax.set_xlabel('Bicicletas Estándar (X1)', fontweight='bold')
    ax.set_ylabel('Bicicletas Eléctricas (X2)', fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', fontsize=8)
    st.pyplot(fig)

with col_tabla:
    st.subheader("Tabla Resumen de Vértices")
    if puntos_interseccion:
        tabla_datos = []
        for idx, p in enumerate(puntos_interseccion, start=1):
            tabla_datos.append({
                "Vértice": f"Vértice {idx}",
                "Intersección": f"{p['r1']} ∩ {p['r2']}",
                "X1 (Estándar)": round(p['x1'], 2),
                "X2 (Eléctrica)": round(p['x2'], 2),
                "Valor Z ($)": f"${p['z']:,.2f}"
            })
        st.dataframe(tabla_datos, use_container_width=True)
    else:
        st.info("Agregue al menos 2 restricciones válidas para calcular los vértices de intersección.")
