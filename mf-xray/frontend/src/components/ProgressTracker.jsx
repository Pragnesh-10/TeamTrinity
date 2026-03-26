import React from 'react';
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export default function ProgressTracker({ currentStep, label, progress }) {
  const steps = [
    "Parse PDF",
    "Build FIFO Ledger",
    "Compute XIRR",
    "Overlap Analysis",
    "Rebalancing & LLM"
  ];

  return (
    <div className="w-full max-w-2xl mx-auto mt-8 p-6 bg-surface rounded-xl border border-border">
      <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-teal animate-pulse"></span>
        Pipeline Active
      </h3>
      
      <div className="relative">
        <div className="absolute top-4 left-4 right-4 h-0.5 bg-border z-0">
          <div 
            className="h-full bg-teal transition-all duration-500 ease-in-out" 
            style={{ width: `${Math.min(100, Math.max(0, ((currentStep - 1) / (steps.length - 1)) * 100))}%` }}
          ></div>
        </div>
        
        <div className="flex justify-between relative z-10">
          {steps.map((stepName, i) => {
            const stepNum = i + 1;
            const isCompleted = currentStep > stepNum;
            const isActive = currentStep === stepNum;
            const isPending = currentStep < stepNum;
            
            return (
              <div key={stepNum} className="flex flex-col items-center w-24">
                <div 
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center font-mono text-sm border-2 transition-colors duration-300",
                    isCompleted ? "bg-teal border-teal text-background" : 
                    isActive ? "bg-background border-teal text-teal animate-pulse" : 
                    "bg-surface border-border text-gray-500"
                  )}
                >
                  {isCompleted ? "✓" : stepNum}
                </div>
                <div className={cn(
                  "text-xs mt-3 text-center whitespace-nowrap",
                  isActive || isCompleted ? "text-white" : "text-gray-500"
                )}>
                  {stepName}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      <div className="mt-8 pt-6 border-t border-border flex flex-col items-center">
        <p className="text-md text-gray-300 mb-3">{label}</p>
        <div className="w-full h-2 bg-background rounded-full overflow-hidden border border-border">
          <div 
            className="h-full bg-teal transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
