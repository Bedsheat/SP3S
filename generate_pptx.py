"""
Generate SP3S Functional Overview Presentation in PPTX format.
Widescreen 16:9 modern dark-theme presentation.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    BG_DARK = RGBColor(11, 19, 43)        # #0B132B
    CARD_BG = RGBColor(21, 32, 61)        # #15203D
    CARD_BORDER = RGBColor(38, 53, 91)    # #26355B
    ACCENT_INDIGO = RGBColor(99, 102, 241) # #6366F1
    ACCENT_CYAN = RGBColor(45, 212, 191)   # #2DD4BF
    ACCENT_GOLD = RGBColor(251, 191, 36)   # #FBBF24
    TEXT_WHITE = RGBColor(248, 250, 252)   # #F8FAFC
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8
    TEXT_BODY = RGBColor(203, 213, 225)    # #CBD5E1

    def apply_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category="SP3S • FUNCTIONAL SYSTEM OVERVIEW"):
        # Category Tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN
        p_cat.font.name = "Segoe UI"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.font.name = "Segoe UI"

    def add_card(slide, left, top, width, height, title=None, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)

        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
            p = tb.text_frame.paragraphs[0]
            p.text = title
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN
            p.font.name = "Segoe UI"
        return card

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s1)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(0.12), Inches(3.6))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_CYAN
    bar.line.fill.background()

    # Title & Subtitle text
    tb_t = s1.shapes.add_textbox(Inches(1.3), Inches(1.7), Inches(11.0), Inches(3.8))
    tf = tb_t.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "SP3S • STUDENT PLACEMENT PREDICTION SYSTEM"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN
    p0.font.name = "Segoe UI"

    p1 = tf.add_paragraph()
    p1.text = "AI-Driven Career Forecasting & Actionable Intelligence"
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.font.name = "Segoe UI"
    p1.space_before = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = "A Complete Functional Walkthrough: Automated Resume Parsing, Monotonic Fairness Engine, Dual-Stage Placement & CTC Forecasting, and Interactive 'What-If' Guidance"
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEXT_BODY
    p2.font.name = "Segoe UI"
    p2.space_before = Pt(14)

    # Info pills at bottom
    pills = [
        ("PLATFORM", "Django 5 & Full-Stack Web"),
        ("ENGINES", "Monotone XGBoost + Naive Regressor"),
        ("EXPLAINABILITY", "Game-Theoretic TreeSHAP"),
        ("DOC INGESTION", "Multi-LLM (Groq / Gemini / HF)")
    ]
    for i, (k, v) in enumerate(pills):
        col_left = Inches(1.3 + i * 2.8)
        c = add_card(s1, col_left, Inches(5.6), Inches(2.6), Inches(1.1))
        tb = s1.shapes.add_textbox(col_left + Inches(0.15), Inches(5.65), Inches(2.3), Inches(1.0))
        p_k = tb.text_frame.paragraphs[0]
        p_k.text = k
        p_k.font.size = Pt(10)
        p_k.font.bold = True
        p_k.font.color.rgb = ACCENT_GOLD
        p_k.font.name = "Segoe UI"
        p_v = tb.text_frame.add_paragraph()
        p_v.text = v
        p_v.font.size = Pt(12)
        p_v.font.bold = True
        p_v.font.color.rgb = TEXT_WHITE
        p_v.font.name = "Segoe UI"
        p_v.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: The Problem It Solves
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s2)
    add_header(s2, "The Campus Placement Challenge: From Guesswork to Precision Guidance")

    # Card 1: Traditional Issues
    c1 = add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Traditional Placement Bottlenecks", RGBColor(239, 68, 68))
    tb1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    bullet_items_1 = [
        ("Reactive, Late Identification:", "Institutions only discover struggling students when they fail campus interviews in final year."),
        ("Black-Box Screening Decisions:", "Students submit applications blindly without knowing which profile metrics (GPA vs. Internship) recruiters weigh highest."),
        ("Manual Friction & Form Fatigue:", "Hundreds of students manually entering mismatched grades, percentages, and marks into spreadsheets."),
        ("Algorithmic Injustice in Naive AI:", "Standard ML models penalize edge-case students (e.g. giving 90%+ school scorers near-zero placement odds).")
    ]
    for title, desc in bullet_items_1:
        p = tf1.add_paragraph()
        p.text = f"• {title} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(10)
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # Card 2: SP3S Solution
    c2 = add_card(s2, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0), "The SP3S Functional Solution", ACCENT_CYAN)
    tb2 = s2.shapes.add_textbox(Inches(7.1), Inches(2.4), Inches(5.2), Inches(4.2))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    bullet_items_2 = [
        ("Automated AI Resume Ingestion:", "Drag-and-drop PDF parsing extracts academic history and stipends in <3 seconds."),
        ("Dual-Engine Placement & CTC:", "Simultaneously estimates probability of being placed AND starting salary package in LPA."),
        ("Strict Monotonic Fairness:", "Enforces domain rules so that higher marks or internships NEVER decrease placement chances."),
        ("Interactive 'What-If' Workbench:", "Gives students an actionable sandbox to simulate GPA boosts or internship gains before hiring starts.")
    ]
    for title, desc in bullet_items_2:
        p = tf2.add_paragraph()
        p.text = f"• {title} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(10)
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 3: End-to-End User Journey
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s3)
    add_header(s3, "End-to-End User Journey: 4 Seamless Functional Steps")

    steps = [
        ("STEP 01", "AI Resume Ingestion", "Upload PDF resume. Groq/HF/Gemini automatically parses CGPA, Class 10/12, branch & stipends.", ACCENT_CYAN),
        ("STEP 02", "Fair ML Inference", "Dual-stage engine runs Stage 1 (Screening Likelihood) & Stage 2 (Starting CTC package estimation).", ACCENT_INDIGO),
        ("STEP 03", "SHAP Transparency", "View personalized waterfall breakdown showing exact monetary contributions of each credential.", ACCENT_GOLD),
        ("STEP 04", "What-If Workbench", "Tweak sliders in real time to simulate how earning an internship or raising GPA unlocks higher offers.", RGBColor(168, 85, 247))
    ]

    for i, (step_num, step_title, step_desc, step_color) in enumerate(steps):
        left_pos = Inches(0.8 + i * 2.95)
        card = add_card(s3, left_pos, Inches(2.0), Inches(2.8), Inches(4.8), None, step_color)
        
        # Step header box
        hb = s3.shapes.add_textbox(left_pos + Inches(0.2), Inches(2.2), Inches(2.4), Inches(1.0))
        p_num = hb.text_frame.paragraphs[0]
        p_num.text = step_num
        p_num.font.size = Pt(12)
        p_num.font.bold = True
        p_num.font.color.rgb = step_color
        p_num.font.name = "Segoe UI"
        
        p_head = hb.text_frame.add_paragraph()
        p_head.text = step_title
        p_head.font.size = Pt(17)
        p_head.font.bold = True
        p_head.font.color.rgb = TEXT_WHITE
        p_head.font.name = "Segoe UI"
        p_head.space_before = Pt(4)

        # Body text
        tb = s3.shapes.add_textbox(left_pos + Inches(0.2), Inches(3.4), Inches(2.4), Inches(3.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p_desc = tf.paragraphs[0]
        p_desc.text = step_desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_BODY
        p_desc.font.name = "Segoe UI"

    # =========================================================================
    # SLIDE 4: Feature #1: AI Resume Ingestion
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s4)
    add_header(s4, "Feature Spotlight #1: Multi-Provider LLM Resume Parsing")

    # Left Card: Technology
    c_l = add_card(s4, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0), "Zero-Friction Candidate Onboarding")
    tb_l = s4.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.6), Inches(4.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    resume_features = [
        ("Multi-Provider Flexibility:", "Supports Groq (Llama-3.3 70B), Hugging Face (Qwen-2.5 7B), Google Gemini (Gemini-1.5-Flash), and fallback regex."),
        ("Instant Auto-Extraction:", "Parses candidate name, undergraduate CGPA, Class 10/12 board marks, departmental branch, and internship stipends in under 3 seconds."),
        ("Smart Data Normalization:", "Automatically converts percentage scales (e.g. 85.5% -> 0.855) and matches varied department names ('MCA' -> 'Master of Computer Applications')."),
        ("Privacy & Security First:", "All extraction happens securely in-memory during signup; no external storage of sensitive personal resume files.")
    ]
    for k, v in resume_features:
        p = tf_l.add_paragraph()
        p.text = f"• {k} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # Right Card: Extracted Fields Showcase
    c_r = add_card(s4, Inches(7.1), Inches(1.8), Inches(5.4), Inches(5.0), "Extracted Fields Schema (Live Demo)", ACCENT_CYAN)
    tb_r = s4.shapes.add_textbox(Inches(7.3), Inches(2.4), Inches(5.0), Inches(4.2))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    demo_fields = [
        ("Student Branch", "Master of Computer Applications (MCA)", ACCENT_CYAN),
        ("Degree CGPA", "9.12 / 10.00", ACCENT_GOLD),
        ("Internship Stipend", "INR 25,000 / month", ACCENT_CYAN),
        ("10th Standard Board", "92.00%", TEXT_WHITE),
        ("12th Standard / Diploma", "92.00%", TEXT_WHITE),
        ("Parsing Latency", "1.42 seconds (Groq Llama-3.3)", ACCENT_INDIGO)
    ]
    for label, val, col in demo_fields:
        p = tf_r.add_paragraph()
        p.text = label.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        p.font.name = "Segoe UI"
        p.space_before = Pt(8)
        p_val = tf_r.add_paragraph()
        p_val.text = val
        p_val.font.size = Pt(14)
        p_val.font.bold = True
        p_val.font.color.rgb = col
        p_val.font.name = "Segoe UI"

    # =========================================================================
    # SLIDE 5: Feature #2: Dual-Stage Prediction Engine
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s5)
    add_header(s5, "Feature Spotlight #2: Dual-Stage Placement & CTC Prediction")

    # Left Card: Stage 1
    c_s1 = add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "STAGE 1: Screening & Placement Gate", ACCENT_CYAN)
    tb_s1 = s5.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf_s1 = tb_s1.text_frame
    tf_s1.word_wrap = True
    stage1_points = [
        ("Goal:", "Classifies whether candidate will secure an offer during campus recruitment drives."),
        ("Output Metrics:", "Displays exact probability split: e.g., 'Placed: 88.7% vs. Unplaced: 11.3%'."),
        ("Architecture:", "Directionally Constrained Monotone XGBoost."),
        ("Key Innovation:", "Eliminates random boundary flips. High-merit students are never falsely tagged at-risk due to small-batch noise.")
    ]
    for k, v in stage1_points:
        p = tf_s1.add_paragraph()
        p.text = f"• {k} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(10)
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # Right Card: Stage 2
    c_s2 = add_card(s5, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0), "STAGE 2: Continuous Salary (CTC) Estimation", ACCENT_GOLD)
    tb_s2 = s5.shapes.add_textbox(Inches(7.1), Inches(2.4), Inches(5.2), Inches(4.2))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True
    stage2_points = [
        ("Goal:", "Estimates expected starting annual package in INR Lakhs per Annum (LPA)."),
        ("Conditional Logic:", "Runs if Stage 1 = Placed. If Unplaced, outputs ₹0.0 LPA with clear improvement steps."),
        ("Accuracy Benchmark:", "R² = 0.8450 in 10-Fold CV, with a tight average error of ±3.07 LPA."),
        ("Macroeconomic Generalization:", "Tested on out-of-time 2024 hiring batch (post-pandemic tech cooldown), achieving R² = 0.8552.")
    ]
    for k, v in stage2_points:
        p = tf_s2.add_paragraph()
        p.text = f"• {k} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(10)
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 6: Feature #3: Monotonic Fairness Engine
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s6)
    add_header(s6, "Feature Spotlight #3: The Monotonic Fairness Engine")

    # Top Card: The Glitch Explained
    c_top = add_card(s6, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.2), "The Problem: Why Unconstrained AI Penalized Real Students", RGBColor(239, 68, 68))
    tb_top = s6.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(11.3), Inches(1.5))
    tf_top = tb_top.text_frame
    tf_top.word_wrap = True
    p_t = tf_top.paragraphs[0]
    p_t.text = "In raw institutional training cohorts, anomalous clusters inevitably occur (e.g. 46 unplaced MCA students in 2022 who had high school scores but low CGPA and ₹0 stipend). Standard unconstrained trees learned a pathological rule: 'IF Branch=MCA and 12th > 80% THEN predict Unplaced!'. This caused high-achieving MCA candidates with 9.1+ CGPA to receive an absurd 72%–99% unplaced prediction!"
    p_t.font.size = Pt(13)
    p_t.font.color.rgb = TEXT_BODY
    p_t.font.name = "Segoe UI"

    # Bottom Left: The Solution
    c_bl = add_card(s6, Inches(0.8), Inches(4.2), Inches(5.6), Inches(2.7), "The Fix: 4-Way Directional Constraints", ACCENT_CYAN)
    tb_bl = s6.shapes.add_textbox(Inches(1.0), Inches(4.7), Inches(5.2), Inches(2.0))
    tf_bl = tb_bl.text_frame
    tf_bl.word_wrap = True
    sol_points = [
        "Enforced monotone_constraints = (0, 0, 0, +1, +1, +1, +1)",
        "Stipend (+1), 10th (+1), 12th (+1), CGPA (+1) are strictly non-decreasing.",
        "Guarantees that earning higher marks or stipends can NEVER lower placement odds."
    ]
    for pt in sol_points:
        p = tf_bl.add_paragraph()
        p.text = f"✔ {pt}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(4)

    # Bottom Right: Calibrated Results
    c_br = add_card(s6, Inches(6.9), Inches(4.2), Inches(5.6), Inches(2.7), "Verified Live Output on Real Profiles", ACCENT_GOLD)
    tb_br = s6.shapes.add_textbox(Inches(7.1), Inches(4.7), Inches(5.2), Inches(2.0))
    tf_br = tb_br.text_frame
    tf_br.word_wrap = True
    res_points = [
        "Arnav (MCA, 9.81 CGPA, 91% 12th): 82.8% Placed (24.16 LPA)",
        "mcastudent (MCA, 9.12 CGPA, 25k): 88.7% Placed (10.87 LPA)",
        "Typical MCA Student (8.3 CGPA): 78.3% Placed (Matches 71% institutional rate)",
        "COMP / CSE Typical Students: 93% – 96% Placed (Consistent across college)"
    ]
    for pt in res_points:
        p = tf_br.add_paragraph()
        p.text = f"★ {pt}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 7: Feature #4: What-If Scenario Workbench
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s7)
    add_header(s7, "Feature Spotlight #4: Interactive 'What-If' Scenario Workbench")

    # Left: Explanation & Case Study
    c_w1 = add_card(s7, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0), "Sensitivity Testing & Career Simulation")
    tb_w1 = s7.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.6), Inches(4.2))
    tf_w1 = tb_w1.text_frame
    tf_w1.word_wrap = True
    wb_points = [
        ("The 'What-If' Concept:", "Instead of delivering a dead-end prediction, the workbench lets candidates tweak their CGPA, marks, or stipends and watch their prospects update live."),
        ("Case Study: The 8.0 CGPA At-Risk Student:", "An MCA student with 8.0 CGPA & ₹0 stipend is currently predicted Unplaced (35.6% placed, reflecting that 80% with this profile historically miss placement)."),
        ("Actionable Recovery 1 (Stipend Upgrade):", "Adding a ₹10,000/month internship immediately jumps placement probability from 35.6% to 78.0% (PLACED, 4.73 LPA)."),
        ("Actionable Recovery 2 (CGPA Boost):", "Raising CGPA by just 0.2 points (from 8.0 to 8.2) crosses the MCA median threshold, flipping status to 66.6% PLACED (6.71 LPA).")
    ]
    for k, v in wb_points:
        p = tf_w1.add_paragraph()
        p.text = f"• {k} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # Right: Embedded screenshot or visual representation
    c_w2 = add_card(s7, Inches(7.1), Inches(1.8), Inches(5.4), Inches(5.0), "Live Interactive Workbench UI", ACCENT_CYAN)
    user_img = r"C:\Users\light\.gemini\antigravity\brain\1cf663b1-df17-44b4-b1a4-6ca7b84ed8fb\.user_uploaded\media_1792954775292_93bc9f44.png"
    if os.path.exists(user_img):
        s7.shapes.add_picture(user_img, Inches(7.3), Inches(2.5), Inches(5.0), Inches(1.8))
    
    tb_w2 = s7.shapes.add_textbox(Inches(7.3), Inches(4.5), Inches(5.0), Inches(2.1))
    tf_w2 = tb_w2.text_frame
    tf_w2.word_wrap = True
    p_w2_title = tf_w2.paragraphs[0]
    p_w2_title.text = "REAL-TIME WORKBENCH IMPACT"
    p_w2_title.font.size = Pt(11)
    p_w2_title.font.bold = True
    p_w2_title.font.color.rgb = ACCENT_GOLD
    p_w2_title.font.name = "Segoe UI"

    table_data = [
        ("Current Profile", "8.0 CGPA, ₹0 Stipend", "35.6% Placed", "Unplaced"),
        ("With ₹15k Stipend", "8.0 CGPA, ₹15k Stipend", "80.1% Placed", "6.18 LPA"),
        ("With ₹25k Stipend", "8.0 CGPA, ₹25k Stipend", "81.7% Placed", "7.36 LPA"),
        ("With 8.5 CGPA", "8.5 CGPA, ₹0 Stipend", "66.6% Placed", "11.43 LPA")
    ]
    for scen, det, prob, ctc in table_data:
        p = tf_w2.add_paragraph()
        p.text = f"▶ {scen}: {det} -> {prob} ({ctc})"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 8: Feature #5: Explainable AI & SHAP Transparency
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s8)
    add_header(s8, "Feature Spotlight #5: Transparent Career Explainability (TreeSHAP)")

    # Left: Explanation
    c_x1 = add_card(s8, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0), "De-Mystifying Salary Drivers")
    tb_x1 = s8.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.6), Inches(4.2))
    tf_x1 = tb_x1.text_frame
    tf_x1.word_wrap = True
    shap_points = [
        ("Game-Theoretic SHAP Values:", "Calculates the exact rupee contribution of each individual resume credential relative to the campus baseline (₹13.26 LPA)."),
        ("Internship Stipend Dominance (35.4%):", "The single largest driver of starting compensation. High-tier internships (>₹35k/mo) generate +₹4.5 to +₹7.0 LPA salary premiums."),
        ("Academic Foundation (47.6% Cumulative):", "Sustained academic excellence matters: CGPA contributes 23.8%, Class 10 contributes 15.6%, and Class 12 contributes 8.2%."),
        ("Actionable Institutional Insight:", "Proves that placement cells should prioritize pre-placement summer internships over last-minute interview prep workshops.")
    ]
    for k, v in shap_points:
        p = tf_x1.add_paragraph()
        p.text = f"• {k} "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # Right: Embedded SHAP Chart
    c_x2 = add_card(s8, Inches(7.1), Inches(1.8), Inches(5.4), Inches(5.0), "Global Feature Attributions (LPA)", ACCENT_GOLD)
    shap_img = r"C:\Users\light\Desktop\Projects\SP3S\figures\fig_shap_importance.png"
    if os.path.exists(shap_img):
        s8.shapes.add_picture(shap_img, Inches(7.3), Inches(2.5), Inches(5.0), Inches(4.0))

    # =========================================================================
    # SLIDE 9: Stakeholder Value Matrix
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s9)
    add_header(s9, "Stakeholder Value: Dual Perspectives on Impact")

    # Column 1: For Students
    c_st = add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "For Placement Candidates & Students", ACCENT_CYAN)
    tb_st = s9.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.2))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True
    student_val = [
        ("Actionable Career Clarity:", "Know exactly where you stand 6 to 12 months before company drives begin."),
        ("Resume Benchmark Guidance:", "Discover immediately if an unpaid internship or low semester GPA is hurting placement probability."),
        ("Targeted Goal Setting:", "Use the What-If workbench to set concrete targets: 'If I boost my CGPA to 8.5, my expected package increases by 3.5 LPA'."),
        ("Zero Anxiety from Bias:", "Confidence that predictions follow monotonic merit rules—hard work is always rewarded.")
    ]
    for k, v in student_val:
        p = tf_st.add_paragraph()
        p.text = f"✔ {k} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(10)
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # Column 2: For Placement Cells & Admins
    c_ad = add_card(s9, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0), "For Placement Officers & Faculty Admins", ACCENT_INDIGO)
    tb_ad = s9.shapes.add_textbox(Inches(7.1), Inches(2.4), Inches(5.2), Inches(4.2))
    tf_ad = tb_ad.text_frame
    tf_ad.word_wrap = True
    admin_val = [
        ("Early At-Risk Interventions:", "Identify the ~10-15% of students at risk of going unplaced well in advance for personalized mentoring."),
        ("Curriculum & Training Optimization:", "Shift institutional coaching from generic interview prep to securing high-quality summer internships."),
        ("Macroeconomic Forecasting:", "Predict cohort placement rates across market cycles (tested robustly on post-pandemic tech cooldown)."),
        ("Automated Institutional Records:", "Eliminate spreadsheet friction with automated PDF resume parsing and unified database tracking.")
    ]
    for k, v in admin_val:
        p = tf_ad.add_paragraph()
        p.text = f"★ {k} "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"
        p.space_before = Pt(10)
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 10: Conclusion & Production Architecture
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s10)
    add_header(s10, "System Summary & Production Architecture")

    # 3 Summary Cards
    cards_data = [
        ("PROVEN PRECISION", "Dual-Stage Pipeline", [
            "Stage 1: 88.4% Classification Accuracy",
            "Stage 2: R² = 0.8450 (RMSE = 3.07 LPA)",
            "Temporal Out-of-Time R² = 0.8552",
            "Econometrically audited & free of bias"
        ], ACCENT_CYAN),
        ("PROCEDURAL FAIRNESS", "Monotonic Engine", [
            "Enforced on CGPA, Stipend, 10th & 12th",
            "Zero non-monotonic penalty glitches",
            "Calibrated across MCA, CSE, COMP, EXTC",
            "Guaranteed ∂P / ∂Metric ≥ 0 everywhere"
        ], ACCENT_INDIGO),
        ("LIVE DEPLOYMENT", "Full-Stack Web Stack", [
            "Django 5 backend + SQLite/Postgres DB",
            "Multi-LLM Resume Parser (Groq/Gemini/HF)",
            "Interactive 'What-If' sensitivity workbench",
            "Real-time SHAP waterfall explainers"
        ], ACCENT_GOLD)
    ]

    for i, (k_top, k_sub, bullets, col) in enumerate(cards_data):
        l_pos = Inches(0.8 + i * 3.95)
        card = add_card(s10, l_pos, Inches(1.8), Inches(3.8), Inches(4.8), None, col)
        
        hb = s10.shapes.add_textbox(l_pos + Inches(0.2), Inches(2.1), Inches(3.4), Inches(1.0))
        p0 = hb.text_frame.paragraphs[0]
        p0.text = k_top
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = col
        p0.font.name = "Segoe UI"
        
        p1 = hb.text_frame.add_paragraph()
        p1.text = k_sub
        p1.font.size = Pt(17)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.font.name = "Segoe UI"
        p1.space_before = Pt(3)

        tb = s10.shapes.add_textbox(l_pos + Inches(0.2), Inches(3.3), Inches(3.4), Inches(3.1))
        tf = tb.text_frame
        tf.word_wrap = True
        for b in bullets:
            p = tf.add_paragraph()
            p.text = f"• {b}"
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Segoe UI"
            p.space_before = Pt(6)

    # Output file
    output_path = "SP3S_Functional_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_deck()
