import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const ALL = "__all__";
const COLORS = ["#0B1B3D", "#E63946", "#D4AF37", "#007260", "#1A2B56", "#94A3B8", "#F59E0B", "#10B981", "#64748B"];

export default function AdminReports() {
  const [summary, setSummary] = useState(null);
  const [meta, setMeta] = useState({ districts: [], categories: [], orgs: [], events: [] });
  const [filters, setFilters] = useState({ district: ALL, category: ALL, organisation: ALL, event_id: ALL });

  useEffect(() => {
    api.get("/reports/summary").then(r => setSummary(r.data));
    Promise.all([api.get("/districts"), api.get("/categories"), api.get("/organisations"), api.get("/events")])
      .then(([d, c, o, e]) => setMeta({ districts: d.data, categories: c.data, orgs: o.data, events: e.data }));
  }, []);

  const setFilter = (k, v) => setFilters(f => ({ ...f, [k]: v }));

  const exportCsv = async () => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v && v !== ALL) params.append(k, v); });
    const token = localStorage.getItem("kfr_token");
    const url = `${process.env.REACT_APP_BACKEND_URL}/api/reports/export?${params.toString()}`;
    const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await r.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "kfr_report.csv";
    link.click();
  };

  if (!summary) return <div className="p-10 text-slate-500">Loading…</div>;

  const t = summary.totals;
  const passRate = t.candidates ? ((t.passed / t.candidates) * 100).toFixed(1) : "0.0";

  return (
    <div className="p-8 lg:p-10">
      <div className="flex flex-wrap justify-between items-end gap-4 mb-8">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Reports</div>
          <h1 className="font-display text-4xl font-bold text-kfr-navy mt-2" data-testid="reports-title">Analytics & Reports</h1>
        </div>
        <Button variant="outline" onClick={exportCsv} data-testid="report-export-btn"><Download className="w-4 h-4 mr-2" /> Export filtered CSV</Button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6 grid md:grid-cols-4 gap-3">
        <FilterSelect placeholder="All districts" value={filters.district} onChange={v => setFilter("district", v)} options={meta.districts.map(d => ({ v: d, l: d }))} testid="rep-filter-district" />
        <FilterSelect placeholder="All categories" value={filters.category} onChange={v => setFilter("category", v)} options={meta.categories.map(c => ({ v: c, l: c }))} testid="rep-filter-category" />
        <FilterSelect placeholder="All organisations" value={filters.organisation} onChange={v => setFilter("organisation", v)} options={meta.orgs.map(o => ({ v: o.name, l: o.name }))} testid="rep-filter-org" />
        <FilterSelect placeholder="All sessions" value={filters.event_id} onChange={v => setFilter("event_id", v)} options={meta.events.map(e => ({ v: e.id, l: e.name }))} testid="rep-filter-event" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Metric label="Total Registered" value={t.candidates} testid="rep-total" />
        <Metric label="Certified" value={t.passed} testid="rep-passed" />
        <Metric label="Failed" value={t.failed} testid="rep-failed" />
        <Metric label="Pass rate" value={`${passRate}%`} testid="rep-passrate" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <ChartCard title="District-wise registration">
          <BarChart data={summary.district}>
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748B" }} interval={0} angle={-25} textAnchor="end" height={70} />
            <YAxis tick={{ fontSize: 11, fill: "#64748B" }} allowDecimals={false} />
            <Tooltip contentStyle={{ background: "#0B1B3D", color: "#fff", border: "none", borderRadius: 8 }} />
            <Bar dataKey="count" fill="#E63946" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ChartCard>
        <ChartCard title="Category distribution">
          <PieChart>
            <Pie data={summary.category} dataKey="count" nameKey="name" innerRadius={50} outerRadius={90} paddingAngle={2}>
              {summary.category.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip contentStyle={{ background: "#0B1B3D", color: "#fff", border: "none", borderRadius: 8 }} />
          </PieChart>
        </ChartCard>
      </div>
    </div>
  );
}

function FilterSelect({ testid, placeholder, value, onChange, options }) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger data-testid={testid}><SelectValue placeholder={placeholder} /></SelectTrigger>
      <SelectContent>
        <SelectItem value={ALL}>{placeholder}</SelectItem>
        {options.map(o => <SelectItem key={o.v} value={o.v}>{o.l}</SelectItem>)}
      </SelectContent>
    </Select>
  );
}

function Metric({ label, value, testid }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <div className="text-xs uppercase tracking-widest text-slate-500 font-bold">{label}</div>
      <div className="font-display text-3xl text-kfr-navy font-bold mt-3" data-testid={testid}>{value}</div>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="text-xs uppercase tracking-widest text-slate-500 font-bold">Chart</div>
      <div className="font-display text-xl text-kfr-navy font-semibold mt-1 mb-6">{title}</div>
      <div className="h-72 min-h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
