'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Trash2, Upload } from 'lucide-react';

interface InputSectionProps {
  value: string;
  onChange: (value: string) => void;
  onSampleInput: () => void;
  disabled?: boolean;
}

const SAMPLE_INPUT = `I've been working on optimizing our Next.js application for the past week. The main issue was that our pages were taking too long to load. I analyzed the bundle size and realized we had some unnecessary dependencies. I removed three packages that weren't being used and updated the others to their latest versions.

Then I implemented code splitting using dynamic imports for routes that weren't critical on initial load. I also added Image optimization with Next.js Image component which reduced our initial payload by about 40%. 

The key decision was whether to use ISR or dynamic rendering. ISR works better for content that doesn't change frequently, so I applied that to our blog pages. For user-specific pages, I used dynamic rendering with proper caching headers.

I faced some challenges with third-party scripts initially. They were blocking the main thread. I moved them to web workers and used the next/script component with the worker strategy.

Finally, I set up performance monitoring with Web Vitals and configured alerts when metrics degrade. This will help us catch regressions early.`;

export function InputSection({ value, onChange, onSampleInput, disabled = false }: InputSectionProps) {
  const [charCount, setCharCount] = useState(value.length);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setCharCount(newValue.length);
    autoResizeTextarea();
  };

  const autoResizeTextarea = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 400)}px`;
    }
  };

  const handleClear = () => {
    onChange('');
    setCharCount(0);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleLoadSample = () => {
    onChange(SAMPLE_INPUT);
    setCharCount(SAMPLE_INPUT.length);
    setTimeout(autoResizeTextarea, 0);
    onSampleInput();
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload file');
        }

        const data = await response.json();
        const content = data.text;
        onChange(content);
        setCharCount(content.length);
        setTimeout(autoResizeTextarea, 0);
      } catch (err) {
        console.error('File upload error:', err);
        alert('Failed to upload/process file. Please try again.');
      }
    }
  };

  const showWarning = charCount > 10000;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground/90">
          Paste your chat conversation or development notes
        </label>
        <div className="text-xs text-muted-foreground">
          {charCount.toLocaleString()} {showWarning && <span className="text-orange-400 ml-2 font-medium">(Large input)</span>}
        </div>
      </div>

      <div className="relative group">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          disabled={disabled}
          placeholder="Paste your context here... or click 'Try Sample Input' to see an example"
          className="w-full min-h-[180px] max-h-[400px] p-4 rounded-xl border border-white/[0.08] bg-white/[0.02] text-foreground placeholder-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-[#e94560]/50 focus:border-[#e94560]/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm group-hover:border-white/[0.12]"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          onClick={handleLoadSample}
          disabled={disabled}
          variant="outline"
          size="sm"
          className="gap-2 border-white/[0.08] hover:border-white/[0.12] hover:bg-white/[0.05] smooth-transition"
        >
          <Upload className="w-4 h-4" />
          Try Sample Input
        </Button>

        <label>
          <input
            type="file"
            accept=".txt,.md,.log"
            onChange={handleFileUpload}
            disabled={disabled}
            className="hidden"
          />
          <Button
            onClick={(e) => {
              e.preventDefault();
              (e.currentTarget as HTMLElement).parentElement?.querySelector('input')?.click();
            }}
            disabled={disabled}
            variant="outline"
            size="sm"
            asChild
            className="gap-2 cursor-pointer border-white/[0.08] hover:border-white/[0.12] hover:bg-white/[0.05] smooth-transition"
          >
            <span>
              <Upload className="w-4 h-4" />
              Upload File
            </span>
          </Button>
        </label>

        {value && (
          <Button
            onClick={handleClear}
            disabled={disabled}
            variant="outline"
            size="sm"
            className="gap-2 border-white/[0.08] hover:border-red-500/30 text-orange-400 hover:text-orange-300 hover:bg-red-500/5 smooth-transition"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </Button>
        )}
      </div>
    </div>
  );
}
