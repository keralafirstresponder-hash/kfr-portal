import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Plus, Trash2, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AdminOrganisations() {
  const [orgs, setOrgs] = useState([]);
  const [name, setName] = useState("");

  const load = () => api.get("/organisations").then(r => setOrgs(r.data));
  useEffect(() => { load(); }, []);

  const add = async () => {
    if (!name.trim()) return;
    try {
      await api.post("/organisations", { name: name.trim() });
      toast.success("Added");
      setName("");
      load();
    } catch (err) { toast.error(err?.response?.data?.detail || "Failed"); }
  };

  const del = async (id) => {
    if (!confirm("Delete this organisation?")) return;
    await api.delete(`/organisations/${id}`);
    load();
  };

  return (
    <div className="p-8 lg:p-10 max-w-3xl">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Organisations</div>
        <h1 className="font-display text-4xl font-bold text-kfr-navy mt-2" data-testid="orgs-title">Partner Organisations</h1>
        <div className="text-slate-500 mt-2 text-sm">These appear in the registration form dropdown.</div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 flex gap-3">
        <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Aster Medcity" onKeyDown={e => e.key === "Enter" && add()} data-testid="org-name-input" />
        <Button className="bg-kfr-red hover:bg-[#d92b3a] text-white" onClick={add} data-testid="org-add-btn"><Plus className="w-4 h-4 mr-2" /> Add</Button>
      </div>

      <div className="mt-6 bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
        {orgs.length === 0 && <div className="p-8 text-slate-400 text-center">No organisations yet.</div>}
        {orgs.map(o => (
          <div key={o.id} className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center"><Building2 className="w-4 h-4 text-kfr-navy" /></div>
              <div className="font-medium text-kfr-navy">{o.name}</div>
            </div>
            <button onClick={() => del(o.id)} className="text-slate-400 hover:text-red-500" data-testid={`del-org-${o.id}`}><Trash2 className="w-4 h-4" /></button>
          </div>
        ))}
      </div>
    </div>
  );
}
