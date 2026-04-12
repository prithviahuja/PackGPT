'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Trash2, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import { CompressionResult } from '@/hooks/use-compression';

export interface HistoryItem {
  id: string;
  input: string;
  result: CompressionResult;
  timestamp: number;
  preview: string;
}

interface HistorySidebarProps {
  history: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
  onClear: (id: string) => void;
  onClearAll: () => void;
  selectedId?: string;
}

export function HistorySidebar({
  history,
  onSelect,
  onClear,
  onClearAll,
  selectedId,
}: HistorySidebarProps) {
  const [isOpen, setIsOpen] = useState(true);

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="flex flex-col h-full bg-white/[0.02] border-r border-white/[0.08] backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/[0.08]">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 text-sm font-semibold text-foreground hover:text-[#e94560] smooth-transition"
        >
          <Clock className="w-4 h-4" />
          History
          {isOpen ? <ChevronUp className="w-4 h-4 ml-auto" /> : <ChevronDown className="w-4 h-4 ml-auto" />}
        </button>
      </div>

      {/* History List */}
      {isOpen && (
        <div className="flex-1 overflow-y-auto space-y-2 p-3">
          {history.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-xs text-muted-foreground">No history yet</p>
              <p className="text-xs text-muted-foreground/60 mt-1">Your compressions will appear here</p>
            </div>
          ) : (
            <>
              {history.map((item) => (
                <div
                  key={item.id}
                  onClick={() => onSelect(item)}
                  className={`glass-card p-3 cursor-pointer smooth-transition hover:border-[#e94560]/50 group ${
                    selectedId === item.id ? 'border-[#e94560]/50 bg-[#e94560]/10 glow-effect-sm' : 'hover:bg-white/[0.05] border-white/[0.08]'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs text-muted-foreground/90 line-clamp-2 group-hover:text-foreground">{item.preview}</p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onClear(item.id);
                        }}
                        className="h-6 w-6 p-0 hover:bg-red-500/20 hover:text-orange-400 opacity-0 group-hover:opacity-100 smooth-transition"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground/60">{formatTime(item.timestamp)}</p>
                  </div>
                </div>
              ))}

              {history.length > 0 && (
                <Button
                  onClick={onClearAll}
                  variant="outline"
                  size="sm"
                  className="w-full text-xs text-orange-400 hover:text-orange-300 hover:bg-red-500/10 border-white/[0.08] hover:border-red-500/30 mt-2 smooth-transition"
                >
                  Clear All History
                </Button>
              )}
            </>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="border-t border-white/[0.08] p-3 text-xs text-muted-foreground/60 text-center">
        {history.length > 0 && <p>{history.length} compression{history.length !== 1 ? 's' : ''}</p>}
      </div>
    </div>
  );
}
