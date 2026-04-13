'use client';

import { useState, useEffect } from 'react';
import { InputSection } from '@/components/input-section';
import { ControlsSection } from '@/components/controls-section';
import { ResultsDisplay } from '@/components/results-display';
import { HistorySidebar, HistoryItem } from '@/components/history-sidebar';
import { useCompression } from '@/hooks/use-compression';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

const STORAGE_KEY = 'compression-engine';

export default function Page() {
  const [input, setInput] = useState('');
  const [model, setModel] = useState('gemini-3-flash-preview');
  const [apiKey, setApiKey] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string>();
  const { loading, error, result, compress, extractJson, reset } = useCompression();
  const { toast } = useToast();

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const { input: savedInput, history: savedHistory, model: savedModel, apiKey: savedApiKey } = JSON.parse(stored);
        setInput(savedInput || '');
        setHistory(savedHistory || []);
        setModel(savedModel || 'gemini-3-flash-preview');
        setApiKey(savedApiKey || '');
      } catch (e) {
        console.error('[CCE] Failed to load from localStorage:', e);
      }
    }
  }, []);

  // Save to localStorage on state change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ input, history, model, apiKey }));
  }, [input, history, model, apiKey]);

  // Show errors as toasts
  useEffect(() => {
    if (error) {
      toast({ title: 'Error', description: error, variant: 'destructive', duration: 5000 });
    }
  }, [error, toast]);

  const handleCompress = async () => {
    const res = await compress(input, model, apiKey);
    if (res) addToHistory(input, res);
  };

  const handleExtract = async () => {
    const res = await extractJson(input, model, apiKey);
    if (res) addToHistory(input, res);
  };

  const addToHistory = (inputText: string, res: any) => {
    const id = Date.now().toString();
    const preview = inputText.substring(0, 50).replace(/\n/g, ' ') + (inputText.length > 50 ? '...' : '');
    const newItem: HistoryItem = { id, input: inputText, result: res, timestamp: Date.now(), preview };
    setHistory((prev) => [newItem, ...prev.slice(0, 19)]);
    setSelectedHistoryId(id);
  };

  const handleSelectHistory = (item: HistoryItem) => {
    setInput(item.input);
    setSelectedHistoryId(item.id);
  };

  const handleClearHistory = (id: string) => {
    setHistory((prev) => prev.filter((item) => item.id !== id));
    if (selectedHistoryId === id) setSelectedHistoryId(undefined);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex relative">
      {/* Ambient background glows */}
      <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-0 w-[600px] h-[600px] rounded-full blur-3xl opacity-[0.07] bg-[#e94560]" />
        <div className="absolute bottom-1/3 right-0 w-[500px] h-[500px] rounded-full blur-3xl opacity-[0.07] bg-[#0f3460]" />
      </div>

      {/* History Sidebar — desktop only */}
      <div className="hidden lg:flex w-64 border-r border-white/[0.08] flex-shrink-0">
        <HistorySidebar
          history={history}
          onSelect={handleSelectHistory}
          onClear={handleClearHistory}
          onClearAll={() => { setHistory([]); setSelectedHistoryId(undefined); }}
          selectedId={selectedHistoryId}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-4 md:p-8 max-w-6xl mx-auto space-y-8">

          {/* Header */}
          <div className="space-y-2 animate-in fade-in-50 duration-500">
            <h1 className="text-3xl md:text-5xl font-extrabold gradient-text tracking-tight">Pack GPT</h1>
            <p className="text-muted-foreground/90 text-lg font-medium">Context Compression Engine</p>
          </div>

          {/* Input + Controls — always landscape: textarea left (2/3), controls right (1/3) */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in-50 duration-500">
            {/* Left: Textarea */}
            <div className="lg:col-span-2 space-y-4">
              <InputSection
                value={input}
                onChange={setInput}
                onSampleInput={() => {}}
                disabled={loading}
              />

              {/* Loading spinner inside the left column */}
              {loading && (
                <div className="glass-card flex items-center justify-center py-12 glow-effect">
                  <div className="flex flex-col items-center gap-3">
                    <Loader2 className="w-9 h-9 animate-spin text-[#e94560]" />
                    <p className="text-sm text-muted-foreground/90">Processing your input…</p>
                  </div>
                </div>
              )}
            </div>

            {/* Right: Controls */}
            <div className="lg:col-span-1">
              <ControlsSection
                onCompress={handleCompress}
                onExtract={handleExtract}
                loading={loading}
                disabled={!input.trim() || loading}
                model={model}
                onModelChange={setModel}
                apiKey={apiKey}
                onApiKeyChange={setApiKey}
              />
            </div>
          </div>

          {/* Results */}
          {!loading && result && (
            <div className="animate-in fade-in-50 duration-500">
              <ResultsDisplay result={result} />
            </div>
          )}

          {/* Mobile history hint */}
          <div className="lg:hidden">
            <button
              onClick={() => toast({ description: 'History sidebar is available on desktop view', duration: 3000 })}
              className="text-sm text-[#e94560] hover:text-[#ff6b81] hover:underline smooth-transition"
            >
              View History
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
