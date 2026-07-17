import { Link } from "react-router-dom";
import { ChevronRight, Sparkles, Users, Award, MapPin, Shield, Activity, Heart, Target, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

// Verified mission imagery (from design_guidelines)
const IMG_CPR_TRAINING = "https://images.unsplash.com/photo-1755549746560-f56c7bd0c82f?auto=format&fit=crop&w=2000&q=85"; // Man practices CPR on training dummy
const IMG_AMBULANCE = "https://images.unsplash.com/photo-1579037005241-a79202c7e9fd?auto=format&fit=crop&w=2000&q=85"; // Ambulance / paramedics
const IMG_GOLD_MEDAL = "https://images.unsplash.com/photo-1769791687730-52b608addf88?auto=format&fit=crop&w=1400&q=85"; // Gold medallion / certificate seal
const IMG_HOSPITAL = "https://images.unsplash.com/photo-1592050103688-a6053fc0e386?auto=format&fit=crop&w=2000&q=85"; // Modern hospital


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
      <nav className="absolute top-0 left-0 right-0 z-30">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-5 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="nav-home-link">
            <img src="/assets/kfr-shield.png" alt="KFR" className="h-11 w-auto drop-shadow-lg" />
            <div>
              <div className="text-white font-display font-bold text-lg leading-none">Kerala First Responders</div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-kfr-gold mt-1">Mission 100K</div>
            </div>
          </Link>
          <div className="flex items-center gap-4">
            <Link to="/register" data-testid="nav-register-btn" className="bg-kfr-red btn-red-hover text-white text-sm font-semibold px-5 py-2.5 rounded-md shadow-lg">
              Register
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO — full-bleed image */}
      <section className="relative min-h-[720px] flex items-center overflow-hidden">
        <div className="absolute inset-0">
          <img src={IMG_CPR_TRAINING} alt="CPR training" className="w-full h-full object-cover" />
          <div className="absolute inset-0" style={{ background: "linear-gradient(90deg, rgba(11,27,61,0.92) 0%, rgba(11,27,61,0.72) 45%, rgba(11,27,61,0.35) 100%)" }} />
        </div>
        <div className="relative max-w-7xl mx-auto px-6 lg:px-12 pt-32 pb-24 w-full">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-kfr-gold/50 bg-white/5 backdrop-blur text-kfr-gold text-xs uppercase tracking-[0.25em] mb-8">
              <Sparkles className="w-3.5 h-3.5" /> Courage to care · Skill to save
            </div>
            <h1 className="font-display text-white text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tight">
              Every Keralite,
              <br />
              <span className="text-kfr-gold">a lifesaver.</span>
            </h1>
            <p className="text-white/85 text-lg md:text-xl mt-8 max-w-2xl leading-relaxed">
              We are on a mission to train <span className="text-white font-semibold">100,000 Keralites</span> in CPR and Basic Life Support — turning ordinary bystanders into confident first responders.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link to="/register" data-testid="hero-register-btn" className="bg-kfr-red btn-red-hover text-white font-semibold px-8 py-4 rounded-md inline-flex items-center gap-2 shadow-xl">
                Register for training <ChevronRight className="w-4 h-4" />
              </Link>
              <a href="#mission" className="text-white hover:text-kfr-gold font-medium px-6 py-4 rounded-md border border-white/30 hover:border-kfr-gold backdrop-blur-sm transition-colors" data-testid="hero-learn-btn">
                Our mission
              </a>
            </div>

            {/* Mission progress inline */}
            <div className="mt-10 max-w-xl">
              <div className="flex items-baseline justify-between mb-3">
                <div className="text-[10px] uppercase tracking-[0.3em] text-kfr-gold font-bold">Mission Progress</div>
                <div className="text-white/60 text-xs">{progress.toFixed(2)}%</div>
              </div>
              <div className="flex items-end justify-between text-white/70 text-sm mb-2">
                <span><span className="text-white font-display font-bold text-2xl mr-1" data-testid="hero-trained-count">{trained.toLocaleString()}</span> certified</span>
                <span>Goal · 100,000</span>
              </div>
              <div className="h-1.5 rounded-full bg-white/15 overflow-hidden">
                <div className="h-full bg-kfr-red" style={{ width: `${progress}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Partner logos row — bottom of hero */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-white/10 bg-[#0b1b3d]/70 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-6 lg:px-12 py-4 flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
            <span className="text-[10px] uppercase tracking-[0.3em] text-white/50 font-bold">In partnership with</span>
            <div className="bg-white rounded-md px-3 py-1.5 shadow-sm">
              <img src="/assets/aster-medcity-logo.png" alt="Aster Medcity" className="h-8 w-auto" />
            </div>
            <img src="/assets/wisdom4future-logo.png" alt="Wisdom 4 Future" className="h-12 w-auto rounded-md shadow-sm" />
          </div>
        </div>
      </section>

      {/* OUR MISSION — pillar cards */}
      <section id="mission" className="max-w-7xl mx-auto px-6 lg:px-12 py-24 lg:py-32">
        <div className="max-w-3xl mb-16">
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Our mission</div>
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-kfr-navy mt-4 leading-[1.05]">
            Because every second matters when a heart stops.
          </h2>
          <p className="text-slate-600 text-lg mt-6 leading-relaxed">
            Sudden cardiac arrest kills more people in India than any other single cause. Immediate CPR by a bystander can <span className="font-semibold text-kfr-navy">double survival rates</span>. Yet fewer than 1 in 20 Keralites know how to perform it. We're changing that — one hundred thousand times over.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-5">
          <PillarCard
            img={IMG_CPR_TRAINING}
            tag="Train"
            title="Hands-on training, statewide."
            desc="Free CPR &amp; BLS workshops delivered by Aster-certified instructors across all 14 districts of Kerala."
            icon={Users}
          />
          <PillarCard
            img={IMG_GOLD_MEDAL}
            tag="Certify"
            title="Skill, verified."
            desc="Every participant is assessed with a 10-question test. Passing scores earn an official Kerala First Responder certificate."
            icon={Award}
          />
          <PillarCard
            img={IMG_AMBULANCE}
            tag="Save"
            title="Build a community that responds."
            desc="A network of 100,000 trained Keralites, ready to act in the critical minutes before medical help arrives."
            icon={Heart}
          />
        </div>
      </section>

      {/* THE URGENCY / Impact strip with photo */}
      <section className="relative">
        <div className="grid lg:grid-cols-2">
          <div className="relative min-h-[420px] lg:min-h-[560px]">
            <img src={IMG_AMBULANCE} alt="Emergency responder" className="absolute inset-0 w-full h-full object-cover" />
            <div className="absolute inset-0" style={{ background: "linear-gradient(45deg, rgba(11,27,61,0.55) 0%, rgba(11,27,61,0.15) 100%)" }} />
          </div>
          <div className="p-10 md:p-16 lg:p-24 bg-slate-50 flex flex-col justify-center">
            <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">The urgency</div>
            <h2 className="font-display text-4xl md:text-5xl font-bold text-kfr-navy mt-4 leading-[1.1]">
              14 minutes. That's the average time it takes for an ambulance to reach.
            </h2>
            <p className="text-slate-600 mt-6 leading-relaxed">
              In those 14 minutes, a person in cardiac arrest can be alive — or gone. Trained bystanders bridge the gap.
            </p>
            <div className="grid grid-cols-3 gap-8 mt-10 pt-10 border-t border-slate-200">
              <ImpactStat icon={Target} big="60%" small="Cardiac arrests happen at home" />
              <ImpactStat icon={Zap} big="4 min" small="Brain damage begins without CPR" />
              <ImpactStat icon={Activity} big="2×" small="Survival rate with early CPR" />
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="max-w-7xl mx-auto px-6 lg:px-12 py-24 lg:py-32">
        <div className="max-w-3xl mb-16">
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">How it works</div>
          <h2 className="font-display text-4xl md:text-5xl font-bold text-kfr-navy mt-4 leading-[1.1]">
            Four steps to becoming a first responder.
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: Users, title: "Register", desc: "Sign up online for a training session near you." },
            { icon: Activity, title: "Train", desc: "Attend a hands-on CPR & BLS workshop." },
            { icon: Shield, title: "Assess", desc: "Take a quick 10-question online assessment." },
            { icon: Award, title: "Certify", desc: "Receive your official KFR certificate by email." },
          ].map((s, i) => {
            const Icon = s.icon;
            return (
              <div key={i} className="relative rounded-xl border border-slate-200 bg-white p-6 hover:border-kfr-navy hover:shadow-lg transition-all">
                <div className="text-6xl font-display font-bold text-slate-100 leading-none">0{i + 1}</div>
                <div className="w-11 h-11 rounded-md kfr-navy flex items-center justify-center absolute top-6 right-6">
                  <Icon className="w-5 h-5 text-kfr-gold" />
                </div>
                <div className="font-display text-xl font-semibold text-kfr-navy mt-4">{s.title}</div>
                <div className="text-slate-600 text-sm mt-2 leading-relaxed">{s.desc}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA banner */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <img src={IMG_HOSPITAL} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0" style={{ background: "linear-gradient(90deg, rgba(11,27,61,0.94) 0%, rgba(11,27,61,0.7) 100%)" }} />
        </div>
        <div className="relative max-w-6xl mx-auto px-6 lg:px-12 py-24 lg:py-32">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 text-kfr-gold text-xs uppercase tracking-[0.3em] mb-6">
              <MapPin className="w-3.5 h-3.5" /> Kerala, India
            </div>
            <h2 className="font-display text-white text-4xl md:text-6xl font-bold leading-tight">
              Be a hero.
              <br />
              <span className="text-kfr-gold">Save a life.</span>
            </h2>
            <p className="text-white/80 mt-6 text-lg max-w-xl leading-relaxed">
              Join thousands of Keralites who are learning to act in the critical first minutes of a cardiac emergency. Free training. Real certification. Lifelong skill.
            </p>
            <Link to="/register" data-testid="cta-register-btn" className="mt-10 inline-flex items-center gap-2 bg-kfr-red btn-red-hover text-white font-semibold px-8 py-4 rounded-md shadow-xl">
              Register now <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      <footer className="kfr-navy border-t border-white/10">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-10">
          <div className="flex flex-col md:flex-row justify-between gap-6">
            <div className="flex items-center gap-3">
              <img src="/assets/kfr-shield.png" alt="KFR" className="h-14" />
              <div>
                <div className="text-white font-display font-semibold">Kerala First Responders</div>
                <div className="text-white/50 text-xs uppercase tracking-[0.25em] mt-1">Mission 100K</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-[10px] uppercase tracking-[0.3em] text-white/40 font-bold">Powered by</div>
                <div className="text-white/70 text-xs mt-1">The BeFirst initiative</div>
              </div>
              <img src="/assets/befirst-logo.png" alt="BeFirst" className="h-11 bg-white rounded px-2 py-1" />
            </div>
          </div>
          <div className="border-t border-white/10 mt-8 pt-6 flex flex-col md:flex-row md:justify-between gap-4 text-white/40 text-xs">
            <div>© {new Date().getFullYear()} Kerala First Responders · An initiative by Wisdom Foundation · Medical partner Aster Medcity</div>
            <div className="flex flex-wrap gap-x-6 gap-y-2">
              <span>Always Ready</span>
              <span>Every Second Counts</span>
              <span>Community First</span>
              <span>Trained to Save</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function PillarCard({ img, tag, title, desc, icon: Icon }) {
  return (
    <div className="group relative rounded-xl overflow-hidden bg-kfr-navy min-h-[440px] flex flex-col justify-end">
      <img src={img} alt={title} className="absolute inset-0 w-full h-full object-cover opacity-70 group-hover:opacity-80 group-hover:scale-105 transition-all duration-500" />
      <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(11,27,61,0.95) 0%, rgba(11,27,61,0.55) 55%, rgba(11,27,61,0.15) 100%)" }} />
      <div className="relative p-7 text-white">
        <div className="w-11 h-11 rounded-md bg-kfr-red flex items-center justify-center mb-6">
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="text-[10px] uppercase tracking-[0.3em] text-kfr-gold font-bold">{tag}</div>
        <div className="font-display text-2xl font-semibold mt-3 leading-snug">{title}</div>
        <div className="text-white/75 text-sm mt-3 leading-relaxed" dangerouslySetInnerHTML={{ __html: desc }} />
      </div>
    </div>
  );
}

function ImpactStat({ icon: Icon, big, small }) {
  return (
    <div>
      <Icon className="w-5 h-5 text-kfr-red mb-3" />
      <div className="font-display text-3xl md:text-4xl text-kfr-navy font-bold">{big}</div>
      <div className="text-slate-500 text-xs mt-2 leading-snug">{small}</div>
    </div>
  );
}
