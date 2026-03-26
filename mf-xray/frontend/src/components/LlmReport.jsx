import React from 'react';

export default function LlmReport({ markdown }) {
  // Simple custom parser since we aren't using react-markdown to keep it lightweight.
  // We process basic ### headings, **bold**, and line breaks.
  
  const formattedText = markdown.split('\n').map((line, idx) => {
    if (line.startsWith('### ')) {
      return <h4 key={idx} className="text-lg font-bold text-white mt-6 mb-2">{line.replace('### ', '')}</h4>;
    }
    if (line.startsWith('## ')) {
      return <h3 key={idx} className="text-2xl font-bold text-teal mt-8 mb-4 border-b border-border pb-2">{line.replace('## ', '')}</h3>;
    }
    if (line.startsWith('> ⚠')) {
      return (
        <div key={idx} className="mt-8 border border-amber/30 bg-amber/5 px-6 py-4 rounded-lg flex items-start gap-4 text-amber text-sm font-medium">
          {line.replace('> ', '')}
        </div>
      );
    }
    if (line.match(/^[1-9]\. /)) {
      // List parsing
      const bolded = line.split(/(\\*\\*.*?\\*\\*)/g).map((chunk, i) => {
        if (chunk.startsWith('**') && chunk.endsWith('**')) {
          return <strong key={i} className="text-white">{chunk.replace(/\\*\\*/g, '')}</strong>;
        }
        return chunk;
      });
      return <div key={idx} className="flex gap-2 text-gray-300 my-2"><span className="text-teal font-mono">{line.substring(0,2)}</span> <span>{bolded.slice(1)}</span></div>;
    }
    if (line.trim() === '') {
      return <br key={idx} />;
    }
    
    // Default text with bold support
    const bolded = line.split(/(\\*\\*.*?\\*\\*)/g).map((chunk, i) => {
      if (chunk.startsWith('**') && chunk.endsWith('**')) {
        return <strong key={i} className="text-white font-semibold">{chunk.replace(/\\*\\*/g, '')}</strong>;
      }
      return chunk;
    });
    
    return <p key={idx} className="text-gray-300 my-1 leading-relaxed">{bolded}</p>;
  });

  return (
    <div className="prose prose-invert max-w-none prose-p:text-gray-300">
      {formattedText}
    </div>
  );
}
