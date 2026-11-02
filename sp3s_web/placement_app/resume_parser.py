import os
import re
import json
import time
import logging
from dotenv import load_dotenv, find_dotenv

# Ensure .env is loaded regardless of invocation environment
load_dotenv(find_dotenv(usecwd=True))

logger = logging.getLogger(__name__)

# Valid branches supported by SP3S model
VALID_BRANCHES = ['COMP', 'CSE', 'EXTC', 'MCA']


def extract_text_from_pdf(pdf_file_path_or_stream):
    """
    Multi-engine PDF text extractor using PyMuPDF (pymupdf), pdfplumber, and pypdf.
    Handles multi-column layouts, tables, and raw PDF streams.
    """
    text = ""

    # Engine 1: PyMuPDF (Fastest, best layout handling)
    try:
        import pymupdf
        if hasattr(pdf_file_path_or_stream, 'read'):
            pdf_bytes = pdf_file_path_or_stream.read()
            if hasattr(pdf_file_path_or_stream, 'seek'):
                pdf_file_path_or_stream.seek(0)
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        else:
            doc = pymupdf.open(pdf_file_path_or_stream)

        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text += page_text + "\n"

        if text.strip():
            logger.info("Successfully extracted PDF text using PyMuPDF")
            return text
    except Exception as e:
        logger.warning(f"PyMuPDF extraction failed: {e}")

    # Engine 2: pdfplumber (Great for layout tables & text)
    try:
        import pdfplumber
        if hasattr(pdf_file_path_or_stream, 'seek'):
            pdf_file_path_or_stream.seek(0)
        with pdfplumber.open(pdf_file_path_or_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if text.strip():
            logger.info("Successfully extracted PDF text using pdfplumber")
            return text
    except Exception as e:
        logger.warning(f"pdfplumber PDF extraction failed: {e}")

    # Engine 3: pypdf (Fallback)
    try:
        from pypdf import PdfReader
        if hasattr(pdf_file_path_or_stream, 'seek'):
            pdf_file_path_or_stream.seek(0)
        reader = PdfReader(pdf_file_path_or_stream)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        logger.info("Extracted PDF text using pypdf fallback")
    except Exception as e:
        logger.error(f"pypdf extraction failed: {e}")

    return text


def parse_resume_with_groq(resume_text, api_key=None, model="qwen/qwen3.8-27b"):
    """
    Parse resume text using Groq Cloud LLM API with high-throughput models (Qwen 3.8 27B / GPT-OSS 120B / Llama 3).
    Supports structured JSON extraction with response_format={"type": "json_object"}.
    """
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        logger.info("No GROQ_API_KEY found.")
        return None, "GROQ_API_KEY not configured"

    try:
        from groq import Groq
        client = Groq(api_key=api_key.strip())

        prompt = f"""You are an expert HR resume parser and placement analytics engine.
Analyze the following student resume text and extract academic, contact, and internship details into a JSON object:

Resume Text:
---
{resume_text[:6000]}
---

Return ONLY a valid JSON object with the exact keys:
{{
    "branch": "one of ['COMP', 'CSE', 'EXTC', 'MCA'] (Map Information Technology, AI, ML, Data Science to 'CSE'; Electronics/Telecomm to 'EXTC'; MCA to 'MCA'; Computer Engineering to 'COMP')",
    "cgpa": float between 0.0 and 10.0 or null,
    "tenth_percentage": float between 0.0 and 100.0 or null,
    "twelfth_percentage": float between 0.0 and 100.0 or null,
    "stipend": float monthly internship stipend in INR or 0.0,
    "full_name": candidate's full name or null,
    "email": candidate's email address or null,
    "skills": ["top 3 to 8 technical skills found in resume"]
}}"""

        models_to_try = [
            model,
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        # Deduplicate while preserving order
        unique_models = []
        for m in models_to_try:
            if m and m not in unique_models:
                unique_models.append(m)

        last_error = None
        for m in unique_models:
            try:
                response = client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": "You are a resume parser. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=1000
                )
                content = response.choices[0].message.content.strip()
                data = json.loads(content)
                logger.info(f"Successfully parsed resume using Groq LLM ({m})")
                return data, f"Groq LLM ({m})"
            except Exception as e:
                last_error = e
                logger.warning(f"Groq model {m} attempt failed: {e}")
                continue

        return None, f"Groq parsing failed: {last_error}"

    except Exception as e:
        logger.error(f"Groq client error: {e}")
        return None, str(e)


def parse_resume_with_huggingface(resume_text, api_key=None, model="meta-llama/Llama-3.2-3B-Instruct"):
    """
    Parse resume text using Hugging Face Serverless / Inference API.
    Uses the OpenAI-compatible router endpoint or direct inference endpoint.
    """
    if not api_key:
        api_key = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")

    if not api_key:
        logger.info("No Hugging Face token found.")
        return None, "HF_TOKEN not configured"

    try:
        import requests

        url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }

        prompt = f"""You are an expert HR resume parser and placement analytics engine.
Analyze the following student resume text and extract academic, contact, and internship details into a JSON object:

Resume Text:
---
{resume_text[:6000]}
---

Return ONLY a valid JSON object with the exact keys:
{{
    "branch": "one of ['COMP', 'CSE', 'EXTC', 'MCA']",
    "cgpa": float between 0.0 and 10.0 or null,
    "tenth_percentage": float between 0.0 and 100.0 or null,
    "twelfth_percentage": float between 0.0 and 100.0 or null,
    "stipend": float monthly internship stipend in INR or 0.0,
    "full_name": candidate's full name or null,
    "email": candidate's email address or null,
    "skills": ["top 3 to 8 technical skills found in resume"]
}}"""

        models_to_try = [
            model,
            "meta-llama/Llama-3.1-8B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/DeepSeek-V4.1-Flash",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "meta-llama/Llama-3.2-3B-Instruct"
        ]
        unique_models = []
        for m in models_to_try:
            if m and m not in unique_models:
                unique_models.append(m)

        # Try with huggingface_hub InferenceClient first if available
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=api_key.strip())
            for m in unique_models:
                try:
                    res = client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": "You are a resume parser. Output only valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=800,
                        temperature=0.1
                    )
                    content = res.choices[0].message.content.strip()
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    data = json.loads(content)
                    model_short = m.split("/")[-1]
                    logger.info(f"Successfully parsed resume using Hugging Face InferenceClient ({model_short})")
                    return data, f"Hugging Face LLM ({model_short})"
                except Exception as e:
                    logger.warning(f"HF InferenceClient attempt for {m} failed: {e}")
                    continue
        except ImportError:
            pass

        # Fallback to direct HTTP router requests
        for m in unique_models:
            try:
                payload = {
                    "model": m,
                    "messages": [
                        {"role": "system", "content": "You are a resume parser. Output only valid JSON without markdown fences."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 800
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=25)
                if resp.status_code == 200:
                    res_json = resp.json()
                    content = res_json["choices"][0]["message"]["content"].strip()
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    data = json.loads(content)
                    model_short = m.split("/")[-1]
                    logger.info(f"Successfully parsed resume using Hugging Face ({model_short})")
                    return data, f"Hugging Face LLM ({model_short})"
                else:
                    logger.warning(f"HF router HTTP {resp.status_code} for {m}: {resp.text[:120]}")
            except Exception as e:
                logger.warning(f"HF model {m} failed: {e}")
                continue

        return None, "Hugging Face Inference failed for available models (402 credits required or unsupported model)"

    except Exception as e:
        logger.error(f"Hugging Face API call error: {e}")
        return None, str(e)


def parse_resume_with_gemini(resume_text, api_key=None):
    """
    Parse resume text using Google Gemini LLM API.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return None, "GEMINI_API_KEY not configured"

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key.strip())

        model_names = ['gemini-1.5-flash', 'gemini-2.5-flash', 'gemini-1.0-pro', 'gemini-pro']
        model = None
        for mname in model_names:
            try:
                model = genai.GenerativeModel(mname)
                break
            except Exception:
                continue

        if not model:
            return None, "Could not initialize Gemini model"

        prompt = f"""
        You are an expert HR resume parser. Extract academic and internship details from the following resume text:

        Resume Content:
        ---
        {resume_text[:5000]}
        ---

        Return ONLY a valid JSON object with NO markdown formatting:
        {{
            "branch": "one of ['COMP', 'CSE', 'EXTC', 'MCA']",
            "cgpa": float between 0.0 and 10.0 or null,
            "tenth_percentage": float between 0.0 and 100.0 or null,
            "twelfth_percentage": float between 0.0 and 100.0 or null,
            "stipend": float monthly stipend in INR or 0.0,
            "full_name": candidate's name or null,
            "email": candidate's email or null,
            "skills": ["key skills"]
        }}
        """

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.startswith("```"):
            response_text = response_text.replace("```", "", 1)
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        data = json.loads(response_text.strip())
        logger.info("Successfully parsed resume using Gemini LLM!")
        return data, "Google Gemini LLM"

    except Exception as e:
        logger.error(f"Gemini LLM Parsing failed: {e}")
        return None, str(e)


def parse_resume_with_regex(text):
    """
    Advanced Regex Parser for extracting CGPA, 10th %, 12th %, Stipend, Branch, Name, Email, and Skills.
    Handles varied resume layouts as a resilient zero-dependency fallback.
    """
    data = {
        "branch": "CSE",
        "cgpa": 8.0,
        "tenth_percentage": 85.0,
        "twelfth_percentage": 85.0,
        "stipend": 0.0,
        "full_name": None,
        "email": None,
        "skills": []
    }

    if not text or not text.strip():
        return data

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Candidate Name (typically 1st or 2nd non-empty line)
    for line in lines[:5]:
        clean_line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = clean_line.split()
        if 2 <= len(words) <= 4 and not any(kw in clean_line.lower() for kw in ['resume', 'curriculum', 'page', 'email', 'phone', 'education', 'contact', 'summary']):
            data["full_name"] = clean_line
            break

    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        data["email"] = email_match.group(0).strip()

    # 1. CGPA Extraction
    cgpa_match = re.search(r'(?:cgpa|gpa|pointer|cpi|sgpa|aggregate)[\s:=]*([0-9]+\.?[0-9]*)\s*(?:\/\s*10)?', text, re.IGNORECASE)
    if cgpa_match:
        try:
            val = float(cgpa_match.group(1))
            if 0.0 < val <= 10.0:
                data["cgpa"] = round(val, 2)
        except ValueError:
            pass

    # 2. 12th Class Percentage
    twelfth_match = re.search(r'(?:12th|class\s*xii\b|hsc|higher\s*secondary|diploma|grade\s*12|senior\s*secondary)[\s\w()]*?[\-:=]\s*([0-9]{2}(?:\.[0-9]+)?)\s*%?', text, re.IGNORECASE)
    if not twelfth_match:
        twelfth_match = re.search(r'(?:hsc|12th|class\s*12)[\s\w()]*?\s*([0-9]{2}(?:\.[0-9]+)?)\s*%', text, re.IGNORECASE)

    if twelfth_match:
        try:
            val = float(twelfth_match.group(1))
            if 40.0 <= val <= 100.0:
                data["twelfth_percentage"] = round(val, 2)
        except ValueError:
            pass

    # 3. 10th Class Percentage
    tenth_match = re.search(r'(?:10th|class\s*x\b|ssc|secondary|grade\s*10|xth|matriculation)[\s\w()]*?[\-:=]\s*([0-9]{2}(?:\.[0-9]+)?)\s*%?', text, re.IGNORECASE)
    if not tenth_match:
        tenth_match = re.search(r'(?:ssc|10th|class\s*10)[\s\w()]*?\s*([0-9]{2}(?:\.[0-9]+)?)\s*%', text, re.IGNORECASE)

    if tenth_match:
        try:
            val = float(tenth_match.group(1))
            if 40.0 <= val <= 100.0:
                data["tenth_percentage"] = round(val, 2)
        except ValueError:
            pass

    # 4. Stipend Extraction
    stipend_match = re.search(r'(?:stipend|internship|paid\s*internship|remuneration)[\s\w,:\-]*?₹?\s*(?:rs\.?|inr)?\s*([0-9,kK]+)\s*(?:per\s*month|\/month|monthly)?', text, re.IGNORECASE)
    if stipend_match:
        st_str = stipend_match.group(1).lower().replace(',', '')
        try:
            if 'k' in st_str:
                val = float(st_str.replace('k', '')) * 1000.0
            else:
                val = float(st_str)
            data["stipend"] = val
        except ValueError:
            pass

    # 5. Branch Detection
    t_lower = text.lower()
    if 'mca' in t_lower or 'master of computer' in t_lower:
        data["branch"] = "MCA"
    elif 'extc' in t_lower or 'electronics' in t_lower or 'telecommunication' in t_lower:
        data["branch"] = "EXTC"
    elif 'comp' in t_lower or 'computer engineering' in t_lower:
        data["branch"] = "COMP"
    elif 'cse' in t_lower or 'computer science' in t_lower or 'aiml' in t_lower or 'data science' in t_lower or 'information technology' in t_lower:
        data["branch"] = "CSE"

    # 6. Common Tech Skills Detection
    common_skills = [
        "Python", "Java", "C++", "SQL", "JavaScript", "TypeScript", "React", "Node.js",
        "Django", "FastAPI", "Flask", "Docker", "Kubernetes", "AWS", "Git", "Machine Learning",
        "Deep Learning", "PyTorch", "TensorFlow", "Pandas", "Scikit-Learn", "PostgreSQL", "MongoDB"
    ]
    detected_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            detected_skills.append(skill)
    data["skills"] = detected_skills[:8]

    return data


def extract_resume_data(pdf_file_path_or_stream, api_key=None, provider=None, model=None):
    """
    Main extraction pipeline:
    1. Extracts PDF raw text via PyMuPDF/pdfplumber.
    2. Runs requested or auto-selected LLM (Groq, Hugging Face, Gemini).
    3. Seamlessly falls back to Advanced Regex if LLM fails or keys are missing.
    4. Merges missing fields from Regex fallback so output is guaranteed complete.
    """
    start_time = time.time()
    text = extract_text_from_pdf(pdf_file_path_or_stream)

    if not text.strip():
        logger.warning("Empty PDF text extracted. Returning default fallback values.")
        return parse_resume_with_regex(""), "Default Fallback (Empty PDF)", 0.0

    provider_clean = (provider or "").strip().lower()
    llm_result = None
    method_name = None

    # Step 1: Provider selection & dispatch
    if provider_clean == "groq" or (provider_clean in ["", "auto"] and (api_key or os.environ.get("GROQ_API_KEY"))):
        llm_result, method_name = parse_resume_with_groq(text, api_key=api_key, model=model or "qwen/qwen3.8-27b")

    if not llm_result and (provider_clean == "huggingface" or (provider_clean in ["", "auto"] and (api_key or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")))):
        llm_result, method_name = parse_resume_with_huggingface(text, api_key=api_key, model=model or "meta-llama/Llama-3.2-3B-Instruct")

    if not llm_result and (provider_clean == "gemini" or (provider_clean in ["", "auto"] and (api_key or os.environ.get("GEMINI_API_KEY")))):
        llm_result, method_name = parse_resume_with_gemini(text, api_key=api_key)

    duration = round(time.time() - start_time, 2)

    # Step 2: Merge with Regex Fallback
    regex_fallback = parse_resume_with_regex(text)

    if llm_result and isinstance(llm_result, dict):
        # Validate branch
        branch = str(llm_result.get("branch", "")).upper()
        if branch not in VALID_BRANCHES:
            # Map common variations
            if any(k in branch for k in ["COMP", "COMPUTER ENG"]):
                llm_result["branch"] = "COMP"
            elif any(k in branch for k in ["ELECTRONIC", "EXTC", "TELECOM"]):
                llm_result["branch"] = "EXTC"
            elif any(k in branch for k in ["MCA", "MASTER"]):
                llm_result["branch"] = "MCA"
            else:
                llm_result["branch"] = regex_fallback["branch"]
        else:
            llm_result["branch"] = branch

        # Ensure numeric values are valid
        for num_field in ["cgpa", "tenth_percentage", "twelfth_percentage", "stipend"]:
            val = llm_result.get(num_field)
            if val is None or not isinstance(val, (int, float)):
                llm_result[num_field] = regex_fallback.get(num_field, 0.0)
            else:
                llm_result[num_field] = round(float(val), 2)

        # Merge contact & skills
        if not llm_result.get("full_name"):
            llm_result["full_name"] = regex_fallback.get("full_name")
        if not llm_result.get("email"):
            llm_result["email"] = regex_fallback.get("email")
        if not llm_result.get("skills"):
            llm_result["skills"] = regex_fallback.get("skills", [])

        return llm_result, method_name, duration

    # Fallback to Advanced Regex Engine
    logger.info("Falling back to Advanced Regex Engine.")
    return regex_fallback, "Advanced Regex Engine (Safety Fallback)", duration
