import React, { useState } from 'react';
import Upload from './pages/Upload';
import Dashboard from './pages/Dashboard';

function App() {
  const [result, setResult] = useState(null);

  if (result) {
    return <Dashboard result={result} onReset={() => setResult(null)} />;
  }

  return <Upload onResultReady={setResult} />;
}

export default App;
