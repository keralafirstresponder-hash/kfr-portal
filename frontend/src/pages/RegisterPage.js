import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Heart, CheckCircle2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function RegisterPage() {
  const [events, setEvents] = useState([]);
  const [orgs, setOrgs] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [cats, setCats] = useState([]);
  const [form, setForm] = useState({
    name: "", phone: "", email: "", dob: "", district: "", category: "", organisation: "", event_id: "",
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const nav = useNavigate();

  useEffect(() => {
    Promise.all([
      api.get("/events"),
      api.get("/organisations"),
      api.get("/districts"),
      api.get("/categories"),
    ]).then(([e, o, d, c]) => {
      setEvents(e.data || []);
      setOrgs(o.data || []);
      setDistricts(d.data || []);
      setCats(c.data || []);
      if (o.data?.length && !form.organisation) setForm((f) => ({ ...f, organisation: o.data[0].name }));
    });
  }, []);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    const req = ["name", "phone", "email", "dob", "district", "category", "organisation", "event_id"];
    for (const k of req) if (!form[k]) { toast.error(`Please fill ${k}`); return; }
    setLoading(true);
    try {
      await api.post("/candidates/register", form);
      toast.success("Registration successful");
      setSubmitted(true);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen kfr-navy flex items-center justify-center px-6">
        <div className="max-w-lg text-center">
          <div className="w-16 h-16 rounded-full bg-kfr-gold flex items-center justify-center mx-auto mb-6">
            <CheckCircle2 className="w-9 h-9 text-kfr-navy" />
          </div>
          <h1 className="font-display text-4xl text-white font-bold" data-testid="register-success-title">You're registered!</h1>
          <p className="text-white/70 mt-5 leading-relaxed">
            Thank you for joining Mission 100K. After you complete your training, your CPR assessment link will be sent to your email. Passing the assessment (5/10) earns you your official Kerala First Responder certificate.
          </p>
          <Link to="/" className="mt-10 inline-flex items-center gap-2 text-kfr-gold hover:text-white text-sm font-semibold" data-testid="register-back-home">
            <ArrowLeft className="w-4 h-4" /> Back to home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="kfr-navy">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-5 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <img src="/assets/kfr-shield.png" alt="KFR" className="h-11 w-auto" />
            <div>
              <div className="text-white font-display font-bold text-lg leading-none">Kerala First Responders</div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-kfr-gold mt-1">Mission 100K</div>
            </div>
          </Link>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="mb-8">
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Registration</div>
          <h1 className="font-display text-4xl md:text-5xl font-bold text-kfr-navy mt-3">Register for CPR Training</h1>
          <p className="text-slate-600 mt-4">Fill in your details to enroll in an upcoming Kerala First Responder training session.</p>
        </div>

        <form onSubmit={submit} className="bg-white border border-slate-200 rounded-xl p-8 grid md:grid-cols-2 gap-5" data-testid="register-form">
          <Field label="Full Name" required>
            <Input data-testid="reg-name" value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Arjun Narayanan" />
          </Field>
          <Field label="Phone Number" required>
            <Input data-testid="reg-phone" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="+91 98••••••••" />
          </Field>
          <Field label="Email" required>
            <Input data-testid="reg-email" type="email" value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="you@example.com" />
          </Field>
          <Field label="Date of Birth" required>
            <Input data-testid="reg-dob" type="date" value={form.dob} onChange={(e) => set("dob", e.target.value)} />
          </Field>
          <Field label="District" required>
            <Select value={form.district} onValueChange={(v) => set("district", v)}>
              <SelectTrigger data-testid="reg-district"><SelectValue placeholder="Select district" /></SelectTrigger>
              <SelectContent>{districts.map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}</SelectContent>
            </Select>
          </Field>
          <Field label="Category" required>
            <Select value={form.category} onValueChange={(v) => set("category", v)}>
              <SelectTrigger data-testid="reg-category"><SelectValue placeholder="Select category" /></SelectTrigger>
              <SelectContent>{cats.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
            </Select>
          </Field>
          <Field label="Organisation" required>
            <Select value={form.organisation} onValueChange={(v) => set("organisation", v)}>
              <SelectTrigger data-testid="reg-organisation"><SelectValue placeholder="Select organisation" /></SelectTrigger>
              <SelectContent>{orgs.map((o) => <SelectItem key={o.id} value={o.name}>{o.name}</SelectItem>)}</SelectContent>
            </Select>
          </Field>
          <Field label="Training Session" required>
            <Select value={form.event_id} onValueChange={(v) => set("event_id", v)}>
              <SelectTrigger data-testid="reg-event"><SelectValue placeholder="Select session" /></SelectTrigger>
              <SelectContent>
                {events.length === 0 && <div className="px-3 py-2 text-sm text-slate-500">No upcoming sessions</div>}
                {events.map((ev) => (
                  <SelectItem key={ev.id} value={ev.id}>
                    {ev.name} — {ev.training_date} · {ev.place}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>

          <div className="md:col-span-2 mt-4 flex items-center justify-between">
            <Link to="/" className="text-sm text-slate-500 hover:text-kfr-navy" data-testid="reg-cancel-link">Cancel</Link>
            <Button type="submit" disabled={loading} data-testid="reg-submit-btn" className="bg-kfr-red hover:bg-[#d92b3a] text-white font-semibold px-8 py-6 h-auto">
              {loading ? "Registering…" : "Complete Registration"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, required, children }) {
  return (
    <div>
      <Label className="text-xs uppercase tracking-widest text-slate-500 font-bold">{label}{required && <span className="text-kfr-red">*</span>}</Label>
      <div className="mt-2">{children}</div>
    </div>
  );
}
