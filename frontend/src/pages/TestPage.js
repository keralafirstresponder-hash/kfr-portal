import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Heart, CheckCircle2, XCircle, Download, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TestPage() {
  const { token } = useParams();
  const [state, setState] = useState({ loading: true });
  const [answers, setAnswers] = useState({});
  const [current, setCurrent] = useState(0);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get(`/test/${token}`).then(r => {
      if (r.data.status === "completed") setResult({ passed: r.data.passed, score: r.data.score, name: r.data.candidate_name, cert_id: r.data.certificate_id, already: true });
      setState({ loading: false, data: r.data });
    }).catch(err => setState({ loading: false, error: err?.response?.data?.detail || "Invalid link" }));
  }, [token]);

  if (state.loading) return <div className="min-h-screen flex items-center justify-center text-slate-500">Loading test…</div>;
  if (state.error) return <ErrorScreen msg={state.error} />;

  const data = state.data;
  if (result) return <ResultScreen result={result} token={token} />;

  const questions = data.questions;
  const q = questions[current];

  const pick = (key) => setAnswers({ ...answers, [q.id]: key });
  const goNext = () => setCurrent(c => Math.min(questions.length - 1, c + 1));
  const goPrev = () => setCurrent(c => Math.max(0, c - 1));

  const submit = async () => {
    if (Object.keys(answers).length < questions.length) {
      if (!confirm(`You've answered ${Object.keys(answers).length}/${questions.length} questions. Submit anyway?`)) return;
    }
    setSubmitting(true);
    try {
      const { data: res } = await api.post(`/test/${token}/submit`, { answers });
      setResult({ passed: res.passed, score: res.score, name: state.data.candidate_name, cert_id: res.certificate_id });
    } catch (err) { toast.error(err?.response?.data?.detail || "Failed to submit"); }
    finally { setSubmitting(false); }
  };

  const progress = ((current + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="kfr-navy">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-kfr-red flex items-center justify-center"><Heart className="w-4 h-4 text-white" fill="white" /></div>
            <div className="text-white font-display font-semibold">KFR Assessment</div>
          </div>
          <div className="text-white/70 text-sm">Candidate: <span className="text-white font-medium">{data.candidate_name}</span></div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto p-6 lg:p-10">
        <div className="mb-6">
          <div className="flex justify-between items-baseline mb-3">
            <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Question {current + 1} of {questions.length}</div>
            <div className="text-xs text-slate-500">{Object.keys(answers).length} answered</div>
          </div>
          <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full bg-kfr-red transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-8" data-testid="question-card">
          <div className="font-display text-2xl text-kfr-navy font-semibold leading-snug" data-testid="question-text">{q.text}</div>
          <div className="mt-8 space-y-3">
            {q.options.map(o => {
              const active = answers[q.id] === o.key;
              return (
                <button
                  key={o.key}
                  onClick={() => pick(o.key)}
                  data-testid={`option-${o.key}`}
                  className={`w-full text-left flex items-start gap-4 p-4 rounded-lg border transition-colors ${active ? "border-kfr-navy bg-kfr-navy/5" : "border-slate-200 hover:border-slate-400"}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-sm font-bold shrink-0 ${active ? "bg-kfr-navy text-white" : "bg-slate-100 text-slate-500"}`}>{o.key}</div>
                  <div className="text-slate-700 pt-1">{o.text}</div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex justify-between mt-6">
          <Button variant="outline" onClick={goPrev} disabled={current === 0} data-testid="prev-btn">Previous</Button>
          {current < questions.length - 1 ? (
            <Button className="bg-kfr-navy hover:bg-[#1a2b56] text-white" onClick={goNext} data-testid="next-btn">Next <ChevronRight className="w-4 h-4 ml-1" /></Button>
          ) : (
            <Button className="bg-kfr-red hover:bg-[#d92b3a] text-white" onClick={submit} disabled={submitting} data-testid="submit-test-btn">
              {submitting ? "Submitting…" : "Submit assessment"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

function ErrorScreen({ msg }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-6">
      <div className="text-center max-w-md">
        <XCircle className="w-14 h-14 text-red-500 mx-auto" />
        <h1 className="font-display text-3xl text-kfr-navy font-bold mt-6">Unable to load test</h1>
        <p className="text-slate-500 mt-3">{msg}</p>
        <Link to="/" className="mt-6 inline-block text-kfr-red hover:underline text-sm font-semibold">Return home</Link>
      </div>
    </div>
  );
}

function ResultScreen({ result, token }) {
  const BACKEND = process.env.REACT_APP_BACKEND_URL;
  return (
    <div className="min-h-screen kfr-navy flex items-center justify-center px-6">
      <div className="max-w-lg text-center">
        {result.passed ? (
          <>
            <div className="w-20 h-20 rounded-full bg-kfr-gold flex items-center justify-center mx-auto"><CheckCircle2 className="w-11 h-11 text-kfr-navy" /></div>
            <div className="text-kfr-gold text-xs uppercase tracking-[0.3em] mt-8 font-bold">You Passed</div>
            <h1 className="font-display text-5xl text-white font-bold mt-3" data-testid="result-passed">Certified.</h1>
            <p className="text-white/70 mt-5">Score: <span className="text-white font-semibold">{result.score}/10</span></p>
            <p className="text-white/70 mt-2 text-sm">Certificate ID: <span className="text-kfr-gold font-mono">{result.cert_id}</span></p>
            <div className="mt-8 flex justify-center gap-3">
              <a href={`${BACKEND}/api/certificate/${token}/pdf`} target="_blank" rel="noreferrer" className="bg-kfr-red hover:bg-[#d92b3a] text-white font-semibold px-6 py-3 rounded-md inline-flex items-center gap-2" data-testid="cert-download-btn">
                <Download className="w-4 h-4" /> Download certificate (PDF)
              </a>
            </div>
            <div className="mt-8 text-white/40 text-xs uppercase tracking-widest">Be a hero. Save a life.</div>
          </>
        ) : (
          <>
            <div className="w-20 h-20 rounded-full bg-white/10 flex items-center justify-center mx-auto"><XCircle className="w-11 h-11 text-white" /></div>
            <h1 className="font-display text-5xl text-white font-bold mt-8" data-testid="result-failed">Not this time.</h1>
            <p className="text-white/70 mt-5">Score: <span className="text-white font-semibold">{result.score}/10</span> · Required: 5/10</p>
            <p className="text-white/70 mt-4 max-w-md mx-auto">Please review the CPR & BLS training material and contact your training coordinator to reattempt.</p>
          </>
        )}
        <Link to="/" className="mt-10 block text-white/60 hover:text-white text-sm">Back to home</Link>
      </div>
    </div>
  );
}
