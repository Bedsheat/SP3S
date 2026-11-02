# SP3S: Student Placement & CTC Prediction System

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Monotone-orange.svg)](https://xgboost.readthedocs.io/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainable%20AI-red.svg)](https://github.com/shap/shap)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

An end-to-end, AI-powered career forecasting and placement intelligence platform developed at **Sardar Patel Institute of Technology (SPIT), Mumbai**. SP3S combines automated multi-LLM resume extraction, sample selection bias mitigation via econometric modeling, monotonic machine learning classifiers, and game-theoretic explainability (TreeSHAP) into an intuitive full-stack web application.

---

## 🌟 Key Highlights & Capabilities

- 📄 **Multi-Engine PDF & LLM Resume Intelligence**
  - Robust multi-engine document ingestion using `PyMuPDF`, `pdfplumber`, and `pypdf`.
  - Zero-shot structured feature extraction via **Groq (Llama 3.3 70B / 3.1 8B)**, **Hugging Face Serverless Inference**, or **Google Gemini**, with local regex/heuristic fallback.
  - Automatically identifies candidate branches (`COMP`, `CSE`, `EXTC`, `MCA`), CGPA, 10th/12th percentages, and internship stipends.

- ⚖️ **Monotonic Fairness Engine (Classification)**
  - Mitigates sample selection bias and edge-case anomalies with a **Monotone XGBoost Classifier**.
  - Guaranteed monotonically non-decreasing placement probability with respect to academic metrics, eliminating algorithmic injustice where high academic scorers are artificially penalized.

- 💰 **Calibrated Two-Step Econometric Salary Forecasting (Regression)**
  - Natural Population Probit Selection model paired with a high-performance XGBoost CTC regressor ($R^2 = 0.8450$, Temporal $R^2 = 0.8552$, $\text{RMSE} = 3.07\text{ LPA}$).
  - Mitigates Heckman selection bias present in non-random campus interview selection data.

- 🔍 **Explainable AI (XAI) & Counterfactual Guidance**
  - Integrated **TreeSHAP** attribution breakdown explaining exactly why a student received a particular placement probability and salary projection.
  - Interactive **"What-If" counterfactual simulator** allowing students to simulate how improving their CGPA or securing a higher internship stipend directly impacts placement odds and target CTC.

- 🖥️ **Modern Full-Stack Web Platform**
  - Built with Django 5, dynamic dashboards, student authentication, PDF report generation, and presentation export utilities.

---

## 🏛️ System Architecture

```text
       [ Candidate Resume (PDF) ]
                   │
                   ▼
       [ Multi-Engine Parser ]
       (PyMuPDF / pdfplumber)
                   │
                   ▼
  [ LLM Extraction & Validation Pipeline ]
  (Groq Llama 3.3 / Gemini / Hugging Face)
                   │
         Extracted Feature Vector
  [ Branch, 10th%, 12th%, CGPA, Stipend ]
                   │
     ┌─────────────┴─────────────┐
     ▼                           ▼
[ Monotone XGBoost ]     [ Probit Selection & ]
[ Placement Classifier ] [ Heckman Regressor  ]
(Placement Probability)   (Estimated CTC / LPA)
     │                           │
     └─────────────┬─────────────┘
                   ▼
      [ TreeSHAP Explainability ]
                   │
                   ▼
     [ Interactive Web Dashboard ]
   • Placement Odds & Salary Range
   • Feature Importance Waterfall
   • Interactive "What-If" Analysis
   • Automated PDF / PPTX Reports
```

---

## 📁 Repository Structure

```text
SP3S/
├── sp3s_web/                             # Full-Stack Django Application
│   ├── manage.py                         # Django management script
│   ├── sp3s_web/                         # Project settings & URL routing
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── placement_app/                    # Core placement intelligence app
│       ├── resume_parser.py              # Multi-engine PDF & LLM extraction
│       ├── views.py                      # Dashboard, prediction & counterfactual views
│       ├── models.py                     # Student profile & prediction models
│       ├── urls.py                       # App route definitions
│       └── templates/placement_app/      # Responsive UI templates
│           ├── base.html
│           ├── dashboard.html
│           ├── login.html
│           └── signup.html
│
├── figures/                              # Model evaluation & benchmark plots
│   ├── fig_kfold_generalization.png
│   ├── fig_probit_hazard_curve.png
│   ├── fig_regressor_benchmarks.png
│   ├── fig_shap_importance.png
│   └── fig_stipend_progression.png
│
├── final_classifier.joblib               # Calibrated Monotone XGBoost Placement Classifier
├── final_probit_selection.joblib         # Probit Selection Model artifact
├── final_regressor_heckman.joblib        # Heckman/Naive XGBoost CTC Regressor
├── final_encoder.joblib                  # Categorical one-hot branch encoder
├── final_augmented_dataset.csv           # Augmented placement dataset
├── processed_data.csv                    # Cleaned feature dataset
│
├── predict.py                            # Standalone CLI prediction pipeline
├── retrain_calibrated_classifier.py      # Classifier calibration & retraining script
├── verify_profiles.py                    # Verification script for candidate edge-cases
├── generate_pdf_report.py                # Automated institutional PDF report generator
├── generate_pptx.py                      # Automated executive PPTX presentation generator
│
├── requirements.txt                      # Python environment dependencies
├── .env.example                          # Environment configuration template
└── README.md                             # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11)
- Git

### 2. Clone Repository
```bash
git clone https://github.com/Bedsheat/SP3S.git
cd SP3S
```

### 3. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure API Keys
Copy `.env.example` to `.env` and supply your LLM inference API key(s):
```bash
cp .env.example .env
```
Edit `.env`:
```ini
# Recommended: Free & fast Llama 3.3 inference
GROQ_API_KEY=your_groq_api_key_here

# Optional: Hugging Face access token
HF_TOKEN=your_huggingface_token_here

# Optional: Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 💻 Usage

### A. Run CLI Placement Prediction
Evaluate student profiles directly from the command line:
```bash
python predict.py --branch CSE --cgpa 8.75 --tenth 89.5 --twelfth 87.0 --stipend 25000
```

### B. Launch the Web Application
Initialize the SQLite database and start the Django development server:
```bash
cd sp3s_web
python manage.py migrate
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser:
1. Register a student account or log in.
2. Upload a candidate resume (PDF) or input academic scores manually.
3. Review placement probability, projected CTC range, SHAP feature impact, and test "What-If" scenarios.

### C. Generate Technical Reports & Decks
```bash
# Generate the executive PowerPoint slide deck
python generate_pptx.py

# Generate technical PDF summary reports
python generate_pdf_report.py
```

---

## 📊 Model Performance & Benchmarks

| Model Component | Evaluation Metric | Result |
| :--- | :--- | :--- |
| **Monotone XGBoost Classifier** | Cross-Validation AUC-ROC | **0.912** |
| **Monotone XGBoost Classifier** | Classification Accuracy | **88.4%** |
| **Naive XGBoost Regressor** | $R^2$ Score | **0.8450** |
| **Naive XGBoost Regressor** | Temporal Holdout $R^2$ | **0.8552** |
| **Naive XGBoost Regressor** | Root Mean Squared Error (RMSE) | **3.07 LPA** |
| **Selection Model** | Probit Bias Significance ($\rho$) | $p < 0.01$ |

---

## 📝 Research & Citations

This repository accompanies the research publication:
> **Mitigating Sample Selection Bias in Campus Placement Salary Prediction: A Calibrated Heckman Two-Step Selection and Explainable Machine Learning Framework**  
> *Wasifah Parkar, Paras Sachdeva, Arnav Rai Viksit*  
> Department of Computer Engineering, Sardar Patel Institute of Technology (SPIT), Mumbai.

---

## 📄 License
This project is licensed under the MIT License.
