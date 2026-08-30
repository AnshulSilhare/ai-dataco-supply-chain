"""
DataCo Supply Chain — AI Delivery Risk Predictor
Gradio 4.36.1 · Hugging Face Spaces
"""

import gradio as gr
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io, os, traceback, threading, time, urllib.request

# ──────────────────────────────────────────────────────────────
# 1. MODEL
# ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model  = joblib.load(os.path.join(BASE_DIR, "dataco_rf_model.joblib"))
scaler = joblib.load(os.path.join(BASE_DIR, "dataco_scaler.joblib"))
_      = joblib.load(os.path.join(BASE_DIR, "dataco_columns.joblib"))
FEAT   = list(model.feature_names_in_)
SCOLS  = list(scaler.feature_names_in_)

# ──────────────────────────────────────────────────────────────
# 2. KEEP-ALIVE
# ──────────────────────────────────────────────────────────────
SPACE_HOST = os.environ.get("SPACE_HOST", "")
def _keep_alive():
    if not SPACE_HOST: return
    url = f"https://{SPACE_HOST}/"
    while True:
        time.sleep(25 * 60)
        try: urllib.request.urlopen(url, timeout=10)
        except: pass
threading.Thread(target=_keep_alive, daemon=True).start()

# ──────────────────────────────────────────────────────────────
# 3. CONSTANTS
# ──────────────────────────────────────────────────────────────
VALID_PAYMENT_TYPES = ["DEBIT", "PAYMENT", "TRANSFER", "CASH"]
VALID_COUNTRIES = ['Afganistßn', 'Albania', 'Alemania', 'Angola', 'Arabia Saudf', 'Argelia', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaiyßn', 'BTlgica', 'BangladTs', 'BarTin', 'Barbados', 'Belice', 'Benfn', 'Bielorrusia', 'Bolivia', 'Bosnia y Herzegovina', 'Botsuana', 'Brasil', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Butßn', 'Camboya', 'Camer·n', 'Canada', 'Chad', 'Chile', 'China', 'Chipre', 'Colombia', 'Corea del Sur', 'Costa Rica', 'Costa de Marfil', 'Croacia', 'Cuba', 'Dinamarca', 'Ecuador', 'Egipto', 'El Salvador', 'Emiratos -rabes Unidos', 'Eritrea', 'Eslovaquia', 'Eslovenia', 'Espa±a', 'Estados Unidos', 'Estonia', 'Etiopfa', 'Filipinas', 'Finlandia', 'Francia', 'Gab=n', 'Georgia', 'Ghana', 'Grecia', 'Guadalupe', 'Guatemala', 'Guayana Francesa', 'Guinea', 'Guinea Ecuatorial', 'Guinea-Bissau', 'Guyana', 'Haitf', 'Honduras', 'Hong Kong', 'Hungrfa', 'India', 'Indonesia', 'Irak', 'Irlanda', 'Irßn', 'Israel', 'Italia', 'Jamaica', 'Jap=n', 'Jordania', 'Kazajistßn', 'Kenia', 'Kirguistßn', 'Kuwait', 'Laos', 'Lesoto', 'Lfbano', 'Liberia', 'Libia', 'Lituania', 'Luxemburgo', 'MTxico', 'Macedonia', 'Madagascar', 'Malasia', 'Mali', 'Marruecos', 'Martinica', 'Mauritania', 'Moldavia', 'Mongolia', 'Montenegro', 'Mozambique', 'Myanmar (Birmania)', 'Namibia', 'Nepal', 'Nfger', 'Nicaragua', 'Nigeria', 'Noruega', 'Nueva Zelanda', 'Omßn', 'Pafses Bajos', 'Pakistßn', 'Panamß', 'Pap·a Nueva Guinea', 'Paraguay', 'Per·', 'Polonia', 'Portugal', 'Qatar', 'Reino Unido', 'Rep·blica Centroafricana', 'Rep·blica Checa', 'Rep·blica Democrßtica del Congo', 'Rep·blica Dominicana', 'Rep·blica de Gambia', 'Rep·blica del Congo', 'Ruanda', 'Rumania', 'Rusia', 'Senegal', 'Serbia', 'Sierra Leona', 'Singapur', 'Siria', 'Somalia', 'Sri Lanka', 'Suazilandia', 'SudAfrica', 'Sudßn', 'Sudßn del Sur', 'Suecia', 'Suiza', 'Surinam', 'Sßhara Occidental', 'Tailandia', 'Taiwßn', 'Tanzania', 'Tayikistßn', 'Togo', 'Trinidad y Tobago', 'Turkmenistßn', 'Turqufa', 'T·nez', 'Ucrania', 'Uganda', 'Uruguay', 'Uzbekistßn', 'Venezuela', 'Vietnam', 'Yemen', 'Yibuti', 'Zambia', 'Zimbabue']
DEFAULTS = {"Days_Scheduled":3, "Order_Item_Quantity":1, "Sales":150.0, "Order_Profit_Per_Order":20.0}
ALIASES = {
    "Payment Type":["type","payment type","transaction type"],
    "Order Country":["country","order_country","destination country","delivery country"],
    "Days_Scheduled":["days scheduled","scheduled days","sla","transit days","days_scheduled"],
    "Order_Item_Quantity":["qty","quantity","item quantity","item_qty","order quantity","pieces"],
    "Sales":["sales","order value","revenue","total sales","amount"],
    "Order_Profit_Per_Order":["profit","margin","order profit","profit_per_order","net profit"],
}

DEMO_CSV = (
    "Payment Type,Order Country,Days_Scheduled,Order_Item_Quantity,Sales,Order_Profit_Per_Order\n"
    "DEBIT,Estados Unidos,5,2,250.50,40.20\nPAYMENT,Francia,4,1,120.00,18.50\n"
    "TRANSFER,Alemania,2,3,450.75,80.40\nCASH,China,6,4,300.60,45.00\n"
    "DEBIT,India,1,1,75.00,12.00\nPAYMENT,Australia,4,2,210.30,35.10\n"
    "TRANSFER,Brasil,5,5,520.00,95.30\nCASH,Reino Unido,2,2,180.00,30.20\n"
    "DEBIT,Italia,6,3,340.00,50.00\nPAYMENT,Jap=n,4,1,95.00,15.00\n"
    "TRANSFER,Espaa,5,2,260.00,38.20\nCASH,MTxico,2,4,480.00,85.60\n"
    "DEBIT,Canada,6,3,330.00,52.30\nPAYMENT,Argentina,4,2,210.00,33.50\n"
    "TRANSFER,Colombia,1,1,90.00,14.20\nCASH,Chile,5,2,240.00,36.00\n"
    "DEBIT,Egipto,2,3,410.00,75.50\nPAYMENT,SudAfrica,4,2,190.00,28.40\n"
    "TRANSFER,Turqufa,6,4,350.00,55.00\nCASH,Rusia,2,1,160.00,25.10\n"
)
with open("/tmp/nexus_demo.csv","w") as _f: _f.write(DEMO_CSV)

# ──────────────────────────────────────────────────────────────
# 4. DESIGN TOKENS
# ──────────────────────────────────────────────────────────────
T = {
    "bg":      "#080c14",
    "surface": "#131d2e",
    "surf2":   "#0f1928",
    "border":  "rgba(56,189,248,0.15)",
    "accent":  "#38bdf8",
    "teal":    "#2dd4bf",
    "green":   "#4ade80",
    "amber":   "#f59e0b",
    "red":     "#f87171",
    "text":    "#e2e8f0",
    "text2":   "#94a3b8",
    "text3":   "#64748b",
    "grid":    "rgba(56,189,248,0.07)",
    "mono":    "'JetBrains Mono', monospace",
    "syne":    "'Syne', sans-serif",
}

# ──────────────────────────────────────────────────────────────
# 5. HTML HELPERS
# ──────────────────────────────────────────────────────────────
def _tag(bg,border,color,icon,msg):
    return(f'<div style="background:{bg};border-left:3px solid {border};border:1px solid {border};'
           f'border-radius:8px;padding:.6rem .9rem;font-family:monospace;font-size:.72rem;'
           f'color:{color};margin:.3rem 0;line-height:1.7;">{icon} {msg}</div>')
def _err(m):  return _tag("rgba(248,113,113,.08)","rgba(248,113,113,.35)","#fca5a5","⚠",m)
def _warn(m): return _tag("rgba(245,158,11,.07)","rgba(245,158,11,.28)","#fcd34d","⚡",m)
def _ok(m):   return _tag("rgba(74,222,128,.06)","rgba(74,222,128,.28)","#86efac","✓",m)
def _info(m): return _tag("rgba(56,189,248,.06)","rgba(56,189,248,.22)","#7dd3fc","ℹ",m)
def _kpi(label,value,sub,color):
    return(f'<div style="background:{T["surface"]};border:1px solid {T["border"]};border-radius:10px;'
           f'padding:.9rem;text-align:center;"><div style="font-family:monospace;font-size:.58rem;'
           f'letter-spacing:2px;text-transform:uppercase;color:{T["text3"]};margin-bottom:.35rem;">{label}</div>'
           f'<div style="font-size:1.7rem;font-weight:700;color:{color};">{value}</div>'
           f'<div style="font-family:monospace;font-size:.6rem;color:#475569;margin-top:.2rem;">{sub}</div></div>')

# ──────────────────────────────────────────────────────────────
# 6. FEATURE ROW BUILDER
# ──────────────────────────────────────────────────────────────
def _build_row(pay_type, country, days, qty, sales, profit):
    d = {c:0.0 for c in FEAT}
    for k,v in [("Days_Scheduled",days),("Order_Item_Quantity",qty),
                ("Sales",sales),("Order_Profit_Per_Order",profit)]:
        if k in d: d[k]=float(v)
    if f"Shipping_Type_{pay_type}"   in d: d[f"Shipping_Type_{pay_type}"]=1.0
    if f"Order_Country_{country}"  in d: d[f"Order_Country_{country}"]=1.0
    df = pd.DataFrame([d])[FEAT]
    df[SCOLS] = scaler.transform(df[SCOLS])
    return df

def _label(f):
    return (f.replace("Shipping_Mode_","Ship: ").replace("Order_Region_","Region: ")
             .replace("Customer_Country_","Country: ").replace("Shipping_Type_","Type: ")
             .replace("Order_Item_Quantity","Item Qty").replace("Order_Profit_Per_Order","Profit/Order")
             .replace("Days_Scheduled","Days Scheduled").replace("_"," "))[:24]

# ──────────────────────────────────────────────────────────────
# 7. CHART: FEATURE IMPORTANCE
#
# Design approach:
#   • Solid, thick horizontal bars (width=0.7) so they look substantial
#   • Square-root scale on X so minor features aren't invisible slivers
#   • Full-width dim track behind each bar for context
#   • Accent colour ramp: #1 = sky blue, #2-3 = teal, rest = slate
#   • % of total shown as text INSIDE the bar (white) when bar is wide enough,
#     otherwise outside (coloured)
#   • Thin horizontal row separator lines
#   • Title uses Syne display font, axis labels JetBrains Mono
# ──────────────────────────────────────────────────────────────
def _chart_importance() -> go.Figure:
    raw = (pd.DataFrame({"F":FEAT,"I":model.feature_importances_})
             .sort_values("I", ascending=True).tail(8))
    labels  = [_label(f) for f in raw["F"]]
    values  = raw["I"].tolist()
    total   = model.feature_importances_.sum()
    pct     = [v/total*100 for v in values]
    sq      = [v**0.5 for v in values]
    max_sq  = max(sq)
    n       = len(values)

    # colour ramp
    def _c(rank):   # rank 0 = top
        if rank == 0: return T["accent"]
        if rank <= 2: return T["teal"]
        return "#2a3f58"

    colors = [_c(n-1-i) for i in range(n)]

    fig = go.Figure()

    # ── dim full-width track ───────────────────────────────────
    fig.add_trace(go.Bar(
        x=[max_sq*1.0]*n, y=labels,
        orientation="h", width=0.70,
        marker=dict(color="rgba(56,189,248,0.05)", line=dict(width=0)),
        hoverinfo="skip", showlegend=False,
    ))

    # ── main bars ─────────────────────────────────────────────
    fig.add_trace(go.Bar(
        x=sq, y=labels,
        orientation="h", width=0.70,
        marker=dict(color=colors, opacity=1.0, line=dict(width=0)),
        customdata=[[f"{p:.1f}%", f"{v:.4f}"] for p,v in zip(pct,values)],
        hovertemplate="<b>%{y}</b><br>Share of model weight: <b>%{customdata[0]}</b><br>Raw score: %{customdata[1]}<extra></extra>",
        showlegend=False,
    ))

    # ── labels: inside bar if wide enough, outside if narrow ──
    threshold = max_sq * 0.18
    for sv, p, lbl, c in zip(sq, pct, labels, colors):
        if sv >= threshold:
            # inside (dark text on coloured bar)
            fig.add_annotation(
                x=sv/2, y=lbl,
                text=f"<b>{p:.1f}%</b>",
                xanchor="center", yanchor="middle", showarrow=False,
                font=dict(size=10, color="#0a101c", family=T["mono"]),
            )
        else:
            # outside (coloured text)
            fig.add_annotation(
                x=sv + max_sq*0.015, y=lbl,
                text=f"<b>{p:.1f}%</b>",
                xanchor="left", yanchor="middle", showarrow=False,
                font=dict(size=10, color=c if c != "#2a3f58" else T["text3"], family=T["mono"]),
            )

    # ── subtle separator after dominant bar ───────────────────
    sep = sq[n-2] + (sq[n-1]-sq[n-2])*0.12
    fig.add_shape(type="line",
        x0=sep, x1=sep, y0=-0.5, y1=n-1.5,
        line=dict(color="rgba(56,189,248,0.18)", width=1, dash="dot"),
    )

    # ── row dividers ──────────────────────────────────────────
    for i in range(n-1):
        fig.add_shape(type="line",
            x0=0, x1=max_sq*1.38, y0=i+0.5, y1=i+0.5,
            line=dict(color="rgba(255,255,255,0.04)", width=1), layer="below",
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=T["surface"],
        font=dict(family=T["mono"], color=T["text2"], size=11),
        margin=dict(l=0, r=64, t=20, b=12),
        height=370,
        barmode="overlay",
        bargap=0.22,
        xaxis=dict(
            showgrid=False, showticklabels=False,
            zeroline=False, showline=False,
            range=[0, max_sq*1.38],
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=10.5, color=T["text2"]),
            automargin=True,
            linecolor=T["border"], linewidth=1, showline=True,
        ),
    )
    return fig


# ──────────────────────────────────────────────────────────────
# 8. CHART: DELIVERY TIMELINE
#
# Design approach:
#   • Two clearly separated rows with generous height (width=0.40)
#   • Full-width dim track per row
#   • Row label is LEFT of chart (y-axis labels), not inside/outside bar
#   • Day count rendered INSIDE bar in dark text
#   • "On time ✓" or "+Xd delay" shown as styled annotation RIGHT of bar
#   • SLA deadline shown as vertical dashed line with top annotation
#   • Delay bracket (double-headed arrow) when delayed
# ──────────────────────────────────────────────────────────────
def _chart_timeline(sched:int, pred:int, prob:float) -> go.Figure:
    extra      = round(prob*5) if pred==1 else 0
    proj       = sched + extra
    delayed    = extra > 0
    proj_color = T["red"] if delayed else T["green"]
    x_max      = max(sched, proj) + max(3, int(sched*0.7))

    rows   = ["  AI Projected", "  Scheduled SLA"]
    widths = [proj, sched]
    colors = [proj_color, T["accent"]]
    tracks = [
        f"rgba({'248,113,113' if delayed else '74,222,128'},0.06)",
        "rgba(56,189,248,0.06)",
    ]

    fig = go.Figure()

    for row, w, c, tr in zip(rows, widths, colors, tracks):
        # track
        fig.add_trace(go.Bar(
            x=[x_max], y=[row], orientation="h", width=0.42,
            marker=dict(color=tr, line=dict(width=0)),
            hoverinfo="skip", showlegend=False,
        ))
        # bar
        fig.add_trace(go.Bar(
            x=[w], y=[row], orientation="h", width=0.42,
            marker=dict(color=c, opacity=0.93, line=dict(width=0)),
            showlegend=False,
            hovertemplate=f"<b>{row.strip()}</b>: {w} days<extra></extra>",
        ))
        # inside label
        fig.add_annotation(
            x=w/2, y=row,
            text=f"<b>{w}d</b>",
            showarrow=False, xanchor="center", yanchor="middle",
            font=dict(size=12, color="#060d1a", family=T["mono"]),
        )

    # right-side status badge for AI row
    badge_text = f"+{extra}d delay" if delayed else "on time ✓"
    badge_color = T["red"] if delayed else T["green"]
    badge_bg    = "rgba(248,113,113,0.15)" if delayed else "rgba(74,222,128,0.12)"
    fig.add_annotation(
        x=proj + x_max*0.025, y="  AI Projected",
        text=f'<span style="background:{badge_bg};padding:2px 8px;'
             f'border-radius:4px;">&nbsp;{badge_text}&nbsp;</span>',
        showarrow=False, xanchor="left", yanchor="middle",
        font=dict(size=11, color=badge_color, family=T["mono"]),
    )

    # SLA vertical dashed line
    fig.add_shape(type="line",
        x0=sched, x1=sched, y0=-0.5, y1=1.5,
        line=dict(color="rgba(56,189,248,0.45)", width=1.5, dash="dot"),
        layer="above",
    )
    fig.add_annotation(
        x=sched, y=1.56,
        text=f"SLA: {sched}d",
        showarrow=False, xanchor="center", yanchor="bottom",
        font=dict(size=9.5, color=T["accent"], family=T["mono"]),
    )

    # delay bracket annotation (arrow from sched to proj on AI row)
    if delayed:
        fig.add_annotation(
            ax=sched, axref="x", x=proj, xref="x",
            ay="  AI Projected", ayref="y", y="  AI Projected", yref="y",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5,
            arrowcolor=T["red"], startarrowhead=2, startarrowsize=1,
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=T["surface"],
        font=dict(family=T["mono"], color=T["text2"], size=11),
        margin=dict(l=0, r=150, t=20, b=52),
        height=230,
        barmode="overlay",
        bargap=0.50,
        xaxis=dict(
            title=dict(text="Days After Dispatch", font=dict(size=10, color=T["text3"])),
            showgrid=True, gridcolor=T["grid"], gridwidth=1,
            zeroline=True, zerolinecolor="rgba(56,189,248,0.2)", zerolinewidth=1,
            tickfont=dict(size=10, color=T["text3"]),
            range=[0, x_max], dtick=1, tickmode="linear",
            linecolor=T["border"], linewidth=1, showline=True,
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color=T["text2"]),
            automargin=True,
            categoryorder="array",
            categoryarray=["  Scheduled SLA","  AI Projected"],
            linecolor=T["border"], linewidth=1, showline=True,
        ),
    )
    return fig

def _empty_chart(msg=""):
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=T["surface"],
        font=dict(family=T["mono"], color=T["text3"]),
        margin=dict(l=8,r=8,t=32,b=8), height=300,
        title=dict(text=msg, font=dict(color=T["text3"],size=12)),
        xaxis=dict(showgrid=False,showticklabels=False,zeroline=False,showline=False),
        yaxis=dict(showgrid=False,showticklabels=False,zeroline=False,showline=False),
    )
    return fig

# ──────────────────────────────────────────────────────────────
# 9. PREDICTION
# ──────────────────────────────────────────────────────────────
def predict_single(ship, region, days, qty, sales, profit, penalty_pct, interv_cost):
    try:
        row  = _build_row(ship, region, days, qty, sales, profit)
        pred = int(model.predict(row)[0])
        prob = float(model.predict_proba(row)[0][1])
        pct  = prob * 100

        if pred == 1:
            v_bg,v_bd,v_c = "rgba(248,113,113,.07)","rgba(248,113,113,.4)","#f87171"
            icon,title = "🚩","HIGH RISK DETECTED"
            
            penalty = float(sales) * (penalty_pct / 100.0)
            savings = penalty - float(interv_cost)
            
            if savings > 0:
                note = f"<b>SLA Penalty Risk: ${penalty:.2f}</b><br>Recommend ${interv_cost:.2f} intervention for <span style='color:#4ade80;font-weight:700'>Net Savings: ${savings:.2f}</span>"
            else:
                note = f"<b>SLA Penalty Risk: ${penalty:.2f}</b><br>Intervention cost (${interv_cost:.2f}) exceeds penalty. No intervention recommended."
            nbg,nc = "rgba(248,113,113,.12)","#fca5a5"
        else:
            v_bg,v_bd,v_c = "rgba(74,222,128,.06)","rgba(74,222,128,.38)","#4ade80"
            icon,title = "✅","ON-TIME PREDICTION"
            note,nbg,nc = "✓ All signals nominal — no intervention required","rgba(74,222,128,.1)","#86efac"

        verdict = f"""
<div style="background:{v_bg};border:1px solid {v_bd};border-radius:12px;
            padding:2rem 1.3rem;text-align:center;
            display:flex;flex-direction:column;align-items:center;
            justify-content:center;gap:.8rem;
            min-height:370px;box-sizing:border-box;">
  <div style="font-size:2.8rem;line-height:1">{icon}</div>
  <div style="font-family:monospace;font-size:.68rem;font-weight:700;color:{v_c};
              letter-spacing:3px;text-transform:uppercase">{title}</div>
  <div style="font-family:monospace;font-size:.62rem;color:{T['text3']};line-height:1.7">
    <span style="color:{T['text2']}">{ship}</span>&nbsp;&nbsp;·&nbsp;&nbsp;<span style="color:{T['text2']}">{region}</span>
  </div>
  <div>
    <div style="font-size:3.6rem;font-weight:700;color:{v_c};line-height:1;
                font-family:monospace;letter-spacing:-2px">{pct:.1f}%</div>
    <div style="font-family:monospace;font-size:.58rem;color:{T['text3']};
                letter-spacing:2px;text-transform:uppercase;margin-top:.35rem">delay probability</div>
  </div>
  <div style="width:100%;background:rgba(255,255,255,.05);border-radius:99px;height:4px;overflow:hidden">
    <div style="width:{min(pct,100):.1f}%;height:100%;background:{v_c};border-radius:99px"></div>
  </div>
  <div style="font-family:monospace;font-size:.66rem;color:{nc};
              background:{nbg};border-radius:8px;padding:.5rem .9rem;
              width:100%;line-height:1.5">{note}</div>
</div>"""

        return verdict, _chart_importance(), _chart_timeline(int(days), pred, prob)

    except Exception:
        tb = traceback.format_exc(); print("ERROR:\n",tb)
        err = (f'<div style="background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.4);'
               f'border-radius:12px;padding:1.2rem;font-family:monospace;font-size:.72rem;color:#f87171;">'
               f'⚠ Inference error<br><pre style="font-size:.62rem;color:#fca5a5;white-space:pre-wrap;'
               f'overflow:auto;background:rgba(0,0,0,.2);padding:.6rem;border-radius:6px;">{tb[-1200:]}</pre></div>')
        return err, _empty_chart("Error"), _empty_chart("Error")

# ──────────────────────────────────────────────────────────────
# 10. BULK
# ──────────────────────────────────────────────────────────────
def _clean(df):
    errors, warnings = [], []
    if df.empty: errors.append("File is empty."); return df,warnings,errors
    renames={}
    for col in df.columns:
        norm=col.lower().replace("_"," ").strip()
        for can,als in ALIASES.items():
            if norm==can.lower().replace("_"," ").strip() or norm in als:
                if col!=can: renames[col]=can
                break
    if renames:
        df=df.rename(columns=renames)
        for o,n in renames.items(): warnings.append(f"Auto-mapped `{o}` → `{n}`")
    for req in ["Payment Type","Order Country"]:
        if req not in df.columns: errors.append(f"Missing: `{req}`")
    if errors: return df,warnings,errors
    bad_sm=df[~df["Payment Type"].isin(VALID_PAYMENT_TYPES)]["Payment Type"].unique().tolist()
    if bad_sm:
        warnings.append(f"Unknown Payment Type(s) → DEBIT"); 
        df["Payment Type"]=df["Payment Type"].where(df["Payment Type"].isin(VALID_PAYMENT_TYPES),"DEBIT")
    bad_rg=df[~df["Order Country"].isin(VALID_COUNTRIES)]["Order Country"].unique().tolist()
    if bad_rg:
        warnings.append(f"Unknown Country(s) → Estados Unidos")
        df["Order Country"]=df["Order Country"].where(df["Order Country"].isin(VALID_COUNTRIES),"Estados Unidos")
    for col in ["Days_Scheduled","Order_Item_Quantity","Sales","Order_Profit_Per_Order"]:
        if col in df.columns:
            c2=pd.to_numeric(df[col],errors="coerce")
            n=int(c2.isna().sum())
            if n: warnings.append(f"`{col}`: {n} non-numeric → default")
            df[col]=c2.fillna(DEFAULTS[col])
        else: df[col]=DEFAULTS[col]
    return df,warnings,errors

def predict_bulk(file_obj):
    try:
        if file_obj is None: raw=pd.read_csv(io.StringIO(DEMO_CSV)); demo=True
        else: raw=pd.read_csv(file_obj.name); demo=False
    except Exception as e: return _err(f"Cannot read file — {e}"),pd.DataFrame(),"",None
    df,warns,errs=_clean(raw.copy())
    if errs: return "".join(_err(e) for e in errs),pd.DataFrame(),"",None
    status="".join(_warn(w) for w in warns)
    if demo: status+=_info("Running on built-in demo data.")
    status+=_ok(f"{len(df):,} records validated.")
    try:
        rows=[]
        for _,r in df.iterrows():
            d={c:0.0 for c in FEAT}
            for k in ["Days_Scheduled","Order_Item_Quantity","Sales","Order_Profit_Per_Order"]:
                if k in d: d[k]=float(r.get(k,DEFAULTS[k]))
            sm=f"Shipping_Type_{r.get('Payment Type','DEBIT')}"
            rg=f"Order_Country_{r.get('Order Country','Estados Unidos')}"
            if sm in d: d[sm]=1.0
            if rg in d: d[rg]=1.0
            rows.append(d)
        X=pd.DataFrame(rows)[FEAT].copy(); X[SCOLS]=scaler.transform(X[SCOLS])
        preds=model.predict(X); probs=model.predict_proba(X)[:,1]
    except Exception:
        tb=traceback.format_exc(); print(tb)
        return _err("Prediction error — see logs."),pd.DataFrame(),"",None
    df=df.copy()
    df["Risk Verdict"]=["🚩 Late Delivery Risk" if p else "✅ On Time" for p in preds]
    df["Risk Score %"]=(probs*100).round(2)
    nr=int(preds.sum()); nok=len(preds)-nr; avg=float(probs.mean()*100); total=len(preds)
    metrics=f"""<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;margin:1rem 0;">
      {_kpi("At-Risk",f"{nr:,}",f"{nr/total*100:.1f}% of batch",T['red'])}
      {_kpi("On-Time",f"{nok:,}",f"{nok/total*100:.1f}% of batch",T['green'])}
      {_kpi("Avg Risk",f"{avg:.1f}%","across all records",T['amber'])}</div>"""
    out="/tmp/nexus_predictions.csv"; df.to_csv(out,index=False)
    status+=_ok(f"Batch complete — {total:,} records scored.")
    return status,df.head(10),metrics,out

# ──────────────────────────────────────────────────────────────
# 11. CSS
# ──────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── page ─────────────────────────────────────────────────── */
.nexus-header{background:rgba(8,12,20,.97);border-bottom:1px solid rgba(56,189,248,.13);
  padding:.9rem 1.6rem;display:flex;align-items:center;justify-content:space-between;}
.nexus-logo{font-family:'JetBrains Mono',monospace;font-size:.8rem;font-weight:600;
  color:#38bdf8;letter-spacing:.12em;}
.nexus-logo span{color:#475569;}
.nexus-status{display:flex;align-items:center;gap:.45rem;font-family:'JetBrains Mono',monospace;
  font-size:.62rem;letter-spacing:.08em;text-transform:uppercase;color:#64748b;}
.status-dot{width:7px;height:7px;border-radius:50%;background:#4ade80;animation:pdot 2s infinite;}
@keyframes pdot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.4)}}

.nexus-hero{padding:2.2rem 1.6rem 1.6rem;max-width:960px;margin:0 auto;}
.nexus-badge{display:inline-flex;align-items:center;gap:.4rem;font-family:'JetBrains Mono',monospace;
  font-size:.63rem;letter-spacing:.1em;text-transform:uppercase;color:#4ade80;
  background:rgba(74,222,128,.07);border:1px solid rgba(74,222,128,.22);
  padding:.28rem .85rem;border-radius:99px;margin-bottom:1rem;}
.nexus-badge::before{content:'';width:6px;height:6px;border-radius:50%;background:#4ade80;animation:pdot 2s infinite;}
.nexus-title{font-family:'Syne',sans-serif;font-size:clamp(1.8rem,4vw,3rem);font-weight:800;
  letter-spacing:-.03em;line-height:1.05;color:#e2e8f0;margin:0 0 .5rem;}
.nexus-title .accent{color:#38bdf8;}
.nexus-sub{font-family:'JetBrains Mono',monospace;font-size:.76rem;color:#64748b;
  letter-spacing:.03em;margin-bottom:1.5rem;line-height:1.7;}
.nexus-counters{display:flex;flex-wrap:wrap;gap:2rem;padding-top:1.2rem;
  border-top:1px solid rgba(56,189,248,.1);}
.nc-val{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:700;color:#38bdf8;line-height:1;}
.nc-lbl{font-family:'JetBrains Mono',monospace;font-size:.56rem;color:#64748b;
  letter-spacing:.08em;text-transform:uppercase;margin-top:.2rem;}

/* ── info cards ───────────────────────────────────────────── */
.nx-card{background:#131d2e;border:1px solid rgba(56,189,248,.15);border-radius:12px;
  padding:1.4rem;position:relative;overflow:hidden;margin-bottom:.9rem;}
.nx-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(56,189,248,.32),transparent);}
.nx-card-title{font-family:'JetBrains Mono',monospace;font-size:.63rem;letter-spacing:.13em;
  text-transform:uppercase;color:#38bdf8;margin-bottom:.9rem;
  display:flex;align-items:center;gap:.45rem;}
.nx-card-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(56,189,248,.22),transparent);}

/* ── tech tags ────────────────────────────────────────────── */
.tech-tag{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.58rem;
  color:#38bdf8;background:rgba(56,189,248,.07);border:1px solid rgba(56,189,248,.18);
  padding:.18rem .55rem;border-radius:4px;margin:.1rem;}

/* ── footer ───────────────────────────────────────────────── */
.nexus-footer{border-top:1px solid rgba(56,189,248,.1);padding:1.1rem 1.6rem;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:.5rem;margin-top:2rem;}
.footer-copy,.footer-tag{font-family:'JetBrains Mono',monospace;font-size:.6rem;
  color:#475569;letter-spacing:.05em;}
.footer-tag span{color:#38bdf8;}

/* ── section label ────────────────────────────────────────── */
.results-label{font-family:'JetBrains Mono',monospace;font-size:.65rem;letter-spacing:.15em;
  text-transform:uppercase;color:#38bdf8;padding:.3rem 0;margin-bottom:.5rem;
  border-bottom:1px solid rgba(56,189,248,.12);}

/* ──────────────────────────────────────────────────────────
   CHART CARDS
   Override Gradio's .block so each chart column looks exactly
   like an .nx-card: same bg, border, border-radius, top glow line.
   The Plotly plot_bgcolor matches this card surface so there's
   zero visual seam between container and chart.
   ────────────────────────────────────────────────────────── */

/* Feature importance chart column */
.imp-card > .block,
.imp-card > .block > .wrap {
  background:    #131d2e !important;
  border:        1px solid rgba(56,189,248,.15) !important;
  border-radius: 12px !important;
  overflow:      visible !important;
  padding:       1.2rem 1rem 1rem !important;
  position:      relative;
}
.imp-card > .block::before {
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(56,189,248,.32),transparent);
  border-radius:12px 12px 0 0;pointer-events:none;z-index:1;
}
.imp-card label, .imp-card .block-label { display:none !important; }
.imp-card > .block > div { overflow:visible !important; }

/* Timeline chart column */
.tl-card > .block,
.tl-card > .block > .wrap {
  background:    #131d2e !important;
  border:        1px solid rgba(56,189,248,.15) !important;
  border-radius: 12px !important;
  overflow:      visible !important;
  padding:       1.2rem 1rem 1rem !important;
  position:      relative;
}
.tl-card > .block::before {
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(56,189,248,.32),transparent);
  border-radius:12px 12px 0 0;pointer-events:none;z-index:1;
}
.tl-card label, .tl-card .block-label { display:none !important; }
.tl-card > .block > div { overflow:visible !important; }

/* Chart card titles (rendered as gr.Markdown inside columns) */
.chart-title p {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: .63rem !important;
  letter-spacing: .13em !important;
  text-transform: uppercase !important;
  color: #38bdf8 !important;
  margin: 0 0 .6rem 0 !important;
  padding-bottom: .5rem !important;
  border-bottom: 1px solid rgba(56,189,248,.12) !important;
}

/* Verdict card: match height of adjacent chart card */
.verdict-col > .block {
  background:    transparent !important;
  border:        none !important;
  padding:       0 !important;
  overflow:      visible !important;
}
"""

# ──────────────────────────────────────────────────────────────
# 12. STATIC HTML
# ──────────────────────────────────────────────────────────────
HEADER_HTML = """
<div class="nexus-header">
  <div class="nexus-logo"><span>// </span>dataco.nexus</div>
  <div class="nexus-status"><div class="status-dot"></div><span>Model Online · RF Ensemble Loaded</span></div>
</div>"""

HERO_HTML = """
<div class="nexus-hero">
  <div class="nexus-badge">🟢 AI Engine Active — Random Forest v3.0</div>
  <h1 class="nexus-title">DataCo Supply Chain<br><span class="accent">AI Risk Predictor.</span></h1>
  <p class="nexus-sub">Predict late delivery risk before dispatch · 180K+ records trained · 240+ engineered features · Explainable AI output</p>
  <div class="nexus-counters">
    <div class="nc"><div class="nc-val">180K+</div><div class="nc-lbl">Records Trained</div></div>
    <div class="nc"><div class="nc-val">240+</div><div class="nc-lbl">Features Engineered</div></div>
    <div class="nc"><div class="nc-val">69.2%</div><div class="nc-lbl">Model Accuracy</div></div>
    <div class="nc"><div class="nc-val">80%</div><div class="nc-lbl">Precision (Late)</div></div>
    <div class="nc"><div class="nc-val">&lt;0.5s</div><div class="nc-lbl">Inference Time</div></div>
  </div>
</div>"""

DIVIDER = '<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(56,189,248,.18),transparent);margin:.5rem 0 1rem;"></div>'
RESULTS_LABEL = '<div class="results-label">⬡ &nbsp;Prediction Output</div>'

IMP_TITLE  = "**⬡ FEATURE ATTRIBUTION**"
TL_TITLE   = "**⬡ DELIVERY TIMELINE PROJECTION**"

SYSINFO_HTML = """
<div class="nx-card">
  <div class="nx-card-title">⚙ Core Engine</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.4rem;">
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#38bdf8;border-bottom:1px solid rgba(56,189,248,.14);padding-bottom:.3rem;margin-bottom:.6rem;">Model Architecture</div>
      <div style="display:flex;flex-direction:column;gap:.38rem;font-family:'JetBrains Mono',monospace;font-size:.7rem;">
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Algorithm</span><span style="color:#e2e8f0">Random Forest</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Estimators</span><span style="color:#e2e8f0">100 trees · depth=25</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Accuracy</span><span style="color:#38bdf8">69.2%</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Precision (Late)</span><span style="color:#4ade80">80%</span></div>
        <div style="display:flex;justify-content:space-between;"><span style="color:#64748b">Normalizer</span><span style="color:#e2e8f0">StandardScaler</span></div>
      </div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#2dd4bf;border-bottom:1px solid rgba(45,212,191,.14);padding-bottom:.3rem;margin-bottom:.6rem;">Performance</div>
      <div style="display:flex;flex-direction:column;gap:.38rem;font-family:'JetBrains Mono',monospace;font-size:.7rem;">
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Routes Indexed</span><span style="color:#4ade80">180,519</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Model Size</span><span style="color:#e2e8f0">22 MB</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Avg Inference</span><span style="color:#e2e8f0">&lt; 0.5 s</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.04);padding-bottom:.3rem;"><span style="color:#64748b">Framework</span><span style="color:#e2e8f0">sklearn · Gradio</span></div>
        <div style="display:flex;justify-content:space-between;"><span style="color:#64748b">Deployed</span><span style="color:#e2e8f0">HF Spaces</span></div>
      </div>
    </div>
  </div>
</div>
<div class="nx-card">
  <div class="nx-card-title">⬡ Engineering Challenges Solved</div>
  <div style="display:flex;flex-direction:column;gap:.85rem;">
    <div style="display:flex;gap:.75rem;"><span style="font-family:'JetBrains Mono',monospace;font-size:.56rem;font-weight:600;color:#38bdf8;background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.2);border-radius:4px;padding:.1rem .38rem;flex-shrink:0;align-self:flex-start;">01</span><div><div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;font-weight:600;color:#e2e8f0;margin-bottom:.18rem;">Matrix Dimensionality Fix</div><div style="font-family:'JetBrains Mono',monospace;font-size:.63rem;color:#64748b;line-height:1.65;">Model trained on 240+ OHE columns; UI accepts 4 inputs. Zero-filled skeleton mapped via <span style="color:#2dd4bf">model.feature_names_in_</span>.</div></div></div>
    <div style="display:flex;gap:.75rem;"><span style="font-family:'JetBrains Mono',monospace;font-size:.56rem;font-weight:600;color:#38bdf8;background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.2);border-radius:4px;padding:.1rem .38rem;flex-shrink:0;align-self:flex-start;">02</span><div><div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;font-weight:600;color:#e2e8f0;margin-bottom:.18rem;">Self-Healing Scaler</div><div style="font-family:'JetBrains Mono',monospace;font-size:.63rem;color:#64748b;line-height:1.65;">Numeric columns isolated via <span style="color:#2dd4bf">scaler.feature_names_in_</span> — prevents shape mismatch on inference.</div></div></div>
    <div style="display:flex;gap:.75rem;"><span style="font-family:'JetBrains Mono',monospace;font-size:.56rem;font-weight:600;color:#38bdf8;background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.2);border-radius:4px;padding:.1rem .38rem;flex-shrink:0;align-self:flex-start;">03</span><div><div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;font-weight:600;color:#e2e8f0;margin-bottom:.18rem;">Model Size Optimisation</div><div style="font-family:'JetBrains Mono',monospace;font-size:.63rem;color:#64748b;line-height:1.65;">749 MB overfit model rebuilt with <span style="color:#2dd4bf">max_depth=25, min_samples_leaf=3</span> → 22 MB, 80% precision retained.</div></div></div>
  </div>
</div>
<div class="nx-card">
  <div class="nx-card-title">✦ Valid Input Reference</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.4rem;">
    <div><div style="font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#38bdf8;margin-bottom:.45rem;">Payment Type</div><div style="display:flex;flex-direction:column;gap:.24rem;"><span style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#94a3b8;">DEBIT · PAYMENT</span><span style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#94a3b8;">TRANSFER · CASH</span></div></div>
    <div><div style="font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#2dd4bf;margin-bottom:.45rem;">Order Country</div><div style="display:flex;flex-direction:column;gap:.24rem;"><span style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#94a3b8;">Estados Unidos · Francia · Alemania</span><span style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#94a3b8;">Brasil · India · China</span></div></div>
  </div>
</div>
<div style="display:flex;flex-wrap:wrap;gap:.32rem;margin-top:.7rem;">
  <span class="tech-tag">Python 3.11</span><span class="tech-tag">scikit-learn 1.8</span><span class="tech-tag">Random Forest</span><span class="tech-tag">Gradio 4.36</span><span class="tech-tag">Plotly</span><span class="tech-tag">pandas</span><span class="tech-tag">NumPy</span><span class="tech-tag">joblib</span><span class="tech-tag">Hugging Face Spaces</span>
</div>
<div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:#475569;text-align:center;letter-spacing:2px;padding-top:.9rem;border-top:1px solid rgba(56,189,248,.06);margin-top:.7rem;">
  ⬡ NEXUS AI · DataCo Global Supply Chain Dataset · Built by
  <a href="https://linkedin.com/in/anshul-silhare" target="_blank" style="color:#38bdf8;text-decoration:none;">Anshul Silhare</a>
  — PGDM Research &amp; Business Analytics, WeSchool Mumbai
</div>"""

FOOTER_HTML = """
<div class="nexus-footer">
  <div class="footer-copy">// dataco.nexus · DataCo Supply Chain AI</div>
  <div class="footer-tag">Built with <span>data-driven precision</span> ·
    <a href="https://anshulsilhare.github.io" target="_blank" style="color:#38bdf8;text-decoration:none;">anshulsilhare.github.io ↗</a>
  </div>
</div>"""

BULK_FMT_HTML = """
<div class="nx-card">
  <div class="nx-card-title">⬡ Required CSV Format</div>
  <div style="display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:.65rem;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:.64rem;padding:.18rem .55rem;background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.3);border-radius:4px;color:#fca5a5;">Payment Type ✱</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:.64rem;padding:.18rem .55rem;background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.3);border-radius:4px;color:#fca5a5;">Order Country ✱</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:.64rem;padding:.18rem .55rem;background:rgba(56,189,248,.07);border:1px solid rgba(56,189,248,.18);border-radius:4px;color:#94a3b8;">Days_Scheduled</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:.64rem;padding:.18rem .55rem;background:rgba(56,189,248,.07);border:1px solid rgba(56,189,248,.18);border-radius:4px;color:#94a3b8;">Order_Item_Quantity</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:.64rem;padding:.18rem .55rem;background:rgba(56,189,248,.07);border:1px solid rgba(56,189,248,.18);border-radius:4px;color:#94a3b8;">Sales</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:.64rem;padding:.18rem .55rem;background:rgba(56,189,248,.07);border:1px solid rgba(56,189,248,.18);border-radius:4px;color:#94a3b8;">Order_Profit_Per_Order</span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:#475569;">✱ Required &nbsp;·&nbsp; Others optional — defaults applied if missing</div>
</div>"""

# ──────────────────────────────────────────────────────────────
# 13. THEME
# ──────────────────────────────────────────────────────────────
theme = gr.themes.Base(
    primary_hue=gr.themes.Color(
        c50="#f0f9ff",c100="#e0f2fe",c200="#bae6fd",c300="#7dd3fc",
        c400="#38bdf8",c500="#0ea5e9",c600="#0284c7",c700="#0369a1",
        c800="#075985",c900="#0c4a6e",c950="#082f49"),
    secondary_hue="slate", neutral_hue="slate",
    font=[gr.themes.GoogleFont("Syne"), gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
).set(
    body_background_fill="#080c14",
    body_text_color="#e2e8f0",
    body_text_size="14px",
    block_background_fill="#131d2e",
    block_border_color="rgba(56,189,248,0.15)",
    block_border_width="1px",
    block_label_text_color="#64748b",
    block_label_text_size="11px",
    block_title_text_color="#e2e8f0",
    input_background_fill="#131d2e",
    input_border_color="rgba(56,189,248,0.2)",
    input_border_width="1px",
    button_primary_background_fill="#38bdf8",
    button_primary_text_color="#080c14",
    button_secondary_background_fill="transparent",
    button_secondary_border_color="rgba(56,189,248,0.3)",
    button_secondary_text_color="#94a3b8",
    slider_color="#38bdf8",
    table_odd_background_fill="#080c14",
    table_even_background_fill="#131d2e",
    table_border_color="rgba(56,189,248,0.1)",
)

# ──────────────────────────────────────────────────────────────
# 14. LAYOUT
# ──────────────────────────────────────────────────────────────
with gr.Blocks(theme=theme, css=CSS, title="DataCo · AI Delivery Risk Predictor") as demo:

    gr.HTML(HEADER_HTML)
    gr.HTML(HERO_HTML)

    with gr.Tabs():

        # ── TAB 1 ─────────────────────────────────────────────
        with gr.Tab("⬡  Single Order"):
            gr.Markdown("### Configure Shipment Parameters")
            with gr.Row():
                ship_dd = gr.Dropdown(VALID_PAYMENT_TYPES, value="DEBIT", label="Payment Type")
                reg_dd  = gr.Dropdown(VALID_COUNTRIES, value="Estados Unidos", label="Order Country")
            with gr.Row():
                days_nb = gr.Number(value=3, minimum=0, maximum=30, label="Scheduled Transit Days")
                qty_sl  = gr.Slider(minimum=1, maximum=5, value=1, step=1, label="Freight Quantity (Units)")
            with gr.Accordion("Advanced Parameters (optional)", open=False):
                with gr.Row():
                    sales_nb  = gr.Number(value=150.0, label="Order Value ($)")
                    profit_nb = gr.Number(value=20.0, label="Profit Per Order ($)")
            with gr.Accordion("Financial Impact Simulator", open=True):
                with gr.Row():
                    penalty_rate = gr.Slider(minimum=1, maximum=50, value=15, step=1, label="SLA Penalty Rate (%)")
                    interv_cost  = gr.Slider(minimum=0, maximum=500, value=50, step=10, label="Intervention Cost ($)")

            run_btn = gr.Button("⬡  Run Predictive Analysis", variant="primary", size="lg")

            gr.HTML(DIVIDER)
            gr.HTML(RESULTS_LABEL)

            # ── Results row 1: Verdict | Feature importance ───
            with gr.Row(equal_height=True):

                # Verdict — transparent block, card styling is inline HTML
                with gr.Column(scale=4, min_width=260, elem_classes=["verdict-col"]):
                    verdict_html = gr.HTML()

                # Feature importance — styled as card via CSS
                with gr.Column(scale=6, min_width=380, elem_classes=["imp-card"]):
                    gr.Markdown(IMP_TITLE, elem_classes=["chart-title"])
                    imp_plot = gr.Plot(show_label=False)

            # ── Results row 2: Timeline full width ────────────
            with gr.Row():
                with gr.Column(elem_classes=["tl-card"]):
                    gr.Markdown(TL_TITLE, elem_classes=["chart-title"])
                    tl_plot = gr.Plot(show_label=False)

            # Link ALL inputs to predict_single, including new sliders
            inputs_list = [ship_dd, reg_dd, days_nb, qty_sl, sales_nb, profit_nb, penalty_rate, interv_cost]
            run_btn.click(
                fn=predict_single,
                inputs=inputs_list,
                outputs=[verdict_html, imp_plot, tl_plot],
            )
            # Make sliders update prediction dynamically
            penalty_rate.change(fn=predict_single, inputs=inputs_list, outputs=[verdict_html, imp_plot, tl_plot])
            interv_cost.change(fn=predict_single, inputs=inputs_list, outputs=[verdict_html, imp_plot, tl_plot])

        # ── TAB 2 ─────────────────────────────────────────────
        with gr.Tab("⬡  Bulk Batch"):
            gr.HTML(BULK_FMT_HTML)
            gr.Markdown("Leave the upload empty to score the **built-in 20-row demo** automatically.")
            with gr.Row():
                bulk_file = gr.File(label="Upload CSV (optional)", file_types=[".csv"])
                with gr.Column():
                    bulk_btn  = gr.Button("⬡  Execute Batch Prediction", variant="primary", size="lg")
                    dl_btn = gr.File(value="sample_template.csv", label="⬇ Download Required Schema Template", interactive=False)
            bulk_status  = gr.HTML()
            bulk_metrics = gr.HTML()
            bulk_preview = gr.Dataframe(label="Results Preview (first 10 rows)", interactive=False, wrap=True)
            bulk_dl      = gr.File(label="⬇ Download Full Results (.csv)", interactive=False)
            bulk_btn.click(fn=predict_bulk, inputs=[bulk_file],
                           outputs=[bulk_status, bulk_preview, bulk_metrics, bulk_dl])

        # ── TAB 3 ─────────────────────────────────────────────
        with gr.Tab("⬡  Model Architecture"):
            gr.HTML(SYSINFO_HTML)

        # ── TAB 4 ─────────────────────────────────────────────
        with gr.Tab("⬡  Data Dictionary"):
            gr.Markdown("""
### 📖 Data Dictionary

| Feature | Description | Required in CSV |
|---------|-------------|-----------------|
| **Payment Type** | Customer's method of payment (DEBIT, PAYMENT, TRANSFER, CASH). Strongly predictive of fraud holds and clearing delays. | **Yes** |
| **Order Country** | The final destination country. Highly predictive of customs holding times and international routing delays. | **Yes** |
| **Days_Scheduled** | The SLA (Service Level Agreement) transit time promised to the customer. | No (defaults to 3) |
| **Order_Item_Quantity** | Number of items in the shipment. Affects freight class. | No (defaults to 1) |
| **Sales** | Gross value of the order. | No (defaults to $150) |
| **Order_Profit_Per_Order** | Net profit margin of the order. | No (defaults to $20) |
            """)

    gr.HTML(FOOTER_HTML)

demo.queue(max_size=20).launch(server_name="0.0.0.0", server_port=7860)