<div align="center">

# 📦 DataCo Supply Chain — AI Risk Intelligence & Decision Support System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.5+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Apache ECharts](https://img.shields.io/badge/Apache_ECharts-5.5-AA344D?style=for-the-badge&logo=apacheecharts&logoColor=white)](https://echarts.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

### *An end-to-end Machine Learning Decision Support System (DSS) that predicts late delivery risks and computes prescriptive freight mitigation ROI.*

**[🚀 Live Demo (Web App)](https://anshulsilhare-ai-dataco-supply-chain.hf.space)** • **[💻 Explore Code](main.py)** • **[📓 Training Notebook](notebooks/Model_Training_Dataco.ipynb)** • **[🤝 Connect on LinkedIn](https://www.linkedin.com/in/anshul-silhare)**

</div>

---

## 🎯 Executive Overview & Business Motivation

In global supply chains, **late delivery SLA violations can erode operating profit margins by up to 25%**. While historical BI reporting (SQL, Power BI) tracks past delays, **it is fundamentally reactive**.

**DataCo DSS** transforms supply chain operations from reactive firefighting to **proactive prescriptive mitigation**:
1. **Predicts Delivery Risk**: Evaluates pending orders against trained Machine Learning models before shipments leave the warehouse.
2. **Quantifies Financial Exposure**: Calculates expected penalty loss liability based on order value and contractual SLA terms.
3. **Prescribes Actionable Interventions**: Determines if spending expedited freight fees is financially justified, preventing over-intervention while safeguarding high-margin orders.

```
       ┌───────────────────┐
       │   Order Intake    │ (Destination, SLA, SKU, Revenue, Margin)
       └─────────┬─────────┘
                 │
                 ▼
       ┌───────────────────┐
       │  Predictive AI    │ (Random Forest Classifier: Delay Probability %)
       └─────────┬─────────┘
                 │
                 ▼
       ┌───────────────────┐
       │  Prescriptive DSS │ Expected Profit (No Action) vs Expected Profit (Expedited)
       └─────────┬─────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
   ⚡ EXPEDITE       🛡️ ABSORB RISK
(Saves Net Profit)  (Protects Margin)
```

---

## ⚡ Key Architectural Features & UI Innovations

### 1. High-Performance FastAPI Backend
Migrated from a basic prototype to a robust, asynchronous **FastAPI + Uvicorn** service supporting sub-50ms inference, streaming batch processing, and automated Excel export.

### 2. Tri-Capsule Floating Header Islands
* **Brand Island**: Dynamic glass capsule with rotating crystal emblem and auto-collapsing version badge.
* **Liquid Nav Island**: Desktop navigation featuring **moving liquid droplet physics** (`cubic-bezier(0.22, 1, 0.36, 1.2)`) with squash-and-stretch fluid animation.
* **Satellite Action Cluster**: Specular glass action buttons for System Guide and Dark/Light mode switching.

### 3. Adaptive Dynamic Island Control Capsule
* **Unified Parameter Hub**: Real-time sticky pill summary tracking active simulation parameters.
* **60fps Fluid Morphing**: Uses native `ResizeObserver` and GPU layer compositing (`translateZ(0)`) to expand/collapse without layout stutter or scrollbar protrusion.

### 4. Explainable AI & Prescriptive Output
* **Real-Time Risk Donut Ring**: Instant visual feedback of delay risk probability.
* **Delivery Timeline Projection**: Compares promised SLA transit windows against AI-projected delivery days.
* **Bidirectional SHAP Attribution**: Vertical column charts detailing exact positive and negative delay risk drivers.
* **Prescriptive Financial Callout**: Direct dollar-for-dollar ROI analysis with executive action badges (`⚡ INTERVENTION RECOMMENDED` vs `🛡️ ABSORB OPERATIONAL RISK`).

---

## 📊 Analytics Modules

| Module | Core Capabilities |
| :--- | :--- |
| **1. Single Order Risk Analyzer** | Real-time single order simulation, timeline projection, SHAP waterfall attribution, and financial intervention ROI calculator. |
| **2. Enterprise Bulk Batch Engine** | Drag-and-drop CSV/Excel processor for thousands of shipments, country-level geospatial risk map, portfolio KPI cards, and formatted Excel report generation (`xlsxwriter`). |
| **3. Model Architecture & Governance** | Technical specifications (100 Trees, Max Depth 20, StandardScaler), global feature importance, and model limitation documentation. |
| **4. Active ERP Data Dictionary** | Live feature schema mapping corporate SCM ERP dimensions to active model inputs. |

---

## 🧠 Machine Learning & Feature Selection Pipeline

* **Source Dataset**: DataCo Smart Supply Chain Dataset (180,519 records).
* **Model Engine**: Scikit-Learn Random Forest Classifier (100 Trees, `n_jobs=-1`).
* **Validation AUC**: **71.9%** | **Test Accuracy**: **66.6%** | **F1-Score**: **66.3%**.

### Dimensionality Pruning (239 → 4 Features)
One-hot encoding expanded categorical columns to 239 features, introducing high inference latency and overfitting. A **two-stage pruning pipeline** was applied:
1. **Variance Thresholding**: Pruned zero and near-zero variance features ($< 0.01$).
2. **SelectFromModel (Gini Importance)**: Retained only features exceeding mean Gini importance.

This isolated the **4 dominant predictive drivers**:
1. `Sales` — Total order revenue value.
2. `Order_Profit_Per_Order` — Base profit margin before penalty.
3. `Days_Scheduled` — Contractual SLA transit days.
4. `Shipping_Type_TRANSFER` — Payment hold flag correlating with warehouse processing delays.

---

## 🛠️ Technology Stack

| Domain | Technology Stack |
| :--- | :--- |
| **Backend & API** | FastAPI, Uvicorn, Pydantic, Python 3.11+ |
| **Machine Learning** | Scikit-Learn, SHAP, Joblib, NumPy, Pandas |
| **Frontend & UI** | Pure Vanilla HTML5, CSS3 Glassmorphism System, ES6+ JavaScript |
| **Visualizations** | Apache ECharts 5.5, Plotly.js, SVG Optical Refraction Filters |
| **Reporting & Export** | XlsxWriter (Formatted Enterprise Excel `.xlsx` generation) |
| **Deployment** | Docker, Render.com, Hugging Face Spaces |

---

## 🚀 Local Installation & Quickstart

### Prerequisites
* Python 3.11 or higher
* Git

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/AnshulSilhare/ai-dataco-supply-chain.git
cd ai-dataco-supply-chain

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the application
python main.py
```

Open your browser and navigate to **`http://localhost:10000`** to view the live dashboard.

---

## 📁 Repository Structure

```
📦 ai-dataco-supply-chain
│
├── 📂 static/
│   ├── 📂 css/
│   │   └── styles.css                   # Glassmorphic CSS design system & liquid physics
│   ├── 📂 js/
│   │   └── app.js                       # Frontend SPA controller & ECharts visualization
│   ├── 📄 index.html                    # Single-page application HTML5 interface
│   └── 📄 favicon.jpg                   # Application icon
│
├── 📂 notebooks/
│   ├── Model_Training_Dataco.ipynb      # EDA, feature selection pipeline, and model training
│   └── index.html                       # HTML export of training notebook
│
├── 📄 main.py                           # High-performance FastAPI ASGI backend
├── 📄 Dockerfile                        # Production container build definition
├── 📄 requirements.txt                  # Python dependencies
├── 📄 dataco_rf_model.joblib            # Trained Random Forest model (4-feature core)
├── 📄 dataco_scaler.joblib              # Fitted StandardScaler
├── 📄 dataco_columns.joblib             # Feature alignment metadata
├── 📄 sample_template.csv               # Sample template for bulk batch testing
└── 📄 README.md                         # Project documentation
```

---

## 🤝 Connect & Collaborate

I am actively open to opportunities in **Business Analytics**, **Supply Chain Intelligence**, and **Machine Learning Engineering**.

* **LinkedIn**: [linkedin.com/in/anshul-silhare](https://www.linkedin.com/in/anshul-silhare)
* **Portfolio**: [AnshulSilhare.github.io](https://anshulsilhare.github.io/)
* **Email**: [Contact via LinkedIn](https://www.linkedin.com/in/anshul-silhare)

---

<div align="center">
⭐ <em>Star this repository if you found it insightful!</em>
</div>
