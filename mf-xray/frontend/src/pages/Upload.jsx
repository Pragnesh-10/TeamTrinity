import React, { useState, useRef, useEffect } from 'react';
import { Upload as UploadIcon, Play } from 'lucide-react';
import { analyzePortfolio } from '../lib/api';

export default function Upload({ onResultReady }) {
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [scenario, setScenario] = useState("Long-Term Wealth Growth");
  const [taxRegime, setTaxRegime] = useState("New Tax Regime");
  const fileInputRef = useRef(null);

  // Cold-start: wake up Render free-tier instance on page load
  useEffect(() => {
    fetch("https://teamtrinity.onrender.com/health").catch(() => {});
  }, []);

  const handleDemoClick = async () => {
    setLoading(true);
    try {
      const result = await analyzePortfolio(null, scenario, taxRegime);
      if (result.detail) alert(result.detail);
      else onResultReady(result);
    } catch (e) {
      console.error(e);
      alert("Error connecting to AI agents.");
    }
    setLoading(false);
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    try {
      const result = await analyzePortfolio(file, scenario, taxRegime);
      if (result.detail) alert(result.detail);
      else onResultReady(result);
    } catch (e) {
      console.error(e);
      alert("Pipeline error.");
    }
    setLoading(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    setLoading(true);
    try {
      const result = await analyzePortfolio(file, scenario, taxRegime);
      if (result.detail) alert(result.detail);
      else onResultReady(result);
    } catch (err) {
      console.error(err);
      alert("Error uploading file.");
    }
    setLoading(false);
  };

  const triggerFileSelect = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="max-w-3xl w-full text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
          MF Portfolio <span className="text-teal text-transparent bg-clip-text bg-gradient-to-r from-teal to-blue-400">X-Ray Agent</span>
        </h1>
        <p className="text-lg text-gray-400">Multi-Agent System for Autonomous Financial Planning</p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center space-y-6">
          <div className="w-12 h-12 border-4 border-teal border-t-transparent rounded-full animate-spin"></div>
          <p className="text-teal animate-pulse font-mono">Agents are analyzing your portfolio...</p>
        </div>
      ) : (
        <div className="w-full max-w-xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 text-left">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wider">Life Scenario Edge Case</label>
              <select 
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full bg-surface border border-border p-4 rounded-xl text-white outline-none focus:border-teal transition-colors"
              >
                <option value="Long-Term Wealth Growth"> Long-Term Wealth (&gt;10y)</option>
                <option value="Retirement Transition"> Retirement Transition (&lt;3y)</option>
                <option value="House Downpayment"> House Downpayment (Short)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wider">Base Tax Regime</label>
              <select 
                value={taxRegime}
                onChange={(e) => setTaxRegime(e.target.value)}
                className="w-full bg-surface border border-border p-4 rounded-xl text-white outline-none focus:border-teal transition-colors"
              >
                <option value="New Tax Regime">New Tax Regime (Default)</option>
                <option value="Old Tax Regime">Old Tax Regime (Section 80C limits)</option>
              </select>
            </div>
          </div>

          <input type="file" accept=".pdf" className="hidden" ref={fileInputRef} onChange={handleFileChange} />
          
          <div  
            onClick={triggerFileSelect}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
            onDrop={handleDrop}
            className={`border-2 border-dashed hover:border-teal/50 transition-colors bg-surface rounded-2xl p-12 text-center flex flex-col items-center justify-center cursor-pointer group ${isDragging ? 'border-teal bg-teal/5' : 'border-border'}`}
          >
            <div className="w-16 h-16 bg-background rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <UploadIcon className="w-8 h-8 text-teal" />
            </div>
            <h3 className="text-xl font-medium mb-2">Drag & Drop your CAS PDF</h3>
            <p className="text-gray-400 text-sm mb-6">Supports .pdf formats up to 10MB</p>
            <button className="bg-white text-black px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
              Select File
            </button>
          </div>

          <div className="flex items-center gap-4 my-8">
            <div className="h-px bg-border flex-1"></div>
            <span className="text-sm text-gray-500 font-mono uppercase">Or</span>
            <div className="h-px bg-border flex-1"></div>
          </div>

          <button 
            onClick={handleDemoClick}
            className="w-full flex items-center justify-center gap-3 bg-surface hover:bg-border border border-border p-4 rounded-xl transition-all"
          >
            <Play className="w-5 h-5 text-amber" />
            <span className="font-medium">Run Multi-Agent Demo Simulation</span>
          </button>
        </div>
      )}
    </div>
  );
}
