import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useNavigate, Navigate, Link } from "react-router-dom";
import { toast } from "sonner";
import { Heart, LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function AdminLogin() {
  const { admin, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  if (admin) return <Navigate to="/admin" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success("Welcome back");
      nav("/admin");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid md:grid-cols-2">
      <div className="hidden md:flex kfr-navy relative overflow-hidden items-center p-12">
        <div className="absolute -right-32 -bottom-32 w-96 h-96 rounded-full bg-kfr-red/20 blur-3xl" />
        <div className="absolute -left-20 -top-20 w-80 h-80 rounded-full bg-kfr-gold/10 blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-16">
            <img src="/assets/kfr-shield.png" alt="KFR" className="h-14 w-auto" />
            <div>
              <div className="text-white font-display font-bold text-lg leading-none">Kerala First Responders</div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-kfr-gold mt-1">Admin Console</div>
            </div>
          </div>
          <h1 className="font-display text-white text-5xl font-bold leading-tight">Command the mission.</h1>
          <p className="text-white/70 mt-6 max-w-md leading-relaxed">Manage candidates, assessments, certificates and district-wise reporting for Mission 100K.</p>
          <div className="mt-16 border-t border-white/10 pt-6 text-white/40 text-xs uppercase tracking-[0.25em]">
            Always Ready · Every Second Counts · Community First
          </div>
        </div>
      </div>
      <div className="flex items-center justify-center p-8 bg-white">
        <form onSubmit={submit} className="w-full max-w-sm" data-testid="admin-login-form">
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Admin Login</div>
          <h2 className="font-display text-3xl font-bold text-kfr-navy mt-3">Sign in to continue</h2>
          <p className="text-slate-500 text-sm mt-2">Use your KFR admin credentials.</p>

          <div className="mt-8 space-y-5">
            <div>
              <Label className="text-xs uppercase tracking-widest text-slate-500 font-bold">Email</Label>
              <Input data-testid="admin-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="admin@kfr.org" className="mt-2" />
            </div>
            <div>
              <Label className="text-xs uppercase tracking-widest text-slate-500 font-bold">Password</Label>
              <Input data-testid="admin-password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" className="mt-2" />
            </div>
            <Button type="submit" disabled={loading} data-testid="admin-login-btn" className="w-full bg-kfr-red hover:bg-[#d92b3a] text-white font-semibold py-6 h-auto">
              {loading ? "Signing in…" : (<><LogIn className="w-4 h-4 mr-2" /> Sign in</>)}
            </Button>
            <Link to="/" className="block text-center text-sm text-slate-500 hover:text-kfr-navy" data-testid="admin-back-link">Back to landing</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
