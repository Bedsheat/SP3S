"""
Retrain and serialize calibrated Monotone XGBoost placement classifier
Enforcing directional monotonic constraints across all academic & compensation features:
  monotone_constraints = (0, 0, 0, 1, 1, 1, 1)
  - Branch_1 (CSE): 0
  - Branch_2 (EXTC): 0
  - Branch_3 (MCA): 0
  - Internship Stipend: +1 (monotonically non-decreasing)
  - 10th Percentage: +1 (monotonically non-decreasing)
  - 12th Percentage: +1 (monotonically non-decreasing)
  - CGPA: +1 (monotonically non-decreasing)
"""

import os
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

# Load dataset
df = pd.read_csv("processed_data.csv")

# Create branch indicators
df["Branch_1"] = (df["Branch"] == 1).astype(float)
df["Branch_2"] = (df["Branch"] == 2).astype(float)
df["Branch_3"] = (df["Branch"] == 3).astype(float)

features = [
    "Branch_1",
    "Branch_2",
    "Branch_3",
    "Internship Stipend",
    "10th Percentage",
    "12th Percentage",
    "CGPA"
]

X = df[features]
y = df["Placement Offer"]

# Monotonic constraints: (CSE=0, EXTC=0, MCA=0, Stipend=+1, 10th=+1, 12th=+1, CGPA=+1)
mono_constraints = (0, 0, 0, 1, 1, 1, 1)

# Evaluate 10-Fold CV metrics
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
aucs, accs, f1s = [], [], []

for train_idx, val_idx in cv.split(X, y):
    m = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        min_child_weight=2,
        subsample=0.9,
        colsample_bytree=0.9,
        monotone_constraints=mono_constraints,
        eval_metric="logloss",
        random_state=42
    )
    m.fit(X.iloc[train_idx], y.iloc[train_idx])
    preds_p = m.predict_proba(X.iloc[val_idx])[:, 1]
    preds_c = (preds_p >= 0.5).astype(int)
    aucs.append(roc_auc_score(y.iloc[val_idx], preds_p))
    accs.append(accuracy_score(y.iloc[val_idx], preds_c))
    f1s.append(f1_score(y.iloc[val_idx], preds_c))

print("=== 10-Fold Stratified Cross-Validation ===")
print(f"ROC-AUC:  {np.mean(aucs):.4f} +/- {np.std(aucs):.4f}")
print(f"Accuracy: {np.mean(accs):.4f} +/- {np.std(accs):.4f}")
print(f"F1-Score: {np.mean(f1s):.4f} +/- {np.std(f1s):.4f}")

# Train final production model on full dataset
final_clf = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    min_child_weight=2,
    subsample=0.9,
    colsample_bytree=0.9,
    monotone_constraints=mono_constraints,
    eval_metric="logloss",
    random_state=42
)
final_clf.fit(X, y)

# Save artifact
out_path = "final_classifier.joblib"
joblib.dump(final_clf, out_path)
print(f"\nSuccessfully serialized calibrated Monotone XGBoost classifier to: {out_path}")
