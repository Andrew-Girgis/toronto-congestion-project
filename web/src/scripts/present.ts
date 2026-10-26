// Deck navigation: keys, clicker, swipe, step reveals, hash per slide, overview (O),
// presenter view (S) synced over BroadcastChannel, and a timer against each slide's target.

const stage = document.querySelector(".stage") as HTMLElement;
const slides = [...document.querySelectorAll<HTMLElement>(".slide")];
const progress = document.querySelector(".progress") as HTMLElement;
const pageno = document.querySelector(".pageno") as HTMLElement;
const isPresenter = new URLSearchParams(location.search).has("presenter");
const chan = "BroadcastChannel" in window ? new BroadcastChannel("cordon-deck") : null;
const timed = slides.filter((s) => !s.hasAttribute("data-appendix"));
const secs = (t: string | null) => (t ? t.split(":").reduce((a, b) => a * 60 + Number(b), 0) : 0);
const TOTAL = timed.reduce((a, s) => a + secs(s.dataset.target ?? null), 0);

let idx = 0;
let step = 0;
let started: number | null = null;

function fit() {
  if (stage.classList.contains("overview")) { stage.style.transform = ""; return; }
  const box = isPresenter ? document.querySelector(".pv-stage") as HTMLElement : document.body;
  const w = box.clientWidth, h = box.clientHeight;
  stage.style.transform = `translate(-50%, -50%) scale(${Math.min(w / 1920, h / 1080)})`;
}

const steps = (s: HTMLElement) => [...s.querySelectorAll<HTMLElement>("[data-step]")];

function show(i: number, st = 0, broadcast = true) {
  idx = Math.max(0, Math.min(slides.length - 1, i));
  const s = slides[idx];
  const all = steps(s);
  step = st < 0 ? all.length : Math.min(st, all.length);
  slides.forEach((x, k) => x.classList.toggle("active", k === idx));
  all.forEach((el, k) => el.classList.toggle("pending", k >= step));
  clipTo(s);
  progress.style.width = `${((timed.indexOf(s) + 1) / timed.length) * 100}%`;
  pageno.textContent = s.classList.contains("sources") ? "sources" : s.hasAttribute("data-appendix") ? "appendix" : `${timed.indexOf(s) + 1} / ${timed.length}`;
  history.replaceState(null, "", `${location.search}#${idx + 1}`);
  if (broadcast) chan?.postMessage({ idx, step });
  if (isPresenter) renderPresenter();
}

// Simulation clip: each click cross-fades to the next frame and bolds its caption.
function clipTo(s: HTMLElement) {
  const frames = [...s.querySelectorAll<HTMLElement>(".clip [data-frame]")];
  const caps = [...s.querySelectorAll<HTMLElement>("[data-cap]")];
  const k = Math.min(step, frames.length - 1);
  frames.forEach((f, j) => f.classList.toggle("on", j === k));
  caps.forEach((c, j) => c.classList.toggle("on", j === k));
}

function next() {
  if (started === null) started = Date.now();
  const all = steps(slides[idx]);
  if (step < all.length) show(idx, step + 1);
  else if (idx < slides.length - 1) show(idx + 1, 0); // past the ask: appendix, then sources
}
function prev() {
  if (step > 0) show(idx, step - 1);
  else if (idx > 0) show(idx - 1, -1);
}

function toggleOverview() {
  stage.classList.toggle("overview");
  fit();
  if (stage.classList.contains("overview")) slides[idx].scrollIntoView({ block: "center" });
}

document.addEventListener("keydown", (e) => {
  if (["ArrowRight", "ArrowDown", "PageDown", " ", "Enter"].includes(e.key)) { e.preventDefault(); next(); }
  else if (["ArrowLeft", "ArrowUp", "PageUp", "Backspace"].includes(e.key)) { e.preventDefault(); prev(); }
  else if (e.key === "Home") show(0);
  else if (e.key === "End") show(timed.length - 1, -1);
  else if (e.key === "o" || e.key === "O" || e.key === "Escape") toggleOverview();
  else if ((e.key === "s" || e.key === "S") && !isPresenter) window.open(`${location.pathname}?presenter#${idx + 1}`, "cordon-presenter", "width=1280,height=760");
  else if (e.key === "t" || e.key === "T") started = Date.now();
});
slides.forEach((s, k) => s.addEventListener("click", () => {
  if (stage.classList.contains("overview")) { toggleOverview(); show(k); }
}));
let x0: number | null = null;
document.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
document.addEventListener("touchend", (e) => {
  if (x0 === null) return;
  const dx = e.changedTouches[0].clientX - x0;
  if (Math.abs(dx) > 50) (dx < 0 ? next : prev)();
  x0 = null;
});
chan?.addEventListener("message", (e) => show(e.data.idx, e.data.step, false));
window.addEventListener("resize", fit);

// Presenter view
const fmt = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
function renderPresenter() {
  const s = slides[idx];
  const nx = slides[idx + 1];
  const title = (el?: HTMLElement) => el?.querySelector("h1, h2")?.textContent?.trim() ?? "end";
  (document.querySelector(".pv-notes") as HTMLElement).innerHTML = s.querySelector(".notes")?.innerHTML ?? "";
  (document.querySelector(".pv-next") as HTMLElement).textContent = `Next: ${title(nx)}`;
  const before = timed.slice(0, Math.max(timed.indexOf(s), 0)).reduce((a, x) => a + secs(x.dataset.target ?? null), 0);
  (document.querySelector(".pv-target") as HTMLElement).textContent =
    `Slide ${s.dataset.target ?? "appendix"} · should be at ${fmt(before)} on entry · total ${fmt(TOTAL)}`;
}
if (isPresenter) {
  document.body.classList.add("presenter");
  setInterval(() => {
    const el = started === null ? 0 : (Date.now() - started) / 1000;
    const t = document.querySelector(".pv-time") as HTMLElement;
    t.textContent = `${fmt(el)} / 5:00`;
    t.classList.toggle("late", el > 300);
  }, 250);
  document.querySelector(".pv-reset")?.addEventListener("click", () => { started = Date.now(); });
}

const start = Number(location.hash.slice(1)) - 1;
show(Number.isFinite(start) && start >= 0 ? start : 0, 0, false);
fit();
