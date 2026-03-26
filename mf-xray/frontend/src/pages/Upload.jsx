import React, { useState, useEffect, useRef } from 'react';
import { Upload as UploadIcon, FileText, Play } from 'lucide-react';
import { triggerDemo, getStatus, getResult, uploadPdf } from '../lib/api';
import ProgressTracker from '../components/ProgressTracker';

export default function Upload({ onJobComplete, onResultReady }) {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    let intervalId;
    if (jobId) {
      intervalId = setInterval(async () => {
        try {
          const res = await getStatus(jobId);
          if (res.error) return;
          setStatus(res);
          
          if (res.step >= 6 || res.progress >= 100) {
            clearInterval(intervalId);
            const result = await getResult(jobId);
            onResultReady(result);
          } else if (res.step === -1) {
            clearInterval(intervalId);
            alert("Pipeline error: " + res.label);
          }
        } catch (e) {
          console.error(e);
        }
      }, 1000);
    }
    return () => clearInterval(intervalId);
  }, [jobId, onResultReady]);

  const handleDemoClick = async () => {
    try {
      const { job_id } = await triggerDemo();
      setJobId(job_id);
      onJobComplete(job_id);
    } catch (e) {
      console.error(e);
      alert("Backend not responding. Is it running?");
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const { job_id } = await uploadPdf(file);
      setJobId(job_id);
      onJobComplete(job_id);
    } catch (e) {
      console.error(e);
      alert("Error uploading file.");
    }
  };

  const triggerFileSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    try {
      const { job_id } = await uploadPdf(file);
      setJobId(job_id);
      onJobComplete(job_id);
    } catch (err) {
      console.error(err);
      alert("Error uploading file.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="max-w-3xl w-full text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
          MF Portfolio <span className="text-teal text-transparent bg-clip-text bg-gradient-to-r from-teal to-blue-400">X-Ray</span>
        </h1>
        <p className="text-lg text-gray-400">Autonomous analysis of your CAMS or KFintech statements.</p>
      </div>

      {!jobId ? (
        <div className="w-full max-w-xl">
          <input 
            type="file" 
            accept=".pdf" 
            className="hidden" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
          />
          <div 
            onClick={triggerFileSelect}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed hover:border-teal/50 transition-colors bg-surface rounded-2xl p-12 text-center flex flex-col items-center justify-center cursor-pointer group ${isDragging ? 'border-teal bg-teal/5' : 'border-border'}`}
          >
            <div className="w-16 h-16 bg-background rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <UploadIcon className="w-8 h-8 text-teal" />
            </div>
            <h3 className="text-xl font-medium mb-2">Drag & Drop your CAS PDF</h3>
            <p className="text-gray-400 text-sm mb-6">Supports .pdf formats up to 10MB</p>
            <button 
              onClick={(e) => { e.stopPropagation(); triggerFileSelect(); }}
              className="bg-white text-black px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Select File
            </button>
          </div>

          <div className="flex items-center gap-4 my-8">
            <div className="h-px bg-border flex-1"></div>
            <span className="text-sm text-gray-500 font-mono uppercase">Or try the</span>
            <div className="h-px bg-border flex-1"></div>
          </div>

          <button 
            onClick={handleDemoClick}
            className="w-full flex items-center justify-center gap-3 bg-surface hover:bg-border border border-border p-4 rounded-xl transition-all"
          >
            <Play className="w-5 h-5 text-amber" />
            <span className="font-medium">Run Built-in Demo Data</span>
          </button>
        </div>
      ) : (
        <ProgressTracker 
          currentStep={status?.step || 1} 
          label={status?.label || 'Initializing...'} 
          progress={status?.progress || 0} 
        />
      )}

      <div className="mt-auto pt-16">
        <div className="border border-amber/30 bg-amber/5 px-6 py-4 rounded-lg flex items-start gap-4 text-amber max-w-4xl text-sm">
          <span className="text-xl">⚠</span>
          <p>
            This is AI-generated analysis for informational purposes only and does not constitute SEBI-registered investment advice. 
            Please consult a SEBI-registered investment advisor before making investment decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
