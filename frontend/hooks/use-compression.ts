import { useState, useCallback } from 'react';

export interface CompressionResult {
  context_pack: string;
  structured: {
    goal?: string;
    tech_stack?: string[];
    key_decisions?: string[];
    problems_faced?: string[];
    solutions_applied?: string[];
    code_snippets?: { label: string; code: string }[];
  };
  token_count?: number;
  compression_ratio?: number;
  processing_time?: number;
}

export interface CompressionState {
  loading: boolean;
  error: string | null;
  result: CompressionResult | null;
}

export function useCompression() {
  const [state, setState] = useState<CompressionState>({
    loading: false,
    error: null,
    result: null,
  });

  const compress = useCallback(async (input: string, model?: string, apiKey?: string) => {
    if (!input.trim()) {
      setState({ loading: false, error: 'Please enter some text to compress', result: null });
      return null;
    }

    setState({ loading: true, error: null, result: null });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const body: Record<string, string> = {
        input,
        model: model || 'gemini-3-flash-preview',
      };
      if (apiKey && apiKey.trim()) body.api_key = apiKey.trim();

      const response = await fetch(`${apiUrl}/compress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `API error: ${response.statusText}`);
      }

      const data: CompressionResult = await response.json();
      setState({ loading: false, error: null, result: data });
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to compress text';
      setState({ loading: false, error: errorMessage, result: null });
      return null;
    }
  }, []);

  const extractJson = useCallback(async (input: string, model?: string, apiKey?: string) => {
    if (!input.trim()) {
      setState({ loading: false, error: 'Please enter some text', result: null });
      return null;
    }

    setState({ loading: true, error: null, result: null });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const body: Record<string, string> = {
        input,
        model: model || 'gemini-3-flash-preview',
      };
      if (apiKey && apiKey.trim()) body.api_key = apiKey.trim();

      const response = await fetch(`${apiUrl}/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `API error: ${response.statusText}`);
      }

      const data: CompressionResult = await response.json();
      setState({ loading: false, error: null, result: data });
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to extract JSON';
      setState({ loading: false, error: errorMessage, result: null });
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, result: null });
  }, []);

  return { ...state, compress, extractJson, reset };
}
