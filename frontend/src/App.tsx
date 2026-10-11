import React, { useState, useRef, useEffect } from 'react';
import { 
  Upload, 
  Play, 
  Pause, 
  Copy, 
  Check, 
  RotateCcw, 
  Download,
  AlertCircle
} from 'lucide-react';

interface Evidence {
  excerpt: string;
  rationale: string;
  severity: string;
  indicator_type: string;
}

interface AnalysisResponse {
  risk_level: string;
  summary: string;
  indicators: Evidence[];
  guidance: string;
  limitations: string;
  is_demo?: boolean;
}

export const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [language, setLanguage] = useState<string>('indic-auto');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  // Audio Guidance TTS
  const [ttsAudioUrl, setTtsAudioUrl] = useState<string | null>(null);
  const [ttsPlaying, setTtsPlaying] = useState<boolean>(false);
  const ttsAudioRef = useRef<HTMLAudioElement | null>(null);

  // UX state
  const [copiedTranscript, setCopiedTranscript] = useState<boolean>(false);

  // Update preview URL when file changes
  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [file]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
      setTtsAudioUrl(null);
    }
  };

  const handleAnalyze = async () => {
    setError(null);
    setTtsAudioUrl(null);

    if (!file) {
      setError('Please choose an audio file first.');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio_file', file);
      formData.append('language', language);

      const res = await fetch('http://localhost:8000/api/v1/end-to-end', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(errorData?.detail || `Server returned error status ${res.status}`);
      }

      const data: AnalysisResponse = await res.json();
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Could not connect to backend server. Make sure FastAPI is running on port 8000.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayTts = async () => {
    if (!result?.guidance) return;

    if (ttsAudioUrl && ttsAudioRef.current) {
      if (ttsPlaying) {
        ttsAudioRef.current.pause();
        setTtsPlaying(false);
      } else {
        ttsAudioRef.current.play();
        setTtsPlaying(true);
      }
      return;
    }

    try {
      setTtsPlaying(true);
      const res = await fetch('http://localhost:8000/api/v1/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: result.guidance,
          language: language,
          voice: 'Nalini'
        })
      });

      if (!res.ok) {
        throw new Error('TTS voice synthesis failed');
      }

      const data = await res.json();
      if (data.audio_content) {
        const url = `data:audio/wav;base64,${data.audio_content}`;
        setTtsAudioUrl(url);
        if (ttsAudioRef.current) {
          ttsAudioRef.current.src = url;
          ttsAudioRef.current.play();
        }
      }
    } catch {
      setError('Failed to generate voice guidance.');
      setTtsPlaying(false);
    }
  };

  const handleCopyTranscript = () => {
    if (!result?.summary) return;
    navigator.clipboard.writeText(result.summary);
    setCopiedTranscript(true);
    setTimeout(() => setCopiedTranscript(false), 2000);
  };

  const handleExportJson = () => {
    if (!result) return;
    const data = {
      title: 'VoiceShield Analysis Report',
      date: new Date().toLocaleString(),
      language: language,
      verdict: result.risk_level,
      transcript: result.summary,
      indicators: result.indicators,
      safety_advice: result.guidance
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `voiceshield_report_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setTtsAudioUrl(null);
  };

  // Risk marker: Red if risky, Green if safe, Yellow if caution
  const renderRiskMarker = (level: string) => {
    const norm = (level || '').toUpperCase();
    if (norm === 'HIGH' || norm === 'FRAUD') {
      return (
        <span className="text-xs font-mono font-bold px-3 py-1 rounded border border-red-500 bg-red-500/10 text-red-400 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-red-500"></span>
          HIGH RISK / SCAM DETECTED
        </span>
      );
    }
    if (norm === 'CAUTION' || norm === 'MEDIUM') {
      return (
        <span className="text-xs font-mono font-bold px-3 py-1 rounded border border-yellow-500 bg-yellow-500/10 text-yellow-400 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
          SUSPICIOUS / CAUTION
        </span>
      );
    }
    return (
      <span className="text-xs font-mono font-bold px-3 py-1 rounded border border-green-500 bg-green-500/10 text-green-400 flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-green-500"></span>
        SAFE / NO SCAM DETECTED
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-black text-neutral-100 flex flex-col justify-between font-sans">
      <audio
        ref={ttsAudioRef}
        onEnded={() => setTtsPlaying(false)}
        onPause={() => setTtsPlaying(false)}
        className="hidden"
      />

      {/* Main Content Area */}
      <main className="max-w-2xl w-full mx-auto px-4 py-12">
        {/* Simple Header */}
        <header className="border-b border-neutral-800 pb-6 mb-8">
          <h1 className="text-2xl font-bold tracking-tight text-white">VoiceShield AI</h1>
          <p className="text-sm text-neutral-400 mt-1">
            Scam call detection system for Hindi, Hinglish, and English
          </p>
        </header>

        <div className="space-y-6">
          {/* File Upload Box */}
          <div className="border border-dashed border-neutral-800 rounded-lg p-8 bg-neutral-950 text-center hover:border-neutral-700 transition-colors">
            <input
              type="file"
              id="file-upload"
              accept="audio/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center justify-center space-y-2"
            >
              <Upload className="w-6 h-6 text-neutral-400 mb-1" />
              <span className="text-sm font-medium text-white">
                {file ? file.name : 'Choose an audio file to analyze'}
              </span>
              <span className="text-xs text-neutral-500">
                Supports WAV, MP3, M4A or OGG (Max 25MB)
              </span>
            </label>

            {file && (
              <div className="mt-4 pt-4 border-t border-neutral-900 flex flex-col items-center gap-3">
                <div className="text-xs text-neutral-400">
                  Selected file: <span className="text-white font-mono">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)
                </div>
                {previewUrl && (
                  <audio controls src={previewUrl} className="w-full max-w-md h-9 mt-1" />
                )}
                <button
                  type="button"
                  onClick={() => { setFile(null); setResult(null); setPreviewUrl(null); }}
                  className="text-xs text-neutral-500 hover:text-neutral-300 underline mt-1"
                >
                  Remove file
                </button>
              </div>
            )}
          </div>

          {/* Language Selector & Analyze Button */}
          <div className="border border-neutral-800 rounded-lg p-5 bg-neutral-950 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <label className="text-xs font-medium text-neutral-300 block mb-1.5">
                  Audio Language
                </label>
                <div className="flex flex-wrap gap-2">
                  {[
                    { id: 'indic-auto', label: 'Auto Detect / Hinglish' },
                    { id: 'hi-IN', label: 'Hindi (हिंदी)' },
                    { id: 'en-IN', label: 'English' },
                  ].map((lang) => (
                    <button
                      key={lang.id}
                      type="button"
                      onClick={() => setLanguage(lang.id)}
                      className={`text-xs px-3 py-1.5 rounded border transition-colors ${
                        language === lang.id
                          ? 'border-white bg-white text-black font-medium'
                          : 'border-neutral-800 text-neutral-400 hover:text-white hover:border-neutral-700'
                      }`}
                    >
                      {lang.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex sm:self-end">
                <button
                  type="button"
                  onClick={handleAnalyze}
                  disabled={loading || !file}
                  className="w-full sm:w-auto bg-white text-black text-xs font-semibold px-6 py-2 rounded hover:bg-neutral-200 disabled:opacity-40 disabled:hover:bg-white transition-colors"
                >
                  {loading ? 'Analyzing...' : 'Analyze Audio'}
                </button>
              </div>
            </div>

            {error && (
              <div className="border border-neutral-800 bg-neutral-900/60 p-3 rounded text-xs text-neutral-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-neutral-400 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Analysis Results */}
          {result && (
            <div className="border border-neutral-800 rounded-lg p-6 bg-neutral-950 space-y-6">
              {/* Verdict Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-neutral-800 pb-4 gap-3">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono text-neutral-500 uppercase tracking-wider">
                    Verdict:
                  </span>
                  {renderRiskMarker(result.risk_level)}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleExportJson}
                    className="text-xs text-neutral-400 hover:text-white border border-neutral-800 px-2.5 py-1 rounded hover:border-neutral-700 flex items-center gap-1.5 transition-colors"
                  >
                    <Download className="w-3 h-3" />
                    Export JSON
                  </button>
                  <button
                    type="button"
                    onClick={handleReset}
                    className="text-xs text-neutral-400 hover:text-white border border-neutral-800 px-2.5 py-1 rounded hover:border-neutral-700 flex items-center gap-1.5 transition-colors"
                  >
                    <RotateCcw className="w-3 h-3" />
                    Reset
                  </button>
                </div>
              </div>

              {/* Transcript */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-neutral-400">
                    Transcribed Audio
                  </span>
                  <button
                    type="button"
                    onClick={handleCopyTranscript}
                    className="text-[11px] text-neutral-500 hover:text-neutral-300 flex items-center gap-1"
                  >
                    {copiedTranscript ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    {copiedTranscript ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <div className="bg-neutral-900 border border-neutral-800 rounded p-3.5 text-xs text-neutral-200 font-mono leading-relaxed whitespace-pre-wrap">
                  {result.summary || 'No transcript text available.'}
                </div>
              </div>

              {/* Scam Indicators */}
              <div className="space-y-2">
                <span className="text-xs font-medium text-neutral-400 block">
                  Scam Indicators ({result.indicators.length})
                </span>

                {result.indicators.length === 0 ? (
                  <p className="text-xs text-neutral-500 italic bg-neutral-900/40 p-3 rounded border border-neutral-900">
                    No scam patterns, threats, or OTP requests were detected in this call.
                  </p>
                ) : (
                  <div className="space-y-2.5">
                    {result.indicators.map((ind, i) => (
                      <div
                        key={i}
                        className="border border-neutral-800 rounded p-3.5 bg-neutral-900/60 space-y-1.5 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-neutral-300 font-medium text-[11px]">
                            {ind.indicator_type}
                          </span>
                          <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                            ind.severity === 'HIGH' 
                              ? 'border-red-500/50 text-red-400 bg-red-950/20' 
                              : 'border-neutral-800 text-neutral-500'
                          }`}>
                            {ind.severity}
                          </span>
                        </div>
                        <div className="text-neutral-300 font-serif italic pl-2 border-l-2 border-neutral-700">
                          "{ind.excerpt}"
                        </div>
                        <p className="text-neutral-400 text-[11px]">
                          {ind.rationale}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recommended Action & Voice Advice */}
              <div className="space-y-2 border-t border-neutral-800 pt-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-neutral-400">
                    Recommended Action
                  </span>
                  <button
                    type="button"
                    onClick={handlePlayTts}
                    className="text-xs border border-neutral-800 hover:border-neutral-600 px-2.5 py-1 rounded text-neutral-300 hover:text-white flex items-center gap-1.5 transition-colors"
                  >
                    {ttsPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                    {ttsPlaying ? 'Pause Audio' : 'Play Voice Advice'}
                  </button>
                </div>

                <div className="bg-neutral-900 border border-neutral-800 rounded p-3.5 text-xs text-neutral-300 leading-relaxed">
                  {result.guidance}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Clean Minimalist Footer */}
      <footer className="border-t border-neutral-800 py-6 text-center text-xs text-neutral-600">
        VoiceShield AI
      </footer>
    </div>
  );
};

export default App;
