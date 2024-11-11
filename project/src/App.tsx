import React, { useState } from 'react';
import { Code2, Play, RotateCcw, Zap } from 'lucide-react';
import CodeEditor from './components/CodeEditor';
import LanguageSelector from './components/LanguageSelector';
import ResultsPanel from './components/ResultsPanel';
import { analyzeCode } from './utils/codeAnalyzer';
import { languages } from './data/languages';

function App() {
  const [code, setCode] = useState('// Write or paste your code here');
  const [language, setLanguage] = useState('javascript');
  const [results, setResults] = useState(null);

  const handleAnalyze = () => {
    const analysisResults = analyzeCode(code, language);
    setResults(analysisResults);
  };

  const handleReset = () => {
    setCode('// Write or paste your code here');
    setResults(null);
  };

  const handleFix = () => {
    if (results) {
      const improvedCode = results.suggestions.reduce((acc, suggestion) => 
        suggestion.fix ? suggestion.fix(acc) : acc, code);
      setCode(improvedCode);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Code2 className="w-10 h-10 text-pink-400" />
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-indigo-400">
              Code Review Pro
            </h1>
          </div>
          <p className="text-gray-300">Automated code analysis for 20+ programming languages</p>
        </header>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-4 shadow-xl">
              <LanguageSelector
                language={language}
                languages={languages}
                onChange={setLanguage}
              />
              <CodeEditor
                code={code}
                language={language}
                onChange={setCode}
              />
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={handleAnalyze}
                className="flex-1 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                <Play className="w-5 h-5" />
                Analyze Code
              </button>
              <button
                onClick={handleFix}
                className="flex items-center justify-center gap-2 bg-pink-600 hover:bg-pink-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                <Zap className="w-5 h-5" />
                Fix Issues
              </button>
              <button
                onClick={handleReset}
                className="flex items-center justify-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                <RotateCcw className="w-5 h-5" />
                Reset
              </button>
            </div>
          </div>

          <ResultsPanel results={results} />
        </div>
      </div>
    </div>
  );
}

export default App;