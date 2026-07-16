import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Plus, Trash2, Edit3, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";

const EMPTY = {
  text: "",
  options: [
    { key: "A", text: "" }, { key: "B", text: "" }, { key: "C", text: "" }, { key: "D", text: "" },
  ],
  correct_key: "A",
};

export default function AdminQuestions() {
  const [qs, setQs] = useState([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY);

  const load = () => api.get("/questions").then(r => setQs(r.data));
  useEffect(() => { load(); }, []);

  const openNew = () => { setEditing(null); setForm(JSON.parse(JSON.stringify(EMPTY))); setOpen(true); };
  const openEdit = (q) => { setEditing(q.id); setForm({ text: q.text, options: q.options, correct_key: q.correct_key }); setOpen(true); };

  const save = async () => {
    if (!form.text.trim()) { toast.error("Question text required"); return; }
    if (form.options.some(o => !o.text.trim())) { toast.error("All options required"); return; }
    try {
      if (editing) await api.put(`/questions/${editing}`, form);
      else await api.post("/questions", form);
      toast.success(editing ? "Updated" : "Added");
      setOpen(false);
      load();
    } catch (err) { toast.error(err?.response?.data?.detail || "Failed"); }
  };

  const del = async (id) => {
    if (!confirm("Delete this question?")) return;
    await api.delete(`/questions/${id}`);
    load();
  };

  const setOpt = (i, v) => { const opts = [...form.options]; opts[i] = { ...opts[i], text: v }; setForm({ ...form, options: opts }); };

  return (
    <div className="p-8 lg:p-10">
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-kfr-red font-bold">Assessment</div>
          <h1 className="font-display text-4xl font-bold text-kfr-navy mt-2" data-testid="questions-title">MCQ Question Bank</h1>
          <div className="text-slate-500 mt-2 text-sm">{qs.length} questions · 10 are randomly picked per candidate.</div>
        </div>
        <Button className="bg-kfr-red hover:bg-[#d92b3a] text-white" onClick={openNew} data-testid="add-question-btn"><Plus className="w-4 h-4 mr-2" /> New question</Button>
      </div>

      <div className="space-y-3">
        {qs.map((q, i) => (
          <div key={q.id} className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex justify-between items-start gap-4">
              <div className="flex-1">
                <div className="text-xs text-slate-400 font-mono">Q{i + 1}</div>
                <div className="font-medium text-kfr-navy mt-1">{q.text}</div>
                <div className="mt-3 grid sm:grid-cols-2 gap-2">
                  {q.options.map(o => (
                    <div key={o.key} className={`text-sm p-2.5 rounded-md border ${o.key === q.correct_key ? "border-emerald-300 bg-emerald-50" : "border-slate-200"}`}>
                      <span className="font-mono text-xs text-slate-500 mr-2">{o.key}.</span>
                      {o.text}
                      {o.key === q.correct_key && <CheckCircle2 className="inline w-4 h-4 text-emerald-600 ml-2" />}
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => openEdit(q)} className="p-2 text-slate-400 hover:text-kfr-navy" data-testid={`edit-q-${q.id}`}><Edit3 className="w-4 h-4" /></button>
                <button onClick={() => del(q.id)} className="p-2 text-slate-400 hover:text-red-500" data-testid={`del-q-${q.id}`}><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader><DialogTitle className="font-display text-2xl text-kfr-navy">{editing ? "Edit question" : "New question"}</DialogTitle></DialogHeader>
          <div className="grid gap-4 mt-4">
            <div><Label>Question text</Label><Textarea rows={2} value={form.text} onChange={e => setForm({ ...form, text: e.target.value })} data-testid="q-text-input" /></div>
            <div>
              <Label>Options (select the correct one)</Label>
              <RadioGroup value={form.correct_key} onValueChange={(v) => setForm({ ...form, correct_key: v })} className="mt-3 grid gap-2">
                {form.options.map((o, i) => (
                  <div key={o.key} className="flex items-center gap-3 border border-slate-200 rounded-md p-2.5">
                    <RadioGroupItem value={o.key} id={`opt-${o.key}`} data-testid={`q-correct-${o.key}`} />
                    <Label htmlFor={`opt-${o.key}`} className="font-mono text-sm text-slate-500 min-w-4">{o.key}</Label>
                    <Input value={o.text} onChange={(e) => setOpt(i, e.target.value)} placeholder={`Option ${o.key}`} className="flex-1 border-0 focus-visible:ring-0" data-testid={`q-opt-${o.key}`} />
                  </div>
                ))}
              </RadioGroup>
            </div>
          </div>
          <DialogFooter className="mt-6">
            <Button className="bg-kfr-red hover:bg-[#d92b3a] text-white" onClick={save} data-testid="q-save-btn">{editing ? "Save changes" : "Add question"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
