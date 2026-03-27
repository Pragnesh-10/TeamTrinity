import React, { useState, useRef, useEffect } from 'react';
import { Upload as UploadIcon, Play, FileText, ChevronRight } from 'lucide-react';
import { analyzePortfolio } from '../lib/api';
import { motion, AnimatePresence } from 'framer-motion';

export default function Upload({ onResultReady }) {
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [scenario, setScenario] = useState("Long-Term Wealth Growth");
  const [taxRegime, setTaxRegime] = useState("New Tax Regime");
  const [hoveredDemo, setHoveredDemo] = useState(false);
  const fileInputRef = useRef(null);

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

  const processFile = async (file) => {
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

  const handleFileChange = (e) => processFile(e.target.files[0]);

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    processFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="min-h-[100vh] flex flex-col items-center justify-center p-6 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-surface via-background to-background relative overflow-hidden">
      
      {/* Decorative blurred background blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-teal/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/5 blur-[120px] pointer-events-none" />

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div 
            key="loading"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            className="flex flex-col items-center justify-center space-y-8 z-10"
          >
            <div className="relative w-32 h-32 flex items-center justify-center">
              <motion.div 
                className="absolute inset-0 border-4 border-teal/10 rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              />
              <motion.div 
                className="absolute inset-2 border-4 border-t-teal border-r-teal border-b-transparent border-l-transparent rounded-full shadow-[0_0_15px_rgba(0,212,170,0.5)]"
                animate={{ rotate: -360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              />
              <motion.div 
                className="w-12 h-12 bg-teal/20 rounded-full flex items-center justify-center backdrop-blur-md"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
              >
                <div className="w-4 h-4 bg-teal rounded-full shadow-[0_0_10px_rgba(0,212,170,1)]"/>
              </motion.div>
            </div>
            <div className="text-center space-y-3">
              <motion.h2 
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="text-2xl font-bold text-white tracking-wide"
              >
                Agents Computing...
              </motion.h2>
              <p className="text-teal/80 font-mono text-sm max-w-sm mx-auto leading-relaxed">
                Extracting mutual fund signatures, analyzing overlap concentrations, and structuring taxation.
              </p>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="upload"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.5, type: 'spring' }}
            className="w-full max-w-2xl z-10"
          >
            <div className="text-center mb-10">
              <motion.div 
                initial={{ scale: 0, rotate: -20 }} 
                animate={{ scale: 1, rotate: 0 }} 
                transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
                className="w-16 h-16 bg-teal/10 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-[0_0_30px_rgba(0,212,170,0.2)] border border-teal/20"
              >
                <UploadIcon className="w-8 h-8 text-teal" />
              </motion.div>
              <h1 className="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight drop-shadow-sm text-white">
                MF Portfolio <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal to-blue-400">X-Ray AI</span>
              </h1>
              <p className="text-lg text-gray-400 font-medium">Upload your CAS PDF to reveal hidden risks and forecast your FIRE timeline.</p>
            </div>

            <div className="bg-surface/60 backdrop-blur-2xl border border-white/5 rounded-3xl p-8 shadow-2xl shadow-black/50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 text-left">
                <div className="space-y-2 relative group">
                  <label className="text-xs font-bold text-teal/80 uppercase tracking-widest pl-1">Investment Horizon</label>
                  <div className="relative">
                    <select 
                      value={scenario}
                      onChange={(e) => setScenario(e.target.value)}
                      className="w-full bg-background/50 border border-white/10 p-3.5 pr-10 rounded-xl text-white outline-none focus:border-teal/50 focus:ring-1 focus:ring-teal/30 transition-all appearance-none font-medium hover:bg-white/5 cursor-pointer"
                    >
                      <option value="Long-Term Wealth Growth">Long-Term Wealth (&gt;10y)</option>
                      <option value="Retirement Transition">Retirement Transition (&lt;3y)</option>
                      <option value="House Downpayment">House Downpayment (Short)</option>
                    </select>
                    <ChevronRight className="w-4 h-4 text-gray-400 absolute right-4 top-1/2 -translate-y-1/2 rotate-90 pointer-events-none group-hover:text-teal transition-colors" />
                  </div>
                </div>
                <div className="space-y-2 relative group">
                  <label className="text-xs font-bold text-teal/80 uppercase tracking-widest pl-1">Tax Strategy</label>
                  <div className="relative">
                    <select 
                      value={taxRegime}
                      onChange={(e) => setTaxRegime(e.target.value)}
                      className="w-full bg-background/50 border border-white/10 p-3.5 pr-10 rounded-xl text-white outline-none focus:border-teal/50 focus:ring-1 focus:ring-teal/30 transition-all appearance-none font-medium hover:bg-white/5 cursor-pointer"
                    >
                      <option value="New Tax Regime">New Tax Regime (Default)</option>
                      <option value="Old Tax Regime">Old Tax Regime (Section 80C)</option>
                    </select>
                    <ChevronRight className="w-4 h-4 text-gray-400 absolute right-4 top-1/2 -translate-y-1/2 rotate-90 pointer-events-none group-hover:text-teal transition-colors" />
                  </div>
                </div>
              </div>

              <input type="file" accept=".pdf" className="hidden" ref={fileInputRef} onChange={handleFileChange} />
              
              <div  
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
                onDrop={handleDrop}
                className={`relative overflow-hidden border-2 transition-all duration-300 rounded-2xl p-10 text-center flex flex-col items-center justify-center cursor-pointer group
                  ${isDragging ? 'border-teal border-solid bg-teal/10 scale-[1.02]' : 'border-dashed border-white/10 hover:border-teal/50 hover:bg-white/5'}`}
              >
                {isDragging && <div className="absolute inset-0 bg-teal/20 blur-[50px] rounded-full pointer-events-none" />}
                
                <motion.div 
                  animate={{ y: isDragging ? -5 : 0 }}
                  className={`w-16 h-16 rounded-full flex items-center justify-center mb-5 transition-all duration-500 shadow-xl ${isDragging ? 'bg-teal text-background scale-110 shadow-teal/50' : 'bg-surface text-teal group-hover:scale-110 group-hover:bg-teal group-hover:text-background border border-white/5 group-hover:shadow-[0_0_20px_rgba(0,212,170,0.3)]'}`}
                >
                  <FileText className="w-7 h-7" />
                </motion.div>
                <h3 className="text-xl font-bold mb-2 text-white">Upload CAMS/KFintech CAS</h3>
                <p className="text-gray-400 text-sm mb-6 max-w-xs">Drag and drop your consolidated mutual fund statement PDF here (up to 10MB)</p>
                <div className="bg-white/10 hover:bg-white/20 text-white border border-white/10 backdrop-blur-md px-6 py-2.5 rounded-xl font-semibold transition-all">
                  Browse Files
                </div>
              </div>

              <div className="flex items-center gap-4 my-8">
                <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-white/10 flex-1"></div>
                <span className="text-xs text-gray-500 font-bold tracking-widest uppercase bg-surface/50 px-2 rounded-md">Or analyze a sample</span>
                <div className="h-px bg-gradient-to-l from-transparent via-white/10 to-white/10 flex-1"></div>
              </div>

              <button 
                onClick={handleDemoClick}
                onMouseEnter={() => setHoveredDemo(true)}
                onMouseLeave={() => setHoveredDemo(false)}
                className="relative w-full overflow-hidden group flex items-center justify-center gap-3 bg-gradient-to-br from-surface to-background hover:from-surface hover:to-surface border border-white/10 p-5 rounded-2xl transition-all duration-300 transform hover:shadow-[0_0_30px_rgba(245,158,11,0.15)] group-hover:border-amber/30"
              >
                <motion.div
                  animate={{ x: hoveredDemo ? 5 : 0, scale: hoveredDemo ? 1.2 : 1 }}
                  transition={{ duration: 0.2 }}
                >
                  <Play className={`w-5 h-5 transition-colors ${hoveredDemo ? 'text-amber fill-amber' : 'text-amber'}`} />
                </motion.div>
                <span className="font-semibold tracking-wide text-white">Run Multi-Agent Demo Profile</span>
              </button>
            </div>
            
            <div className="mt-8 text-center text-xs text-gray-500 font-mono">
              <p>Your data is processed securely via edge-agents and never permanently stored.</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}