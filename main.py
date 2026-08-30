import os, tempfile, json
import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import io
import uvicorn

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

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

THEMES = {
    "light": {
        "bg": "#f8fafc", "surface": "#ffffff", "card": "#ffffff",
        "border": "rgba(15,23,42,0.08)", "grid": "#e2e8f0",
        "accent": "#1e3a5f", "teal": "#0d9488", "green": "#16a34a",
        "amber": "#d97706", "red": "#dc2626",
        "text": "#0f172a", "text2": "#475569", "text3": "#94a3b8",
        "font": "'DM Sans', sans-serif",
    },
    "dark": {
        "bg": "#0b0f19", "surface": "#1e293b", "card": "#1e293b",
        "border": "rgba(255,255,255,0.06)", "grid": "#1e293b",
        "accent": "#3b82f6", "teal": "#2dd4bf", "green": "#34d399",
        "amber": "#fbbf24", "red": "#f87171",
        "text": "#f8fafc", "text2": "#cbd5e1", "text3": "#64748b",
        "font": "'DM Sans', sans-serif",
    }
}

def get_theme(theme: str = "dark") -> dict:
    return THEMES.get(theme, THEMES["dark"])

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

def build_prediction_vector(inputs: dict, scale=True) -> pd.DataFrame:
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
    return vector[model_columns]

def calculate_financials(sales, profit, prob, penalty_rate, intervention_cost):
    loss = (penalty_rate / 100) * sales
    exp_profit_no = profit - (prob * loss)
    exp_profit_yes = profit - intervention_cost
    return {
        "sales": sales,
        "profit": profit,
        "delay_probability": prob,
        "penalty_loss": loss,
        "expected_profit": round(exp_profit_no, 2),
        "expected_profit_with_intervention": round(exp_profit_yes, 2),
        "intervention_recommended": "Yes" if exp_profit_yes > exp_profit_no else "No"
    }

def _empty_chart(msg, theme="dark"):
    return {"error": msg}

def _chart_importance(theme="dark"):
    if model is None:
        return _empty_chart("Model not loaded", theme)
    raw = (pd.DataFrame({"F": FEAT, "I": model.feature_importances_})
             .sort_values("I", ascending=True).tail(8))
    labels = [get_label(f) for f in raw["F"]]
    values = raw["I"].tolist()
    total = float(model.feature_importances_.sum())
    pct = [float(v / total * 100) for v in values]
    sq = [float(v ** 0.5) for v in values]
    return {
        "labels": labels,
        "values": [float(v) for v in values],
        "pct": pct,
        "sq": sq
    }

def _chart_timeline(sched, pred, prob, theme="dark"):
    extra = round(prob * 5) if pred == 1 else 0
    proj = sched + extra
    return {
        "sched": float(sched),
        "proj": float(proj),
        "pred": int(pred)
    }

def _chart_shap(vector, theme="dark"):
    if not HAS_SHAP or model is None:
        return _empty_chart("SHAP explanation unavailable", theme)
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(vector)
        
        # Handle different SHAP output formats (list vs 3D array vs 2D array)
        if isinstance(shap_values, list):
            sv = np.array(shap_values[1][0])
        else:
            shap_arr = np.array(shap_values)
            if shap_arr.ndim == 3:
                sv = shap_arr[0, :, 1]
            elif shap_arr.ndim == 2:
                sv = shap_arr[0]
            else:
                sv = shap_arr.flatten()
            
        feature_names = list(vector.columns)
        sv = sv.flatten() # ensure 1D
        abs_sv = np.abs(sv)
        top_idx = np.argsort(abs_sv)[-5:]
        
        y_labels = [get_label(str(feature_names[int(i)])) for i in top_idx]
        x_vals = [float(sv[int(i)]) for i in top_idx]
        
        return {
            "labels": y_labels,
            "values": x_vals
        }
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(err_msg)
        return _empty_chart(f"Error generating SHAP: {e}", theme)

app = FastAPI(title="DataCo DSS")
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            return f.read()
    return "<h1>DataCo Supply Chain Risk Intelligence API is Running. No frontend found in static/</h1>"

class PredictRequest(BaseModel):
    country: str = "United States"
    shipping_mode: str = "Standard Class"
    days_scheduled: float = 3.0
    quantity: float = 1.0
    sales: float = 150.0
    profit: float = 20.0
    penalty_rate: float = 5.0
    intervention_cost: float = 10.0
    segment: str = "Consumer"
    payment: str = "DEBIT"
    category: str = "Computers"
    day: str = "Monday"
    theme: str = "dark"

@app.get("/api/config")
async def config():
    return {
        "countries": COUNTRY_LIST,
        "shipping_modes": SHIPPING_MODES,
        "segments": SEGMENTS,
        "payments": PAYMENTS,
        "categories": CATEGORIES,
        "days": DAYS_LIST,
        "months": MONTHS_LIST,
        "model_version": MODEL_VERSION,
        "model_loaded": model is not None
    }

@app.post("/api/predict")
async def predict(req: PredictRequest):
    if model is None:
        return JSONResponse(status_code=500, content={"error": "Model not loaded"})
    
    inputs = {
        "Order Country": req.country,
        "Payment Type": req.payment,
        "Product Category": req.category,
        "Customer Segment": req.segment,
        "Order Day of Week": req.day,
        "Days_Scheduled": req.days_scheduled,
        "Order_Item_Quantity": req.quantity,
        "Sales": req.sales,
        "Order_Profit_Per_Order": req.profit
    }
    
    vector = build_prediction_vector(inputs)
    prob = float(model.predict_proba(vector)[0][1])
    pred = 1 if prob >= 0.5 else 0
    
    financials = calculate_financials(req.sales, req.profit, prob, req.penalty_rate, req.intervention_cost)
    
    return {
        "prediction": pred,
        "probability": round(prob, 4),
        "verdict": "HIGH RISK" if pred == 1 else "ON TRACK",
        "financials": financials,
        "timeline_chart": _chart_timeline(req.days_scheduled, pred, prob, req.theme),
        "shap_chart": _chart_shap(vector, req.theme)
    }

@app.post("/api/batch")
async def batch(
    file: UploadFile = File(...),
    penalty_rate: float = Form(5.0),
    intervention_cost: float = Form(10.0),
    theme: str = Form("dark")
):
    if model is None:
        return JSONResponse(status_code=500, content={"error": "Model not loaded"})
    
    content = await file.read()
    if file.filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(io.BytesIO(content))
    else:
        return JSONResponse(status_code=400, content={"error": "Unsupported file format"})
        
    df_lower = {c.lower(): c for c in df.columns}
    normalized_cols = {}
    for target, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in df_lower:
                normalized_cols[df_lower[alias.lower()]] = target
                break
    df.rename(columns=normalized_cols, inplace=True)
    
    missing_req = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing_req:
        return JSONResponse(status_code=400, content={"error": f"Missing required columns: {missing_req}"})
        
    for c in OPTIONAL_COLS:
        if c not in df.columns:
            df[c] = DEFAULT_VALS[c]
            
    df = df.fillna(value=DEFAULT_VALS)
    
    results_list = []
    total_sales = 0
    high_risk_count = 0
    val_at_risk = 0
    savings = 0
    
    for idx, row in df.iterrows():
        inputs = row.to_dict()
        vec = build_prediction_vector(inputs)
        prob = float(model.predict_proba(vec)[0][1])
        pred = 1 if prob >= 0.5 else 0
        
        fin = calculate_financials(inputs["Sales"], inputs["Order_Profit_Per_Order"], prob, penalty_rate, intervention_cost)
        
        out_row = inputs.copy()
        out_row["Late Delivery Flag"] = "Late Delivery Risk" if pred == 1 else "On Time"
        out_row["Risk Probability"] = prob
        out_row["Intervention Recommended"] = fin["intervention_recommended"]
        out_row["Expected Profit (No Intervention)"] = fin["expected_profit"]
        out_row["Expected Profit (With Intervention)"] = fin["expected_profit_with_intervention"]
        out_row["Penalty Loss"] = fin["penalty_loss"]
        
        results_list.append(out_row)
        
        total_sales += inputs["Sales"]
        if pred == 1:
            high_risk_count += 1
            val_at_risk += inputs["Sales"]
            if fin["expected_profit_with_intervention"] > fin["expected_profit"]:
                savings += (fin["expected_profit_with_intervention"] - fin["expected_profit"])
                
    df_results = pd.DataFrame(results_list)
    total_orders = len(df_results)
    
    # Generate Map Chart Data
    agg = df_results.groupby("Order Country").agg(
        total=("Sales", "count"),
        delayed=("Late Delivery Flag", lambda x: (x == "Late Delivery Risk").sum())
    ).reset_index()
    agg["Delay Rate"] = (agg["delayed"] / agg["total"] * 100).round(1)
    
    map_data = []
    for _, r in agg.iterrows():
        map_data.append({
            "name": r["Order Country"],
            "value": float(r["Delay Rate"]),
            "total": int(r["total"]),
            "delayed": int(r["delayed"])
        })
    
    # Generate ROI Chart Data
    roi_df = df_results[df_results["Intervention Recommended"] == "Yes"]
    roi_data = []
    if not roi_df.empty and "Product Category" in roi_df.columns:
        sv_cat = roi_df.groupby("Product Category").apply(
            lambda x: (x["Expected Profit (With Intervention)"] - x["Expected Profit (No Intervention)"]).sum(),
            include_groups=False
        ).reset_index(name="Savings").sort_values("Savings", ascending=True).tail(5)
        for _, r in sv_cat.iterrows():
            roi_data.append({
                "category": r["Product Category"],
                "savings": float(r["Savings"])
            })
    
    filename = "dataco_batch_results.xlsx"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    df_results.to_excel(writer, index=False, sheet_name='Results')
    workbook = writer.book
    worksheet = writer.sheets['Results']
    
    header_format = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'top',
        'fg_color': '#1E3A8A', 'font_color': 'white', 'border': 1
    })
    risk_format = workbook.add_format({'bg_color': '#FCA5A5', 'font_color': '#991B1B'})
    safe_format = workbook.add_format({'bg_color': '#86EFAC', 'font_color': '#166534'})
    currency_format = workbook.add_format({'num_format': '$#,##0.00'})
    percent_format = workbook.add_format({'num_format': '0.0%'})
    
    for col_num, value in enumerate(df_results.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(col_num, col_num, 15)
        
        if "Flag" in str(value):
            worksheet.conditional_format(1, col_num, len(df_results), col_num, {
                'type': 'cell', 'criteria': '==', 'value': '"Late Delivery Risk"',
                'format': risk_format
            })
            worksheet.conditional_format(1, col_num, len(df_results), col_num, {
                'type': 'cell', 'criteria': '==', 'value': '"On Time"',
                'format': safe_format
            })
        elif "Profit" in str(value) or "Loss" in str(value) or "Sales" in str(value):
            worksheet.set_column(col_num, col_num, 15, currency_format)
        elif "Probability" in str(value):
            worksheet.set_column(col_num, col_num, 15, percent_format)
            
    writer.close()

    return {
        "success": True,
        "message": f"Processed {total_orders} orders successfully.",
        "kpis": {
            "total_orders": total_orders,
            "total_revenue": total_sales,
            "high_risk_orders": high_risk_count,
            "delay_rate": round(high_risk_count / total_orders * 100, 2) if total_orders > 0 else 0,
            "value_at_risk": val_at_risk,
            "roi_savings": savings
        },
        "results": results_list,
        "map_chart": map_data,
        "roi_chart": roi_data,
        "download_filename": filename
    }

@app.get("/api/batch/download/{filename}")
async def download_batch(filename: str):
    filepath = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.get("/api/charts/importance")
async def charts_importance(theme: str = Query("dark")):
    return {"chart": _chart_importance(theme)}

@app.get("/api/template")
async def get_template():
    filepath = os.path.join(BASE_DIR, "sample_template.csv")
    if os.path.exists(filepath):
        return FileResponse(filepath, filename="sample_template.csv", media_type="text/csv")
    return JSONResponse(status_code=404, content={"error": "Template not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
