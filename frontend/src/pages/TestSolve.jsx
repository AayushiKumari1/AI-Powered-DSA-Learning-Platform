import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ChevronLeft, ChevronRight, ClipboardX, Flag, Maximize, Play, ShieldAlert, TriangleAlert } from "lucide-react";
import { api } from "@/lib/api";
import Workspace from "@/components/Workspace";
import { Button, ErrorState, Skeleton } from "@/components/ui";

function loadScript(src) {
  return new Promise((res, rej) => { if (document.querySelector(`script[src="${src}"]`)) return res(); const s = Object.assign(document.createElement("script"), { src, onload: res, onerror: rej }); document.head.appendChild(s); });
}

export default function TestSolve() {
  const { id, index } = useParams();
  const i = Number(index);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["test", id], queryFn: () => api.get(`/api/tests/${id}`) });
  const [started, setStarted] = useState(() => sessionStorage.getItem(`em_test_${id}`) === "1");
  const [violations, setViolations] = useState(0);
  const last = useRef(null);
  const qStart = useRef(Date.now());
  const leaving = useRef(false);
  const lastViolation = useRef(0);
  const camRef = useRef(null);
  useEffect(() => { last.current = null; qStart.current = Date.now(); }, [index]);

  const question = data?.test.questions[i];
  const total = data?.test.questions.length || 0;

  async function saveAndGo(url, auto) {
    if (!last.current && !auto && !confirm("You haven't submitted this question. Move on and mark it as failed?")) return;
    leaving.current = true;
    try {
      await api.post("/coding-tests/submit-result", { test_id: Number(id), question_id: question.id, status: last.current?.status || "Failed", time_taken: Math.floor((Date.now() - qStart.current) / 1000) });
      if (url.endsWith("/result")) { sessionStorage.removeItem(`em_test_${id}`); if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); qc.invalidateQueries({ queryKey: ["tests"] }); }
      navigate(url);
    } catch (e) { leaving.current = false; toast.error("Couldn't save your result. Check your connection and try again."); }
    setTimeout(() => { leaving.current = false; }, 500);
  }
  const finish = (auto) => saveAndGo(`/tests/${id}/result`, auto);
  const finishRef = useRef(finish); finishRef.current = finish;

  // Proctoring
  useEffect(() => {
    if (!started) return;
    let tabSwitches = 0, raf, faceTimer, stream;
    const violation = (reason) => {
      if (leaving.current) return;
      const now = Date.now(); if (now - lastViolation.current < 5000) return; lastViolation.current = now;
      setViolations((v) => { const n = v + 1; toast.error(`Violation: ${reason} (${n}/3)`); if (n >= 3) { toast.error("Too many violations — submitting your test."); setTimeout(() => finishRef.current(true), 1500); } return n; });
    };
    const onVis = () => { if (document.hidden && ++tabSwitches > 1) violation("Switched tab"); };
    const block = (label) => (e) => { e.preventDefault(); violation(label); };
    const onCopy = block("Copy attempt"), onPaste = block("Paste attempt"), onCtx = block("Right click");
    const onFs = () => { if (!document.fullscreenElement) violation("Exited fullscreen"); };
    document.addEventListener("visibilitychange", onVis);
    document.addEventListener("copy", onCopy, true); document.addEventListener("paste", onPaste, true);
    document.addEventListener("contextmenu", onCtx); document.addEventListener("fullscreenchange", onFs);
    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (camRef.current) { camRef.current.srcObject = new MediaStream(stream.getVideoTracks()); await camRef.current.play(); }
        const ctx = new (window.AudioContext || window.webkitAudioContext)(); const an = ctx.createAnalyser(); an.fftSize = 256;
        ctx.createMediaStreamSource(new MediaStream(stream.getAudioTracks())).connect(an);
        const buf = new Uint8Array(an.frequencyBinCount);
        const loop = () => { an.getByteFrequencyData(buf); if (buf.reduce((a, b) => a + b, 0) / buf.length > 60) violation("Suspicious audio"); raf = requestAnimationFrame(loop); }; loop();
        await loadScript("https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.17.0/dist/tf.min.js");
        await loadScript("https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.1.0/dist/blazeface.min.js");
        const model = await window.blazeface.load();
        faceTimer = setInterval(async () => { const v = camRef.current; if (!v || v.readyState !== 4) return; const faces = await model.estimateFaces(v, false); if (faces.length > 1) violation("Multiple faces detected"); }, 3000);
      } catch { toast.warning("Camera or microphone unavailable. Proctoring continues without them."); }
    })();
    return () => {
      document.removeEventListener("visibilitychange", onVis); document.removeEventListener("copy", onCopy, true); document.removeEventListener("paste", onPaste, true);
      document.removeEventListener("contextmenu", onCtx); document.removeEventListener("fullscreenchange", onFs);
      cancelAnimationFrame(raf); clearInterval(faceTimer); stream?.getTracks().forEach((t) => t.stop());
    };
  }, [started]);

  async function start() {
    try { await document.documentElement.requestFullscreen(); } catch { /* not allowed */ }
    sessionStorage.setItem(`em_test_${id}`, "1"); setStarted(true);
  }

  if (isLoading) return <div className="p-4"><Skeleton className="h-[calc(100vh-6rem)]" /></div>;
  if (error) return <ErrorState error={error} retry={refetch} />;
  if (!question) return <ErrorState error={{ message: "That question doesn't exist in this test." }} />;

  return (
    <>
      <Workspace key={question.id} isTest problem={question} draftKey={`t${id}_${question.id}`} onSubmitted={(r) => { last.current = r; }}
        toolbarLeft={<>
          <span className="inline-flex items-center gap-1.5 rounded-md border border-hard/30 bg-hard/15 px-2 py-0.5 text-xs font-medium text-hard"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-hard" />{data.test.title}</span>
          <span className="font-mono text-xs text-muted-foreground">Q{i + 1}/{total}</span>
          <span className="hidden items-center gap-1 rounded-md border border-border px-2 py-0.5 text-xs text-muted-foreground md:inline-flex"><ShieldAlert className="h-3.5 w-3.5 text-medium" />{violations}/3</span>
        </>}
        toolbarRight={<>
          <div className="mx-1 h-5 w-px bg-border" />
          {i > 0 && <Button variant="outline" size="sm" aria-label="Previous question" onClick={() => saveAndGo(`/tests/${id}/solve/${i - 1}`, true)}><ChevronLeft /></Button>}
          {i + 1 < total ? <Button variant="outline" size="sm" onClick={() => saveAndGo(`/tests/${id}/solve/${i + 1}`)}>Next <ChevronRight /></Button>
            : <Button size="sm" className="border border-easy/40 bg-easy/15 text-easy hover:bg-easy/25" onClick={() => finish(false)}><Flag /> Finish test</Button>}
        </>}
      />
      {started && <video ref={camRef} muted playsInline className="fixed bottom-4 left-4 z-40 w-32 rounded-lg border-2 border-hard/60 shadow-lg md:left-[17rem]" />}
      {!started && (
        <div className="fixed inset-0 z-[90] grid place-items-center bg-background/90 p-4 backdrop-blur-sm">
          <div className="glow-border w-full max-w-md rounded-xl border border-border bg-card p-6">
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-hard"><span className="h-2 w-2 animate-pulse rounded-full bg-hard" /> PROCTORED TEST</div>
            <h2 className="text-xl font-semibold tracking-tight">{data.test.title}</h2>
            <p className="mt-1 text-sm text-muted-foreground">Question {i + 1} of {total}. Starting enters fullscreen and asks for camera and microphone access.</p>
            <ul className="mt-4 space-y-2 text-sm">
              <li className="flex gap-2"><Maximize className="mt-0.5 h-4 w-4 text-muted-foreground" /> Leaving fullscreen or switching tabs counts as a violation</li>
              <li className="flex gap-2"><ClipboardX className="mt-0.5 h-4 w-4 text-muted-foreground" /> Copy, paste and right-click are blocked</li>
              <li className="flex gap-2"><TriangleAlert className="mt-0.5 h-4 w-4 text-muted-foreground" /> 3 violations submit the test automatically</li>
            </ul>
            <Button className="mt-6 w-full" onClick={start}><Play /> {i === 0 ? "Start test" : "Continue test"}</Button>
            <Button variant="ghost" className="mt-2 w-full" to={`/tests/${id}`}>Back to overview</Button>
          </div>
        </div>
      )}
    </>
  );
}
