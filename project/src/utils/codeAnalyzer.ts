interface AnalysisResult {
  score: number;
  issues: Array<{
    type: 'error' | 'warning';
    message: string;
    line?: number;
  }>;
  suggestions: Array<{
    message: string;
    fix?: (code: string) => string;
  }>;
}

const commonIssues = {
  javascript: {
    patterns: [
      { regex: /console\.log/, message: 'Remove console.log statements in production code' },
      { regex: /var\s/, message: 'Use const or let instead of var' },
      { regex: /==[^=]/, message: 'Use === for strict equality comparison' },
    ],
  },
  python: {
    patterns: [
      { regex: /print\(/, message: 'Consider using a logging framework instead of print statements' },
      { regex: /except:/, message: 'Avoid bare except clauses' },
      { regex: /\t/, message: 'Use spaces instead of tabs for indentation' },
    ],
  },
  // Add patterns for other languages...
};

const bestPractices = {
  javascript: [
    'Use meaningful variable names',
    'Add proper error handling with try/catch blocks',
    'Include JSDoc comments for functions',
    'Implement proper type checking',
  ],
  python: [
    'Follow PEP 8 style guide',
    'Use type hints for better code clarity',
    'Implement proper exception handling',
    'Use virtual environments for dependencies',
  ],
  // Add best practices for other languages...
};

export function analyzeCode(code: string, language: string): AnalysisResult {
  const issues: AnalysisResult['issues'] = [];
  const suggestions: AnalysisResult['suggestions'] = [];
  let score = 100;

  // Basic code quality checks
  if (code.length < 10) {
    score -= 20;
    issues.push({
      type: 'error',
      message: 'Code sample is too short for meaningful analysis',
    });
  }

  // Language-specific checks
  const languagePatterns = commonIssues[language as keyof typeof commonIssues]?.patterns || [];
  languagePatterns.forEach(({ regex, message }) => {
    if (regex.test(code)) {
      score -= 5;
      issues.push({
        type: 'warning',
        message,
      });
    }
  });

  // Add best practice suggestions
  const practices = bestPractices[language as keyof typeof bestPractices] || [];
  practices.forEach((practice) => {
    suggestions.push({
      message: practice,
    });
  });

  // Code complexity checks
  const lines = code.split('\n');
  if (lines.some(line => line.length > 100)) {
    score -= 5;
    suggestions.push({
      message: 'Consider breaking long lines into multiple lines for better readability',
    });
  }

  // Ensure score stays within bounds
  score = Math.max(0, Math.min(100, score));

  return {
    score,
    issues,
    suggestions,
  };
}