import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Calcul Armatures - By El Hizazi Hatim", layout="centered")

# --- HEADER ---
st.markdown("""
<h1 style="text-align:center; color:#4A4A4A;">🧱 Calcul des Armatures</h1>
<h4 style="text-align:center; color:gray;">In Concrete We Believe</h4>
<h5 style="text-align:center; color:gray;">Made with ❤️ by EL HIZAZI Hatim</h5>
<hr>
""", unsafe_allow_html=True)

# Inputs
b_cm = st.number_input("b (cm)", value=30.0)
h_cm = st.number_input("h (cm)", value=50.0)
d_cm = st.number_input("d utile (cm)", value=45.0)
dp_cm = st.number_input("d' (cm)", value=4.0)
fc28 = st.number_input("fc28 (MPa)", value=25.0)
fe = st.selectbox("Acier (FeE)", [400, 500])

Mu = st.number_input("Mu (valeur)", value=150.0)
Mu_unit = st.selectbox("Unité Mu", ["kN·m", "MN·m", "N·m"])  # default kN·m

Ms = st.number_input("Ms (valeur)", value=0.0)
Ms_unit = st.selectbox("Unité Ms", ["kN·m", "MN·m", "N·m"], key="Ms_unit")
crack_type = st.selectbox("Type fissuration", ["FPP", "FP", "FTP"], index=0)

# --- BOUTON CALCUL ELU ---
if st.button("Calculer ELU"):
    # --- conversions ---
    b = b_cm * 10.0
    d = d_cm * 10.0
    dp = dp_cm * 10.0
    unit_factor_Nm = {"N·m": 1.0, "kN·m": 1e3, "MN·m": 1e6}[Mu_unit]
    Mu_Nmm = Mu * unit_factor_Nm * 1000.0

    sigma_bc = 0.85 * fc28 / 1.5
    mu = Mu_Nmm / (b * d**2 * sigma_bc)

    st.write(f"σ_bc = {sigma_bc:.4f} MPa")
    st.write(f"μ = {mu:.6f}")

    mu_ab = 0.186
    pivot = "A" if mu < mu_ab else "B"
    pivot_color = "#CCE5FF" if pivot == "A" else "#FFDACC"
    with st.container():
        st.markdown(f"<div style='background-color:{pivot_color};padding:10px;border-radius:5px;text-align:center;font-weight:bold;'>Pivot {pivot}</div>", unsafe_allow_html=True)

    sigma_st = fe / 1.15

    col1, col2 = st.columns(2)

    if pivot == "A":
        mu1 = 0.104
        if mu < mu1:
            st.error("Mauvaise utilisation béton : redimensionner la section.")
        else:
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            Z = d * (1 - 0.4 * alpha)
            Ast_mm2 = Mu_Nmm / (Z * sigma_st)
            Ast_cm2 = Ast_mm2 / 100.0

            with col1:
                st.markdown("<div style='background-color:#D1E7DD;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Ast acier en traction (Armatures simples)")
                st.write(f"α = {alpha:.4f}")
                st.write(f"Z = {Z:.2f} mm ({Z/10:.2f} cm)")
                st.success(f"Ast = {Ast_cm2:.2f} cm²")
                st.markdown("</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='background-color:#F8D7DA;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Asc acier en compression")
                st.info("N/A pour Pivot A")
                st.markdown("</div>", unsafe_allow_html=True)

            # stocker pour ELS
            st.session_state['Ast_cm2'] = Ast_cm2
            st.session_state['Asc_cm2'] = 0.0

    else:  # pivot B
        mu_r = 0.391 if fe == 400 else 0.371
        alpha_r = 0.669 if fe == 400 else 0.617
        eps_els = 1.74e-3 if fe == 400 else 2.17e-3

        if mu < mu_r:
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            Z = d * (1 - 0.4 * alpha)
            Ast_mm2 = Mu_Nmm / (Z * sigma_st)

            with col1:
                st.markdown("<div style='background-color:#D1E7DD;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Ast acier en traction (Armatures simples)")
                st.success(f"Ast = {Ast_mm2/100:.2f} cm²")
                st.markdown("</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='background-color:#F8D7DA;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Asc acier en compression")
                st.info("N/A (armatures simples)")
                st.markdown("</div>", unsafe_allow_html=True)

            st.session_state['Ast_cm2'] = Ast_mm2/100
            st.session_state['Asc_cm2'] = 0.0
        else:
            MR = b * d**2 * sigma_bc * mu_r
            Mr = Mu_Nmm - MR
            Zr = d * (1 - 0.4 * alpha_r)

            eps_sc = ((d - dp) / d) * (eps_els + 3.5e-3) - eps_els
            if eps_sc >= eps_els:
                sigma_sc = fe / 1.15
            else:
                E = 2_718_200.0
                sigma_sc = E * eps_sc

            Ast_mm2 = (MR / Zr + Mr / (d - dp)) / sigma_st
            Asc_mm2 = (Mr / (d - dp)) / sigma_sc

            Ast_cm2 = Ast_mm2 / 100.0
            Asc_cm2 = Asc_mm2 / 100.0

            with col1:
                st.markdown("<div style='background-color:#D1E7DD;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Ast acier en traction (Armatures doubles)")
                st.success(f"Ast = {Ast_cm2:.2f} cm²")
                st.markdown("</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='background-color:#F8D7DA;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Asc acier en compression (Armatures doubles)")
                st.write(f"MR = {MR:.2f} N·mm")
                st.write(f"Mr = {Mr:.2f} N·mm")
                st.write(f"Zr = {Zr:.2f} mm ({Zr/10:.2f} cm)")
                st.write(f"ε_sc = {eps_sc:.6f}")
                st.write(f"σ_sc = {sigma_sc:.2f} MPa")
                st.info(f"Asc = {Asc_cm2:.2f} cm²")
                st.markdown("</div>", unsafe_allow_html=True)

            st.session_state['Ast_cm2'] = Ast_cm2
            st.session_state['Asc_cm2'] = Asc_cm2

# --- BOUTON CALCUL ELS ---
if 'Ast_cm2' in st.session_state and 'Asc_cm2' in st.session_state:
    if st.button("Calculer ELS"):
        Ast = st.session_state['Ast_cm2']
        Asc = st.session_state['Asc_cm2']

        A_b = b_cm
        d = d_cm
        dp = dp_cm

        A = A_b
        B = 30.0 * (Asc + Ast)
        C = -30.0 * (Asc * dp + Ast * d)

        disc = B**2 - 4*A*C
        if disc < 0:
            st.error("Discriminant < 0 : pas de solution réelle pour y1")
        else:
            y1_pos = (-B + math.sqrt(disc)) / (2*A)
            y1_neg = (-B - math.sqrt(disc)) / (2*A)
            y1 = next((v for v in (y1_pos, y1_neg) if 0 < v < d), max(y1_pos, y1_neg))

            Igg = (A_b * y1**3) / 3.0 + 15.0 * Asc * (y1 - dp)**2 + 15.0 * Ast * (d - y1)**2

            factor = {"N·m":1.0, "kN·m":1e3, "MN·m":1e6}[Ms_unit]
            Ms_Ncm = Ms * factor * 100.0

            K = Ms_Ncm / Igg

            sigma_b_Npcm2 = K * y1
            sigma_s_Npcm2 = 15.0 * K * (d - y1)

            sigma_b_MPa = sigma_b_Npcm2 / 100.0
            sigma_s_MPa = sigma_s_Npcm2 / 100.0

            sigma_b_adm = 0.6 * fc28
            ft28 = 0.6 + 0.06 * fc28

            if crack_type == "FPP":
                sigma_s_adm = fe / 1.15
            elif crack_type == "FP":
                sigma_s_adm = min(fe * 2.0/3.0, 110.0 * math.sqrt(1.6 * ft28))
            else:
                sigma_s_adm = min(fe * 0.5, 90.0 * math.sqrt(1.6 * ft28))

            st.write(f"y1 = {y1:.3f} cm")
            st.write(f"Igg' = {Igg:.3f} cm⁴")
            st.write(f"K = {K:.6e} N/cm³")
            st.write(f"σ_b = {sigma_b_MPa:.3f} MPa  (adm = {sigma_b_adm:.3f} MPa) → {'OK' if sigma_b_MPa <= sigma_b_adm else 'NO'}")
            st.write(f"σ_s = {sigma_s_MPa:.3f} MPa  (adm = {sigma_s_adm:.3f} MPa) → {'OK' if sigma_s_MPa <= sigma_s_adm else 'NO'}")

st.write("---")
st.markdown("<p style='text-align:center;color:gray;'>In Concrete We Believe ✨</p>", unsafe_allow_html=True)
