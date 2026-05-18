import React, { useState, useEffect } from 'react';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

function App() {
  const [subjects, setSubjects] = useState([]);
  const [faculties, setFaculties] = useState([]);
  const [currentFacultyId, setCurrentFacultyId] = useState("1");
  const [selectedSemester, setSelectedSemester] = useState("4");
  const [preferences, setPreferences] = useState({ first: "", second: "", third: "" });
  const [allocationResults, setAllocationResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const refreshSystemMetrics = async () => {
    try {
      const subRes = await fetch(`${API_URL}/subjects/available/`);
      if (subRes.ok) {
        const subData = await subRes.json();
        setSubjects(subData);
      }
      const facRes = await fetch(`${API_URL}/faculty-list/`);
      if (facRes.ok) {
        const facData = await facRes.json();
        setFaculties(facData);
        if (facData.length > 0 && !currentFacultyId) {
          setCurrentFacultyId(String(facData[0].id));
        }
      }
    } catch (err) {
      console.error("Critical failure during live sync loop:", err);
    }
  };

  useEffect(() => {
    async function bootSequence() {
      try {
        await fetch(`${API_URL}/seed-data/`, { method: 'POST' });
        await refreshSystemMetrics();
      } catch (e) {
        console.error("Initialization sequence fault:", e);
      }
    }
    bootSequence();
  }, []);

  const handleSelectionChange = (priority, value) => {
    setPreferences(prev => ({ ...prev, [priority]: value }));
  };

  const submitPreferences = async () => {
    const values = Object.values(preferences).filter(v => v !== "");
    if (values.length < 3) {
      alert("Please designate all 3 distinct choices before submitting.");
      return;
    }
    if (new Set(values).size !== values.length) {
      alert("Error: Duplicate selection found within this profile layout.");
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/submit-preferences/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          faculty_id: Number(currentFacultyId),
          first_choice_id: Number(preferences.first),
          second_choice_id: Number(preferences.second),
          third_choice_id: Number(preferences.third),
        })
      });
      if (res.ok) {
        alert(`Choices recorded for Faculty Profile #${currentFacultyId}! Conflicting targets will now filter out.`);
        setPreferences({ first: "", second: "", third: "" });
        await refreshSystemMetrics();
      } else {
        const payload = await res.json();
        alert(`Fault: ${payload.detail}`);
      }
    } catch (e) {
      alert("Network connectivity pipeline loss.");
    }
  };

  const executeAllocationMatrix = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/allocate/`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setAllocationResults(data.allocations);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // NEW FEATURE: Download Choice Audit PDF (Who has chosen what?)
  const downloadChoiceAuditPDF = async () => {
    try {
      const response = await fetch(`${API_URL}/preferences/master-report/`);
      const data = await response.json();
      
      if (data.length === 0) {
        alert("No submissions are active in system registry memory yet.");
        return;
      }

      const doc = new jsPDF();
      doc.setFont("helvetica", "bold");
      doc.setFontSize(15);
      doc.text("MASTER FACULTY SUBJECT SELECTION SUBMISSIONS REGISTRY", 14, 20);

      const rows = data.map((item, i) => [
        i + 1,
        item.faculty_name,
        `Sem ${item.semester}`,
        `[${item.subject_code}] ${item.subject_name}`,
        `Choice #${item.priority}`
      ]);

      autoTable(doc, {
        startY: 28,
        head: [['Index', 'Faculty Account Name', 'Semester', 'Selected Subject Specification', 'Stated Priority']],
        body: rows,
        theme: 'striped',
        headStyles: { fillColor: [51, 65, 85] }
      });

      doc.save("Faculty_Selections_Audit_Log.pdf");
    } catch (e) {
      console.error(e);
    }
  };

  const downloadAllocationPDF = () => {
    if (!allocationResults) return;
    const doc = new jsPDF();
    doc.setFont("helvetica", "bold");
    doc.setFontSize(15);
    doc.text("FINAL MASTER SUBJECT ALLOCATION MAP REGISTRY", 14, 20);

    const rows = allocationResults.map((item, i) => [
      i + 1,
      item.faculty_name,
      item.subject_name,
      `Priority Match #${item.priority_matched}`
    ]);

    autoTable(doc, {
      startY: 28,
      head: [['Index', 'Faculty Assignment Target', 'Allocated Course Assignment', 'Allocation Basis']],
      body: rows,
      theme: 'grid',
      headStyles: { fillColor: [15, 23, 42] }
    });
    doc.save("Final_Academic_Allocations.pdf");
  };

  const filteredSubjects = subjects.filter(sub => String(sub.semester) === String(selectedSemester));

  return (
    <div className="min-h-screen bg-slate-100 p-6 font-sans">
      <header className="mb-6 bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h1 className="text-2xl font-bold text-slate-800">Faculty Allocation Matrix System (25 Faculty & 50 Subjects)</h1>
        <p className="text-xs text-slate-400 mt-1">Defensive data-type mapping interface with auto-filtering active.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Step 1 Layout */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <h2 className="font-semibold text-slate-700 text-base mb-1">1. Simulate Identity Profile</h2>
          <p className="text-[11px] text-slate-400 mb-4">Switch accounts to simulate preferences for multiple faculty members.</p>
          
          <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Active Simulation Context</label>
          <select 
            value={currentFacultyId}
            onChange={(e) => setCurrentFacultyId(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-xs focus:ring-1 focus:ring-blue-500"
          >
            {faculties.map(f => (
              <option key={f.id} value={String(f.id)}>{f.name}</option>
            ))}
          </select>

          <button 
            onClick={downloadChoiceAuditPDF}
            className="w-full bg-slate-700 hover:bg-slate-800 text-white font-bold text-xs py-2 rounded-lg mt-4 transition"
          >
            📋 Download Choices Audit PDF
          </button>
        </div>

        {/* Step 2 Layout */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <h2 className="font-semibold text-slate-700 text-base mb-1">2. Secure Preference Registry</h2>
          <p className="text-[11px] text-slate-400 mb-3">Subjects will automatically filter out of the pool once their allocation sections are filled.</p>
          
          <div className="mb-4">
            <span className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5">Curriculum Filter by Semester</span>
            <div className="flex flex-wrap gap-1">
              {[1, 2, 3, 4, 5, 6, 7, 8].map(sem => (
                <button 
                  key={sem}
                  type="button"
                  onClick={() => setSelectedSemester(String(sem))}
                  className={`px-2.5 py-1 rounded text-[11px] font-bold transition ${String(selectedSemester) === String(sem) ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}`}
                >
                  S{sem}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3 border-t border-slate-100 pt-3">
            {['first', 'second', 'third'].map(p => (
              <div key={p}>
                <label className="block text-[10px] text-slate-400 font-bold uppercase mb-1 capitalize">{p} Choice Assignment</label>
                <select 
                  value={preferences[p]} 
                  onChange={(e) => handleSelectionChange(p, e.target.value)}
                  className="w-full border border-slate-300 bg-white rounded-lg p-2 text-xs"
                >
                  <option value="">-- Choose Course Pool (Sem {selectedSemester}) --</option>
                  {filteredSubjects.map(sub => (
                    <option key={sub.id} value={String(sub.id)}>[{sub.subject_code}] {sub.subject_name}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          <button 
            onClick={submitPreferences}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2 rounded-lg mt-4 transition"
          >
            Lock Choices for this Profile
          </button>
        </div>

        {/* Step 3 Layout */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
          <h2 className="font-semibold text-slate-700 text-base mb-1">3. Executive Engine Dispatch</h2>
          <p className="text-[11px] text-slate-400 mb-4">Run the processing matrix matching algorithm across the database.</p>
          
          <div className="space-y-2">
            <button 
              onClick={executeAllocationMatrix}
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-2.5 rounded-lg transition"
            >
              {loading ? "COMPUTING MATCHES..." : "⚡ RUN ENGINE ALLOCATION"}
            </button>
            
            {allocationResults && (
              <button 
                onClick={downloadAllocationPDF}
                className="w-full bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold py-2 rounded-lg transition"
              >
                📥 Download Allocation Map PDF
              </button>
            )}
          </div>

          <div className="border-t border-slate-100 mt-4 pt-3">
            <span className="text-[10px] font-bold text-slate-400 uppercase block mb-2">Live Map Output Stream ({allocationResults?.length || 0} Filled)</span>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {allocationResults?.map((alloc, idx) => (
                <div key={idx} className="bg-slate-50 border border-slate-200 p-2 rounded text-[10px] flex flex-col gap-0.5">
                  <div className="flex justify-between font-medium">
                    <span className="text-slate-700">{alloc.faculty_name}</span>
                    <span className="text-blue-600 font-mono">{alloc.priority_matched == 1 ? "1st Pref" : alloc.priority_matched == 2 ? "2nd Pref" : "3rd Pref"}</span>
                  </div>
                  <span className="text-slate-400 font-mono text-[9px]">{alloc.subject_name}</span>
                </div>
              )) || <div className="text-xs text-slate-300 italic text-center py-4">No active allocations processed yet.</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;