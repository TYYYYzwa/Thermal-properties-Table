import subprocess
import sys

def install_coolprop():
    try:
        import coolprop
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "coolprop"])

import streamlit as st
import math

# from CoolProp.CoolProp import FluidsList
import GetProperties
import CoolProp.CoolProp as CP

# 獲取所有流體清單（以逗號分隔的字串）
fluids_string = CP.get_global_param_string("FluidsList")

# 將字串轉換為列表 (List) 方便閱讀
fluids_list = fluids_string.split(',')
fluid_db = FluidsList + ['PG25(DOW)']+['PG55(DOW)']


# ==============================
# Core function (原始計算邏輯)
# ==============================
def straightpipe_pd_approximation(T_in,Tsat,fluid_name,P):
    P_sat = 0
    VLIQ = 0
    VVAP = 0
    DENLIQ = 0
    DENVAP = 0
    TCXLIQ = 0
    CPLIQ = 0
    CPVAP = 0
    TCXVAP = 0
    H_LV = 0
    T_in = T_in + 273.15  # K
    Tsat = Tsat + 273.15  # K
    T_min = 0
    T_max = 0
    # ===== Fluid Properties =====
    try:
        print('T_in:', T_in)
        print('Tsat:', Tsat)
        if T_in < Tsat or T_in > Tsat:
            if fluid_name == 'PG25(DOW)':
                VLIQ = 1.44657e-6*T_in**2 - 0.000178*T_in + 0.0060857  # Pa·s
                DENLIQ = -0.002862487*T_in**2 - 0.290577*T_in + 1036.8704    # kg/m3
                CPLIQ = -0.013209494*T_in**2 + 3.1413829*T_in + 4010.774     # J/kg-K
                TCXLIQ = -5.92621e-6*T_in**2 + 0.0013567*T_in + 0.4315547      # W/m-K
                T_min = 273.15 -5  # K
                T_max = 373.15 +80  # K

            elif fluid_name == 'PG55(DOW)':
                VLIQ = 1.41818E-06* T_in**2 - 0.000234788*T_in + 0.011193939
                DENLIQ =-0.003484848 * T_in**2	-0.400090909*T_in+	1064.175758
                CPLIQ =4.8684E-17* T_in**2+	5.03030303*T_in+	3175.757576
                TCXLIQ =-4.09091E-06 * T_in**2 + 0.000795303*T_in +	0.306439394
                T_min = 273.15 +35  # K
                T_max = 373.15 +80  # K
            if fluid_name in FluidsList:
                ff = GetProperties.Fluid_NotSat(fluid_name,P, T_in)
                Tsat = ff.T_sat()
                VLIQ = ff.V()
                DENLIQ = ff.DEN()
                CPLIQ = ff.CP()
                TCXLIQ = ff.TCX()
        elif T_in == Tsat:
            ff = GetProperties.Fluid_Sat(fluid_name, Tsat)
            T_min = ff.T_min()
            T_max = ff.T_max()
            P_sat = ff.P_sat()
            VLIQ = ff.VLIQ()
            DENLIQ = ff.DENLIQ()
            CPLIQ = ff.CPLIQ()
            TCXLIQ = ff.TCXLIQ()
            VVAP = ff.VVAP()
            DENVAP = ff.DENVAP()
            CPVAP = ff.CPVAP()
            TCXVAP = ff.TCXVAP()
            H_LV = ff.H_LV()
    except:
        pass
    print('T_in:', T_in)
    return {
        'T_min': T_min,
        'T_max': T_max,
        'T_sat': Tsat,
        'P_sat': P_sat,
        'VLIQ': VLIQ,
        'VVAP': VVAP,
        'DENLIQ': DENLIQ,
        'DENVAP': DENVAP,
        'TCXLIQ': TCXLIQ,
        'CPLIQ': CPLIQ,
        'CPVAP': CPVAP,
        'TCXVAP': TCXVAP,
        'H_LV': H_LV
    }
    
#test

# test_result = straightpipe_pd_approximation(6.0, 200.0, 2.0, 313.0,'PG25')
# print(test_result)

# ==============================
# Streamlit UI
# ==============================
st.set_page_config(page_title="Straight Pipe Pressure Drop Tool", layout="centered")

st.title("Fluid Thermal Property Tool")
st.caption("Fluid Thermal Property table(ICTBG DNIBU YY)")

st.divider()

# -------- Input Section --------



fluid_name = st.sidebar.radio(
    "Select Working Fluid",
    options=fluid_db,
    disabled=False,
    
)


Tsat = st.number_input(
    "Fluid Saturation Temperature (C)",
    min_value=20.0,
    max_value=115.0,
    step=1.0,
    value=40.0,
    format="%.1f",
    key="Tsat"
)

T_in = st.number_input(
    "Fluid Inlet Temperature (C)",
    min_value=20.0,
    max_value=100.0,
    step=1.0,
    value=40.0,
    format="%.1f",
    key="T_in"
)
P = st.number_input(
    "Operating Pressure (Pa)",
    min_value=101325.0,
    max_value=5000000.0,
    step=10.0,
    value=101325.0,
    format="%.1f",
    key="P"
)
st.divider()


# -------- Calculation --------
if st.button("Check Thermal property", type="primary"):
    # print(pipe_dia, pipe_L, flow_rate, Tsat, T_in)
    result = straightpipe_pd_approximation(
        T_in, Tsat, fluid_name,P
    )

    st.subheader("Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Min. Temperature(C)", f"{result['T_min']-273.15 :.1f}")
        st.metric("Max. Temperature(C)", f"{result['T_max']-273.15 :.1f}")
        st.metric("Saturation Temperature(C)", f"{result['T_sat']-273.15 :.1f}")
        st.metric("Saturation Pressure(Pa)", f"{result['P_sat']:.1f}")
        st.metric("Saturation Pressure(Psi)", f"{result['P_sat']*0.000145:.1f}")
        # st.metric("Velocity [m/s]", f"{result['Velocity_mps']:.3f}")

    with col2:

        st.metric("Liquid Viscosity(Pa-s)", f"{result['VLIQ']:.10f}")
        st.metric("Liquid Density(kg/m3)", f"{result['DENLIQ']:.1f}")
        st.metric("Liquid Thermal Conductivity(W/m-K)", f"{result['TCXLIQ']:.5f}")
        st.metric("Liquid Specific Heat(J/kg-K)", f"{result['CPLIQ']:.1f}")

    with col3:
        st.metric("Vapor Viscosity(Pa-s)", f"{result['VVAP']:.10f}")
        st.metric("Vapor Density(kg/m3)", f"{result['DENVAP']:.2f}")
        st.metric("Vapor Thermal Conductivity(W/m-K)", f"{result['TCXVAP']:.5f}")
        st.metric("Vapor Specific Heat(J/kg-K)", f"{result['CPVAP']:.2f}")
        st.metric("Latent Heat of Vaporization(J/kg)", f"{result['H_LV']:.1f}") 
    # with st.expander("Additional Details"):
    #     st.write(f"Prandtl Number: {result['Prandtl_Number']:.3f}")








