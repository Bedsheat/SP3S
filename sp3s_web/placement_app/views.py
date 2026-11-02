import os
import sys
import json
import logging
import shap
import pandas as pd
import numpy as np

from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings

from .models import UserProfile, BRANCH_CHOICES
from .resume_parser import extract_resume_data

logger = logging.getLogger(__name__)

# Ensure parent directory is in sys.path for predict.py
PARENT_DIR = str(Path(__file__).resolve().parent.parent.parent)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# Import model inference from predict.py
try:
    from predict import predict_student, load_artifacts, FEATURE_ORDER, calculate_imr, encode_student_features
    clf, probit, reg, encoder = load_artifacts()
    explainer = shap.TreeExplainer(reg)
    MODEL_LOADED = True
    logger.info("Model artifacts successfully reloaded in Django views!")
except Exception as e:
    logger.error(f"Error loading prediction model: {e}")
    MODEL_LOADED = False


@csrf_exempt
def parse_resume_api(request):
    """AJAX API endpoint to parse uploaded PDF resume via Groq, Hugging Face, Gemini, or Fallback Regex."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method is allowed.'}, status=405)

    if 'resume_pdf' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No resume file uploaded.'}, status=400)

    pdf_file = request.FILES['resume_pdf']
    if not pdf_file.name.lower().endswith('.pdf'):
        return JsonResponse({'success': False, 'error': 'File must be a PDF document.'}, status=400)

    api_key = request.POST.get('api_key') or request.headers.get('X-API-Key') or None
    provider = request.POST.get('provider', 'auto').strip()
    model = request.POST.get('model', '').strip() or None

    try:
        data, method, duration = extract_resume_data(pdf_file, api_key=api_key, provider=provider, model=model)
        return JsonResponse({
            'success': True,
            'data': data,
            'method': method,
            'duration': duration,
            'filename': pdf_file.name
        })
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def llm_status_api(request):
    """API endpoint returning available/configured LLM providers and server defaults."""
    groq_configured = bool(os.environ.get('GROQ_API_KEY'))
    hf_configured = bool(os.environ.get('HF_TOKEN') or os.environ.get('HUGGINGFACE_API_KEY') or os.environ.get('HUGGINGFACEHUB_API_TOKEN'))
    gemini_configured = bool(os.environ.get('GEMINI_API_KEY'))

    active_provider = "groq" if groq_configured else ("huggingface" if hf_configured else ("gemini" if gemini_configured else "regex"))

    return JsonResponse({
        'groq': {'configured': groq_configured, 'default_model': 'qwen/qwen3.8-27b'},
        'huggingface': {'configured': hf_configured, 'default_model': 'meta-llama/Llama-3.2-3B-Instruct'},
        'gemini': {'configured': gemini_configured, 'default_model': 'gemini-1.5-flash'},
        'active_provider': active_provider
    })


def signup_view(request):
    """User registration view with automatic PDF Resume LLM extraction and detail population."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_msg = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        branch = request.POST.get('branch', 'CSE')
        stipend = request.POST.get('stipend', '0')
        tenth = request.POST.get('tenth_percentage', '85')
        twelfth = request.POST.get('twelfth_percentage', '85')
        cgpa = request.POST.get('cgpa', '8.0')

        resume_file = request.FILES.get('resume_pdf')
        api_key = request.POST.get('api_key') or None
        provider = request.POST.get('provider', 'auto')

        # Extract details automatically from PDF resume on submission
        if resume_file and resume_file.name.lower().endswith('.pdf'):
            try:
                parsed_data, method, duration = extract_resume_data(resume_file, api_key=api_key, provider=provider)
                if parsed_data.get('branch'):
                    branch = parsed_data['branch']
                if parsed_data.get('stipend') is not None:
                    stipend = str(parsed_data['stipend'])
                if parsed_data.get('tenth_percentage') is not None:
                    tenth = str(parsed_data['tenth_percentage'])
                if parsed_data.get('twelfth_percentage') is not None:
                    twelfth = str(parsed_data['twelfth_percentage'])
                if parsed_data.get('cgpa') is not None:
                    cgpa = str(parsed_data['cgpa'])
                logger.info(f"Automatically populated profile details from resume via {method} in {duration}s")
            except Exception as e:
                logger.error(f"Resume extraction error on signup: {e}")

        # Validations
        if not username or not password:
            error_msg = "Username and password are required."
        elif password != confirm_password:
            error_msg = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error_msg = f"Username '{username}' is already taken."
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                profile = UserProfile.objects.create(
                    user=user,
                    branch=branch,
                    stipend=float(stipend or 0),
                    tenth_percentage=float(tenth or 85),
                    twelfth_percentage=float(twelfth or 85),
                    cgpa=float(cgpa or 8.0)
                )
                if resume_file:
                    profile.resume = resume_file
                    profile.save()

                login(request, user)
                return redirect('dashboard')
            except Exception as e:
                error_msg = f"Error creating account: {e}"

    return render(request, 'placement_app/signup.html', {
        'branches': BRANCH_CHOICES,
        'error': error_msg
    })


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_msg = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_msg = "Invalid username or password."

    return render(request, 'placement_app/login.html', {'error': error_msg})


def logout_view(request):
    """User logout view."""
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main Prediction Dashboard displaying placement status, predicted CTC, IMR, and SHAP breakdown."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    student_data = {
        "Branch": profile.branch,
        "Internship Stipend": profile.stipend,
        "10th Percentage": profile.tenth_percentage,
        "12th Percentage": profile.twelfth_percentage,
        "CGPA": profile.cgpa
    }

    prediction = None
    shap_breakdown = []
    base_value = 13.15
    placed_pct = 50.0
    unplaced_pct = 50.0

    if MODEL_LOADED:
        try:
            prediction = predict_student(student_data, clf, probit, reg, encoder)

            probs = prediction.get('placement_probabilities (%)', {})
            placed_pct = probs.get('Placed (1)', 50.0)
            unplaced_pct = probs.get('Unplaced (0)', 50.0)

            # Compute SHAP breakdown for placed prediction using updated Naive XGBoost model
            input_df = encode_student_features(student_data, encoder)
            imr_val = float(calculate_imr(probit, input_df)[0])

            user_shap = explainer(input_df)
            base_value = float(explainer.expected_value) if not hasattr(explainer.expected_value, '__len__') else float(explainer.expected_value[0])

            # SHAP features: Branch_1 (CSE), Branch_2 (EXTC), Branch_3 (MCA), Stipend, 10th %, 12th %, CGPA
            shap_vals = user_shap.values[0]
            # Aggregate branch SHAP impact based on candidate's branch
            b1_shap = float(shap_vals[0])
            b2_shap = float(shap_vals[1])
            b3_shap = float(shap_vals[2])

            if profile.branch == "CSE":
                branch_impact = b1_shap
            elif profile.branch == "EXTC":
                branch_impact = b2_shap
            elif profile.branch == "MCA":
                branch_impact = b3_shap
            else:
                # COMP (reference class)
                branch_impact = 0.0

            feature_display = [
                ("Department Specialization", f"{profile.branch}", "COMP Cohort Baseline", branch_impact),
                ("Internship Stipend", f"₹{int(profile.stipend):,}", "₹23,797 Placed Avg", float(shap_vals[3])),
                ("10th Percentage", f"{profile.tenth_percentage}%", "90.45% Placed Avg", float(shap_vals[4])),
                ("12th Percentage", f"{profile.twelfth_percentage}%", "85.98% Placed Avg", float(shap_vals[5])),
                ("Undergraduate CGPA", f"{profile.cgpa}", "8.09 Placed Avg", float(shap_vals[6])),
                ("Selection Hazard Diagnostic (λ)", f"{imr_val:.4f}", "0.2333 Mean Natural Hazard", 0.0),
            ]

            for fname, fval, avg_val, sval in feature_display:
                shap_breakdown.append({
                    "feature": fname,
                    "val": fval,
                    "avg": avg_val,
                    "impact": round(float(sval), 2),
                    "is_positive": sval >= 0
                })

        except Exception as e:
            logger.error(f"Inference error: {e}")

    return render(request, 'placement_app/dashboard.html', {
        'profile': profile,
        'student_data': student_data,
        'prediction': prediction,
        'placed_pct': placed_pct,
        'unplaced_pct': unplaced_pct,
        'shap_breakdown': shap_breakdown,
        'base_value': round(base_value, 2),
        'branches': BRANCH_CHOICES,
    })


@login_required
def upload_resume_view(request):
    """View to upload/update PDF resume on Dashboard and automatically extract & update student details."""
    if request.method == 'POST' and 'resume_pdf' in request.FILES:
        pdf_file = request.FILES['resume_pdf']
        if pdf_file.name.lower().endswith('.pdf'):
            try:
                profile = request.user.profile
                profile.resume = pdf_file
                
                api_key = request.POST.get('api_key') or None
                provider = request.POST.get('provider', 'auto')
                model = request.POST.get('model', '').strip() or None

                # Parse resume automatically using Groq / Hugging Face / Gemini / Regex
                parsed_data, method, duration = extract_resume_data(pdf_file, api_key=api_key, provider=provider, model=model)
                
                if parsed_data.get('branch'):
                    profile.branch = parsed_data['branch']
                if parsed_data.get('stipend') is not None:
                    profile.stipend = float(parsed_data['stipend'])
                if parsed_data.get('tenth_percentage') is not None:
                    profile.tenth_percentage = float(parsed_data['tenth_percentage'])
                if parsed_data.get('twelfth_percentage') is not None:
                    profile.twelfth_percentage = float(parsed_data['twelfth_percentage'])
                if parsed_data.get('cgpa') is not None:
                    profile.cgpa = float(parsed_data['cgpa'])
                
                profile.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('is_ajax') == 'true':
                    return JsonResponse({
                        'success': True,
                        'data': parsed_data,
                        'method': method,
                        'duration': duration,
                        'message': f"Resume uploaded and updated via {method} in {duration}s."
                    })

                messages.success(request, f"Resume uploaded successfully! Details updated automatically via {method} ({duration}s).")
            except Exception as e:
                logger.error(f"Error updating details from resume: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('is_ajax') == 'true':
                    return JsonResponse({'success': False, 'error': str(e)}, status=500)
                messages.error(request, f"Error processing resume: {e}")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('is_ajax') == 'true':
                return JsonResponse({'success': False, 'error': 'Uploaded file must be a PDF document.'}, status=400)
            messages.error(request, "Uploaded file must be a PDF document.")

    return redirect('dashboard')


@login_required
def update_profile_view(request):
    """Allows student to update parameters right from dashboard for What-If scenario simulations."""
    if request.method == 'POST':
        profile = request.user.profile
        profile.branch = request.POST.get('branch', profile.branch)
        profile.stipend = float(request.POST.get('stipend', profile.stipend) or 0)
        profile.tenth_percentage = float(request.POST.get('tenth_percentage', profile.tenth_percentage) or 85)
        profile.twelfth_percentage = float(request.POST.get('twelfth_percentage', profile.twelfth_percentage) or 85)
        profile.cgpa = float(request.POST.get('cgpa', profile.cgpa) or 8.0)
        profile.save()
        messages.success(request, "Academic details updated successfully!")
        
    return redirect('dashboard')
