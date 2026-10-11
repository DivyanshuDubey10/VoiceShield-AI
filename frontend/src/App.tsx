import React, { useState, useRef } from 'react';
import { Shield, Upload, AlertTriangle, CheckCircle, Info, Mic, Volume2, AlertCircle } from 'lucide-react';

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

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState('en-IN');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setResult(null);
      setAudioUrl(null);
      setErrorMessage(null);
    }
  };

  const handleAnalyze = async () => {
    setErrorMessage(null);
    setAudioUrl(null);

    // If no file uploaded, provide an explicit offline demonstration scenario
    if (!file) {
      setIsAnalyzing(true);
      setTimeout(() => {
        setResult({
          risk_level: 'HIGH',
          summary: '[DEMO MODE] "Hello, calling from your bank. Please share the OTP sent to your phone immediately to block the fraudulent transaction."',
          indicators: [
            { indicator_type: 'OTP_REQUEST', excerpt: 'Please share the OTP sent to your phone', rationale: 'Explicit request to disclose a one-time password or PIN.', severity: 'HIGH' },
            { indicator_type: 'PAYMENT_PRESSURE', excerpt: 'immediately to block the fraudulent transaction', rationale: 'Creating false urgency or threatening account action to force payment.', severity: 'HIGH' }
          ],
          guidance: 'Warning. High-risk indicators detected. Never share your OTP, PIN, or password with anyone, even if they claim to be from the bank. Hang up immediately and contact your institution directly using their official verified phone number.',
          limitations: 'Advisory analysis based on pattern matching. Does not definitively authenticate callers or prove fraud.',
          is_demo: true
        });
        setIsAnalyzing(false);
      }, 1000);
      return;
    }

    setIsAnalyzing(true);
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
        const detail = errorData?.detail || `Analysis request failed with status ${res.status}`;
        throw new Error(detail);
      }

      const data: AnalysisResponse = await res.json();
      setResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to connect to backend.';
      setErrorMessage(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const playGuidance = async () => {
    if (!result?.guidance) return;
    
    if (audioUrl) {
      if (audioRef.current) {
        audioRef.current.play();
        setIsPlaying(true);
      }
      return;
    }

    try {
      setIsPlaying(true);
      const res = await fetch('http://localhost:8000/api/v1/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: result.guidance, language })
      });
      
      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || 'Speech synthesis failed');
      }

      const data = await res.json();
      if (data.audio_content) {
        const url = `data:audio/wav;base64,${data.audio_content}`;
        setAudioUrl(url);
        if (audioRef.current) {
          audioRef.current.src = url;
          audioRef.current.play();
        }
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to synthesize guidance.';
      setErrorMessage(message);
      setIsPlaying(false);
    }
  };

  const isDemo = Boolean(result?.is_demo || result?.summary.includes('[DEMO MODE]'));

  return (
    <div className="max-w-6xl mx-auto p-6 font-sans">
      <header className="flex items-center gap-3 mb-10 border-b border-slate-800 pb-6">
        <Shield className="w-10 h-10 text-brand" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">VoiceShield <span className="text-brand">AI</span></h1>
          <p className="text-slate-400 text-sm">Multilingual Voice Scam Intelligence and Prevention System</p>
        </div>
      </header>

      {errorMessage && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-200">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-400" />
          <p className="text-sm font-medium">{errorMessage}</p>
        </div>
      )}

      <main className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section className="space-y-6">
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5 text-brand" /> Upload Recording
            </h2>
            <div className="space-y-4">
              <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-brand transition-colors">
                <input type="file" id="audio" accept="audio/*" onChange={handleFileChange} className="hidden" />
                <label htmlFor="audio" className="cursor-pointer flex flex-col items-center">
                  <Mic className="w-12 h-12 text-slate-500 mb-3" />
                  <span className="text-slate-300 font-medium">Click to upload suspicious audio</span>
                  <span className="text-slate-500 text-sm mt-1">Supports WAV, MP3 (Max 20MB)</span>
                </label>
                {file && <p className="mt-4 text-brand font-medium">Selected: {file.name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Primary Language (Gnani Prisma)</label>
                <select 
                  value={language} 
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-brand"
                >
                  <option value="en-IN">English (India)</option>
                  <option value="hi-IN">Hindi (हिंदी)</option>
                  <option value="indic-auto">Hinglish / Auto-Detect (indic-auto)</option>
                </select>
              </div>

              <button 
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="w-full bg-brand/10 text-brand border border-brand/30 hover:bg-brand/20 font-semibold py-3 px-4 rounded-lg transition-all disabled:opacity-50"
              >
                {isAnalyzing ? 'Analyzing with VoiceShield AI...' : (file ? 'Analyze Recording' : 'Run Demo Analysis')}
              </button>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <Info className="w-5 h-5 text-slate-400" /> Methodology & Privacy
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">
              VoiceShield AI transcribes calls and uses explainable, rule-based indicators to detect social-engineering tactics. 
              Audio data is processed ephemerally and never written to permanent disk storage.
            </p>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
              <p className="text-xs text-slate-500 italic">
                Disclaimer: VoiceShield is an advisory educational tool. It highlights high-risk patterns but does not prove caller identity or verify legal fraud. Always verify directly through verified official channels.
              </p>
            </div>
          </div>
        </section>

        <section>
          {result ? (
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-700 pb-4">
                <div className="flex items-center gap-2">
                  <h2 className="text-2xl font-bold">Analysis Results</h2>
                  {isDemo && (
                    <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded font-mono font-medium">
                      DEMO MODE
                    </span>
                  )}
                </div>
                <div className={`px-4 py-2 rounded-full font-bold flex items-center gap-2 ${
                  result.risk_level === 'HIGH' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                  result.risk_level === 'CAUTION' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : 
                  'bg-green-500/20 text-green-400 border border-green-500/30'
                }`}>
                  {result.risk_level === 'HIGH' && <AlertTriangle className="w-5 h-5" />}
                  {result.risk_level === 'LOW' && <CheckCircle className="w-5 h-5" />}
                  RISK: {result.risk_level}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Transcript Summary</h3>
                <p className="text-slate-300 italic bg-slate-900 p-4 rounded-lg border border-slate-700 leading-relaxed">
                  {result.summary}
                </p>
              </div>

              {result.indicators.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Detected Evidence</h3>
                  <div className="space-y-3">
                    {result.indicators.map((ind, i) => (
                      <div key={i} className="bg-slate-900 border-l-4 border-red-500 p-4 rounded-r-lg">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-red-400 font-bold text-sm">{ind.indicator_type.replace(/_/g, ' ')}</span>
                          <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400 font-semibold">{ind.severity}</span>
                        </div>
                        <p className="text-white font-medium mb-1">"{ind.excerpt}"</p>
                        <p className="text-slate-400 text-sm">{ind.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="bg-brand/5 border border-brand/20 p-5 rounded-lg">
                <h3 className="text-sm font-semibold text-brand uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Shield className="w-4 h-4" /> Spoken Safety Guidance
                </h3>
                <p className="text-slate-200 mb-4 font-medium leading-relaxed">
                  {result.guidance}
                </p>
                <button 
                  onClick={playGuidance}
                  className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-brand border border-slate-700 py-2 px-4 rounded-md transition-colors text-sm font-medium"
                >
                  <Volume2 className="w-4 h-4" />
                  {isPlaying ? 'Playing via Gnani Timbre...' : 'Listen to Guidance'}
                </button>
                <audio 
                  ref={audioRef} 
                  onEnded={() => setIsPlaying(false)}
                  className="hidden"
                />
              </div>
            </div>
          ) : (
            <div className="h-full bg-slate-800/50 border border-slate-700/50 rounded-xl flex flex-col items-center justify-center p-12 text-center text-slate-500 min-h-[300px]">
              <Shield className="w-16 h-16 mb-4 opacity-20" />
              <p className="text-lg font-medium">No active analysis</p>
              <p className="text-sm mt-2 max-w-sm">Upload a recording or click "Run Demo Analysis" to inspect evidence and safety guidance.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default App;
