import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="TERMINAL VALUATION V4", layout="wide", page_icon="💠")

# ==============================================================================
# 🛠️ ZONE DE SAISIE MANUELLE (TON "EXCEL" DANS LE CODE)
# ==============================================================================
MANUAL_DATA = {
    "AMZN": {
        # Flux & Bénéfices (en dollars complets, pas en millions)
        "fcf": 7695000000, "ocf": 139000000000, "net_income": 77670000000, "capex": 13200000000,
        "shares": 10400000000, "manual_pe_trail": 32.3, "manual_pe_fwd": 27.83, "debt": 200000000000,      
        "roe": 18.9, "roic": 10.7, "roce": 13.3, "market_cap": 134000000000, 
    },

     "NVO": {
        "fcf": 56184000000, "ocf": 11900000000, "net_income": 16134000000,
        "capex": 6300000000, "manual_pe_trail": 12.83, "manual_pe_fwd": 11,
        "debt": 2056000000, "roe": 52.8, "roic": 29.6, "roce": 39.1,
    },

    "CSU.TO": {
       "fcf": 2501000000, "ocf": 2573000000, "net_income": 687000000,
        "capex": 71000000, "manual_pe_trail": 15, "manual_pe_fwd": 15,
        "debt": 5440000000, "roe": 26.2, "roic": 4.9, "roce": 7.1,
    },

     "NBIS": {
        "fcf": -1528000000, "ocf": -155000000, "net_income": 218000000, "capex": -1373000000,
        "manual_pe_trail": 100, "manual_pe_fwd": 80,
        "debt": 4570000000, "roe": -19.7, "roic": -13.3, "roce": -13.4,
        },

    "CRM": {"fcf": 12895000000, "ocf": 13502000000, "net_income": 7222000000, "capex": 607000000,
        "manual_pe_trail": 14.5, "manual_pe_fwd": 14, "debt": 11140000000, 
        "roic": 7.9, "roe": 10.15, "roce": 9.6,
        },

    "FICO": {"fcf": 735000000, "ocf": 759000000, "net_income": 657790000, "capex": 24000000,
        "manual_pe_trail": 50, "manual_pe_fwd": 50,"debt": 3230000000, 
        "roic": 53, "roe": -37.3, "roce": 90.8,
        },

    "NOW": {"fcf": 4576000000, "ocf": 5444000000, "net_income": 1748000000, "capex": 868000000,
        "shares": 4500000000, "manual_pe_trail": 23, "manual_pe_fwd": 20,
        "debt": 5000000000, "cash": 8000000000, "roe": 13.5, "roic": 9.0, "roce": 11.7,
        },
}


# --- CSS FUTURISTE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

    /* --- GLOBAL THEME --- */
    .stApp {
        background: radial-gradient(circle at top left, #1a1e2e, #0a0e17 60%);
        font-family: 'Rajdhani', sans-serif;
    }
    h1, h2, h3, h4, p, div,  { font-family: 'Rajdhani', sans-serif !important; letter-spacing: 0.05em; }
    h1 { text-transform: uppercase; letter-spacing: 0.1em; background: linear-gradient(90deg, #00f2ff, #00c853); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    h3 { text-transform: uppercase; color: #00f2ff; font-weight: 700; font-size: 1.1rem; margin-bottom: 15px; border-bottom: 1px solid rgba(0, 242, 255, 0.2); padding-bottom: 5px; }

    /* --- GLASSMORPHISM CARDS --- */
    /* --- MODIFICATION 1 : CARTES DASHBOARD (TAB 1) --- */
    .cyber-card {
        background: rgba(20, 25, 40, 0.7);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 255, 0.1);
        padding: 15px;
        transition: all 0.3s ease-in-out;
        min-height: auto;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    /* Titres H3 plus petits et sur une ligne */
    .cyber-card h3 { 
        text-transform: uppercase; 
        color: #00f2ff; 
        font-weight: 700; 
        font-size: 0.85rem !important; /* Réduit pour tenir sur une ligne */
        white-space: nowrap;          /* Empêche le retour à la ligne */
        overflow: hidden;             /* Sécurité si ça dépasse */
        text-overflow: ellipsis; 
        margin-bottom: 10px; 
        border-bottom: 1px solid rgba(0, 242, 255, 0.2); 
        padding-bottom: 5px; 
    }

    /* --- MODIFICATION 2 : PRIX ACTION (EN HAUT À DROITE) --- */
    .price-card-up {
        background: linear-gradient(135deg, rgba(0, 200, 83, 0.2), rgba(0, 10, 20, 0.8)); 
        border: 1px solid #00C853; /* Bordure complète au lieu de juste à droite */
        border-radius: 12px; 
        padding: 15px; 
        text-align: center !important; /* Centré */
        box-shadow: 0 0 15px rgba(0, 200, 83, 0.2);
    }
    .price-card-down {
        background: linear-gradient(135deg, rgba(255, 23, 68, 0.2), rgba(0, 10, 20, 0.8)); 
        border: 1px solid #FF1744; 
        border-radius: 12px; 
        padding: 15px; 
        text-align: center !important; /* Centré */
        box-shadow: 0 0 15px rgba(255, 23, 68, 0.2);
    }
    .price-big { 
        font-size: 42px !important; /* Beaucoup plus gros */
        font-weight: 800; 
        color: #fff; 
        margin: 0; 
        line-height: 1.1;
        text-shadow: 0 0 15px rgba(255,255,255,0.4); 
    }
    .price-var { 
        font-size: 20px !important; /* Pourcentage plus gros */
        font-weight: 600; 
        margin-top: 5px; 
    }

</style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def format_usd(value):
    if value is None or pd.isna(value) or value == 0: return "-"
    if abs(value) >= 1e9: return f"${value / 1e9:.2f} B"
    elif abs(value) >= 1e6: return f"${value / 1e6:.2f} M"
    return f"${value:.2f}"

def format_pct(value):
    if value is None or pd.isna(value) or value == 0: return "-"
    return f"{value:.2f}%"

# Fonction pour afficher une métrique avec le nouveau style
def styled_metric(label, value, delta=None, delta_color="normal"):
    st.markdown(f"""<div class="metric-container"><p class="metric-lbl">{label}</p></div>""", unsafe_allow_html=True)
    st.metric("", value, delta=delta, delta_color=delta_color)

def analyze_quality(info, manual_data):
    score = 0
    details = []
    pe = manual_data.get('manual_pe_trail') or info.get('trailingPE')
    fwd_pe = manual_data.get('manual_pe_fwd') or info.get('forwardPE')
    roe = manual_data.get('roe') or (info.get('returnOnEquity', 0) * 100)
    
    used_pe = fwd_pe if fwd_pe and fwd_pe > 0 else (pe if pe and pe > 0 else 0)
    if used_pe > 0:
        if used_pe < 25: score += 6; details.append("✅ Valo : Bon marché (PE < 25)")
        elif used_pe < 45: score += 4; details.append("✅ Valo : Raisonnable (PE < 45)")
        elif used_pe < 60: score += 2; details.append("⚠️ Valo : Élevé")
        else: details.append("❌ Valo : Très cher (PE > 60)")
    else: details.append("⚠️ Valo : Pas de PE significatif")

    if roe > 20: score += 4; details.append(f"✅ Rentabilité : ROE Excellent ({roe:.1f}%)")
    elif roe > 12: score += 2; details.append(f"✅ Rentabilité : ROE Correct ({roe:.1f}%)")
    else: details.append(f"❌ Rentabilité : ROE Faible ({roe:.1f}%)")
    
    margins = info.get('profitMargins', 0)
    if margins > 0.15: score += 4; details.append(f"✅ Marges : Élevées ({margins:.1%})")
    
    rev_growth = info.get('revenueGrowth', 0)
    if rev_growth > 0.10: score += 3; details.append(f"✅ Croissance : Dynamique ({rev_growth:.1%})")

    if manual_data.get('roic', 0) > 15: score += 2; details.append("✅ Bonus : ROIC élevé (Donnée Expert)")
    return min(score, 20), details

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(" 💠 UNITÉ DE SÉLECTION")
    favorites_list = list(MANUAL_DATA.keys()) if MANUAL_DATA else ["MSFT"]
    ticker_input = st.selectbox("Base de données active", favorites_list, index=0 if favorites_list else 0)
    st.caption("Recherche manuelle de cible :")
    ticker_search = st.text_input("Entrer Symbole", "").upper()
    if ticker_search: ticker_input = ticker_search

# --- MAIN ---
if ticker_input:
    try:
        ticker_yf = yf.Ticker(ticker_input)
        info_yf = ticker_yf.info
        hist = ticker_yf.history(period="5y")
        my_data = MANUAL_DATA.get(ticker_input, {})

        # --- PREP DONNÉES ---
        curr_price = info_yf.get('currentPrice', 0)
        final_fcf = my_data.get("fcf")
        if final_fcf is None:
             cf = ticker_yf.cashflow
             if cf is not None and not cf.empty and 'Free Cash Flow' in cf.index:
                 final_fcf = cf.loc['Free Cash Flow'].iloc[0]
             else: final_fcf = 0
             
        final_ocf = my_data.get("ocf") or info_yf.get('operatingCashflow', 0)
        final_ni = my_data.get("net_income") or info_yf.get('netIncomeToCommon', 0)
        final_shares = my_data.get("shares") or info_yf.get('sharesOutstanding', 1)
        final_debt = my_data.get("debt") or info_yf.get('totalDebt', 0)
        final_cash = my_data.get("cash") or info_yf.get('totalCash', 0)
        final_net_debt = final_debt - final_cash
        final_roe = my_data.get("roe") or (info_yf.get('returnOnEquity', 0) * 100)
        final_roic = my_data.get("roic", 0)
        final_roce = my_data.get("roce", 0)

        # --- EN-TÊTE ---
        score, reasons = analyze_quality(info_yf, my_data)
        color_score = "#00E676" if score >= 15 else ("#FFAB00" if score >= 10 else "#FF5252")

        col_header, col_score_box, col_price_box = st.columns([0.55, 0.20, 0.25], gap="small")
        with col_header:
            st.title(info_yf.get('longName', ticker_input))
            st.markdown(f"<span style='color:#00f2ff;'>SECTEUR:</span> {info_yf.get('sector', 'N/A')} | <span style='color:#00f2ff;'>DEVISE:</span> {info_yf.get('currency', 'USD')}", unsafe_allow_html=True)
        
        with col_score_box:
            st.markdown(f"""
            <div class="score-box">
                <p style="margin: 0; color: #00f2ff; font-size: 0.8rem; font-weight: 700; letter-spacing: 2px;">QUALITY SCORE</p>
                <p style="margin: 5px 0; font-size: 2.2rem; font-weight: 900; line-height: 1; color: {color_score}; text-shadow: 0 0 10px {color_score};">{score}/20</p>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("ANALYSE DIAGNOSTIC", expanded=False):
                for r in reasons: st.caption(r)

        with col_price_box:
            prev_close = info_yf.get('previousClose', curr_price)
            change_pct = ((curr_price - prev_close) / prev_close) * 100 if prev_close else 0
            css = "price-card-up" if change_pct >= 0 else "price-card-down"
            color = "text-green" if change_pct >= 0 else "text-red"
            sign = "+" if change_pct >= 0 else ""
            st.markdown(f"""
            <div class="{css}">
                <p class="price-big">${curr_price:.2f}</p>
                <p class="price-var {color}">{sign}{change_pct:.2f}%</p>
            </div>""", unsafe_allow_html=True)

        # --- TABS ---
        st.write("") # Spacer
        tab_overview, tab_chart, tab_sim, tab_comp = st.tabs(["📊 DONNÉES FONDAMENTALES", "📈 GRAPHIQUE TERMINAL", "🔮 SIMULATEUR QUANTIQUE", "⚔️ MATRICE DE COMPARAISON"])

        # === TAB 1 : VUE D'ENSEMBLE ===
        with tab_overview:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown('<div class="cyber-card"><h3>💰 FLUX & BÉNÉFICES</h3>', unsafe_allow_html=True)
                styled_metric("Free Cash Flow", format_usd(final_fcf))
                styled_metric("Operating Cash Flow", format_usd(final_ocf))
                styled_metric("Net Income", format_usd(final_ni))
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="cyber-card"><h3>⚖️ VALO & ACTIONS</h3>', unsafe_allow_html=True)
                styled_metric("Prix Actuel", f"${curr_price:.2f}")
                styled_metric("Market Cap", format_usd(curr_price * final_shares))
                calc_pe = (curr_price * final_shares) / final_ni if final_ni else 0
                styled_metric("P/E (Calculé)", f"{calc_pe:.2f}x")
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="cyber-card"><h3>🏦 STRUCTURE BILAN</h3>', unsafe_allow_html=True)
                styled_metric("Cash Disponible", format_usd(final_cash))
                styled_metric("Dette Totale", format_usd(final_debt))
                styled_metric("Dette Nette", format_usd(final_net_debt), delta_color="inverse")
                st.markdown('</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="cyber-card" style="height: 100%;"><h3>🚀 RENTABILITÉ</h3>', unsafe_allow_html=True)
                styled_metric("ROE", format_pct(final_roe))
                styled_metric("ROIC (Expert)", format_pct(final_roic))
                styled_metric("ROCE (Expert)", format_pct(final_roce))
                st.markdown('</div>', unsafe_allow_html=True)

        # === TAB 2 : GRAPHIQUE ===
        with tab_chart:
            if not hist.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', line=dict(color='#00f2ff', width=2), fill='tozeroy', fillcolor='rgba(0, 242, 255, 0.1)'))
                fig.update_layout(
                    title=dict(text=f"COURS ACTION: {ticker_input}", font=dict(color="#00f2ff", family="Rajdhani", size=20)),
                    template="plotly_dark", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.2)',
                    xaxis=dict(showgrid=False, gridcolor='rgba(0,242,255,0.1)'), yaxis=dict(showgrid=True, gridcolor='rgba(0,242,255,0.1)')
                )
                st.plotly_chart(fig, use_container_width=True)

        # === TAB 3 : SIMULATEUR QUANTIQUE ===
        with tab_sim:
            st.markdown("### ☢️ MODÈLE DE PROJECTION DE RENDEMENT (CAGR)")
            col_sim_inputs, col_sim_viz = st.columns([1, 2], gap="medium")

            with col_sim_inputs:
                st.markdown('<div class="sim-control-panel">', unsafe_allow_html=True)
                st.markdown("<h4>1. PARAMÈTRES DU MODÈLE</h4>", unsafe_allow_html=True)
                metric_choice = st.radio("Métrique de base :", ["Free Cash Flow", "Net Income (EPS)"], horizontal=True)
                years_choice = st.radio("Horizon Temporel :", [1, 3, 5], horizontal=True, format_func=lambda x: f"{x} ANS")
                
                start_val_total = final_fcf if metric_choice == "Free Cash Flow" else final_ni
                if start_val_total <= 0: start_val_total = 1
                start_per_share = start_val_total / final_shares
                current_multiple = curr_price / start_per_share if start_per_share else 0

                st.markdown("<hr style='border-color: rgba(0,242,255,0.2);'>", unsafe_allow_html=True)
                st.markdown("<h4>2. VECTEURS DE CROISSANCE</h4>", unsafe_allow_html=True)
                sim_growth = st.number_input(f"Croissance Annuelle {metric_choice} (%)", value=12.0, step=0.5, format="%.1f")
                sim_shares_chg = st.number_input("Variation Actions/An (%) (Neg = Rachat)", value=-1.5, step=0.1, format="%.1f")
                
                st.markdown("<hr style='border-color: rgba(0,242,255,0.2);'>", unsafe_allow_html=True)
                st.markdown("<h4>3. TERMINAL VALUE</h4>", unsafe_allow_html=True)
                st.caption(f"Multiple actuel détecté : {current_multiple:.1f}x")
                sim_exit_multiple = st.number_input("Multiple de Sortie Cible", value=float(round(current_multiple, 1)), step=0.5, format="%.1f")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- CALCULS SIM ---
            future_per_share = start_per_share
            years_arr = list(range(datetime.now().year, datetime.now().year + years_choice + 1))
            for i in range(years_choice):
                growth_factor = (1 + sim_growth / 100)
                share_factor = 1 / (1 + sim_shares_chg / 100)
                future_per_share = future_per_share * growth_factor * share_factor
            
            target_price = future_per_share * sim_exit_multiple
            if curr_price > 0:
                cagr = (target_price / curr_price) ** (1 / years_choice) - 1
                upside = (target_price - curr_price) / curr_price
            else: cagr = 0; upside = 0

            chart_data = pd.DataFrame({"Année": years_arr, "Prix": np.linspace(curr_price, target_price, len(years_arr))})

            with col_sim_viz:
                # VISUALISATION
                fig_sim = go.Figure()
                fig_sim.add_trace(go.Scatter(x=chart_data["Année"], y=chart_data["Prix"], mode='lines+markers', name='Trajectoire',
                    line=dict(color='#00f2ff', width=3, dash='dashdot'), marker=dict(size=10, color='#00f2ff', line=dict(width=2, color='white'))))
                
                fig_sim.add_trace(go.Scatter(x=[years_arr[0]], y=[curr_price], mode='markers', name='Départ', marker=dict(color='white', size=12)))
                fig_sim.add_trace(go.Scatter(x=[years_arr[-1]], y=[target_price], mode='markers+text', name='Cible',
                    text=[f"${target_price:.2f}"], textposition="top left", textfont=dict(color="#00E676", size=16, family="Rajdhani"), marker=dict(color='#00E676', size=18, symbol="diamond")))

                fig_sim.update_layout(title=dict(text="TRAJECTOIRE DU PRIX CIBLE", font=dict(family="Rajdhani", color="#00f2ff")),
                    template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,242,255,0.05)',
                    xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(0,242,255,0.1)'))
                st.plotly_chart(fig_sim, use_container_width=True)

                # RÉSULTATS (CODE MODIFIÉ POUR AFFICHAGE COMPLET)
                r1, r2, r3, r4 = st.columns(4)
                
                # J'ai réduit la font-size de 1.8rem à 1.4rem pour que les gros chiffres rentrent
                with r1:
                    st.markdown(f"""
                    <div class="sim-result-card">
                        <p class="metric-lbl">PRIX ACTUEL</p>
                        <p style="font-size:1.4rem; font-weight:700; margin:0; color:#fff;">${curr_price:.2f}</p>
                    </div>""", unsafe_allow_html=True)
                
                with r2:
                    color_target = "#00E676" if target_price > curr_price else "#FF5252"
                    st.markdown(f"""
                    <div class="sim-result-card" style="border: 1px solid {color_target}; box-shadow: 0 0 10px {color_target};">
                        <p class="metric-lbl">PRIX FUTUR (T+{years_choice})</p>
                        <p style="font-size:1.4rem; font-weight:700; margin:0; color:{color_target};">${target_price:.2f}</p>
                        <small style="color:{color_target}">{upside*100:+.2f}%</small>
                    </div>""", unsafe_allow_html=True)
                
                with r3:
                     st.markdown(f"""
                    <div class="sim-result-card">
                        <p class="metric-lbl">CAGR ATTENDU</p>
                        <p style="font-size:1.4rem; font-weight:700; margin:0; color:#00f2ff; text-shadow: 0 0 10px #00f2ff;">{cagr*100:.2f}%</p>
                        <small style="color:#aaa;">Rendement annuel</small>
                    </div>""", unsafe_allow_html=True)
                
                with r4:
                    st.markdown(f"""
                    <div class="sim-result-card">
                        <p class="metric-lbl">{metric_choice[:3].upper()}/ACTION FINAL</p>
                        <p style="font-size:1.4rem; font-weight:700; margin:0; color:#fff;">${future_per_share:.2f}</p>
                    </div>""", unsafe_allow_html=True)

        # === TAB 4 : COMPARAISON ===
        with tab_comp:
             st.markdown("### 🛰️ SCANNER COMPARATIF")
             peers = st.text_input("Entrer concurrents (séparés par virgule)", "MSFT, GOOGL, META").upper().split(',')
             if st.button("LANCER LE SCAN"):
                 comp_data = []
                 for p in peers:
                     p = p.strip()
                     try:
                         i = yf.Ticker(p).info
                         comp_data.append({"Ticker": p, "Prix ($)": i.get('currentPrice'), "P/E Fwd": i.get('forwardPE'), "ROE (%)": i.get('returnOnEquity',0)*100, "Marge Nette (%)": i.get('profitMargins',0)*100})
                     except: pass
                 st.dataframe(pd.DataFrame(comp_data).set_index("Ticker"), use_container_width=True)

    except Exception as e: st.error(f"SYSTEM ERROR: {e}")