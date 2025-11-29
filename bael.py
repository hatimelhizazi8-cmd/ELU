import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Calcul Armatures - By El Hizazi Hatim", layout="centered")

# --- HEADER ---
st.markdown("""
<h1 style="text-align:center; color:#4A4A4A;">🧱 Calcul des Armatures</h1>
<h4 style="text-align:center; color:gray;">In Concrete We Believe</h4>
<h5 style="text-align:center; color:gray;">Réalisé par El Hizazi Hatim</h5>
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

# Bouton calcul
if st.button("Calculer"):
    # --- conversions pour calculs internes (tout en mm et N·mm)
    b = b_cm * 10.0        # cm -> mm
    d = d_cm * 10.0
    dp = dp_cm * 10.0
    # Mu -> N·mm
    unit_factor_Nm = {"N·m": 1.0, "kN·m": 1e3, "MN·m": 1e6}[Mu_unit]
    Mu_Nmm = Mu * unit_factor_Nm * 1000.0  # N·m -> N·mm

    # sigma_bc (MPa = N/mm^2)
    sigma_bc = 0.85 * fc28 / 1.5

    # mu (sans unité)
    mu = Mu_Nmm / (b * d**2 * sigma_bc)

    st.write(f"σ_bc = {sigma_bc:.4f} MPa")
    st.write(f"μ = {mu:.6f}")

    # pivot A / B
    mu_ab = 0.186
    if mu < mu_ab:
        pivot = "A"
    else:
        pivot = "B"

    # Affichage du pivot avec style
    pivot_color = "#CCE5FF" if pivot == "A" else "#FFDACC"
    with st.container():
        st.markdown(f"<div style='background-color:{pivot_color};padding:10px;border-radius:5px;text-align:center;font-weight:bold;'>Pivot {pivot}</div>", unsafe_allow_html=True)

    sigma_st = fe / 1.15  # MPa = N/mm^2

    # Créer deux colonnes pour afficher les résultats
    col1, col2 = st.columns(2)

    # PIVOT A
    if pivot == "A":
        mu1 = 0.104
        if mu < mu1:
            st.error("Mauvaise utilisation béton : redimensionner la section.")
        else:
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            Z = d * (1 - 0.4 * alpha)  # mm
            Ast_mm2 = Mu_Nmm / (Z * sigma_st)  # mm^2
            Ast_cm2 = Ast_mm2 / 100.0  # mm^2 -> cm^2

            # Section traction
            with col1:
                st.markdown("<div style='background-color:#D1E7DD;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Ast acier en traction (Armatures simples)")
                st.write(f"α = {alpha:.4f}")
                st.write(f"Z = {Z:.2f} mm ({Z/10:.2f} cm)")
                st.success(f"Ast = {Ast_cm2:.2f} cm²")
                st.markdown("</div>", unsafe_allow_html=True)

            # Section compression (vide mais uniforme)
            with col2:
                st.markdown("<div style='background-color:#F8D7DA;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Asc acier en compression")
                st.info("N/A pour Pivot A")
                st.markdown("</div>", unsafe_allow_html=True)

    # PIVOT B
    if pivot == "B":
        mu_r = 0.391 if fe == 400 else 0.371
        alpha_r = 0.669 if fe == 400 else 0.617
        eps_els = 1.74e-3 if fe == 400 else 2.17e-3

        if mu < mu_r:
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            Z = d * (1 - 0.4 * alpha)
            Ast_mm2 = Mu_Nmm / (Z * sigma_st)

            # Section traction
            with col1:
                st.markdown("<div style='background-color:#D1E7DD;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Ast acier en traction (Armatures simples)")
                st.success(f"Ast = {Ast_mm2/100:.2f} cm²")
                st.markdown("</div>", unsafe_allow_html=True)

            # Section compression (vide mais uniforme)
            with col2:
                st.markdown("<div style='background-color:#F8D7DA;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Asc acier en compression")
                st.info("N/A (armatures simples)")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # armatures doubles
            MR = b * d**2 * sigma_bc * mu_r      # N·mm
            Mr = Mu_Nmm - MR                     # N·mm
            Zr = d * (1 - 0.4 * alpha_r)         # mm

            eps_sc = ((d - dp) / d) * (eps_els + 3.5e-3) - eps_els
            if eps_sc >= eps_els:
                sigma_sc = fe / 1.15
            else:
                E = 2_718_200.0  # MPa
                sigma_sc = E * eps_sc

            Ast_mm2 = (MR / Zr + Mr / (d - dp)) / sigma_st
            Asc_mm2 = (Mr / (d - dp)) / sigma_sc

            # conversion mm^2 -> cm^2
            Ast_cm2 = Ast_mm2 / 100.0
            Asc_cm2 = Asc_mm2 / 100.0

            # Section traction
            with col1:
                st.markdown("<div style='background-color:#D1E7DD;padding:10px;border-radius:5px'>", unsafe_allow_html=True)
                st.markdown("### Ast acier en traction (Armatures doubles)")
                st.success(f"Ast = {Ast_cm2:.2f} cm²")
                st.markdown("</div>", unsafe_allow_html=True)

            # Section compression
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

st.write("---")
st.markdown("<p style='text-align:center;color:gray;'>In Concrete We Believe ✨</p>", unsafe_allow_html=True)
