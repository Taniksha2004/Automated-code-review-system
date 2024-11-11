import React from 'react';
import { Code } from 'lucide-react';

interface LanguageSelectorProps {
  language: string;
  languages: { id: string; name: string }[];
  onChange: (language: string) => void;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ language, languages, onChange }) => {
  return (
    <div className="flex items-center gap-2 mb-4">
      <Code className="w-5 h-5 text-gray-400" />
      <select
        value={language}
        onChange={(e) => onChange(e.target.value)}
        className="bg-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        {languages.map((lang) => (
          <option key={lang.id} value={lang.id}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default LanguageSelector;