import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
import ast

class CodeAnalyzer:
    """
    Static code analysis utility for measuring code quality metrics
    """
    
    def analyze(self, code, language='python'):
        """
        Perform comprehensive code analysis
        """
        if language.lower() == 'python':
            return self._analyze_python(code)
        else:
            return self._analyze_generic(code)
    
    def _analyze_python(self, code):
        """
        Analyze Python code specifically
        """
        try:
            # Complexity analysis
            complexity_results = cc_visit(code)
            avg_complexity = sum(item.complexity for item in complexity_results) / len(complexity_results) if complexity_results else 0
            
            # Maintainability index
            mi_score = mi_visit(code, multi=True)
            
            # Halstead metrics
            halstead = h_visit(code)
            
            # Line counts
            lines = code.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            
            # Issues detection
            issues = self._detect_python_issues(code)
            
            # Calculate quality score (0-100)
            quality_score = self._calculate_quality_score(
                avg_complexity,
                mi_score,
                len(issues),
                comment_lines / total_lines if total_lines > 0 else 0
            )
            
            return {
                'quality_score': round(quality_score, 2),
                'complexity': round(avg_complexity, 2),
                'maintainability_index': round(mi_score, 2),
                'total_lines': total_lines,
                'code_lines': code_lines,
                'comment_lines': comment_lines,
                'issues_count': len(issues),
                'issues': issues,
                'halstead_difficulty': round(halstead.total.difficulty, 2) if halstead and halstead.total else 0
            }
            
        except Exception as e:
            return self._analyze_generic(code)
    
    def _analyze_generic(self, code):
        """
        Generic analysis for non-Python languages
        """
        lines = code.split('\n')
        total_lines = len(lines)
        
        # Basic metrics
        code_lines = len([line for line in lines if line.strip()])
        comment_lines = self._count_comments(code)
        
        # Simple issues detection
        issues = []
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'severity': 'low',
                    'message': 'Line too long (>120 characters)'
                })
        
        # Check for trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                issues.append({
                    'line': i,
                    'severity': 'low',
                    'message': 'Trailing whitespace'
                })
        
        quality_score = max(0, 100 - (len(issues) * 5))
        
        return {
            'quality_score': quality_score,
            'complexity': 0,
            'maintainability_index': 0,
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'issues_count': len(issues),
            'issues': issues
        }
    
    def _detect_python_issues(self, code):
        """
        Detect common Python code issues
        """
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if 'eval(' in line:
                issues.append({
                    'line': i,
                    'severity': 'high',
                    'message': 'Use of eval() is dangerous'
                })
            
            if 'exec(' in line:
                issues.append({
                    'line': i,
                    'severity': 'high',
                    'message': 'Use of exec() is dangerous'
                })
            
            if 'import *' in line:
                issues.append({
                    'line': i,
                    'severity': 'medium',
                    'message': 'Avoid wildcard imports'
                })
            
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'severity': 'low',
                    'message': 'Line too long (PEP 8 recommends max 79-120 chars)'
                })
            
            if 'except:' in line and 'except Exception:' not in line:
                issues.append({
                    'line': i,
                    'severity': 'medium',
                    'message': 'Bare except clause catches all exceptions'
                })
        
        return issues
    
    def _calculate_quality_score(self, complexity, maintainability, issues_count, comment_ratio):
        """
        Calculate overall quality score based on various metrics
        """
        # Start with maintainability index (0-100 scale)
        score = maintainability
        
        # Penalize high complexity
        if complexity > 10:
            score -= (complexity - 10) * 2
        
        # Penalize issues
        score -= issues_count * 3
        
        # Reward good commenting (5-20% is ideal)
        if 0.05 <= comment_ratio <= 0.20:
            score += 5
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))
    
    def _count_comments(self, code):
        """
        Count comment lines in code
        """
        comment_patterns = [
            r'^\s*#',      # Python comments
            r'^\s*//',     # JavaScript, Java, C++ comments
            r'^\s*/\*',    # Multi-line comment start
            r'^\s*\*',     # Multi-line comment continuation
        ]
        
        lines = code.split('\n')
        comment_count = 0
        
        for line in lines:
            for pattern in comment_patterns:
                if re.match(pattern, line):
                    comment_count += 1
                    break
        
        return comment_count