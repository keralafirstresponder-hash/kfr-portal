import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import { Download } from "lucide-react";

export default function CertificatePage() {
  const { token } = useParams();
  const [info, setInfo] = useState(null);
  const [err, setErr] = useState(null);
  const BACKEND = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    api.get(`/certificate/${token}`).then(r => setInfo(r.data)).catch(e => setErr(e?.response?.data?.detail || "Certificate not available"));
  }, [token]);

  if (err) return <div className="min-h-screen flex items-center justify-center text-slate-500">{err}</div>;
  if (!info) return <div className="min-h-screen flex items-center justify-center text-slate-500">Loading…</div>;

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-6">
      <div className="max-w-3xl w-full text-center">
        <div className="font-display text-3xl text-kfr-navy font-bold" data-testid="cert-page-title">Your certificate is ready</div>
        <p className="text-slate-500 mt-3">Congratulations {info.candidate_name}! You scored {info.score}/10 on the KFR CPR &amp; BLS Assessment.</p>
        <div className="mt-6 bg-white border border-slate-200 rounded-xl p-6 grid sm:grid-cols-3 gap-4 text-left">
          <Item label="Certificate ID" value={info.certificate_id} />
          <Item label="Training date" value={info.training_date} />
          <Item label="Training centre" value={info.training_place} />
        </div>
        <a href={`${BACKEND}/api/certificate/${token}/pdf`} target="_blank" rel="noreferrer" className="mt-8 inline-flex items-center gap-2 bg-kfr-red hover:bg-[#d92b3a] text-white font-semibold px-8 py-4 rounded-md" data-testid="cert-page-download-btn">
          <Download className="w-4 h-4" /> Download Certificate (PDF)
        </a>
        <div className="mt-8"><Link to="/" className="text-slate-500 hover:text-kfr-navy text-sm">Back to home</Link></div>
      </div>
    </div>
  );
}

function Item({ label, value }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-widest text-slate-500 font-bold">{label}</div>
      <div className="text-kfr-navy font-medium mt-1">{value || "—"}</div>
    </div>
  );
}
