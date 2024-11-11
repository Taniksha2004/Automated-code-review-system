import React from 'react';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

interface Result {
  type: 'error' | 'warning' | 'suggestion';
  message: string;
  line?: number;
  fix?: (code: string) => string;
}

interface ResultsPanelProps {
  results: {
    score: number;
    issues: Result[];
    suggestions: Result[];
  } | null;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results }) => {
  if (!results) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 shadow-xl h-full flex items-center justify-center">
        <p className="text-gray-400 text-center">
          Click "Analyze Code" to see results
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-xl overflow-auto max-h-[600px]">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Analysis Results</h2>
          <div className="text-2xl font-bold text-white">
            Score: {results.score}/100
          </div>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 transition-all duration-500"
            style={{ width: `${results.score}%` }}
          />
        </div>
      </div>

      {results.issues.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium text-white mb-3">Issues Found</h3>
          <div className="space-y-3">
            {results.issues.map((issue, index) => (
              <div
                key={index}
                className="flex items-start gap-3 bg-gray-700/50 rounded-lg p-3"
              >
                {issue.type === 'error' ? (
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                ) : (
                  <Info className="w-5 h-5 text-yellow-400 flex-shrink-0" />
                )}
                <div>
                  <p className="text-white">{issue.message}</p>
                  {issue.line && (
                    <p className="text-sm text-gray-400">Line: {issue.line}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {results.suggestions.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-white mb-3">Suggestions</h3>
          <div className="space-y-3">
            {results.suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="flex items-start gap-3 bg-gray-700/50 rounded-lg p-3"
              >
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <p className="text-white">{suggestion.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsPanel;