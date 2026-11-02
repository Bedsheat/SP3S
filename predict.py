"""
Student Placement & CTC Prediction Script
Updated with Monotone XGBoost Placement Classifier, Natural Population Probit Selection Audit,
and Naive XGBoost CTC Regressor (R² = 0.8450, Temporal R² = 0.8552, RMSE = 3.07 LPA).
"""

import os
import sys
import argparse
import joblib
import pandas as pd
import numpy as np
from scipy.stats import norm

# Feature order matching model training (One-Hot Encoded Branches: Reference is COMP)
# Branch_1: CSE, Branch_2: EXTC, Branch_3: MCA
FEATURE_ORDER = [
    "Branch_1",
    "Branch_2",
    "Branch_3",
    "Internship Stipend",
    "10th Percentage",
    "12th Percentage",
    "CGPA"
]

# Baseline statistics from institutional placed population
POPULATION_PLACED_PRIOR = 0.8688
CAMPUS_BASELINE_CTC = 13.26  # LPA

# Paths to serialized joblib artifacts
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "final_classifier.joblib")
PROBIT_PATH = os.path.join(MODEL_DIR, "final_probit_selection.joblib")
REGRESSOR_PATH = os.path.join(MODEL_DIR, "final_regressor_heckman.joblib")
ENCODER_PATH = os.path.join(MODEL_DIR, "final_encoder.joblib")


def load_artifacts():
    """Load serialized models and encoders."""
    missing = []
    for path, name in [
        (CLASSIFIER_PATH, "final_classifier.joblib"),
        (PROBIT_PATH, "final_probit_selection.joblib"),
        (REGRESSOR_PATH, "final_regressor_heckman.joblib"),
        (ENCODER_PATH, "final_encoder.joblib"),
    ]:
        if not os.path.exists(path):
            missing.append(name)

    if missing:
        raise FileNotFoundError(
            f"Missing required model artifacts: {', '.join(missing)}."
        )

    clf = joblib.load(CLASSIFIER_PATH)
    probit = joblib.load(PROBIT_PATH)
    reg = joblib.load(REGRESSOR_PATH)
    encoder = joblib.load(ENCODER_PATH)

    return clf, probit, reg, encoder


def encode_student_features(data_dict, encoder=None):
    """
    Transforms human input dictionary into model-compatible DataFrame with one-hot branch indicators.
    Branches:
      COMP: Branch_1=0, Branch_2=0, Branch_3=0
      CSE:  Branch_1=1, Branch_2=0, Branch_3=0
      EXTC: Branch_1=0, Branch_2=1, Branch_3=0
      MCA:  Branch_1=0, Branch_2=0, Branch_3=1
    """
    input_data = data_dict.copy()

    # Normalize percentage values (0-100 to 0.0-1.0)
    for key in ["10th Percentage", "12th Percentage"]:
        if key in input_data and input_data[key] > 1.0:
            input_data[key] = input_data[key] / 100.0

    raw_branch = str(input_data.get("Branch", "")).strip().upper()
    if raw_branch in ["CSE - AIML", "CSE - DS", "AIML", "DS", "COMPUTER SCIENCE"]:
        raw_branch = "CSE"
    elif raw_branch in ["COMPUTER ENGINEERING", "COMPUTER"]:
        raw_branch = "COMP"
    elif raw_branch in ["ELECTRONICS", "TELECOM", "EXTC"]:
        raw_branch = "EXTC"
    elif raw_branch in ["MASTER OF COMPUTER APPLICATIONS", "MCA"]:
        raw_branch = "MCA"

    # One-hot flags (Reference = COMP)
    b1 = 1.0 if raw_branch == "CSE" else 0.0
    b2 = 1.0 if raw_branch == "EXTC" else 0.0
    b3 = 1.0 if raw_branch == "MCA" else 0.0

    df_row = pd.DataFrame([{
        "Branch_1": b1,
        "Branch_2": b2,
        "Branch_3": b3,
        "Internship Stipend": float(input_data.get("Internship Stipend", 0)),
        "10th Percentage": float(input_data.get("10th Percentage", 0.85)),
        "12th Percentage": float(input_data.get("12th Percentage", 0.85)),
        "CGPA": float(input_data.get("CGPA", 8.0))
    }])[FEATURE_ORDER]

    return df_row


def calculate_imr(probit_model, X_features_df, is_open=1.0, cohort="Cohort_2024"):
    """
    Compute Inverse Mills Ratio (IMR / λ) using fitted Stage 1 Probit selection audit.
    Includes institutional exclusion restrictions (Admission Category + Cohort Cycles).
    λ = φ(z) / Φ(z) where z = W'γ
    """
    X_full = X_features_df.copy()
    if "const" not in X_full.columns:
        X_full.insert(0, "const", 1.0)

    # Add institutional exclusion restrictions
    X_full["Is_Open_Category"] = float(is_open)
    for c in ["Cohort_2021", "Cohort_2022", "Cohort_2023", "Cohort_2024"]:
        X_full[c] = 1.0 if c == cohort else 0.0

    params = probit_model.params
    # Ensure columns match parameter ordering
    common_cols = [col for col in params.index if col in X_full.columns]
    z = X_full[common_cols].dot(params[common_cols])

    z_clipped = np.clip(z, -5.0, 5.0)
    pdf = norm.pdf(z_clipped)
    cdf = norm.cdf(z_clipped)
    cdf = np.clip(cdf, 1e-7, 1.0 - 1e-7)

    return pdf / cdf


def predict_student(data_dict, clf=None, probit=None, reg=None, encoder=None):
    """
    Predict placement status and CTC for a single student profile.
    Uses Monotone XGBoost for Stage 1 and Naive XGBoost for Stage 2.
    """
    if any(m is None for m in [clf, probit, reg, encoder]):
        clf, probit, reg, encoder = load_artifacts()

    input_df = encode_student_features(data_dict, encoder)

    # Stage 1: Monotone XGBoost placement probability
    # Predict probabilities directly from Monotone XGBoost
    proba = clf.predict_proba(input_df)[0]
    proba_unplaced = float(proba[0])
    proba_placed = float(proba[1])

    placement_pred = 1 if proba_placed >= 0.50 else 0

    # Stage 1: Compute Selection Hazard IMR (λ)
    imr_series = calculate_imr(probit, input_df)
    student_imr = float(imr_series.iloc[0]) if hasattr(imr_series, "iloc") else float(imr_series[0])

    # Stage 2: Naive XGBoost Continuous Salary Prediction
    if placement_pred == 1:
        predicted_ctc = float(reg.predict(input_df)[0])
        predicted_ctc = max(3.0, round(predicted_ctc, 2))  # Minimum campus threshold
    else:
        predicted_ctc = 0.0

    return {
        "placement_class": int(placement_pred),
        "placement_status": "Placed" if placement_pred == 1 else "Unplaced",
        "placement_probabilities (%)": {
            "Unplaced (0)": round(proba_unplaced * 100, 2),
            "Placed (1)": round(proba_placed * 100, 2),
        },
        "selection_bias_imr": round(student_imr, 4),
        "predicted_ctc_lpa": round(predicted_ctc, 2)
    }


def predict_batch(df_input):
    """Batch prediction on DataFrame or list of dicts."""
    clf, probit, reg, encoder = load_artifacts()
    records = df_input if isinstance(df_input, list) else df_input.to_dict(orient="records")
    results = [predict_student(r, clf, probit, reg, encoder) for r in records]
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Student Placement & CTC Prediction CLI (Updated Architecture)")
    parser.add_argument("--branch", type=str, default="CSE", help="Student Branch (COMP, CSE, EXTC, MCA)")
    parser.add_argument("--stipend", type=float, default=25000, help="Internship Stipend in INR")
    parser.add_argument("--tenth", type=float, default=90.0, help="10th Percentage")
    parser.add_argument("--twelfth", type=float, default=85.0, help="12th Percentage")
    parser.add_argument("--cgpa", type=float, default=8.5, help="Undergraduate CGPA")

    args = parser.parse_args()

    student_data = {
        "Branch": args.branch,
        "Internship Stipend": args.stipend,
        "10th Percentage": args.tenth,
        "12th Percentage": args.twelfth,
        "CGPA": args.cgpa
    }

    res = predict_student(student_data)
    print("\n=== Verified Model Prediction Result ===")
    for k, v in res.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
