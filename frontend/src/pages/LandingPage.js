import { Link } from "react-router-dom";
import { ChevronRight, Sparkles, Users, Award, MapPin, Heart, Shield, Activity } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const IMG_CPR = "https://images.unsplash.com/photo-1755549746560-f56c7bd0c82f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1ODR8MHwxfHNlYXJjaHwzfHxDUFIlMjB0cmFpbmluZyUyMGNsYXNzfGVufDB8fHx8MTc4NDE3NTI5OHww&ixlib=rb-4.1.0&q=85&w=1600";
const IMG_AMBULANCE = "https://images.unsplash.com/photo-1579037005241-a79202c7e9fd?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHwxfHxwYXJhbWVkaWNzJTIwZW1lcmdlbmN5JTIwcmVzcG9uZGVyc3xlbnwwfHx8fDE3ODQxNzUyOTh8MA&ixlib=rb-4.1.0&q=85&w=1600";
const IMG_HOSPITAL = "https://images.unsplash.com/photo-1592050103688-a6053fc0e386?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MTN8MHwxfHNlYXJjaHwyfHxob3NwaXRhbCUyMGJ1aWxkaW5nJTIwQXN0ZXIlMjBNZWRjaXR5JTIwb3IlMjBnZW5lcmljJTIwbW9kZXJuJTIwaG9zcGl0YWx8ZW58MHx8fHwxNzg0MTc1Mjk4fDA&ixlib=rb-4.1.0&q=85&w=1600";
const IMG_TRAINING_1 = "https://images.unsplash.com/photo-1584515933487-779824d29309?auto=format&fit=crop&w=1200&q=80";
const IMG_TRAINING_2 = "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80";

export default function LandingPage() {
  const [totals, setTotals] = useState({ candidates: 0, passed: 0, mission_goal: 100000 });

  useEffect(() => {
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
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="nav-home-link">
            <img src="/assets/kfr-shield.png" alt="Kerala First Responder" className="h-11 w-auto" />
            <div>
              <div className="text-white font-display font-bold text-lg leading-none">Kerala First Responders</div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-kfr-gold mt-1">Mission 100K</div>
            </div>
          </Link>
          <div className="flex items-center gap-4">
            <Link to="/admin/login" className="hidden sm:inline text-sm text-white/70 hover:text-white px-3" data-testid="nav-admin-link">Admin</Link>
            <Link to="/register" data-testid="nav-register-btn" className="bg-kfr-red btn-red-hover text-white text-sm font-semibold px-5 py-2.5 rounded-md">
              Register
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative kfr-navy grain overflow-hidden">
        <div className="absolute inset-0 opacity-25">
          <img src={IMG_CPR} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0" style={{ background: "linear-gradient(90deg, #0b1b3d 0%, #0b1b3d 45%, rgba(11,27,61,0.7) 100%)" }} />
        </div>
        <div className="absolute -right-40 -top-40 w-[500px] h-[500px] rounded-full bg-kfr-red/10 blur-3xl" />
        <div className="absolute -left-40 -bottom-40 w-[400px] h-[400px] rounded-full bg-kfr-gold/10 blur-3xl" />
        <div className="relative max-w-7xl mx-auto px-6 lg:px-12 py-20 lg:py-28 grid lg:grid-cols-12 gap-12">
          <div className="lg:col-span-7">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-kfr-gold/40 bg-white/5 text-kfr-gold text-xs uppercase tracking-[0.25em] mb-8">
              <Sparkles className="w-3.5 h-3.5" /> Courage to care · Skill to save
            </div>
            <h1 className="font-display text-white text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tight">
              Training <span className="text-kfr-gold">100,000</span> Keralites <br className="hidden md:block" /> to save a life.
            </h1>
            <p className="text-white/70 text-lg mt-8 max-w-xl leading-relaxed">
              A statewide movement to teach CPR &amp; Basic Life Support. An initiative by <span className="text-white font-medium">Wisdom Foundation</span> · Medical partner <span className="text-white font-medium">Aster Medcity</span>.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link to="/register" data-testid="hero-register-btn" className="bg-kfr-red btn-red-hover text-white font-semibold px-7 py-3.5 rounded-md inline-flex items-center gap-2">
                Register for training <ChevronRight className="w-4 h-4" />
              </Link>
              <a href="#mission" className="text-white/80 hover:text-white font-medium px-5 py-3.5 rounded-md border border-white/20 hover:border-white/40 transition-colors" data-testid="hero-learn-btn">
                Learn the mission
              </a>
            </div>

            <div className="mt-14 flex items-center gap-8 opacity-90">
              <img src="/assets/aster-medcity-logo.png" alt="Aster Medcity" className="h-9 md:h-10 bg-white/95 rounded px-2 py-1" />
              <img src="/assets/wisdom4future-logo.png" alt="Wisdom 4 Future" className="h-10 md:h-12" />
              <img src="/assets/befirst-logo.png" alt="BeFirst" className="h-9 md:h-10 bg-white/95 rounded px-2 py-1" />
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col gap-4">
            <div className="rounded-2xl border border-white/10 bg-[#1a2b56]/90 backdrop-blur p-8">
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

      {/* Impact strip with ambulance photo */}
      <section className="relative">
        <div className="grid md:grid-cols-2">
          <div className="p-12 lg:p-20 bg-white">
            <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Why this matters</div>
            <h2 className="font-display text-4xl md:text-5xl font-bold text-kfr-navy mt-4 leading-tight">Cardiac arrest can happen anywhere. Anytime.</h2>
            <p className="text-slate-600 mt-6 leading-relaxed">
              Every second without CPR reduces the chance of survival by 10%. In Kerala, an ambulance takes an average of <span className="font-semibold text-kfr-navy">14 minutes</span> to arrive. Trained bystanders bridge that gap.
            </p>
            <div className="mt-8 grid grid-cols-3 gap-6">
              <Stat big="60%" small="Cardiac arrests happen at home" />
              <Stat big="4 min" small="Brain damage begins" />
              <Stat big="2×" small="Survival with early CPR" />
            </div>
          </div>
          <div className="relative min-h-[380px]">
            <img src={IMG_AMBULANCE} alt="Emergency responders" className="absolute inset-0 w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
            <div className="absolute bottom-8 left-8 text-white">
              <div className="text-xs uppercase tracking-[0.25em] text-kfr-gold font-bold">Every second counts</div>
              <div className="font-display text-2xl font-bold mt-2 max-w-xs">Community responders save lives before help arrives.</div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="mission" className="max-w-7xl mx-auto px-6 lg:px-12 py-24">
        <div className="grid lg:grid-cols-12 gap-10">
          <div className="lg:col-span-4">
            <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">How it works</div>
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

      {/* Certificate showcase */}
      <section className="bg-slate-50 border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-24 grid lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-5">
            <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Your certificate</div>
            <h2 className="font-display text-4xl md:text-5xl font-bold text-kfr-navy mt-4 leading-tight">Officially certified. <br /> Instantly issued.</h2>
            <p className="text-slate-600 mt-6 leading-relaxed">
              Pass the assessment and receive a beautifully designed Kerala First Responder certificate — endorsed by Aster Medcity and Wisdom 4 Future. Emailed and downloadable as PDF.
            </p>
            <ul className="mt-8 space-y-3 text-sm text-slate-700">
              {["Unique certificate ID", "Signed by Aster Medcity leadership", "Downloadable PDF format", "Shareable with employers"].map((l, i) => (
                <li key={i} className="flex items-center gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-kfr-red" /> {l}
                </li>
              ))}
            </ul>
          </div>
          <div className="lg:col-span-7">
            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-kfr-gold/20 to-transparent rounded-2xl blur-2xl" />
              <img src="/assets/certificate-sample.jpg" alt="Sample certificate" className="relative w-full rounded-xl shadow-2xl border border-slate-200" />
            </div>
          </div>
        </div>
      </section>

      {/* Training gallery */}
      <section className="max-w-7xl mx-auto px-6 lg:px-12 py-24">
        <div className="mb-12">
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">From the field</div>
          <h2 className="font-display text-4xl md:text-5xl font-bold text-kfr-navy mt-4">Training in action.</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          <GalleryItem src={IMG_CPR} title="Hands-on CPR practice" tag="Skill" />
          <GalleryItem src={IMG_TRAINING_1} title="Small-group workshops" tag="Community" />
          <GalleryItem src={IMG_TRAINING_2} title="Certified BLS trainers" tag="Expert" />
        </div>
      </section>

      {/* Partners banner */}
      <section className="border-y border-slate-200 bg-slate-50/70">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-14 grid md:grid-cols-3 gap-8 items-center">
          <div className="flex items-center gap-4">
            <img src="/assets/wisdom4future-logo.png" alt="Wisdom 4 Future" className="h-14" />
            <div>
              <div className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">An Initiative by</div>
              <div className="font-display text-xl text-kfr-navy font-bold">Wisdom 4 Future</div>
            </div>
          </div>
          <div className="md:border-x md:border-slate-200 md:px-8 flex items-center gap-4">
            <img src="/assets/aster-medcity-logo.png" alt="Aster Medcity" className="h-14 bg-white rounded" />
            <div>
              <div className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">Medical Partner</div>
              <div className="font-display text-xl text-kfr-navy font-bold">Aster Medcity</div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <img src="/assets/befirst-logo.png" alt="BeFirst" className="h-14" />
            <div>
              <div className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">Program Ally</div>
              <div className="font-display text-xl text-kfr-navy font-bold">BeFirst · Aster Emergency</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="kfr-navy relative overflow-hidden">
        <div className="absolute inset-0 opacity-15">
          <img src={IMG_HOSPITAL} alt="" className="w-full h-full object-cover" />
        </div>
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
          <div className="flex items-center gap-3">
            <img src="/assets/kfr-shield.png" alt="KFR" className="h-8" />
            <div>© {new Date().getFullYear()} Kerala First Responders · Mission 100K</div>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            <span>Always Ready</span><span>Every Second Counts</span><span>Community First</span><span>Trained to Save</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function Stat({ big, small }) {
  return (
    <div>
      <div className="font-display text-3xl text-kfr-navy font-bold">{big}</div>
      <div className="text-slate-500 text-xs mt-2 leading-snug">{small}</div>
    </div>
  );
}

function GalleryItem({ src, title, tag }) {
  return (
    <div className="relative rounded-xl overflow-hidden aspect-[4/5] group">
      <img src={src} alt={title} className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
      <div className="absolute inset-0 bg-gradient-to-t from-kfr-navy via-kfr-navy/40 to-transparent" style={{ background: "linear-gradient(to top, rgba(11,27,61,0.9), rgba(11,27,61,0.1) 60%)" }} />
      <div className="absolute bottom-6 left-6 right-6 text-white">
        <div className="text-[10px] uppercase tracking-[0.3em] text-kfr-gold font-bold">{tag}</div>
        <div className="font-display text-xl font-semibold mt-2">{title}</div>
      </div>
    </div>
  );
}
