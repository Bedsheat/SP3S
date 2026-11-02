import os
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .resume_parser import extract_resume_data, parse_resume_with_regex


class ResumeParserTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_regex_extraction(self):
        sample_text = """
        Wasifah Parkar
        Email: parkarwasifah@gmail.com
        Sardar Patel Institute of Technology
        Master of Computer Applications, CGPA: 9.34
        Royal College of Arts, Science and Commerce
        HSC (Commerce) - 88.83%
        SSC - 90.0%
        Stipend: Rs. 25000 per month
        Skills: Python, Django, Machine Learning, SQL
        """
        data = parse_resume_with_regex(sample_text)
        self.assertEqual(data["branch"], "MCA")
        self.assertEqual(data["cgpa"], 9.34)
        self.assertEqual(data["twelfth_percentage"], 88.83)
        self.assertEqual(data["tenth_percentage"], 90.0)
        self.assertEqual(data["stipend"], 25000.0)
        self.assertEqual(data["email"], "parkarwasifah@gmail.com")
        self.assertIn("Python", data["skills"])

    def test_llm_status_api(self):
        response = self.client.get('/api/llm-status/')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('groq', json_data)
        self.assertIn('huggingface', json_data)
        self.assertIn('active_provider', json_data)

    def test_parse_resume_api_no_file(self):
        response = self.client.post('/api/parse-resume/')
        self.assertEqual(response.status_code, 400)

    def test_parse_resume_api_invalid_file_extension(self):
        txt_file = SimpleUploadedFile("resume.txt", b"Hello world", content_type="text/plain")
        response = self.client.post('/api/parse-resume/', {'resume_pdf': txt_file})
        self.assertEqual(response.status_code, 400)
