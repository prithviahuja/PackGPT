'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Copy, Download, ChevronDown, ChevronUp } from 'lucide-react';
import { CompressionResult } from '@/hooks/use-compression';
import { useToast } from '@/hooks/use-toast';

interface ResultsDisplayProps {
  result: CompressionResult | null;
}

interface StatCardProps {
  label: string;
  value: string | number;
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="glass-card p-4 glow-effect hover:border-[#e94560]/50 hover:shadow-[0_0_15px_rgba(233,69,96,0.2)] smooth-transition group cursor-default">
      <div className="text-xs text-muted-foreground/80 mb-2 font-medium uppercase tracking-wide">{label}</div>
      <div className="text-2xl font-bold bg-gradient-to-r from-[#e94560] to-[#ff6b81] bg-clip-text text-transparent group-hover:from-[#ff6b81] group-hover:to-[#e94560] smooth-transition">{value}</div>
    </div>
  );
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const { toast } = useToast();
  const [expandedSections, setExpandedSections] = useState<string[]>(['goal', 'tech_stack']);

  if (!result) {
    return (
      <Card className="p-8 text-center border-dashed">
        <div className="text-muted-foreground">
          <p className="text-sm">No compression results yet.</p>
          <p className="text-xs mt-1">Enter text and click &quot;Compress&quot; to get started.</p>
        </div>
      </Card>
    );
  }

  const toggleSection = (section: string) => {
    setExpandedSections((prev) =>
      prev.includes(section) ? prev.filter((s) => s !== section) : [...prev, section]
    );
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast({
      description: `${label} copied to clipboard`,
      duration: 2000,
    });
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadContextPack = () => {
    downloadFile(result.context_pack, 'context-pack.txt', 'text/plain');
    toast({ description: 'Context Pack downloaded', duration: 2000 });
  };

  const handleDownloadJSON = () => {
    const jsonContent = JSON.stringify(result.structured, null, 2);
    downloadFile(jsonContent, 'structured-data.json', 'application/json');
    toast({ description: 'JSON downloaded', duration: 2000 });
  };

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-500">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Token Count" value={result.token_count || '-'} />
        <StatCard label="Compression Ratio" value={`${result.compression_ratio?.toFixed(1)}x` || '-'} />
        <StatCard label="Processing Time" value={`${result.processing_time?.toFixed(1)}s` || '-'} />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="context-pack" className="space-y-4">
        <TabsList className="w-full grid grid-cols-2 lg:grid-cols-4 bg-white/[0.02] border border-white/[0.08] rounded-lg p-1">
          <TabsTrigger value="context-pack" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-[#e94560] data-[state=active]:to-[#ff6b81] data-[state=active]:text-white data-[state=active]:shadow-md data-[state=active]:glow-effect-sm rounded-md smooth-transition">Context Pack</TabsTrigger>
          <TabsTrigger value="structured" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-[#e94560] data-[state=active]:to-[#ff6b81] data-[state=active]:text-white data-[state=active]:shadow-md data-[state=active]:glow-effect-sm rounded-md smooth-transition">Structured</TabsTrigger>
          <TabsTrigger value="code" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-[#e94560] data-[state=active]:to-[#ff6b81] data-[state=active]:text-white data-[state=active]:shadow-md data-[state=active]:glow-effect-sm rounded-md smooth-transition">Code</TabsTrigger>
          <TabsTrigger value="json" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-[#e94560] data-[state=active]:to-[#ff6b81] data-[state=active]:text-white data-[state=active]:shadow-md data-[state=active]:glow-effect-sm rounded-md smooth-transition">JSON</TabsTrigger>
        </TabsList>

        {/* Context Pack Tab */}
        <TabsContent value="context-pack" className="space-y-3 animate-in fade-in-50 duration-300">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-foreground text-sm">Context Pack</h3>
            <div className="flex-1" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(result.context_pack, 'Context Pack')}
              className="h-8 w-8 p-0 hover:bg-white/[0.05] hover:text-[#e94560]"
            >
              <Copy className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDownloadContextPack}
              className="h-8 w-8 p-0 hover:bg-white/[0.05] hover:text-[#e94560]"
            >
              <Download className="w-4 h-4" />
            </Button>
          </div>
          <div className="glass-card max-h-96 overflow-y-auto p-4 glow-effect-sm">
            <pre className="text-xs text-foreground/90 whitespace-pre-wrap break-words font-mono">
              {result.context_pack}
            </pre>
          </div>
        </TabsContent>

        {/* Structured Tab */}
        <TabsContent value="structured" className="space-y-3">
          <div className="space-y-3">
            {result.structured.goal && (
              <ExpandableSection
                title="Goal"
                content={result.structured.goal}
                isExpanded={expandedSections.includes('goal')}
                onToggle={() => toggleSection('goal')}
                onCopy={() => copyToClipboard(result.structured.goal || '', 'Goal')}
              />
            )}

            {result.structured.tech_stack && result.structured.tech_stack.length > 0 && (
              <ExpandableSection
                title="Tech Stack"
                content={result.structured.tech_stack.join(', ')}
                isExpanded={expandedSections.includes('tech_stack')}
                onToggle={() => toggleSection('tech_stack')}
                onCopy={() => copyToClipboard(result.structured.tech_stack?.join(', ') || '', 'Tech Stack')}
              />
            )}

            {result.structured.key_decisions && result.structured.key_decisions.length > 0 && (
              <ExpandableSection
                title="Key Decisions"
                content={result.structured.key_decisions.map((d, i) => `${i + 1}. ${d}`).join('\n')}
                isExpanded={expandedSections.includes('key_decisions')}
                onToggle={() => toggleSection('key_decisions')}
                onCopy={() =>
                  copyToClipboard(
                    result.structured.key_decisions?.map((d, i) => `${i + 1}. ${d}`).join('\n') || '',
                    'Key Decisions'
                  )
                }
              />
            )}

            {result.structured.problems_faced && result.structured.problems_faced.length > 0 && (
              <ExpandableSection
                title="Problems Faced"
                content={result.structured.problems_faced.map((p, i) => `${i + 1}. ${p}`).join('\n')}
                isExpanded={expandedSections.includes('problems_faced')}
                onToggle={() => toggleSection('problems_faced')}
                onCopy={() =>
                  copyToClipboard(
                    result.structured.problems_faced?.map((p, i) => `${i + 1}. ${p}`).join('\n') || '',
                    'Problems Faced'
                  )
                }
              />
            )}

            {result.structured.solutions_applied && result.structured.solutions_applied.length > 0 && (
              <ExpandableSection
                title="Solutions Applied"
                content={result.structured.solutions_applied.map((s, i) => `${i + 1}. ${s}`).join('\n')}
                isExpanded={expandedSections.includes('solutions_applied')}
                onToggle={() => toggleSection('solutions_applied')}
                onCopy={() =>
                  copyToClipboard(
                    result.structured.solutions_applied?.map((s, i) => `${i + 1}. ${s}`).join('\n') || '',
                    'Solutions Applied'
                  )
                }
              />
            )}
          </div>
        </TabsContent>

        {/* Code Tab */}
        <TabsContent value="code" className="space-y-3 animate-in fade-in-50 duration-300">
          {result.structured.code_snippets && result.structured.code_snippets.length > 0 ? (
            <div className="space-y-3">
              {result.structured.code_snippets.map((snippet, i) => (
                <div key={i} className="glass-card p-4 glow-effect-sm">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-mono text-sm font-semibold text-[#e94560]">{snippet.label || `Snippet ${i + 1}`}</h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(snippet.code, snippet.label || `Code Snippet ${i + 1}`)}
                      className="h-8 w-8 p-0 hover:bg-white/[0.05] hover:text-[#e94560]"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                  <pre className="bg-white/[0.02] border border-white/[0.08] p-4 rounded-lg text-xs text-foreground/90 overflow-x-auto font-mono">
                    {snippet.code}
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card p-8 text-center">
              <p className="text-sm text-muted-foreground">No code snippets found in the compression.</p>
            </div>
          )}
        </TabsContent>

        {/* JSON Tab */}
        <TabsContent value="json" className="space-y-3 animate-in fade-in-50 duration-300">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-foreground text-sm">Structured Data (JSON)</h3>
            <div className="flex-1" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(JSON.stringify(result.structured, null, 2), 'JSON')}
              className="h-8 w-8 p-0 hover:bg-white/[0.05] hover:text-[#e94560]"
            >
              <Copy className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDownloadJSON}
              className="h-8 w-8 p-0 hover:bg-white/[0.05] hover:text-[#e94560]"
            >
              <Download className="w-4 h-4" />
            </Button>
          </div>
          <div className="glass-card max-h-96 overflow-y-auto p-4 glow-effect-sm">
            <pre className="text-xs text-foreground/90 whitespace-pre-wrap break-words font-mono">
              {JSON.stringify(result.structured, null, 2)}
            </pre>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

interface ExpandableSectionProps {
  title: string;
  content: string;
  isExpanded: boolean;
  onToggle: () => void;
  onCopy: () => void;
}

function ExpandableSection({ title, content, isExpanded, onToggle, onCopy }: ExpandableSectionProps) {
  return (
    <div className="glass-card overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-white/[0.05] smooth-transition group"
      >
        <h4 className="font-semibold text-foreground text-sm group-hover:text-[#e94560]">{title}</h4>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-muted-foreground group-hover:text-[#e94560]" />
        ) : (
          <ChevronDown className="w-4 h-4 text-muted-foreground group-hover:text-[#e94560]" />
        )}
      </button>
      {isExpanded && (
        <div className="border-t border-white/[0.08] px-4 py-3 animate-in fade-in-50 duration-300">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-muted-foreground/60"></span>
            <Button variant="ghost" size="sm" onClick={onCopy} className="h-8 w-8 p-0 hover:bg-white/[0.05] hover:text-[#e94560]">
              <Copy className="w-4 h-4" />
            </Button>
          </div>
          <pre className="text-xs text-foreground/90 whitespace-pre-wrap break-words font-mono bg-white/[0.02] border border-white/[0.08] p-3 rounded-lg">
            {content}
          </pre>
        </div>
      )}
    </div>
  );
}
