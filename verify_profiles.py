from predict import predict_student

users = [
    {"name": "Arnav (MCA, 9.81 CGPA, 0 stip)", "Branch": "MCA", "CGPA": 9.81, "Internship Stipend": 0, "10th Percentage": 93.8, "12th Percentage": 91.2},
    {"name": "sai_abhinav (MCA, 9.1 CGPA, 0 stip)", "Branch": "MCA", "CGPA": 9.1, "Internship Stipend": 0, "10th Percentage": 81.0, "12th Percentage": 92.0},
    {"name": "mcastudent (MCA, 9.12 CGPA, 25k)", "Branch": "MCA", "CGPA": 9.12, "Internship Stipend": 25000, "10th Percentage": 92.0, "12th Percentage": 92.0},
    {"name": "Wasifah (MCA, 9.34 CGPA, 0 stip)", "Branch": "MCA", "CGPA": 9.34, "Internship Stipend": 0, "10th Percentage": 88.0, "12th Percentage": 80.0},
    {"name": "MCA Typical (8.3 CGPA, 0 stip)", "Branch": "MCA", "CGPA": 8.3, "Internship Stipend": 0, "10th Percentage": 83.0, "12th Percentage": 73.0},
    {"name": "MCA Borderline (7.2 CGPA, 0 stip)", "Branch": "MCA", "CGPA": 7.2, "Internship Stipend": 0, "10th Percentage": 75.0, "12th Percentage": 68.0},
    {"name": "MCA At-Risk (6.4 CGPA, 0 stip)", "Branch": "MCA", "CGPA": 6.4, "Internship Stipend": 0, "10th Percentage": 70.0, "12th Percentage": 62.0},
    {"name": "testuser_audit (CSE, 9.1 CGPA, 50k)", "Branch": "CSE", "CGPA": 9.1, "Internship Stipend": 50000, "10th Percentage": 92.0, "12th Percentage": 90.0},
    {"name": "COMP Student (COMP, 8.1 CGPA)", "Branch": "COMP", "CGPA": 8.1, "Internship Stipend": 0, "10th Percentage": 92.0, "12th Percentage": 88.0},
    {"name": "EXTC Student (EXTC, 7.9 CGPA)", "Branch": "EXTC", "CGPA": 7.9, "Internship Stipend": 0, "10th Percentage": 90.0, "12th Percentage": 86.0},
]

print(f"{'Candidate':42s} | {'Status':8s} | {'Placed %':8s} | {'Unplaced %':10s} | {'Predicted CTC':14s}")
print("-" * 92)
for u in users:
    r = predict_student(u)
    pl = r['placement_probabilities (%)']['Placed (1)']
    un = r['placement_probabilities (%)']['Unplaced (0)']
    ctc = f"{r['predicted_ctc_lpa']:.2f} LPA" if r['placement_status'] == 'Placed' else "0.00 LPA"
    print(f"{u['name']:42s} | {r['placement_status']:8s} | {pl:6.1f}%  | {un:8.1f}%  | {ctc:14s}")
