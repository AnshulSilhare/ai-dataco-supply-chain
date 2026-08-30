---
title: DataCo Supply Chain AI
emoji: 📦
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.36.1
python_version: '3.11'
app_file: app.py
pinned: false
license: mit
---

# 📦 DataCo Supply Chain — AI Delivery Risk Predictor

<div align="center">

![VS Code](https://img.shields.io/badge/VS_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-4.36.1-ff4b4b?style=for-the-badge&logo=gradio&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.2+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)

### _An end-to-end Machine Learning web application predicting supply chain delays and calculating prescriptive intervention ROI._

**Can we predict late deliveries? | Why do they happen? | How do we intervene proactively?**

**I built an AI tool to transition supply chain management from reactive to proactive.**

<div align="center">

[🚀 Live App Demo](https://huggingface.co/spaces/AnshulSilhare/ai-dataco-supply-chain) • [💻 Explore Code](app.py) • [🤝 Connect on LinkedIn](https://www.linkedin.com/in/anshul-silhare)

</div>

</div>

---

## 🎯 Project Motivation

As a PGDM student in Research & Business Analytics at WeSchool, my previous projects focused heavily on descriptive analytics (SQL extraction, Power BI dashboards). While historical tracking is great for analyzing past performance, **it is fundamentally reactive.**

Stakeholders don't just want to know *why* an order was late last month; they want to know if *tomorrow's* order is going to be late so they can intervene today.

**The Goal:** Build a predictive intelligence tool that flags high-risk deliveries and calculates a **Prescriptive Intervention ROI** (e.g. deciding whether paying for expedited shipping is cheaper than losing order profits to late-delivery SLA penalties).

---

## 📊 Dataset & Feature Selection Overview

**Source:** DataCo Smart Supply Chain Dataset
**Scale:** 180,519 global shipping records
**Business Domain:** Supply Chain, Logistics, Operations
**Target Variable:** Late Delivery Risk (Binary Classification: 1 = Late, 0 = On Time)

### 🧠 The Feature Selection Pipeline
To prevent model overfitting and eliminate noise from one-hot encoded variables (which expanded the training matrix to 239+ columns), I implemented a **two-stage feature selection pipeline** in the training notebook:

1. **Variance Thresholding**: Removed columns with variance below `0.01` (less than 1% variance), eliminating constant or near-constant features.
2. **SelectFromModel (Random Forest Gini Importance)**: Ran a diagnostic Random Forest to calculate the relative feature importances. Only features with a **Gini importance at or above the average (mean) importance** were kept.

This reduced the model from **239 features to 4 core predictive drivers**:
*   `Sales` (Order revenue value)
*   `Order_Profit_Per_Order` (Base expected profit margin)
*   `Days_Scheduled` (Scheduled delivery SLA window)
*   `Shipping_Type_TRANSFER` (Payment method = TRANSFER, correlating with warehouse hold times)

---

## ✨ Key Dashboard Features (Gradio UI)

The web application is structured into three dedicated analytics tabs:

### 1️⃣ Tab 1: Single Order Risk Analyzer
*   **Predictive Inference**: Evaluates single order inputs and returns a color-coded circular gauge of the delay probability.
*   **Delivery Timeline**: Plots an interactive horizontal timeline comparing the scheduled SLA days against the AI-projected delivery timeline.
*   **Prescriptive ROI Analysis**: Computes whether the cost of expedited shipping is financially justified compared to the expected SLA penalty loss.
*   **Explainable AI (SHAP Waterfall)**: Renders a Plotly waterfall chart showing how the active features adjusted log-odds away from the model's base value.

### 2️⃣ Tab 2: Enterprise Batch Prescriptive Analytics
*   **Bulk Processing**: Supports drag-and-drop CSV/Excel uploads of thousands of pending orders.
*   **Export Capabilities**: One-click download of processed data and prescriptive insights into formatted Excel (`.xlsx`) reports.
*   **Operations KPIs**: Displays aggregate metrics (Total Orders, Average Delay Risk, Financial Penalty Exposure, and Net Intervention Savings) in a streamlined top-bar layout.
*   **Geospatial Risk Distribution**: Visualizes country-level delay risks in a global choropleth map.
*   **Bulk Savings Charts**: Compares business-as-usual losses against optimizer savings.

---

## 📸 Application Screenshots

*(Screenshots of the UI highlighting the Single Order Risk Analyzer and Bulk Batch Prescriptive Analytics)*

<div align="center">
  <img src="Screenshot%202026-06-10%20at%2023-31-13%20Supply%20Chain%20Risk%20Intelligence.png" alt="Single Order Risk Analyzer" width="800"/>
</div>
<br>
<div align="center">
  <img src="Screenshot%202026-06-10%20at%2023-33-53%20Supply%20Chain%20Risk%20Intelligence.png" alt="Batch Processing Dashboard" width="800"/>
</div>

### 3️⃣ Tab 3: Model Architecture & Governance
*   **Model Parameters**: Outlines Random Forest hyperparameters (100 Trees, max depth 20, standard scaling).
*   **Active Data Dictionary**: Displays an interactive table detailing the active mapping schema and clearly highlighting which features are **ACTIVE** (green) vs. **DROPPED** (gray) by the selector pipeline.
*   **Model Limitations**: Advises on cold-starts, feature drift, and data constraints.

---

## 🧠 Technical Challenges Solved

### Challenge 1: Matrix Dimensionality Pruning
*   **The Problem:** One-hot encoding categorical variables (e.g. 163 countries) expanded the dataset to 239 features. Feeding all of these into a Random Forest caused overfitting and high inference latency.
*   **The Fix:** Pruned the feature space to the top 4 active drivers using Gini importance selection. This compressed the model file from 750MB to **35MB** and reduced local/cloud inference speeds to milliseconds.

### Challenge 2: Dynamic Prediction Vector Alignment
*   **The Problem:** The user interface collects standard inputs, but the trained model requires a specific aligned columns matrix.
*   **The Fix:** Engineered a robust `build_prediction_vector` function in [app.py](app.py). It initializes a template dataframe matching the active columns, maps user choices to the respective indices, scales numeric features, and slices the vector to the exact model shape dynamically.

### Challenge 3: C++ DLL Library Version Clashes
*   **The Problem:** C++ DLL load failures due to package version mismatches between pip-installed PyArrow and Scikit-Learn binaries on Python 3.11+.
*   **The Fix:** Designed a clean, decoupled dependency environment. We pinned stable releases in `requirements.txt` to align low-level bindings and ensure stable execution.

---

## 🛠️ Technical Stack

| **Category**                 | **Technologies**                               |
| ---------------------------- | ---------------------------------------------- |
| **Language**                 | Python 3.11+                                   |
| **Machine Learning**         | Scikit-Learn (Random Forest Ensemble)          |
| **Data Processing**          | pandas, numpy, joblib, shap                    |
| **Front-End / UI**           | Gradio, Plotly (Choropleth Maps & Waterfalls)  |
| **AI Development Tools**     | Google Antigravity (Pair Programming Agent)    |

---

## 🚀 Getting Started

To run the application locally on your machine, follow these steps:

### Prerequisites
*   Python 3.11 or Python 3.13 installed
*   Git

### Installation & Setup

**1. Clone the repository:**
```bash
git clone https://github.com/AnshulSilhare/dataco-supply-chain-ai.git
cd dataco-supply-chain-ai
```

**2. Set up a virtual environment (Conda is recommended for binary stability):**
```bash
conda create -n dataco_env python=3.11 -y
conda activate dataco_env
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Launch the application:**
```bash
python app.py
```
*(The terminal will print a local URL, typically `http://127.0.0.1:7860`. Open this in your browser to view the dashboard.)*

---

## 📁 Repository Structure

```bash
📦 dataco-supply-chain-ai
│
├── 📂 notebooks/
│   ├── Model_Training_Dataco.ipynb   # Visual EDA, Feature Selection, and Model Tuning
│   └── index.html                    # Rendered HTML of the training notebook
│
├── 📄 app.py                         # Main Gradio application source code
├── 📄 requirements.txt               # Pinned package dependency file
├── 📄 dataco_rf_model.joblib         # Saved Random Forest classifier (4 features)
├── 📄 dataco_scaler.joblib           # Saved StandardScaler parameters
├── 📄 dataco_columns.joblib          # Saved active column name list
├── 📄 sample_template.csv            # Sample CSV file for testing batch predictions
└── 📄 README.md                      # This documentation file
```

---

## 🔮 Future Roadmap

- [ ] **SQL Database Integration**: Connect the Gradio server to a simulated SQL database to ingest new orders automatically.
- [ ] **Multi-Model Comparison**: Add a sidebar toggle to switch between Random Forest, XGBoost, and LightGBM engines.
- [ ] **Live API Endpoint**: Expose a REST API endpoint via Hugging Face Spaces for external ERP integration.

---

## 🤝 Let's Connect

I'm actively seeking Summer 2026 roles in **Business Analytics**, **Data Science**, or **Supply Chain Analytics**. 

If you are looking for an analyst who can not only write complex SQL queries and design Power BI dashboards, but also build, prune, and deploy interactive machine learning tools, let's connect!

*   **LinkedIn**: [linkedin.com/in/anshul-silhare](https://linkedin.com/in/anshul-silhare)
*   **Portfolio Showcase**: [Hugging Face Space Demo](https://huggingface.co/spaces/AnshulSilhare/ai-dataco-supply-chain)

---
<div align="center">
⭐ Support this project by giving it a star on GitHub!
</div>
