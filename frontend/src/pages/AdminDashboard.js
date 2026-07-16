import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import { Users, Award, TimerReset, XCircle, Building2, CalendarDays } from "lucide-react";

const COLORS = ["#0B1B3D", "#E63946", "#D4AF37", "#007260", "#1A2B56", "#94A3B8", "#F59E0B", "#10B981", "#64748B"];

export default function AdminDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/reports/summary").then((r) => setData(r.data));
  }, []);

  if (!data) return <div className="p-10 text-slate-500">Loading dashboard…</div>;
  const t = data.totals;
  const progress = Math.min(100, (t.passed / t.mission_goal) * 100);

  return (
    <div className="p-8 lg:p-10">
      <div className="flex items-end justify-between mb-8">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Overview</div>
          <h1 className="font-display text-4xl font-bold text-kfr-navy mt-2" data-testid="dashboard-title">Mission Command</h1>
        </div>
        <div className="text-right">
          <div className="text-xs uppercase tracking-widest text-slate-500">Mission Goal</div>
          <div className="font-display text-3xl text-kfr-navy font-bold">100,000</div>
        </div>
      </div>

      {/* North star */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 mb-6">
        <div className="flex justify-between items-baseline">
          <div>
            <div className="text-xs uppercase tracking-widest text-slate-500">Certified Responders</div>
            <div className="font-display text-5xl text-kfr-navy font-bold mt-2" data-testid="stat-passed">{t.passed}</div>
          </div>
          <div className="text-right text-sm text-slate-500">{progress.toFixed(3)}% of Mission 100K</div>
        </div>
        <div className="mt-5 h-2 rounded-full bg-slate-100 overflow-hidden">
          <div className="h-full bg-kfr-red" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Stat icon={Users} label="Total Registered" value={t.candidates} color="#0B1B3D" testid="stat-total" />
        <Stat icon={TimerReset} label="Tests Pending" value={t.pending} color="#D4AF37" testid="stat-pending" />
        <Stat icon={XCircle} label="Failed" value={t.failed} color="#E63946" testid="stat-failed" />
        <Stat icon={CalendarDays} label="Training Sessions" value={t.events} color="#007260" testid="stat-events" />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* District bar chart */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <div className="text-xs uppercase tracking-widest text-slate-500 font-bold">District-wise</div>
              <div className="font-display text-xl text-kfr-navy font-semibold mt-1">Registrations by district</div>
            </div>
          </div>
          <div className="h-72 min-h-[280px] w-full" data-testid="chart-district">
            {data.district.length === 0 ? (
              <EmptyChart label="No registrations yet" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.district}>
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748B" }} interval={0} angle={-25} textAnchor="end" height={70} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748B" }} allowDecimals={false} />
                  <Tooltip contentStyle={{ background: "#0B1B3D", color: "#fff", border: "none", borderRadius: 8 }} />
                  <Bar dataKey="count" fill="#0B1B3D" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Category donut */}
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-bold">Category</div>
          <div className="font-display text-xl text-kfr-navy font-semibold mt-1 mb-6">By category</div>
          <div className="h-72 min-h-[280px] w-full" data-testid="chart-category">
            {data.category.length === 0 ? (
              <EmptyChart label="No data" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={data.category} dataKey="count" nameKey="name" innerRadius={45} outerRadius={80} paddingAngle={2}>
                    {data.category.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#0B1B3D", color: "#fff", border: "none", borderRadius: 8 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Organisation table */}
        <div className="lg:col-span-3 bg-white border border-slate-200 rounded-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <div className="text-xs uppercase tracking-widest text-slate-500 font-bold">Organisations</div>
              <div className="font-display text-xl text-kfr-navy font-semibold mt-1">Registrations by partner</div>
            </div>
          </div>
          {data.organisation.length === 0 ? <div className="text-slate-400 text-sm">No data</div> : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {data.organisation.map((o, i) => (
                <div key={i} className="border border-slate-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-slate-500 text-xs"><Building2 className="w-3.5 h-3.5" /> {o.name}</div>
                  <div className="font-display text-2xl text-kfr-navy font-bold mt-2">{o.count}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Stat({ icon: Icon, label, value, color, testid }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-widest text-slate-500 font-bold">{label}</div>
        <div className="w-8 h-8 rounded-md flex items-center justify-center" style={{ background: color }}><Icon className="w-4 h-4 text-white" /></div>
      </div>
      <div className="font-display text-3xl text-kfr-navy font-bold mt-4" data-testid={testid}>{value}</div>
    </div>
  );
}

function EmptyChart({ label }) {
  return <div className="h-full flex items-center justify-center text-slate-400 text-sm">{label}</div>;
}
