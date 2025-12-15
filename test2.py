import streamlit as st
import math

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Calcul BAEL - El Hizazi Hatim", layout="wide")

# ================= SIDEBAR =================
st.sidebar.title("🧱 Type d’élément")
section_type = st.sidebar.radio(
    "",
    [
        "Section carrée – flexion simple",
        "Section Té – flexion simple",
        "Poutre",
        "Poteau",
    ],
)
st.sidebar.markdown("---")
st.sidebar.markdown("**In Concrete We Believe**")

# ================= HEADER =================
st.markdown(
    """
    <h1 style='text-align:center;'>🧱 Calcul des Armatures BAEL</h1>
    <h4 style='text-align:center;color:gray;'>In Concrete We Believe</h4>
    <h5 style='text-align:center;color:gray;'>Made with ❤️ by El Hizazi Hatim</h5>
    <hr>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# ===== MODULE : SECTION CARRÉE – FLEXION SIMPLE ===========
# =========================================================
if section_type == "Section carrée – flexion simple":

    st.info("Module actif : Section carrée – flexion simple")

    # ================= INPUTS =================
    colG, colE = st.columns(2)

    with colG:
        st.subheader("📐 Données géométriques")
        b_cm = st.number_input("b (cm)", value=30.0)
        h_cm = st.number_input("h (cm)", value=50.0)
        d_cm = st.number_input("d (cm)", value=45.0)
        dp_cm = st.number_input("d' (cm)", value=4.0)
        fc28 = st.number_input("fc28 (MPa)", value=25.0)
        fe = st.selectbox("Acier (FeE)", [400, 500])

    with colE:
        st.subheader("⚖️ Efforts")
        Mu = st.number_input("Mu (valeur)", value=150.0)
        Mu_unit = st.selectbox("Unité Mu", ["kN·m", "MN·m", "N·m"])
        Ms = st.number_input("Ms (valeur)", value=0.0)
        Ms_unit = st.selectbox("Unité Ms", ["kN·m", "MN·m", "N·m"])
        crack_type = st.selectbox("Type de fissuration", ["FPP", "FP", "FTP"])

    # ================= ELU =================
    if st.button("Calculer ELU"):

        b = b_cm * 10.0
        d = d_cm * 10.0
        dp = dp_cm * 10.0

        Mu_Nmm = Mu * {"N·m":1, "kN·m":1e3, "MN·m":1e6}[Mu_unit] * 1000
        sigma_bc = 0.85 * fc28 / 1.5
        mu = Mu_Nmm / (b * d**2 * sigma_bc)

        st.write(f"σ_bc = {sigma_bc:.4f} MPa")
        st.write(f"μ = {mu:.6f}")

        pivot = "A" if mu < 0.186 else "B"
        color = "#CCE5FF" if pivot == "A" else "#FFDACC"
        st.markdown(
            f"<div style='background:{color};padding:10px;border-radius:5px;text-align:center;font-weight:bold;'>Pivot {pivot}</div>",
            unsafe_allow_html=True,
        )

        sigma_st = fe / 1.15
        col1, col2 = st.columns(2)

        if pivot == "A":
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            Z = d * (1 - 0.4 * alpha)
            Ast_cm2 = (Mu_Nmm / (Z * sigma_st)) / 100

            with col1:
                st.success(f"Ast = {Ast_cm2:.2f} cm²")
            with col2:
                st.info("Asc = N/A")

            st.session_state["Ast_cm2"] = Ast_cm2
            st.session_state["Asc_cm2"] = 0.0

        else:
            mu_r = 0.391 if fe == 400 else 0.371
            alpha_r = 0.669 if fe == 400 else 0.617
            eps_els = 1.74e-3 if fe == 400 else 2.17e-3

            if mu < mu_r:
                Z = d * (1 - 0.4 * (1.25 * (1 - math.sqrt(1 - 2 * mu))))
                Ast_cm2 = (Mu_Nmm / (Z * sigma_st)) / 100

                with col1:
                    st.success(f"Ast = {Ast_cm2:.2f} cm²")
                with col2:
                    st.info("Asc = N/A")

                st.session_state["Ast_cm2"] = Ast_cm2
                st.session_state["Asc_cm2"] = 0.0

            else:
                MR = b * d**2 * sigma_bc * mu_r
                Mr = Mu_Nmm - MR
                Zr = d * (1 - 0.4 * alpha_r)

                eps_sc = ((d - dp)/d)*(eps_els + 3.5e-3) - eps_els
                sigma_sc = fe/1.15 if eps_sc >= eps_els else 2_718_200 * eps_sc

                Ast_cm2 = ((MR/Zr + Mr/(d-dp))/sigma_st)/100
                Asc_cm2 = ((Mr/(d-dp))/sigma_sc)/100

                with col1:
                    st.success(f"Ast = {Ast_cm2:.2f} cm²")
                with col2:
                    st.success(f"Asc = {Asc_cm2:.2f} cm²")

                st.session_state["Ast_cm2"] = Ast_cm2
                st.session_state["Asc_cm2"] = Asc_cm2

    # ================= ELS =================
    if "Ast_cm2" in st.session_state and st.button("Vérifier les contraintes ELS"):

        Ast = st.session_state["Ast_cm2"]
        Asc = st.session_state["Asc_cm2"]

        A = b_cm
        B = 30*(Ast+Asc)
        C = -30*(Ast*d_cm + Asc*dp_cm)

        y1 = (-B + math.sqrt(B**2 - 4*A*C))/(2*A)

        Igg = (A*y1**3)/3 + 15*Asc*(y1-dp_cm)**2 + 15*Ast*(d_cm-y1)**2

        Ms_Ncm = Ms * {"N·m":1, "kN·m":1e3, "MN·m":1e6}[Ms_unit] * 100
        K = Ms_Ncm / Igg

        sigma_b = (K*y1)/100
        sigma_s = (15*K*(d_cm-y1))/100

        ft28 = 0.6 + 0.06*fc28
        sigma_s_adm = (
            fe/1.15 if crack_type=="FPP"
            else min(fe*2/3,110*math.sqrt(1.6*ft28))
            if crack_type=="FP"
            else min(fe/2,90*math.sqrt(1.6*ft28))
        )

        st.write(f"y1 = {y1:.2f} cm")
        st.write(f"Igg' = {Igg:.2f} cm⁴")
        st.write(f"K = {K:.3e} N/cm³  ({K*1e3:.3f} MN/m³)")
        st.write(f"σ_b = {sigma_b:.2f} MPa  → {'OK' if sigma_b<=0.6*fc28 else 'NO'}")
        st.write(f"σ_s = {sigma_s:.2f} MPa  → {'OK' if sigma_s<=sigma_s_adm else 'NO'}")

else:
    st.warning("Module en cours de développement")

st.markdown("<hr><p style='text-align:center;color:gray;'>In Concrete We Believe ✨</p>", unsafe_allow_html=True)
