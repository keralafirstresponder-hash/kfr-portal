import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Send, Search, Download, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

const ALL = "__all__";

export default function AdminCandidates() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(new Set());
  const [filters, setFilters] = useState({ district: ALL, category: ALL, organisation: ALL, event_id: ALL, test_status: ALL });
  const [search, setSearch] = useState("");
  const [meta, setMeta] = useState({ districts: [], categories: [], orgs: [], events: [] });
  const [generating, setGenerating] = useState(false);

  const load = async () => {
    setLoading(true);
    const params = {};
    Object.entries(filters).forEach(([k, v]) => { if (v && v !== ALL) params[k] = v; });
    try {
      const { data } = await api.get("/candidates", { params });
      setRows(data);
      setSelected(new Set());
    } finally { setLoading(false); }
  };

  useEffect(() => {
    Promise.all([
      api.get("/districts"), api.get("/categories"), api.get("/organisations"), api.get("/events"),
    ]).then(([d, c, o, e]) => setMeta({ districts: d.data, categories: c.data, orgs: o.data, events: e.data }));
  }, []);

  useEffect(() => { load(); }, [filters]);

  const filtered = useMemo(() => {
    if (!search) return rows;
    const s = search.toLowerCase();
    return rows.filter(r => r.name?.toLowerCase().includes(s) || r.email?.toLowerCase().includes(s) || r.phone?.includes(s));
  }, [rows, search]);

  const toggle = (id) => {
    const n = new Set(selected);
    n.has(id) ? n.delete(id) : n.add(id);
    setSelected(n);
  };
  const toggleAll = () => setSelected(selected.size === filtered.length ? new Set() : new Set(filtered.map(r => r.id)));

  const generateTest = async () => {
    if (selected.size === 0) { toast.error("Select at least one candidate"); return; }
    setGenerating(true);
    try {
      const { data } = await api.post("/admin/generate-test", { candidate_ids: Array.from(selected) });
      toast.success(`Test link sent to ${data.sent} of ${data.total} candidates`);
      load();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to generate test");
    } finally { setGenerating(false); }
  };

  const exportCsv = async () => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v && v !== ALL) params.append(k, v); });
    const token = localStorage.getItem("kfr_token");
    const url = `${process.env.REACT_APP_BACKEND_URL}/api/reports/export?${params.toString()}`;
    const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await r.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "kfr_candidates.csv";
    link.click();
  };

  const setFilter = (k, v) => setFilters(f => ({ ...f, [k]: v }));

  return (
    <div className="p-8 lg:p-10">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Candidates</div>
          <h1 className="font-display text-4xl font-bold text-kfr-navy mt-2" data-testid="candidates-title">Registered Candidates</h1>
          <div className="text-sm text-slate-500 mt-2">{filtered.length} candidates · {selected.size} selected</div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportCsv} data-testid="export-csv-btn"><Download className="w-4 h-4 mr-2" /> Export CSV</Button>
          <Button disabled={generating || selected.size === 0} onClick={generateTest} data-testid="generate-test-btn" className="bg-kfr-red hover:bg-[#d92b3a] text-white">
            <Send className="w-4 h-4 mr-2" /> {generating ? "Sending…" : `Generate Test (${selected.size})`}
          </Button>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-4 grid md:grid-cols-6 gap-3">
        <div className="md:col-span-2 relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search name, email, phone" className="pl-9" data-testid="candidates-search" />
        </div>
        <FilterSelect testid="filter-district" placeholder="All districts" value={filters.district} onChange={v => setFilter("district", v)} options={meta.districts.map(d => ({ v: d, l: d }))} />
        <FilterSelect testid="filter-category" placeholder="All categories" value={filters.category} onChange={v => setFilter("category", v)} options={meta.categories.map(c => ({ v: c, l: c }))} />
        <FilterSelect testid="filter-organisation" placeholder="All organisations" value={filters.organisation} onChange={v => setFilter("organisation", v)} options={meta.orgs.map(o => ({ v: o.name, l: o.name }))} />
        <FilterSelect testid="filter-status" placeholder="All statuses" value={filters.test_status} onChange={v => setFilter("test_status", v)} options={[
          { v: "not_sent", l: "Not sent" }, { v: "pending", l: "Pending" }, { v: "passed", l: "Passed" }, { v: "failed", l: "Failed" },
        ]} />
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm" data-testid="candidates-table">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider">
              <tr>
                <th className="p-4 w-10"><Checkbox checked={selected.size > 0 && selected.size === filtered.length} onCheckedChange={toggleAll} data-testid="select-all-cb" /></th>
                <th className="p-4 text-left">Name</th>
                <th className="p-4 text-left">Contact</th>
                <th className="p-4 text-left">District</th>
                <th className="p-4 text-left">Category</th>
                <th className="p-4 text-left">Session</th>
                <th className="p-4 text-left">Status</th>
                <th className="p-4 text-left">Test link</th>
              </tr>
            </thead>
            <tbody>
              {loading && <tr><td colSpan={8} className="p-8 text-center text-slate-400">Loading…</td></tr>}
              {!loading && filtered.length === 0 && <tr><td colSpan={8} className="p-8 text-center text-slate-400">No candidates match your filters.</td></tr>}
              {filtered.map(r => (
                <tr key={r.id} className="border-b border-slate-100 hover:bg-slate-50/60">
                  <td className="p-4"><Checkbox checked={selected.has(r.id)} onCheckedChange={() => toggle(r.id)} data-testid={`cb-${r.id}`} /></td>
                  <td className="p-4">
                    <div className="font-medium text-kfr-navy">{r.name}</div>
                    <div className="text-xs text-slate-500">{r.organisation}</div>
                  </td>
                  <td className="p-4">
                    <div className="text-slate-700">{r.email}</div>
                    <div className="text-xs text-slate-500">{r.phone}</div>
                  </td>
                  <td className="p-4">{r.district}</td>
                  <td className="p-4">{r.category}</td>
                  <td className="p-4">
                    <div className="text-slate-700">{r.event_name || "—"}</div>
                    <div className="text-xs text-slate-500">{r.event_date}</div>
                  </td>
                  <td className="p-4"><StatusBadge status={r.test_status} score={r.test_score} /></td>
                  <td className="p-4">
                    {r.test_token ? (
                      <a href={`/test/${r.test_token}`} target="_blank" rel="noreferrer" className="text-kfr-red hover:underline inline-flex items-center gap-1 text-xs" data-testid={`test-link-${r.id}`}>
                        Open <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : <span className="text-slate-300 text-xs">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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

function StatusBadge({ status, score }) {
  const map = {
    not_sent: { l: "Not sent", cls: "bg-slate-100 text-slate-600" },
    pending: { l: "Pending", cls: "bg-amber-100 text-amber-700" },
    passed: { l: `Passed (${score}/10)`, cls: "bg-emerald-100 text-emerald-700" },
    failed: { l: `Failed (${score}/10)`, cls: "bg-red-100 text-red-700" },
  };
  const m = map[status] || map.not_sent;
  return <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${m.cls}`}>{m.l}</span>;
}
