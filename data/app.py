# -*- coding: utf-8 -*-
"""
DataCo Supply Chain - Decision Support System
Management Consulting Aesthetic - Gradio
Built by Anshul Silhare
"""

import gradio as gr
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import plotly.express as px

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

# ===============================================================
# 1. MODEL LOADING
# ===============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_VERSION = "v3.0"
try:
    with open(os.path.join(BASE_DIR, "dataco_rf_model_version.txt"), "r") as f:
        MODEL_VERSION = f.read().strip()
except Exception:
    pass

try:
    model = joblib.load(os.path.join(BASE_DIR, "dataco_rf_model.joblib"))
    scaler = joblib.load(os.path.join(BASE_DIR, "dataco_scaler.joblib"))
    model_columns = joblib.load(os.path.join(BASE_DIR, "dataco_columns.joblib"))
    FEAT = list(model.feature_names_in_)
    SCOLS = list(scaler.feature_names_in_)
except Exception as e:
    print(f"Error loading models: {e}")
    model, scaler, model_columns = None, None, None
    FEAT, SCOLS = [], []

# ===============================================================
# 2. CONSTANTS & DICTIONARIES
# ===============================================================
COUNTRIES_MAPPING = {
    "United States": "Estados Unidos", "Germany": "Alemania", "France": "Francia",
    "United Kingdom": "Reino Unido", "Canada": "Canada", "Mexico": "Mexico",
    "Brazil": "Brasil", "India": "India", "China": "China", "Japan": "Japon",
    "Australia": "Australia", "Spain": "Espana", "Italy": "Italia",
    "Netherlands": "Paises Bajos", "Belgium": "Belgica"
}
COUNTRY_LIST = list(COUNTRIES_MAPPING.keys())

SHIPPING_MODES = ["Standard Class", "First Class", "Second Class", "Same Day"]
SEGMENTS = ['Corporate', 'Home Office', 'Consumer']
PAYMENTS = ['DEBIT', 'PAYMENT', 'TRANSFER', 'CASH']
CATEGORIES = [
    'Camping & Hiking', 'Cardio Equipment', 'Computers', 'Consumer Electronics',
    'Electronics', 'Fishing', 'Fitness Accessories', 'Indoor/Outdoor Games',
    "Men's Clothing", "Men's Footwear", "Women's Apparel", "Women's Clothing"
]
DAYS_LIST = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONTHS_LIST = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

REQUIRED_COLS = ["Order Country", "Sales"]
OPTIONAL_COLS = [
    "Days_Scheduled", "Order_Item_Quantity", "Order_Profit_Per_Order",
    "Payment Type", "Customer Segment", "Product Category",
    "Order Month", "Order Day of Week", "Customer Country"
]
COLUMN_ALIASES = {
    "Order ID": ["order_id", "order id", "id", "order"],
    "Order Country": ["country", "destination country", "order_country", "order country", "dest country"],
    "Sales": ["sales", "order value", "revenue", "total sales", "amount", "order_value"],
    "Days_Scheduled": ["days scheduled", "scheduled days", "sla", "transit days", "days_scheduled", "days"],
    "Order_Item_Quantity": ["qty", "quantity", "item quantity", "order quantity", "pieces", "units", "order_item_quantity"],
    "Order_Profit_Per_Order": ["profit", "margin", "order profit", "profit_per_order", "net profit"],
    "Payment Type": ["payment", "payment method", "type", "payment_type", "payment type"],
    "Customer Segment": ["segment", "customer_segment", "customer segment"],
    "Product Category": ["category", "category name", "category_name", "product_category", "product category"],
    "Order Month": ["month", "order_month", "order month"],
    "Order Day of Week": ["day", "order_day", "day_of_week", "day of week"],
    "Customer Country": ["customer country", "customer_country", "origin country"]
}
DEFAULT_VALS = {
    "Days_Scheduled": 3, "Order_Item_Quantity": 1, "Sales": 150.0,
    "Order_Profit_Per_Order": 20.0, "Payment Type": "DEBIT",
    "Customer Segment": "Consumer", "Product Category": "Computers",
    "Order Month": "January", "Order Day of Week": "Monday", "Customer Country": "Other"
}

# ===============================================================
# 3. DESIGN TOKENS (Executive Dark Theme)
# ===============================================================
T = dict(
    bg="#090D16",       # Deep near-black slate
    surface="#151F32",  # Sleek dark navy surface
    card="#151F32",     # Same surface background for cards
    border="#24324F",   # Muted dark blue-gray border
    accent="#3B82F6",   # Sleek corporate blue accent
    teal="#14B8A6",     # Crisp teal
    green="#10B981",    # Emerald green
    amber="#F59E0B",    # Vibrant amber
    red="#EF4444",      # Crimson red
    text="#F8FAFC",     # High-contrast white/light gray
    text2="#CBD5E1",    # Medium gray for secondary text
    text3="#94A3B8",    # Muted gray for captions/labels
    grid="#1C283F",     # Grid lines inside charts
    font="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
)

# ===============================================================
# 4. CSS
# ===============================================================
custom_css = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* -- page -------------------------------------------------- */
body, .gradio-container {{
  font-family: {T['font']} !important;
  background-color: {T['bg']} !important;
  color: {T['text']} !important;
}}
.gradio-container {{
  max-width: 98% !important;
  margin: 0 auto !important;
  padding: 0 1.5rem !important;
}}

/* Hide native browser number input spinners for a clean modern look */
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button {{ 
  -webkit-appearance: none !important; 
  margin: 0 !important; 
}}
input[type=number] {{
  -moz-appearance: textfield !important;
}}

/* -- header ------------------------------------------------ */
.nexus-header{{background:{T['surface']};border-bottom:1px solid {T['border']};
  padding:1rem 0;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);}}
.nexus-header-content{{max-width:98%;margin:0 auto;padding:0 1.5rem;
  display:flex;align-items:center;justify-content:space-between;}}
.nexus-logo{{font-size:1rem;font-weight:700;color:{T['text']};letter-spacing:-0.01em;}}
.nexus-logo span{{color:{T['accent']};font-weight:600;}}
.nexus-status{{display:flex;align-items:center;gap:.5rem;font-size:.7rem;
  font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:{T['text3']};}}
.status-dot{{width:8px;height:8px;border-radius:50%;background:{T['green']};}}

/* -- hero -------------------------------------------------- */
.nexus-hero{{padding:2.5rem 0 2rem;max-width:98%;margin:0 auto;}}
.nexus-badge{{display:inline-flex;align-items:center;gap:.4rem;
  font-size:.65rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:{T['accent']};
  background:rgba(59, 130, 246, 0.15);border:1px solid rgba(59, 130, 246, 0.3);
  padding:.3rem .8rem;border-radius:6px;margin-bottom:1.2rem;}}
.nexus-title{{font-size:clamp(1.8rem,4vw,2.5rem);font-weight:800;
  letter-spacing:-.02em;line-height:1.15;color:{T['text']};margin:0 0 .6rem;}}
.nexus-title .accent{{color:{T['accent']};}}
.nexus-sub{{font-size:1rem;color:{T['text2']};line-height:1.6;margin-bottom:1.8rem;max-width:800px;}}

.nexus-counters{{display:flex;flex-wrap:wrap;gap:2.5rem;padding-top:1.2rem;
  border-top:1px solid {T['border']};}}
.nc-val{{font-size:1.6rem;font-weight:700;color:{T['text']};line-height:1;}}
.nc-lbl{{font-size:.65rem;font-weight:600;color:{T['text3']};
  letter-spacing:.05em;text-transform:uppercase;margin-top:.3rem;}}

/* -- cards ------------------------------------------------- */
.nx-card{{background:{T['card']};border:1px solid {T['border']};border-radius:12px;
  padding:1.5rem;position:relative;margin-bottom:1rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);}}
.nx-card-title{{font-size:.75rem;font-weight:700;letter-spacing:.05em;
  text-transform:uppercase;color:{T['text']};margin-bottom:1rem;
  display:flex;align-items:center;gap:.5rem;border-bottom:1px solid {T['border']};padding-bottom:.6rem;}}

.nx-html-card,
.nx-html-card [class*="svelte-"],
.gradio-html,
.gradio-html [class*="svelte-"],
.verdict-col,
.verdict-col > .block {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  width: 100% !important;
  max-width: none !important;
}}

/* -- kpi bar ----------------------------------------------- */
.kb{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:16px;margin:0 0 16px;}}
.batch-kpi-row .kb{{grid-template-columns:repeat(5,1fr) !important;}}
.kc{{background:{T['card']};border:1px solid {T['border']};border-radius:12px;
  padding:1.2rem 1.4rem;position:relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition:transform .2s ease, box-shadow .2s ease;}}
.kc:hover{{transform:translateY(-2px);box-shadow:0 10px 15px -3px rgba(0,0,0,0.4),0 4px 6px -2px rgba(0,0,0,0.3);}}
.kl{{font-size:.65rem;font-weight:600;color:{T['text3']};letter-spacing:.05em;
  text-transform:uppercase;margin-bottom:.5rem;}}
.kv{{font-size:1.6rem;font-weight:700;color:{T['text']};line-height:1;}}
.ks{{font-size:.7rem;color:{T['text3']};margin-top:.3rem;}}

/* -- tabs -------------------------------------------------- */
.tabs > .tab-nav{{border-bottom:1px solid {T['border']} !important;background:transparent !important;
  margin-bottom: 1.5rem !important;}}
.tabs > .tab-nav > button{{font-family:{T['font']} !important;font-size:.85rem !important;font-weight:600 !important;
  color:{T['text3']} !important;background:transparent !important;
  border:none !important;border-bottom:2px solid transparent !important;
  padding:.8rem 1.4rem !important;border-radius: 6px 6px 0 0 !important;
  transition:all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;}}
.tabs > .tab-nav > button.selected{{color:#FFFFFF !important;border-bottom-color:{T['accent']} !important;
  background:rgba(59, 130, 246, 0.05) !important;}}
.tabs > .tab-nav > button:hover{{color:{T['text']} !important;background:rgba(255, 255, 255, 0.03) !important;}}

/* -- plot cards -------------------------------------------- */
.nx-plot-card .block,
.nx-plot-card .wrap,
.nx-plot-card .form,
.nx-plot-card .block-label,
.nx-plot-card label {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}}
.chart-title{{margin:0 0 1rem 0 !important;}}
.chart-title p{{font-weight:700 !important;font-size:.75rem !important;
  letter-spacing:.05em !important;text-transform:uppercase !important;color:{T['text']} !important;
  margin:0 !important;padding-bottom:.6rem !important;
  border-bottom:1px solid {T['border']} !important;}}

/* -- verdict card ------------------------------------------ */

/* -- tech tags --------------------------------------------- */
.tech-tag{{display:inline-block;font-size:.65rem;font-weight:500;
  color:{T['text2']};background:rgba(255, 255, 255, 0.05);border:1px solid {T['border']};
  padding:.2rem .6rem;border-radius:4px;margin:.15rem;}}

/* -- architecture ------------------------------------------ */
.arch-flow{{display:flex;align-items:center;justify-content:center;gap:1rem;
  padding:2rem 0;flex-wrap:wrap;}}
.arch-node{{background:{T['surface']};border:1px solid {T['border']};
  border-radius:10px;padding:1.2rem;text-align:center;min-width:140px;
  box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.2);}}
.arch-lbl{{font-size:.6rem;font-weight:700;letter-spacing:.05em;
  text-transform:uppercase;color:{T['text3']};margin-bottom:.4rem;}}
.arch-val{{font-size:1.2rem;font-weight:700;color:{T['text']};line-height:1;}}
.arch-sub{{font-size:.65rem;color:{T['text2']};margin-top:.4rem;line-height:1.4;}}
.arch-arrow{{font-size:1.2rem;color:{T['text3']};font-weight:400;padding:0 .2rem;}}

/* -- data dictionary --------------------------------------- */
.dd-table{{width:100%;border-collapse:collapse;font-size:.8rem;}}
.dd-table th{{text-align:left;font-size:.65rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  color:{T['text2']};padding:.8rem 1rem;border-bottom:2px solid {T['grid']};background:rgba(0, 0, 0, 0.2);}}
.dd-table td{{padding:.8rem 1rem;color:{T['text2']};border-bottom:1px solid {T['grid']};
  line-height:1.5;vertical-align:top;}}

/* -- interactive animations -------------------------------- */
.gradio-container button {{
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
.gradio-container button:hover {{
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
}}
.gradio-container h3 {{
  font-size: 1.15rem !important;
  font-weight: 700 !important;
  color: #FFFFFF !important;
  margin-top: 0 !important;
  margin-bottom: 1.2rem !important;
  letter-spacing: -0.01em !important;
}}

.footer-link-card {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: {T['text2']} !important;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid {T['border']};
  padding: 0.4rem 0.9rem;
  border-radius: 8px;
  text-decoration: none !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}}
.footer-link-card:hover {{
  color: #FFFFFF !important;
  background: rgba(59, 130, 246, 0.12) !important;
  border-color: {T['accent']} !important;
  transform: translateY(-1.5px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}}
.footer-link-card svg {{
  width: 14px;
  height: 14px;
  fill: currentColor;
  transition: fill 0.2s ease;
}}

/* -- bulk tab spacing overrides --------------------------- */
#bulk-tab {{
  gap: 10px !important;
}}
#bulk-tab .nx-card {{
  padding: 1.1rem 1.3rem !important;
  margin-bottom: 0.6rem !important;
}}
#bulk-tab .gradio-row, #bulk-tab .gr-row, #bulk-tab .row {{
  gap: 10px !important;
}}
#bulk-tab .gradio-column, #bulk-tab .gr-column, #bulk-tab .column {{
  gap: 10px !important;
}}
#bulk-tab .form {{
  gap: 8px !important;
}}
#bulk-tab .block {{
  padding: 6px !important;
  margin-bottom: 6px !important;
}}
#bulk-tab .form > .block {{
  margin-bottom: 4px !important;
}}
#bulk-tab .file-preview {{
  margin-top: 0 !important;
  padding: 4px !important;
}}
#bulk-tab .file-preview-holder {{
  padding: 4px !important;
}}
#bulk-tab input[type=file] {{
  padding: 6px 10px !important;
}}
/* compact KPI cards in bulk */
.batch-kpi-row .kb {{
  display: grid !important;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 6px !important;
  margin: 0 !important;
}}
.batch-kpi-row .kb > *:last-child {{
  grid-column: span 4 !important;
}}
.batch-kpi-row .kc {{
  padding: 0.5rem 0.6rem !important;
  border-radius: 8px !important;
}}
.batch-kpi-row .kv {{
  font-size: 1.1rem !important;
}}
.batch-kpi-row .kl {{
  font-size: 0.52rem !important;
  margin-bottom: 0.1rem !important;
}}
.batch-kpi-row .ks {{
  font-size: 0.55rem !important;
  margin-top: 0.1rem !important;
}}
/* minimize padding above and below processed batch message */
#batch-msg-container {{
  margin-top: -14px !important;
  margin-bottom: -28px !important;
  padding: 0 !important;
}}
#batch-msg-container > div, #batch-msg-container > p {{
  margin: 0 !important;
  padding: 0 !important;
}}
#batch-dataframe {{
  margin-top: -18px !important;
}}
#batch-dataframe > div {{
  margin-top: 0 !important;
}}
"""

# ===============================================================
# 5. HTML TEMPLATES (Corporate Light Theme)
# ===============================================================
HEADER_HTML = f"""
<div class="nexus-header">
  <div class="nexus-header-content">
    <div class="nexus-logo">DataCo<span>DSS</span></div>
    <div class="nexus-status">
      <div class="status-dot"></div><span>System Online</span>
    </div>
  </div>
</div>
"""

HERO_HTML = f"""
<div class="nexus-hero">
  <div class="nexus-badge">Portfolio Showcase / Proof of Concept</div>
  <div class="nexus-title">Supply Chain <span class="accent">Risk Intelligence</span></div>
  <div class="nexus-sub">
    A late delivery risk prediction and prescriptive mitigation engine. Trained on the benchmark <strong>DataCo Smart Supply Chain Dataset</strong>, this demonstration portal uses Random Forest to evaluate fulfillment operations, SLA penalty exposure, and shipping intervention ROI.
  </div>
  <div class="nexus-counters">
    <div><div class="nc-val">180,519</div><div class="nc-lbl">Training Records</div></div>
    <div><div class="nc-val">71.9%</div><div class="nc-lbl">Validation AUC</div></div>
    <div><div class="nc-val">66.6%</div><div class="nc-lbl">Test Accuracy</div></div>
    <div><div class="nc-val">66.3%</div><div class="nc-lbl">F1-Score</div></div>
  </div>
</div>
"""

def get_verdict_html(pred, prob, df_out):
    if pred == 1:
        v_col, v_text, v_sub = T["red"], "HIGH RISK", "Predicted to violate SLA delivery windows"
        alert_bg = "rgba(239, 68, 68, 0.12)"
    else:
        v_col, v_text, v_sub = T["green"], "ON TRACK", "Predicted to meet SLA schedule"
        alert_bg = "rgba(16, 185, 129, 0.12)"

    prob_pct = int(prob * 100)
    dash_offset = 440 - (440 * prob)

    html = f"""
    <div class="nx-card" style="display:flex;align-items:center;gap:1.5rem;background:{alert_bg};border-color:{v_col};">
      <div style="position:relative;width:90px;height:90px;flex-shrink:0;">
        <svg viewBox="0 0 160 160" style="width:100%;height:100%;transform:rotate(-90deg);">
          <circle cx="80" cy="80" r="70" fill="none" stroke="{T['grid']}" stroke-width="12" />
          <circle cx="80" cy="80" r="70" fill="none" stroke="{v_col}" stroke-width="12"
            stroke-dasharray="440" stroke-dashoffset="{dash_offset}" stroke-linecap="round"
            style="transition:stroke-dashoffset 1s ease-out;" />
        </svg>
        <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
          font-size:1.4rem;font-weight:700;color:{v_col};">{prob_pct}%</div>
      </div>
      <div>
        <div style="font-size:.75rem;font-weight:700;color:{v_col};letter-spacing:.05em;margin-bottom:.2rem;">
          {v_text}
        </div>
        <div style="font-size:1.1rem;font-weight:700;color:{T['text']};line-height:1.2;margin-bottom:.4rem;">
          Risk Probability: {prob_pct}%
        </div>
        <div style="font-size:.8rem;color:{T['text2']};line-height:1.4;">
          {v_sub}
        </div>
      </div>
    </div>
    """

    df_html = f"""
    <div class="nx-card">
      <div class="nx-card-title">Scenario Financial Analysis</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
        <div style="background:{T['bg']};padding:.8rem;border-radius:6px;border:1px solid {T['border']};">
          <div style="font-size:.65rem;font-weight:600;color:{T['text3']};margin-bottom:.2rem;text-transform:uppercase;">Expected Profit (No Intervention)</div>
          <div style="font-size:1.2rem;font-weight:700;color:{T['red'] if df_out['Expected_Profit'].iloc[0] < 0 else T['green']};">
            ${df_out['Expected_Profit'].iloc[0]:,.2f}
          </div>
        </div>
        <div style="background:{T['bg']};padding:.8rem;border-radius:6px;border:1px solid {T['border']};">
          <div style="font-size:.65rem;font-weight:600;color:{T['text3']};margin-bottom:.2rem;text-transform:uppercase;">Expected Profit (With Intervention)</div>
          <div style="font-size:1.2rem;font-weight:700;color:{T['red'] if df_out['Expected_Profit_with_Intervention'].iloc[0] < 0 else T['green']};">
            ${df_out['Expected_Profit_with_Intervention'].iloc[0]:,.2f}
          </div>
        </div>
      </div>
    </div>
    """
    return html, df_html

BULK_FMT_HTML = f"""
<div style="display:flex;gap:.5rem;margin-bottom:1rem;flex-wrap:wrap;">
  <span style="font-size:.7rem;font-weight:600;color:{T['text3']};padding:.3rem 0;">Supported Formats:</span>
  <span class="tech-tag">CSV (.csv)</span>
  <span class="tech-tag">Excel (.xlsx)</span>
</div>
"""

SYSINFO_HTML = f"""
<div class="kb">
  <div class="kc"><div class="kl">Core Algorithm</div><div class="kv" style="font-size:1.1rem;">Random Forest Classifier</div></div>
  <div class="kc"><div class="kl">Ensemble Size</div><div class="kv">100</div><div class="ks">Decision Trees</div></div>
  <div class="kc"><div class="kl">Max Depth</div><div class="kv">20</div><div class="ks">Nodes</div></div>
  <div class="kc"><div class="kl">Data Scaling</div><div class="kv" style="font-size:1.1rem;">StandardScaler</div></div>
</div>
"""

RF_ARCH_HTML = f"""
<div class="arch-flow">
  <div class="arch-node" style="border-color:{T['accent']};background:rgba(59, 130, 246, 0.15);">
    <div class="arch-lbl">Input Layer</div>
    <div class="arch-val">4 Drivers</div>
    <div class="arch-sub">Selected Features</div>
  </div>
  <div class="arch-arrow">-></div>
  <div class="arch-node" style="border-color:{T['accent']};background:rgba(59, 130, 246, 0.15);">
    <div class="arch-lbl">Ensemble</div>
    <div class="arch-val">100 Trees</div>
    <div class="arch-sub">Parallel Processing</div>
  </div>
  <div class="arch-arrow">-></div>
  <div class="arch-node">
    <div class="arch-lbl">Aggregation</div>
    <div class="arch-val">Voting</div>
    <div class="arch-sub">Soft Probability</div>
  </div>
  <div class="arch-arrow">-></div>
  <div class="arch-node" style="border-color:{T['green']};background:rgba(16, 185, 129, 0.15);">
    <div class="arch-lbl">Output</div>
    <div class="arch-val">Risk %</div>
    <div class="arch-sub">Binary Classification</div>
  </div>
</div>
"""

CHALLENGES_HTML = f"""
<div class="nx-card" style="height:100%;">
  <div class="nx-card-title">Model Governance & Limitations</div>
  <ul style="font-size:.85rem;color:{T['text2']};line-height:1.85;margin:0;padding-left:1.2rem;">
    <li style="margin-bottom:2.2rem;"><strong>Feature Reduction:</strong> The model relies exclusively on 4 core predictive drivers. If other factors (like destination country customs strikes) occur, the model cannot capture them directly.</li>
    <li style="margin-bottom:2.2rem;"><strong>SLA Fluidity:</strong> Hardcoded SLA threshold assumptions must be regularly reviewed against carrier contractual updates to maintain accuracy.</li>
    <li style="margin-bottom:2.2rem;"><strong>Feature Drift:</strong> Seasonal volume spikes (e.g., Q4 holidays) can cause data distributions to drift, requiring periodic model retraining.</li>
    <li><strong>Categorical Sparsity:</strong> Dropping secondary categorical dimensions like product category reduces model overfitting but limits sub-segment drift detection.</li>
  </ul>
</div>
"""

RECRUITER_BRIEF_HTML = f"""
<div class="nx-card-title" style="color: {T['accent']}; border-bottom-color: rgba(59, 130, 246, 0.2); margin-bottom: 0.8rem;">
  Operations Analytics &amp; Decision Support Brief
</div>
<div style="font-size: 0.8rem; line-height: 1.5; display: flex; flex-direction: column; gap: 0.8rem;">
  <div>
    <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 0.2rem;">SCM Business Challenge</div>
    <p style="color: #CBD5E1; margin: 0;">
      Late delivery SLA violations erode margins by up to 25%. This DSS acts as a <strong>Prescriptive Mitigation Engine</strong> - leveraging the benchmark <strong>DataCo Smart Supply Chain Dataset</strong> to quantify SLA liability and determine when to spend expedited freight costs to salvage net order profits.
    </p>
  </div>
  <div>
    <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 0.2rem;">Operations Decision Logic (ROI)</div>
    <p style="color: #CBD5E1; margin: 0;">
      <strong>Prescriptive Action:</strong> Intervene if <code>Expected Profit (No Intervention) &lt; Expected Profit (Expedited Shipping)</code>. Prevents over-intervention while protecting high-risk, high-value freight.
    </p>
  </div>
  <div>
    <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 0.4rem;">Model Evaluation Metrics</div>
    <div style="display: flex; justify-content: space-between; background: {T['bg']}; padding: 0.6rem; border-radius: 6px; border: 1px solid {T['border']};">
      <div><span style="color: #10B981; font-weight: 700; font-size: 0.9rem;">71.9%</span><br><span style="color: #94A3B8; font-size: 0.65rem;">AUC-ROC</span></div>
      <div><span style="color: #10B981; font-weight: 700; font-size: 0.9rem;">66.6%</span><br><span style="color: #94A3B8; font-size: 0.65rem;">Accuracy</span></div>
      <div><span style="color: #10B981; font-weight: 700; font-size: 0.9rem;">66.3%</span><br><span style="color: #94A3B8; font-size: 0.65rem;">F1-Score</span></div>
      <div><span style="color: #3B82F6; font-weight: 700; font-size: 0.9rem;">100</span><br><span style="color: #94A3B8; font-size: 0.65rem;">Trees</span></div>
    </div>
  </div>
  <div>
    <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 0.3rem;">Key Predictive Drivers (SHAP)</div>
    <div style="display: flex; flex-wrap: wrap; gap: 0.35rem;">
      <span class="tech-tag" style="font-size: 0.65rem; margin: 0; padding: 0.15rem 0.45rem; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); color: #93C5FD;">Sales Value</span>
      <span class="tech-tag" style="font-size: 0.65rem; margin: 0; padding: 0.15rem 0.45rem; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); color: #93C5FD;">Order Profit</span>
      <span class="tech-tag" style="font-size: 0.65rem; margin: 0; padding: 0.15rem 0.45rem; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); color: #93C5FD;">Scheduled Transit SLA</span>
      <span class="tech-tag" style="font-size: 0.65rem; margin: 0; padding: 0.15rem 0.45rem; background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); color: #93C5FD;">Transfer Payment Method</span>
    </div>
  </div>
  <div style="font-size: 0.7rem; color: {T['text3']}; border-top: 1px solid {T['border']}; padding-top: 0.5rem; margin-top: 0.2rem; font-style: italic;">
    ⚠️ Note: This is a standalone portfolio demonstration. SCM ERP parameters are mock-simulated and do not connect to a live production database.
  </div>
</div>
"""

def get_label(feature_name: str) -> str:
    f = feature_name.replace("Order Country_", "Country: ")
    f = f.replace("Shipping Mode_", "Mode: ")
    f = f.replace("Customer Segment_", "Segment: ")
    f = f.replace("Product Category_", "Category: ")
    f = f.replace("Payment Type_", "Payment: ")
    f = f.replace("Order Day of Week_", "Day: ")
    f = f.replace("Shipping_Type_", "Payment: ")
    f = f.replace("Order_Profit_Per_Order", "Profit Per Order")
    f = f.replace("Days_Scheduled", "Scheduled SLA Days")
    return f

DATA_DICT_HTML = f"""
<div class="nx-card">
  <div style="font-size:.8rem;color:{T['text3']};margin-bottom:1rem;line-height:1.6;">
    Active mapping definitions between corporate SCM ERP columns and target machine learning features. Following the feature selection pipeline, only 4 features are active in the model.
  </div>
  <table class="dd-table">
    <thead><tr><th>Feature Column Name</th><th>Status</th><th>Type</th><th>ERP Equivalent</th><th>Business Context &amp; Selection Rationale</th></tr></thead>
    <tbody>
      <tr style="background: rgba(16, 185, 129, 0.05);"><td style="color:{T['green']};font-weight:600;">Sales</td><td style="color:{T['green']};font-weight:600;">ACTIVE</td><td>Float</td><td>Sales ($)</td><td>Total revenue generated by the order. Primary driver of value-at-risk and SLA penalty liability. Selected by RandomForest importance.</td></tr>
      <tr style="background: rgba(16, 185, 129, 0.05);"><td style="color:{T['green']};font-weight:600;">Order_Profit_Per_Order</td><td style="color:{T['green']};font-weight:600;">ACTIVE</td><td>Float</td><td>Profit ($)</td><td>Expected profit margin per order. Base financial buffer used to calculate expedited freight ROI. Selected by RandomForest importance.</td></tr>
      <tr style="background: rgba(16, 185, 129, 0.05);"><td style="color:{T['green']};font-weight:600;">Days_Scheduled</td><td style="color:{T['green']};font-weight:600;">ACTIVE</td><td>Integer</td><td>Transit SLA</td><td>Contractual scheduled delivery days. Sets transit deadline to compare against AI delay probability. Selected by RandomForest importance.</td></tr>
      <tr style="background: rgba(16, 185, 129, 0.05);"><td style="color:{T['green']};font-weight:600;">Shipping_Type_TRANSFER</td><td style="color:{T['green']};font-weight:600;">ACTIVE</td><td>Categorical</td><td>Payment = TRANSFER</td><td>Orders paid via TRANSFER. Strong indicator of warehouse hold and credit clearance delay. Selected by RandomForest importance.</td></tr>
      <tr style="opacity: 0.55;"><td style="color:{T['text3']};font-weight:600;">Order Country</td><td style="color:{T['text3']};">DROPPED</td><td>Categorical (163)</td><td>Order Country</td><td>Destination country. Dropped because it fell below variance and mean Gini importance thresholds.</td></tr>
      <tr style="opacity: 0.55;"><td style="color:{T['text3']};font-weight:600;">Order_Item_Quantity</td><td style="color:{T['text3']};">DROPPED</td><td>Integer</td><td>Quantity</td><td>Total item volume. Dropped because it had high collinearity with Sales and low predictive power.</td></tr>
      <tr style="opacity: 0.55;"><td style="color:{T['text3']};font-weight:600;">Customer Segment</td><td style="color:{T['text3']};">DROPPED</td><td>Categorical (3)</td><td>Segment</td><td>Consumer, Corporate, or Home Office. Dropped due to lack of distinct signal relative to core variables.</td></tr>
      <tr style="opacity: 0.55;"><td style="color:{T['text3']};font-weight:600;">Product Category</td><td style="color:{T['text3']};">DROPPED</td><td>Categorical (49)</td><td>Category</td><td>Product category. Dropped because it had very low individual feature importance (under 1%).</td></tr>
    </tbody>
  </table>
</div>"""

FOOTER_HTML = f"""
<div style="margin-top:2rem;border-top:1px solid {T['border']};padding-top:1.5rem;text-align:center;">
  <div style="font-size:.8rem;font-weight:600;color:{T['text']};margin-bottom:.3rem;">DataCo DSS - Supply Chain Risk Intelligence</div>
  <div style="font-size:.7rem;color:{T['text3']};margin-bottom:1rem;">
    Anshul Silhare - PGDM Research &amp; Business Analytics, WeSchool Mumbai
  </div>
  
  <div style="display:flex;gap:.8rem;justify-content:center;margin:1rem 0;flex-wrap:wrap;">
    <a href="https://linkedin.com/in/anshul-silhare" target="_blank" class="footer-link-card">
      <svg viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
      <span>LinkedIn</span>
    </a>
    <a href="https://github.com/AnshulSilhare" target="_blank" class="footer-link-card">
      <svg viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
      <span>GitHub</span>
    </a>
    <a href="https://anshulsilhare.github.io" target="_blank" class="footer-link-card">
      <svg viewBox="0 0 24 24"><path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-2.018 21.084c-.664-1.393-1.127-3.161-1.293-5.084h6.622c-.166 1.923-.629 3.691-1.293 5.084h-4.036zm-4.301-5.084c.18 2.36.792 4.417 1.666 5.828-2.617-1.428-4.664-3.87-5.437-6.828h3.771zm10.938 5.828c.874-1.411 1.486-3.468 1.666-5.828h3.771c-.773 2.958-2.82 5.4-5.437 6.828zm6.541-7h-4.22c-.122-2.185-.544-4.234-1.194-5.916 2.378.892 4.29 2.766 5.414 5.916zm-7.16 0h-5.96c-.143-2.022-.533-3.864-1.077-5.267.828-.423 1.905-.733 3.057-.733 1.152 0 2.229.31 3.057.733-.544 1.403-.934 3.245-1.077 5.267zm-8.22 0h-4.22c1.124-3.15 3.036-5.024 5.414-5.916-.65 1.682-1.072 3.731-1.194 5.916zm3.178-7.923c.884.453 1.892.735 2.962.753-.021-.57-.08-1.168-.178-1.786-1.087.164-2.073.518-2.784 1.033zm5.728-1.033c-.098.618-.157 1.216-.178 1.786 1.07-.018 2.078-.3 2.962-.753-.711-.515-1.697-.869-2.784-1.033z"/></svg>
      <span>Portfolio</span>
    </a>
  </div>

  <div style="display:flex;flex-wrap:wrap;gap:.3rem;justify-content:center;padding-bottom:1rem;">
    <span class="tech-tag">Python 3.11</span><span class="tech-tag">scikit-learn</span>
    <span class="tech-tag">Random Forest</span><span class="tech-tag">Gradio</span>
    <span class="tech-tag">Plotly</span><span class="tech-tag">pandas</span>
  </div>
</div>"""

def _empty_chart(msg="No Data"):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, showarrow=False,
                       font=dict(size=14, color=T["text3"], family=T["font"]))
    fig.update_layout(
        paper_bgcolor=T["card"], plot_bgcolor=T["card"],
        margin=dict(l=8, r=8, t=32, b=8), height=250,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, showline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, showline=False))
    return fig

# ===============================================================
# 6. CORE PREDICTION LOGIC
# ===============================================================
def build_prediction_vector(inputs: dict, scale=True) -> pd.DataFrame:
    # Union of features: model expected features + scaler expected features
    scaler_cols = list(scaler.feature_names_in_) if (scaler is not None and hasattr(scaler, "feature_names_in_")) else []
    all_init_cols = list(set(model_columns) | set(scaler_cols))
    
    vector = pd.DataFrame(0.0, index=[0], columns=all_init_cols)

    vector.at[0, "Days_Scheduled"] = float(inputs.get("Days_Scheduled", 3))
    vector.at[0, "Order_Item_Quantity"] = float(inputs.get("Order_Item_Quantity", 1))
    vector.at[0, "Sales"] = float(inputs.get("Sales", 100))
    vector.at[0, "Order_Profit_Per_Order"] = float(inputs.get("Order_Profit_Per_Order", 20))

    def set_cat(col_prefix, val):
        col_name = f"{col_prefix}_{val}"
        if col_name in all_init_cols:
            vector.at[0, col_name] = 1.0

    set_cat("Order_Country", COUNTRIES_MAPPING.get(inputs.get("Order Country", "United States"), inputs.get("Order Country")))
    set_cat("Customer_Segment", inputs.get("Customer Segment"))
    set_cat("Shipping_Type", inputs.get("Payment Type"))
    set_cat("Category_Name", inputs.get("Product Category"))
    set_cat("Day_of_Week", inputs.get("Order Day of Week"))

    if scale and len(scaler_cols) > 0:
        vector[scaler_cols] = scaler.transform(vector[scaler_cols])

    # Return exactly the columns expected by the model
    return vector[model_columns]

# ===============================================================
# 7. CHART BUILDERS
# ===============================================================
def _chart_importance():
    """Global feature importance - top 8 with square-root scaling."""
    if model is None:
        return _empty_chart("Model not loaded")
    raw = (pd.DataFrame({"F": FEAT, "I": model.feature_importances_})
             .sort_values("I", ascending=True).tail(8))
    labels = [get_label(f) for f in raw["F"]]
    values = raw["I"].tolist()
    total = model.feature_importances_.sum()
    pct = [v / total * 100 for v in values]
    sq = [v ** 0.5 for v in values]
    max_sq = max(sq) if sq else 1
    n = len(values)

    def _c(rank):
        if rank == 0: return T["accent"]
        if rank <= 2: return T["teal"]
        return "#94A3B8"
    colors = [_c(n - 1 - i) for i in range(n)]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=[max_sq * 1.05] * n, y=labels, orientation="h", width=0.6,
         marker=dict(color=T["bg"], line=dict(width=0)),
         hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Bar(x=sq, y=labels, orientation="h", width=0.6,
         marker=dict(color=colors, opacity=1.0, line=dict(width=0)),
         customdata=[[f"{p:.1f}%", f"{v:.4f}"] for p, v in zip(pct, values)],
         hovertemplate="<b>%{y}</b><br>Share: <b>%{customdata[0]}</b><br>Raw: %{customdata[1]}<extra></extra>",
         showlegend=False))

    threshold = max_sq * 0.15
    for sv, p, lbl, c in zip(sq, pct, labels, colors):
        if sv >= threshold:
            fig.add_annotation(x=sv / 2, y=lbl, text=f"<b>{p:.1f}%</b>",
                xanchor="center", yanchor="middle", showarrow=False,
                font=dict(size=11, color="white", family=T["font"]))
        else:
            fig.add_annotation(x=sv + max_sq * 0.02, y=lbl, text=f"<b>{p:.1f}%</b>",
                xanchor="left", yanchor="middle", showarrow=False,
                font=dict(size=11, color=T["text2"], family=T["font"]))

    fig.update_layout(
        paper_bgcolor=T["card"], plot_bgcolor=T["card"],
        font=dict(family=T["font"], color=T["text2"], size=12),
        margin=dict(l=0, r=60, t=16, b=10), height=340,
        barmode="overlay", bargap=0.2,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, showline=False,
            range=[0, max_sq * 1.1]),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color=T["text"]),
            automargin=True, linecolor=T["border"], linewidth=1, showline=True))
    return fig

def _chart_timeline(sched, pred, prob):
    """Delivery timeline: Scheduled SLA vs AI Projected."""
    extra = round(prob * 5) if pred == 1 else 0
    proj = sched + extra
    mx = max(sched, proj) + 2

    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, x1=sched, y0=1.6, y1=2.4,
        fillcolor=T["grid"], line=dict(width=1, color=T["border"]))
    fig.add_shape(type="rect", x0=0, x1=proj, y0=0.6, y1=1.4,
        fillcolor="rgba(239, 68, 68, 0.2)" if pred == 1 else "rgba(16, 185, 129, 0.2)",
        line=dict(width=1, color=T["red"] if pred == 1 else T["green"]))

    fig.add_annotation(x=sched/2, y=2, text=f"<b>SLA: {int(sched)} Days</b>",
        showarrow=False, font=dict(color=T["text2"], size=12))
    
    status_text = f"<b>Predicted: {int(proj)} Days</b>"
    if pred == 1:
        status_text += f" (+{int(proj - sched)} Delay)"
        
    fig.add_annotation(x=proj/2, y=1, text=status_text,
        showarrow=False, font=dict(color=T["red"] if pred == 1 else T["green"], size=12))

    fig.update_layout(
        paper_bgcolor=T["card"], plot_bgcolor=T["card"],
        font=dict(family=T["font"], color=T["text2"]),
        margin=dict(l=0, r=20, t=20, b=30), height=280,
        xaxis=dict(showgrid=True, gridcolor=T["grid"], range=[0, mx],
            tickfont=dict(size=11), title="Transit Days"),
        yaxis=dict(showgrid=False, showticklabels=False, range=[0, 3]))
    return fig

def _chart_shap(vector):
    """Custom Plotly Waterfall replacing SHAP force plot."""
    if not HAS_SHAP or model is None:
        return _empty_chart("SHAP not available")
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(vector)
        
        # Robustly extract 1D SHAP values for class 1 (delay risk)
        if isinstance(shap_values, list):
            vals = shap_values[1][0]
            base_val = explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
        elif isinstance(shap_values, np.ndarray):
            if shap_values.ndim == 3: # shape (samples, features, classes)
                vals = shap_values[0][:, 1]
                base_val = explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
            elif shap_values.ndim == 2: # shape (samples, features)
                vals = shap_values[0]
                base_val = explainer.expected_value
            else:
                vals = shap_values.flatten()
                base_val = explainer.expected_value
        else:
            vals = shap_values[0]
            base_val = explainer.expected_value

        df_s = pd.DataFrame({"F": FEAT, "V": vals, "Val": vector.iloc[0].values})
        df_s["Abs"] = df_s["V"].abs()
        df_s = df_s.sort_values("Abs", ascending=False).head(5)

        names = ["Base Value"] + [get_label(f) for f in df_s["F"]] + ["Prediction"]
        measures = ["absolute"] + ["relative"] * 5 + ["total"]
        y_vals = [base_val] + df_s["V"].tolist() + [base_val + df_s["V"].sum()]

        fig = go.Figure(go.Waterfall(
            orientation="h", measure=measures, y=names, x=y_vals,
            connector={"line": {"color": T["border"], "width": 1, "dash": "dot"}},
            decreasing={"marker": {"color": T["green"]}},
            increasing={"marker": {"color": T["red"]}},
            totals={"marker": {"color": T["accent"]}}
        ))
        fig.update_layout(
            paper_bgcolor=T["card"], plot_bgcolor=T["card"],
            font=dict(family=T["font"], color=T["text2"]),
            margin=dict(l=10, r=10, t=30, b=10), height=280,
            xaxis=dict(showgrid=True, gridcolor=T["grid"], title="Log Odds Contribution"),
            yaxis=dict(autorange="reversed", showgrid=False)
        )
        return fig
    except Exception as e:
        return _empty_chart(f"SHAP Error: {e}")

# ===============================================================
# 8. FINANCIAL ANALYSIS
# ===============================================================
def calculate_financials(sales, profit, prob, penalty_rate, intervention_cost):
    loss = (penalty_rate / 100) * sales
    exp_profit_no = profit - (prob * loss)
    exp_profit_yes = profit - intervention_cost
    return pd.DataFrame([{
        "Sales": sales,
        "Profit": profit,
        "Delay_Probability": prob,
        "Penalty_Loss": loss,
        "Expected_Profit": exp_profit_no,
        "Expected_Profit_with_Intervention": exp_profit_yes,
        "Intervention_Recommended": "Yes" if exp_profit_yes > exp_profit_no else "No"
    }])

# ===============================================================
# 9. RUNNERS
# ===============================================================
def run_analysis(country, mode, days, qty, sales, profit, penalty_rate, intervention_cost, segment, payment, category, day):
    if model is None:
        return "<div class='nx-card' style='color:red;'>Model failed to load.</div>", None, "", None

    inputs = {
        "Order Country": country, "Shipping Mode": mode, "Days_Scheduled": days,
        "Order_Item_Quantity": qty, "Sales": sales, "Order_Profit_Per_Order": profit,
        "Customer Segment": segment, "Payment Type": payment, "Product Category": category,
        "Order Day of Week": day
    }
    vec = build_prediction_vector(inputs)

    prob = model.predict_proba(vec)[0][1]
    pred = int(prob > 0.5)

    df_fin = calculate_financials(sales, profit, prob, penalty_rate, intervention_cost)

    v_html, f_html = get_verdict_html(pred, prob, df_fin)
    fig_tl = _chart_timeline(days, pred, prob)
    fig_sh = _chart_shap(vec)

    return v_html, fig_tl, f_html, fig_sh

def _kpi_html(df):
    t_ord = len(df)
    t_val = df["Sales"].sum()
    d_ord = df["Predicted_Delay"].sum()
    d_rate = (d_ord / t_ord * 100) if t_ord else 0
    t_pen = df["Penalty_Loss"].sum()
    
    intervened = df[df["Intervention_Recommended"] == "Yes"]
    sv = (intervened["Expected_Profit_with_Intervention"] - intervened["Expected_Profit"]).sum()

    t_val_str = f"${t_val/1000:,.1f}K"
    t_pen_str = f"${t_pen/1000:,.1f}K"
    d_rate_str = f"{d_rate:.1f}%"
    sv_str = f"${sv:,.0f}"

    return f"""
    <div class="kb">
      <div class="kc"><div class="kl">Total Volume</div><div class="kv">{t_ord}</div><div class="ks">Orders Processed</div></div>
      <div class="kc"><div class="kl">Total Revenue</div><div class="kv">{t_val_str}</div><div class="ks">Batch Value</div></div>
      <div class="kc"><div class="kl">High Risk Orders</div><div class="kv" style="color:{T['red']};">{d_ord}</div><div class="ks">{d_rate_str} of Batch</div></div>
      <div class="kc"><div class="kl">Value at Risk</div><div class="kv" style="color:{T['red']};">{t_pen_str}</div><div class="ks">Potential Penalties</div></div>
      <div class="kc" style="background:rgba(16, 185, 129, 0.12);border-color:{T['green']};"><div class="kl" style="color:{T['green']};">ROI / Savings</div><div class="kv" style="color:{T['green']};">{sv_str}</div><div class="ks">Net Mitigation Return</div></div>
    </div>
    """

def run_batch_analysis(file_obj, penalty_rate, intervention_cost):
    if file_obj is None:
        return pd.DataFrame(), "<div style='color:red;'>No file uploaded.</div>", "", None, None, gr.DownloadButton(visible=False)
    if model is None:
        return pd.DataFrame(), "<div style='color:red;'>Model error.</div>", "", None, None, gr.DownloadButton(visible=False)

    try:
        path = file_obj.name
        if path.endswith(".csv"): df = pd.read_csv(path)
        elif path.endswith((".xls", ".xlsx")): df = pd.read_excel(path)
        else: return pd.DataFrame(), "<div style='color:red;'>Unsupported format. Use CSV/XLSX.</div>", "", None, None, gr.DownloadButton(visible=False)

        if df.empty:
            return pd.DataFrame(), "<div style='color:red;'>File is empty.</div>", "", None, None, gr.DownloadButton(visible=False)

        # Normalize columns using aliases
        for canonical, aliases in COLUMN_ALIASES.items():
            for col in list(df.columns):
                col_clean = str(col).strip().lower().replace("_", " ").replace("-", " ")
                aliases_clean = [str(a).strip().lower().replace("_", " ").replace("-", " ") for a in aliases]
                canonical_clean = str(canonical).strip().lower().replace("_", " ").replace("-", " ")
                
                if col_clean in aliases_clean or col_clean == canonical_clean:
                    if col != canonical:
                        if canonical in df.columns:
                            df.drop(columns=[col], inplace=True)
                        else:
                            df.rename(columns={col: canonical}, inplace=True)

        for req in REQUIRED_COLS:
            if req not in df.columns:
                return pd.DataFrame(), f"<div style='color:red;'>Missing required column: {req}</div>", "", None, None, gr.DownloadButton(visible=False)

        # Fill optional columns with default values if they are missing
        for oc in OPTIONAL_COLS:
            if oc not in df.columns:
                df[oc] = DEFAULT_VALS[oc]

        recs = []
        for _, row in df.iterrows():
            inp = {c: row[c] for c in REQUIRED_COLS}
            for oc in OPTIONAL_COLS:
                inp[oc] = row[oc]
            recs.append(inp)

        vecs = pd.concat([build_prediction_vector(r) for r in recs], ignore_index=True)
        probs = model.predict_proba(vecs)[:, 1]
        preds = (probs > 0.5).astype(int)

        df["Delay_Probability"] = probs
        df["Predicted_Delay"] = preds

        df["Penalty_Loss"] = df["Predicted_Delay"] * df["Sales"] * (penalty_rate / 100)
        df["Expected_Profit"] = df["Order_Profit_Per_Order"] - df["Penalty_Loss"]
        df["Expected_Profit_with_Intervention"] = df["Order_Profit_Per_Order"] - intervention_cost
        df["Intervention_Recommended"] = np.where(df["Expected_Profit_with_Intervention"] > df["Expected_Profit"], "Yes", "No")

        msg = f"<div class='nexus-badge' style='background:#ECFDF5;color:{T['green']};border-color:#A7F3D0;margin-bottom:0;'>Processed {len(df)} orders successfully.</div>"
        
        # Maps
        map_df = df.groupby("Order Country")["Predicted_Delay"].mean().reset_index()
        fig_map = px.choropleth(map_df, locations="Order Country", locationmode="country names",
            color="Predicted_Delay", color_continuous_scale="Reds")
        fig_map.update_layout(
            paper_bgcolor=T["card"], plot_bgcolor=T["card"],
            geo=dict(showframe=False, showcoastlines=True, coastlinecolor=T["border"],
                     projection_type="equirectangular", bgcolor=T["card"],
                     showland=True, landcolor=T["bg"], showlakes=True, lakecolor=T["card"],
                     showcountries=True, countrycolor=T["border"]),
            margin=dict(l=0, r=0, t=30, b=0), height=300,
            font=dict(family=T["font"], color=T["text2"])
        )

        # ROI Chart
        roi_df = df[df["Intervention_Recommended"] == "Yes"]
        if not roi_df.empty:
            sv_cat = roi_df.groupby("Product Category").apply(
                lambda x: (x["Expected_Profit_with_Intervention"] - x["Expected_Profit"]).sum(),
                include_groups=False
            ).reset_index(name="Savings").sort_values("Savings", ascending=True).tail(5)
            fig_roi = px.bar(sv_cat, x="Savings", y="Product Category", orientation="h")
            fig_roi.update_traces(marker_color=T["green"])
        else:
            fig_roi = _empty_chart("No interventions recommended")
        fig_roi.update_layout(
            paper_bgcolor=T["card"], plot_bgcolor=T["card"],
            margin=dict(l=10, r=20, t=30, b=10), height=300,
            font=dict(family=T["font"], color=T["text2"]),
            xaxis=dict(showgrid=True, gridcolor=T["grid"]),
            yaxis=dict(showgrid=False)
        )

        # Prepare user-friendly dataframe output at the front
        output_cols = []
        if "Order ID" in df.columns:
            output_cols.append("Order ID")
            
        output_cols.extend([
            "Predicted_Delay", "Delay_Probability", "Intervention_Recommended",
            "Expected_Profit", "Expected_Profit_with_Intervention", "Penalty_Loss"
        ])
        
        output_cols.extend([c for c in df.columns if c not in output_cols])
        
        df_out = df[output_cols].copy()
        
        df_out.rename(columns={
            "Predicted_Delay": "Late Delivery Flag",
            "Delay_Probability": "Risk Probability",
            "Intervention_Recommended": "Intervention Recommended",
            "Expected_Profit": "Expected Profit (No Intervention)",
            "Expected_Profit_with_Intervention": "Expected Profit (With Intervention)",
            "Penalty_Loss": "Penalty Loss"
        }, inplace=True)
        
        df_out["Late Delivery Flag"] = df_out["Late Delivery Flag"].map({1: "Late Delivery Risk 🚩", 0: "On Time ✅"})

        import tempfile
        temp_dir = tempfile.gettempdir()
        out_excel_path = os.path.join(temp_dir, "dataco_batch_results.xlsx")
        
        writer = pd.ExcelWriter(out_excel_path, engine='xlsxwriter')
        df_out.to_excel(writer, index=False, sheet_name='Risk Analysis')
        
        workbook = writer.book
        worksheet = writer.sheets['Risk Analysis']
        
        header_format = workbook.add_format({
            'bold': True, 'text_wrap': True, 'valign': 'top',
            'fg_color': '#1E293B', 'font_color': 'white', 'border': 1
        })
        
        risk_format = workbook.add_format({'font_color': '#EF4444', 'bold': True})
        safe_format = workbook.add_format({'font_color': '#10B981', 'bold': True})
        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.0%'})
        
        for col_num, value in enumerate(df_out.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        worksheet.set_column('A:A', 15)  # Order ID
        worksheet.set_column('B:B', 25)  # Late Delivery Flag
        worksheet.set_column('C:C', 18, percent_format)  # Risk Probability
        worksheet.set_column('D:D', 25)  # Intervention Recommended
        worksheet.set_column('E:G', 32, currency_format)  # Financials
        worksheet.set_column('H:Z', 20)  # Other
        
        worksheet.conditional_format('B2:B10000', {'type': 'text', 'criteria': 'containing', 'value': 'Risk', 'format': risk_format})
        worksheet.conditional_format('B2:B10000', {'type': 'text', 'criteria': 'containing', 'value': 'Time', 'format': safe_format})
        worksheet.conditional_format('D2:D10000', {'type': 'text', 'criteria': 'containing', 'value': 'Yes', 'format': risk_format})
        
        writer.close()

        return df_out.round(2), msg, _kpi_html(df), fig_map, fig_roi, gr.update(value=out_excel_path, visible=True)

    except Exception as e:
        return pd.DataFrame(), f"<div style='color:red;'>Error: {e}</div>", "", None, None, gr.update(visible=False)

# ===============================================================
# 10. APP LAYOUT & LAUNCH
# ===============================================================
# Pre-generate static plots
fig_imp_global = _chart_importance()

# Executive Dark Theme
dark_theme = gr.themes.Base(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
).set(
    body_background_fill=T["bg"],
    block_background_fill=T["surface"],
    block_border_width="1px",
    block_border_color=T["border"],
    block_radius="12px",
    container_radius="12px",
    button_large_radius="12px",
    button_small_radius="8px",
    input_radius="8px",
    input_background_fill="#1E293B",
    input_border_color=T["border"],
    button_primary_background_fill=T["accent"],
    button_primary_background_fill_hover="#2563EB",
    button_primary_text_color="#ffffff",
    
    body_background_fill_dark=T["bg"],
    block_background_fill_dark=T["surface"],
    input_background_fill_dark="#1E293B",
    button_primary_background_fill_dark=T["accent"],
)

force_dark_js = """
() => {
    document.documentElement.classList.add('dark');
}
"""

with gr.Blocks(theme=dark_theme, css=custom_css, title="DataCo DSS - Supply Chain Risk Intelligence", js=force_dark_js) as app:
    
    gr.HTML(HEADER_HTML, elem_classes="nx-html-card")
    gr.HTML(HERO_HTML, elem_classes="nx-html-card")

    with gr.Tabs():
        # TAB 1: SINGLE ORDER PREDICTOR
        with gr.TabItem("- Single Order"):
            with gr.Row():
                with gr.Column(scale=1, min_width=300):
                    with gr.Column(elem_classes="nx-card"):
                        gr.HTML(RECRUITER_BRIEF_HTML, elem_classes="nx-html-card")
                    
                    with gr.Column(elem_classes="nx-card"):
                        gr.Markdown("### Input Parameters")
                        country = gr.Dropdown(choices=COUNTRY_LIST, value="United States", label="Destination Country")
                        mode = gr.Dropdown(choices=SHIPPING_MODES, value="Standard Class", label="Shipping Mode")
                        days = gr.Slider(minimum=0, maximum=10, step=1, value=3, label="SLA Scheduled Transit Days")

                    with gr.Column(elem_classes="nx-card"):
                        gr.Markdown("### Commercial Parameters")
                        qty = gr.Number(value=1, label="Order Item Quantity")
                        sales = gr.Number(value=150.0, label="Total Order Value ($)")
                        profit = gr.Number(value=20.0, label="Estimated Net Profit ($)")
                        penalty_rate = gr.Slider(minimum=0, maximum=50, step=5, value=25, label="SLA Penalty Rate (% of Sales)")
                        intervention_cost = gr.Number(value=50.0, label="Expedited Intervention Cost ($)")

                        with gr.Accordion("Advanced Segments", open=False):
                            segment = gr.Dropdown(choices=SEGMENTS, value="Corporate", label="Customer Segment")
                            payment = gr.Dropdown(choices=PAYMENTS, value="DEBIT", label="Payment Type")
                            category = gr.Dropdown(choices=CATEGORIES, value="Computers", label="Product Category")
                            day = gr.Dropdown(choices=DAYS_LIST, value="Monday", label="Order Day of Week")
                    
                    run_btn = gr.Button("Execute Analysis", variant="primary")

                with gr.Column(scale=1, min_width=300):
                    with gr.Column(elem_classes="verdict-col"):
                        gr.Markdown("### Prediction Output")
                        verdict_html = gr.HTML("", elem_classes="nx-html-card")
                    
                    details_html = gr.HTML("", elem_classes="nx-html-card")

                    with gr.Column(elem_classes="nx-card nx-plot-card"):
                        gr.Markdown("**DELIVERY TIMELINE PROJECTION**", elem_classes="chart-title")
                        timeline_plot = gr.Plot(show_label=False)

                    with gr.Column(elem_classes="nx-card nx-plot-card"):
                        gr.Markdown("**TOP RISK FACTORS (SHAP)**", elem_classes="chart-title")
                        shap_plot = gr.Plot(show_label=False)
                        gr.Markdown(
                            "💡 **How to interpret the Waterfall Chart:**\n\n"
                            "- **Base Value** represents the average baseline probability of late delivery across historical operations.\n"
                            "- <span style='color:#EF4444;font-weight:600;'>Red blocks (+)</span> increase delay risk for this specific order (e.g., short SLA window or high shipping distance).\n"
                            "- <span style='color:#10B981;font-weight:600;'>Green blocks (-)</span> decrease delay risk, pulling the probability back down.\n"
                            "- The chart aggregates these positive and negative drivers to calculate the final **Prediction** score."
                        )

            run_btn.click(
                fn=run_analysis,
                inputs=[country, mode, days, qty, sales, profit, penalty_rate, intervention_cost, segment, payment, category, day],
                outputs=[verdict_html, timeline_plot, details_html, shap_plot]
            )

        # TAB 2: BULK BATCH ENGINE
        with gr.TabItem("- Bulk Batch", elem_id="bulk-tab"):
            gr.Markdown("### Enterprise Batch Prescriptive Analytics")
            
            gr.HTML(BULK_FMT_HTML, elem_classes="nx-html-card")
            
            with gr.Row():
                with gr.Column(elem_classes="nx-card", scale=1, min_width=300):
                    gr.Markdown("### Parameters & Files")
                    bulk_penalty_rate = gr.Slider(minimum=0, maximum=100, step=1, value=15, label="Bulk SLA Penalty Rate (% of Sales)")
                    bulk_intervention_cost = gr.Number(value=50.0, label="Bulk Intervention Cost ($/order)")
                    file_upload = gr.File(value="sample_template.csv", label="Upload Operations Data")
                    dl_btn = gr.DownloadButton("Download Schema Template", value="sample_template.csv")
                    batch_btn = gr.Button("Execute Batch Analysis", variant="primary")
                
                with gr.Column(scale=1, min_width=300):
                    gr.HTML(f"""
<div style="background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.28);
  border-radius:10px;padding:0.9rem 1.1rem;font-size:0.8rem;color:{T['text2']};line-height:1.6;box-sizing:border-box;margin-bottom:10px;">
  <div style="font-weight:700;color:{T['accent']};margin-bottom:0.5rem;
    text-transform:uppercase;font-size:0.7rem;letter-spacing:0.07em;">&#9432;&nbsp; How to Use This Engine</div>
  <ol style="margin:0;padding-left:1.1rem;display:flex;flex-direction:column;gap:0.4rem;">
    <li><strong style="color:{T['text']};">Upload Data</strong><br/>Drop your CSV/Excel file with order records. Use the sample template as a starting point.</li>
    <li><strong style="color:{T['text']};">Set SLA Penalty Rate</strong><br/>The % of order sales value forfeited when delivery breaches the SLA window.</li>
    <li><strong style="color:{T['text']};">Set Intervention Cost</strong><br/>The flat fee (per order) to expedite a risky shipment and avoid the penalty.</li>
    <li><strong style="color:{T['text']};">Run &amp; Export</strong><br/>Get risk flags, financial ROI, geographic map, and download a formatted Excel report.</li>
  </ol>
</div>""", elem_classes="nx-html-card")
                    batch_kpi = gr.HTML("", elem_classes=["nx-html-card", "batch-kpi-row"])

            batch_msg = gr.HTML("", elem_classes="nx-html-card", elem_id="batch-msg-container")
            batch_df = gr.Dataframe(interactive=False, elem_id="batch-dataframe")
            export_file = gr.DownloadButton("Download Formatted Output Excel (.xlsx)", visible=False)

            with gr.Row():
                with gr.Column(elem_classes="nx-card nx-plot-card", scale=1, min_width=300):
                    gr.Markdown("**GEOGRAPHIC RISK DENSITY**", elem_classes="chart-title")
                    batch_map = gr.Plot(show_label=False)
                with gr.Column(elem_classes="nx-card nx-plot-card", scale=1, min_width=300):
                    gr.Markdown("**TOP MITIGATION SAVINGS**", elem_classes="chart-title")
                    batch_roi = gr.Plot(show_label=False)

            batch_btn.click(
                fn=run_batch_analysis,
                inputs=[file_upload, bulk_penalty_rate, bulk_intervention_cost],
                outputs=[batch_df, batch_msg, batch_kpi, batch_map, batch_roi, export_file]
            )

        # TAB 3: MODEL ARCHITECTURE
        with gr.TabItem("- Model Architecture"):
            gr.Markdown("### Machine Learning Interpretability")
            gr.HTML(SYSINFO_HTML, elem_classes="nx-html-card")
            gr.HTML(RF_ARCH_HTML, elem_classes="nx-html-card")

            with gr.Row():
                with gr.Column(scale=1, elem_classes="nx-card nx-plot-card", min_width=150):
                    gr.Markdown("**GLOBAL FEATURE ATTRIBUTION**", elem_classes="chart-title")
                    imp_plot = gr.Plot(value=fig_imp_global, show_label=False)
                with gr.Column(scale=1, min_width=150):
                    gr.HTML(CHALLENGES_HTML, elem_classes="nx-html-card")

        # TAB 4: DATA DICTIONARY
        with gr.TabItem("- Data Dictionary"):
            gr.Markdown("### Feature Dictionary & ERP Schema")
            gr.HTML(DATA_DICT_HTML, elem_classes="nx-html-card")

    gr.HTML(FOOTER_HTML, elem_classes="nx-html-card")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
