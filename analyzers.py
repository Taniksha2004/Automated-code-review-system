import subprocess
import json
import tempfile
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAnalyzer(ABC):
    """Base class for code analyzers"""
    
    @abstractmethod
    def analyze(self, code_content: str, filename: str) -> Dict[str, Any]:
        """Analyze code and return results"""
        pass
    
    def _run_command(self, command: List[str], input_data: str = None) -> Dict[str, Any]:
        """Run external command and return results"""
        try:
            process = subprocess.run(
                command,
                input=input_data,
                text=True,
                capture_output=True,
                timeout=300  # 5 minutes timeout
            )
            return {
                'returncode': process.returncode,
                'stdout': process.stdout,
                'stderr': process.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Analysis timeout'
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }

class PythonAnalyzer(BaseAnalyzer):
    """Python code analyzer using pylint and flake8"""
    
    def analyze(self, code_content: str, filename: str) -> Dict[str, Any]:
        issues = []
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code_content)
            temp_file_path = temp_file.name
        
        try:
            # Run pylint
            pylint_issues = self._run_pylint(temp_file_path)
            issues.extend(pylint_issues)
            
            # Run flake8
            flake8_issues = self._run_flake8(temp_file_path)
            issues.extend(flake8_issues)
            
            # Run bandit for security issues
            bandit_issues = self._run_bandit(temp_file_path)
            issues.extend(bandit_issues)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
        return self._calculate_results(issues)
    
    def _run_pylint(self, file_path: str) -> List[Dict[str, Any]]:
        """Run pylint analysis"""
        command = ['pylint', '--output-format=json', '--reports=no', file_path]
        result = self._run_command(command)
        
        issues = []
        if result['returncode'] != 0 and result['stdout']:
            try:
                pylint_output = json.loads(result['stdout'])
                for issue in pylint_output:
                    issues.append({
                        'rule_id': issue.get('message-id', 'unknown'),
                        'rule_name': issue.get('symbol', 'Unknown'),
                        'severity': self._map_pylint_severity(issue.get('type', 'info')),
                        'message': issue.get('message', ''),
                        'line_number': issue.get('line', 0),
                        'column_number': issue.get('column', 0),
                        'suggestion': ''
                    })
            except json.JSONDecodeError:
                pass
        
        return issues
    
    def _run_flake8(self, file_path: str) -> List[Dict[str, Any]]:
        """Run flake8 analysis"""
        command = ['flake8', '--format=json', file_path]
        result = self._run_command(command)
        
        issues = []
        if result['stdout']:
            try:
                flake8_output = json.loads(result['stdout'])
                for filename, file_issues in flake8_output.items():
                    for issue in file_issues:
                        issues.append({
                            'rule_id': issue.get('code', 'unknown'),
                            'rule_name': issue.get('code', 'Unknown'),
                            'severity': 'warning',
                            'message': issue.get('text', ''),
                            'line_number': issue.get('line_number', 0),
                            'column_number': issue.get('column_number', 0),
                            'suggestion': ''
                        })
            except json.JSONDecodeError:
                pass
        
        return issues
    
    def _run_bandit(self, file_path: str) -> List[Dict[str, Any]]:
        """Run bandit security analysis"""
        command = ['bandit', '-f', 'json', file_path]
        result = self._run_command(command)
        
        issues = []
        if result['stdout']:
            try:
                bandit_output = json.loads(result['stdout'])
                for issue in bandit_output.get('results', []):
                    issues.append({
                        'rule_id': issue.get('test_id', 'unknown'),
                        'rule_name': issue.get('test_name', 'Security Issue'),
                        'severity': self._map_bandit_severity(issue.get('issue_severity', 'LOW')),
                        'message': issue.get('issue_text', ''),
                        'line_number': issue.get('line_number', 0),
                        'column_number': 0,
                        'suggestion': issue.get('issue_confidence', '')
                    })
            except json.JSONDecodeError:
                pass
        
        return issues
    
    def _map_pylint_severity(self, pylint_type: str) -> str:
        """Map pylint severity to our severity levels"""
        mapping = {
            'error': 'error',
            'warning': 'warning',
            'refactor': 'info',
            'convention': 'info',
            'info': 'info'
        }
        return mapping.get(pylint_type.lower(), 'info')
    
    def _map_bandit_severity(self, bandit_severity: str) -> str:
        """Map bandit severity to our severity levels"""
        mapping = {
            'HIGH': 'critical',
            'MEDIUM': 'error',
            'LOW': 'warning'
        }
        return mapping.get(bandit_severity.upper(), 'warning')
    
    def _calculate_results(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall results from issues"""
        severity_counts = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0
        }
        
        for issue in issues:
            severity = issue.get('severity', 'info')
            severity_counts[severity] += 1
        
        # Calculate score (0-100, higher is better)
        total_issues = len(issues)
        if total_issues == 0:
            score = 100.0
        else:
            # Weight different severities
            weighted_score = (
                severity_counts['critical'] * 10 +
                severity_counts['error'] * 5 +
                severity_counts['warning'] * 2 +
                severity_counts['info'] * 1
            )
            score = max(0, 100 - weighted_score)
        
        return {
            'issues': issues,
            'overall_score': score,
            'total_issues': total_issues,
            'critical_issues': severity_counts['critical'],
            'error_issues': severity_counts['error'],
            'warning_issues': severity_counts['warning'],
            'info_issues': severity_counts['info']
        }

class JavaScriptAnalyzer(BaseAnalyzer):
    """JavaScript/TypeScript analyzer using ESLint"""
    
    def analyze(self, code_content: str, filename: str) -> Dict[str, Any]:
        issues = []
        
        # Determine file extension
        extension = '.js'
        if filename.endswith('.ts'):
            extension = '.ts'
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as temp_file:
            temp_file.write(code_content)
            temp_file_path = temp_file.name
        
        try:
            # Run ESLint
            eslint_issues = self._run_eslint(temp_file_path)
            issues.extend(eslint_issues)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
        return self._calculate_results(issues)
    
    def _run_eslint(self, file_path: str) -> List[Dict[str, Any]]:
        """Run ESLint analysis"""
        command = ['eslint', '--format=json', file_path]
        result = self._run_command(command)
        
        issues = []
        if result['stdout']:
            try:
                eslint_output = json.loads(result['stdout'])
                for file_result in eslint_output:
                    for message in file_result.get('messages', []):
                        issues.append({
                            'rule_id': message.get('ruleId', 'unknown'),
                            'rule_name': message.get('ruleId', 'Unknown'),
                            'severity': self._map_eslint_severity(message.get('severity', 1)),
                            'message': message.get('message', ''),
                            'line_number': message.get('line', 0),
                            'column_number': message.get('column', 0),
                            'suggestion': message.get('fix', {}).get('text', '')
                        })
            except json.JSONDecodeError:
                pass
        
        return issues
    
    def _map_eslint_severity(self, eslint_severity: int) -> str:
        """Map ESLint severity to our severity levels"""
        if eslint_severity == 2:
            return 'error'
        elif eslint_severity == 1:
            return 'warning'
        else:
            return 'info'
    
    def _calculate_results(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall results from issues"""
        severity_counts = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0
        }
        
        for issue in issues:
            severity = issue.get('severity', 'info')
            severity_counts[severity] += 1
        
        # Calculate score (0-100, higher is better)
        total_issues = len(issues)
        if total_issues == 0:
            score = 100.0
        else:
            # Weight different severities
            weighted_score = (
                severity_counts['critical'] * 10 +
                severity_counts['error'] * 5 +
                severity_counts['warning'] * 2 +
                severity_counts['info'] * 1
            )
            score = max(0, 100 - weighted_score)
        
        return {
            'issues': issues,
            'overall_score': score,
            'total_issues': total_issues,
            'critical_issues': severity_counts['critical'],
            'error_issues': severity_counts['error'],
            'warning_issues': severity_counts['warning'],
            'info_issues': severity_counts['info']
        }

# Analyzer registry
ANALYZERS = {
    'python': PythonAnalyzer,
    'javascript': JavaScriptAnalyzer,
    'typescript': JavaScriptAnalyzer,
}

def get_analyzer(language: str) -> BaseAnalyzer:
    """Get analyzer instance for given language"""
    analyzer_class = ANALYZERS.get(language.lower())
    if not analyzer_class:
        raise ValueError(f"No analyzer available for language: {language}")
    return analyzer_class()
