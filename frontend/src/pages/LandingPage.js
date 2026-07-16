import { Link } from "react-router-dom";
import { Heart, Shield, Activity, ChevronRight, Sparkles, Users, Award, MapPin } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function LandingPage() {
  const [totals, setTotals] = useState({ candidates: 0, passed: 0, mission_goal: 100000 });

  useEffect(() => {
    // Public summary (fallback if fails)
    api.get("/reports/summary").catch(() => null).then((r) => {
      if (r?.data?.totals) setTotals(r.data.totals);
    });
  }, []);

  const trained = totals.passed || 0;
  const progress = Math.min(100, (trained / totals.mission_goal) * 100);

  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="relative z-20 border-b border-white/10" style={{ background: "#0b1b3d" }}>
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-5 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="nav-home-link">
            <div className="w-10 h-10 rounded-md bg-kfr-red flex items-center justify-center">
              <Heart className="w-5 h-5 text-white" fill="white" />
            </div>
            <div>
              <div className="text-white font-display font-bold text-lg leading-none">Kerala First Responders</div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-kfr-gold mt-1">Mission 100K</div>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <Link to="/admin/login" className="hidden sm:inline text-sm text-white/70 hover:text-white px-3" data-testid="nav-admin-link">Admin</Link>
            <Link to="/register" data-testid="nav-register-btn" className="bg-kfr-red btn-red-hover text-white text-sm font-semibold px-5 py-2.5 rounded-md">
              Register
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative kfr-navy grain overflow-hidden">
        <div className="absolute -right-40 -top-40 w-[500px] h-[500px] rounded-full bg-kfr-red/10 blur-3xl" />
        <div className="absolute -left-40 -bottom-40 w-[400px] h-[400px] rounded-full bg-kfr-gold/10 blur-3xl" />
        <div className="relative max-w-7xl mx-auto px-6 lg:px-12 py-24 lg:py-32 grid lg:grid-cols-12 gap-12">
          <div className="lg:col-span-7">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-kfr-gold/40 bg-white/5 text-kfr-gold text-xs uppercase tracking-[0.25em] mb-8">
              <Sparkles className="w-3.5 h-3.5" /> Courage to care · Skill to save
            </div>
            <h1 className="font-display text-white text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tight">
              Training <span className="text-kfr-gold">100,000</span> Keralites <br className="hidden md:block" /> to save a life.
            </h1>
            <p className="text-white/70 text-lg mt-8 max-w-xl leading-relaxed">
              A statewide movement to teach CPR &amp; Basic Life Support. Powered by <span className="text-white font-medium">Wisdom Foundation</span> · Medical partner <span className="text-white font-medium">Aster Medcity</span>.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link to="/register" data-testid="hero-register-btn" className="bg-kfr-red btn-red-hover text-white font-semibold px-7 py-3.5 rounded-md inline-flex items-center gap-2">
                Register for training <ChevronRight className="w-4 h-4" />
              </Link>
              <a href="#mission" className="text-white/80 hover:text-white font-medium px-5 py-3.5 rounded-md border border-white/20 hover:border-white/40 transition-colors" data-testid="hero-learn-btn">
                Learn the mission
              </a>
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col gap-4">
            <div className="rounded-2xl border border-white/10 bg-[#1a2b56] p-8">
              <div className="text-xs uppercase tracking-[0.25em] text-kfr-gold">Mission Progress</div>
              <div className="mt-4 flex items-baseline gap-2">
                <div className="font-display text-5xl text-white font-bold" data-testid="hero-trained-count">{trained.toLocaleString()}</div>
                <div className="text-white/50 text-sm">/ {totals.mission_goal.toLocaleString()} certified</div>
              </div>
              <div className="mt-5 h-2 rounded-full bg-white/10 overflow-hidden">
                <div className="h-full bg-kfr-red" style={{ width: `${progress}%` }} />
              </div>
              <div className="mt-4 text-white/50 text-xs">Every second counts. Every hand saves.</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-xl border border-white/10 bg-white/5 p-5">
                <Users className="w-5 h-5 text-kfr-gold mb-3" />
                <div className="text-white font-display text-2xl font-bold">{totals.candidates || 0}</div>
                <div className="text-white/60 text-xs mt-1 uppercase tracking-wider">Registered</div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-5">
                <Award className="w-5 h-5 text-kfr-gold mb-3" />
                <div className="text-white font-display text-2xl font-bold">14</div>
                <div className="text-white/60 text-xs mt-1 uppercase tracking-wider">Districts covered</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission strip */}
      <section id="mission" className="max-w-7xl mx-auto px-6 lg:px-12 py-24">
        <div className="grid lg:grid-cols-12 gap-10">
          <div className="lg:col-span-4">
            <div className="text-xs uppercase tracking-[0.25em] text-kfr-red font-bold">How it works</div>
            <h2 className="font-display text-4xl md:text-5xl font-bold text-kfr-navy mt-4 leading-tight">A simple 4-step path from bystander to first responder.</h2>
            <p className="text-slate-600 mt-6 leading-relaxed">Attend hands-on training. Pass a 10-question assessment. Get your Kerala First Responder certificate.</p>
          </div>
          <div className="lg:col-span-8 grid sm:grid-cols-2 gap-4">
            {[
              { icon: Users, title: "Register", desc: "Sign up for a training session near you." },
              { icon: Activity, title: "Train", desc: "Learn CPR & BLS from Aster-certified trainers." },
              { icon: Shield, title: "Assess", desc: "Take a quick 10-question online assessment." },
              { icon: Award, title: "Certify", desc: "Get your KFR certificate delivered by email." },
            ].map((s, i) => {
              const Icon = s.icon;
              return (
                <div key={i} className="rounded-xl border border-slate-200 bg-white p-6 hover:border-kfr-gold transition-colors">
                  <div className="w-11 h-11 rounded-md kfr-navy flex items-center justify-center mb-4">
                    <Icon className="w-5 h-5 text-kfr-gold" />
                  </div>
                  <div className="text-xs text-slate-400 font-mono">0{i + 1}</div>
                  <div className="font-display text-2xl font-semibold text-kfr-navy mt-1">{s.title}</div>
                  <div className="text-slate-600 text-sm mt-2 leading-relaxed">{s.desc}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Partners banner */}
      <section className="border-y border-slate-200 bg-slate-50/70">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-14 grid md:grid-cols-3 gap-8 items-center">
          <div>
            <div className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">An Initiative by</div>
            <div className="font-display text-2xl text-kfr-navy font-bold mt-2">Wisdom Foundation</div>
            <div className="text-slate-500 text-xs mt-1">Empowering lives. Enriching futures.</div>
          </div>
          <div className="md:border-x md:border-slate-200 md:px-8">
            <div className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">Medical Partner</div>
            <div className="font-display text-2xl text-kfr-navy font-bold mt-2">Aster Medcity</div>
            <div className="text-slate-500 text-xs mt-1">We'll treat you well.</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">Program</div>
            <div className="font-display text-2xl text-kfr-navy font-bold mt-2">Mission 100K</div>
            <div className="text-slate-500 text-xs mt-1">100,000 CPR-trained Keralites.</div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="kfr-navy relative overflow-hidden">
        <div className="absolute -right-20 -top-20 w-72 h-72 rounded-full bg-kfr-red/20 blur-3xl" />
        <div className="max-w-5xl mx-auto px-6 lg:px-12 py-24 text-center relative">
          <div className="inline-flex items-center gap-2 justify-center text-kfr-gold text-xs uppercase tracking-[0.3em] mb-6">
            <MapPin className="w-3.5 h-3.5" /> Kerala, India
          </div>
          <h2 className="font-display text-white text-4xl md:text-6xl font-bold leading-tight">Be a hero. Save a life.</h2>
          <p className="text-white/70 mt-6 max-w-2xl mx-auto">Join thousands of Keralites who are ready to respond in the critical first minutes of a cardiac emergency.</p>
          <Link to="/register" data-testid="cta-register-btn" className="mt-10 inline-flex items-center gap-2 bg-kfr-red btn-red-hover text-white font-semibold px-8 py-4 rounded-md">
            Register now <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <footer className="kfr-navy border-t border-white/10">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-8 text-white/50 text-xs flex flex-col md:flex-row justify-between gap-4">
          <div>© {new Date().getFullYear()} Kerala First Responders · Mission 100K</div>
          <div className="flex gap-6">
            <span>Always Ready</span><span>Every Second Counts</span><span>Community First</span><span>Trained to Save</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
