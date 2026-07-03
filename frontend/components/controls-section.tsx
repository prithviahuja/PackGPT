'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Loader2, Sparkles, Code2, Eye, EyeOff } from 'lucide-react';

interface ControlsSectionProps {
  onCompress: () => void;
  onExtract: () => void;
  loading?: boolean;
  disabled?: boolean;
  apiKey?: string;
  onApiKeyChange?: (key: string) => void;
  model?: string;
  onModelChange?: (model: string) => void;
}

// Models the backend can actually serve. Each can run on the server-side key
// or on a personal key of the matching provider (Gemini or Groq) if supplied.
const DEFAULT_MODELS = [
  {
    id: 'gemini-3-flash-preview',
    label: 'Gemini 3 Flash',
    description: 'Large context support, detailed results',
    keyHint: 'Uses server Gemini key (or your Gemini key)',
  },
  {
    id: 'llama-3.3-70b-versatile',
    label: 'Llama 3.3 70B',
    description: 'Fast & concise results',
    keyHint: 'Uses server Groq key (or your Groq key)',
  },
];

export function ControlsSection({
  onCompress,
  onExtract,
  loading = false,
  disabled = false,
  apiKey = '',
  onApiKeyChange,
  model = 'gemini-3-flash-preview',
  onModelChange,
}: ControlsSectionProps) {
  const [showApiKey, setShowApiKey] = useState(false);

  const hasPersonalKey = apiKey.trim().length > 0;
  const allModels = DEFAULT_MODELS;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        onCompress();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onCompress]);

  const selectedModel = allModels.find((m) => m.id === model) || allModels[0];

  return (
    <div className="glass-card space-y-4 p-5 glow-effect-sm h-full flex flex-col">
      <div className="space-y-4 flex-1">
        {/* Model Selection */}
        <div>
          <label className="text-sm font-medium text-foreground/90 mb-2 block">Model</label>
          <select
            value={model}
            onChange={(e) => onModelChange?.(e.target.value)}
            disabled={disabled || loading}
            className="w-full px-3 py-2.5 rounded-lg border border-white/[0.08] bg-white/[0.02] text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-[#e94560]/50 focus:border-[#e94560]/50 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm smooth-transition hover:border-white/[0.12]"
          >
            {DEFAULT_MODELS.map((m) => (
              <option key={m.id} value={m.id} className="bg-[#161b22] text-foreground">
                {m.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-muted-foreground mt-1.5">{selectedModel?.description}</p>
        </div>

        {/* API Key */}
        {onApiKeyChange && (
          <div>
            <label className="text-sm font-medium text-foreground/90 mb-2 block">
              API Key <span className="text-muted-foreground font-normal">(Optional)</span>
            </label>
            <div className="flex gap-2">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => onApiKeyChange(e.target.value)}
                disabled={disabled || loading}
                placeholder="Enter your API key"
                className="flex-1 px-3 py-2.5 rounded-lg border border-white/[0.08] bg-white/[0.02] text-foreground text-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-[#e94560]/50 focus:border-[#e94560]/50 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm smooth-transition hover:border-white/[0.12]"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowApiKey(!showApiKey)}
                disabled={disabled || loading}
                className="px-3 border-white/[0.08] hover:border-white/[0.12] hover:bg-white/[0.05]"
              >
                {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-1.5">
              {hasPersonalKey
                ? 'Using your personal key for the selected provider (Gemini or Groq)'
                : 'Uses server-side key if left blank'}
            </p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 gap-3 pt-4 border-t border-white/[0.08]">
        <Button
          onClick={onCompress}
          disabled={disabled || loading}
          size="lg"
          className="gap-2 bg-gradient-to-r from-[#e94560] to-[#ff6b81] hover:from-[#ff6b81] hover:to-[#e94560] text-white font-medium shadow-lg hover:shadow-[0_0_20px_rgba(233,69,96,0.4)] smooth-transition hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Compressing...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Compress
            </>
          )}
        </Button>

        <Button
          onClick={onExtract}
          disabled={disabled || loading}
          size="lg"
          className="gap-2 border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.05] hover:border-[#0f3460]/50 text-foreground smooth-transition hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Extracting...
            </>
          ) : (
            <>
              <Code2 className="w-4 h-4" />
              Extract JSON
            </>
          )}
        </Button>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        💡 Press{' '}
        <kbd className="px-2 py-1 rounded-md bg-white/[0.05] border border-white/[0.08] font-mono text-xs">
          Ctrl + Enter
        </kbd>{' '}
        to compress
      </p>
    </div>
  );
}
