import json
import requests
from config import Config
from utils.code_analyzer import CodeAnalyzer


class AIService:
    def __init__(self):
        self.model = Config.AI_MODEL
        self.analyzer = CodeAnalyzer()

    def _fallback_review(self, code, language='python'):
        analysis = self.analyzer.analyze(code, language)
        feedback = {
            'quality_score': analysis.get('quality_score', 0),
            'summary': 'Automated static analysis summary (no OpenAI available).',
            'issues': analysis.get('issues', []),
            'best_practices': [],
            'refactoring': [],
            'security': [],
            'performance': [],
            'testing': []
        }
        return feedback

    def review_code(self, code, language='python'):
        """Analyze code using Gemini AI when available, otherwise fallback to static analysis."""
        if not Config.GEMINI_API_KEY:
            return self._fallback_review(code, language)

        prompt = f"""
You are an expert senior software engineer and code reviewer. Analyze the following {language} code and respond as JSON with keys: quality_score, summary, issues, best_practices, refactoring, security, performance, testing.

Code:
{code}
"""

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if not content:
                return self._fallback_review(code, language)

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    'quality_score': 70,
                    'summary': content,
                    'issues': [],
                    'best_practices': [],
                    'refactoring': [],
                    'security': [],
                    'performance': [],
                    'testing': []
                }

        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return self._fallback_review(code, language)

    def generate_portfolio_description(self, project_data):
        tech_stack = project_data.get('tech_stack', 'Not specified')
        features = project_data.get('features', 'Not specified')
        if isinstance(tech_stack, list):
            tech_stack = ', '.join(tech_stack)
        if isinstance(features, list):
            features = ', '.join(features)

        if not Config.GEMINI_API_KEY:
            return f"{project_data.get('name', 'Project')} built with {tech_stack}."

        prompt = f"""Create a comprehensive and professional portfolio description (4-5 sentences) for this software project:

Project Name: {project_data.get('name', 'Untitled Project')}
Tech Stack: {tech_stack}
Features/Description: {features}

The description should:
- Explain what the project does and its main purpose
- Highlight key features and functionality
- Mention the technologies used and why they're beneficial
- Emphasize the value it provides to users
- Sound professional and impressive for a developer portfolio

Write in a compelling, professional tone that showcases technical expertise."""
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return f"{project_data.get('name', 'Project')} built with {tech_stack}."

    def suggest_improvements(self, code, language='python'):
        if not Config.GEMINI_API_KEY:
            analysis = self.analyzer.analyze(code, language)
            return f"Static analysis: {analysis.get('issues_count',0)} issues, quality {analysis.get('quality_score')}"

        prompt = f"Review this {language} code and provide 3 specific improvements:\n\n{code}\n"
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return f"Error generating suggestions: {str(e)}"
