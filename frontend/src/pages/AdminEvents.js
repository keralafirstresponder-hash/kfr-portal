import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Plus, Trash2, CalendarDays, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";

export default function AdminEvents() {
  const [events, setEvents] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", training_date: "", place: "", trainer: "", organisation: "Aster Medcity" });

  const load = () => api.get("/events").then(r => setEvents(r.data));
  useEffect(() => { load(); }, []);

  const create = async () => {
    if (!form.name || !form.training_date || !form.place) { toast.error("Fill all required fields"); return; }
    try {
      await api.post("/events", form);
      toast.success("Training session created");
      setOpen(false);
      setForm({ name: "", training_date: "", place: "", trainer: "", organisation: "Aster Medcity" });
      load();
    } catch (err) { toast.error(err?.response?.data?.detail || "Failed"); }
  };

  const del = async (id) => {
    if (!confirm("Delete this training session?")) return;
    await api.delete(`/events/${id}`);
    toast.success("Deleted");
    load();
  };

  return (
    <div className="p-8 lg:p-10">
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Training</div>
          <h1 className="font-display text-4xl font-bold text-kfr-navy mt-2" data-testid="events-title">Training Sessions</h1>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-kfr-red hover:bg-[#d92b3a] text-white" data-testid="add-event-btn"><Plus className="w-4 h-4 mr-2" /> New session</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle className="font-display text-2xl text-kfr-navy">New training session</DialogTitle></DialogHeader>
            <div className="grid gap-4 mt-4">
              <div><Label>Name</Label><Input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="KFR CPR Training — Kochi Batch 2" data-testid="event-name-input" /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Date</Label><Input type="date" value={form.training_date} onChange={e => setForm({ ...form, training_date: e.target.value })} data-testid="event-date-input" /></div>
                <div><Label>Organisation</Label><Input value={form.organisation} onChange={e => setForm({ ...form, organisation: e.target.value })} data-testid="event-org-input" /></div>
              </div>
              <div><Label>Place</Label><Input value={form.place} onChange={e => setForm({ ...form, place: e.target.value })} placeholder="Aster Medcity, Kochi" data-testid="event-place-input" /></div>
              <div><Label>Trainer</Label><Input value={form.trainer} onChange={e => setForm({ ...form, trainer: e.target.value })} placeholder="Dr. Anish Menon" data-testid="event-trainer-input" /></div>
            </div>
            <DialogFooter className="mt-6">
              <Button className="bg-kfr-red hover:bg-[#d92b3a] text-white" onClick={create} data-testid="event-save-btn">Create session</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {events.length === 0 && <div className="text-slate-500 col-span-full text-center p-16 bg-white border border-slate-200 rounded-xl">No training sessions yet.</div>}
        {events.map(ev => (
          <div key={ev.id} className="bg-white border border-slate-200 rounded-xl p-6 hover:border-kfr-gold transition-colors">
            <div className="flex justify-between items-start">
              <div className="w-10 h-10 rounded-md bg-kfr-navy flex items-center justify-center"><CalendarDays className="w-5 h-5 text-kfr-gold" /></div>
              <button onClick={() => del(ev.id)} className="text-slate-400 hover:text-red-500" data-testid={`del-event-${ev.id}`}><Trash2 className="w-4 h-4" /></button>
            </div>
            <div className="font-display text-lg font-semibold text-kfr-navy mt-4">{ev.name}</div>
            <div className="text-sm text-slate-500 mt-3 flex items-center gap-2"><CalendarDays className="w-3.5 h-3.5" /> {ev.training_date}</div>
            <div className="text-sm text-slate-500 mt-1 flex items-center gap-2"><MapPin className="w-3.5 h-3.5" /> {ev.place}</div>
            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
              <span className="text-slate-400">Trainer:</span> {ev.trainer || "—"} · <span className="text-slate-400">Org:</span> {ev.organisation}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
