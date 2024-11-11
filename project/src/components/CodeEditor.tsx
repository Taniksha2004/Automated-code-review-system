import React from 'react';

interface CodeEditorProps {
  code: string;
  language: string;
  onChange: (code: string) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ code, onChange }) => {
  return (
    <div className="relative mt-4">
      <textarea
        value={code}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-[400px] bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
        spellCheck="false"
      />
    </div>
  );
}

export default CodeEditor;