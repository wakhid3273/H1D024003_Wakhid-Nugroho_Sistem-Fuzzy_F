/* ================================================================
   main.js — ScholarCheck Premium UI v3
   ================================================================ */

// ── Cursor Glow (ambient only, kursor tetap normal) ───────────────────────────
const glow = document.getElementById('cursorGlow');
document.addEventListener('mousemove', e => {
  glow.style.left = e.clientX + 'px';
  glow.style.top  = e.clientY + 'px';
});

// ── Navbar scroll effect ──────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const nb = document.getElementById('navbar');
  nb.style.background = window.scrollY > 60
    ? 'rgba(8,15,13,.97)' : 'rgba(8,15,13,.8)';
});

// ── Info card mouse-tracking glow ─────────────────────────────────────────────
document.querySelectorAll('.icard').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width  * 100).toFixed(1) + '%';
    const y = ((e.clientY - rect.top)  / rect.height * 100).toFixed(1) + '%';
    card.style.setProperty('--mx', x);
    card.style.setProperty('--my', y);
  });
});

// ── Intersection Observer: slide-in on scroll ─────────────────────────────────
const io = new IntersectionObserver(entries => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      e.target.style.opacity = '0';
      e.target.style.transform = 'translateY(28px)';
      setTimeout(() => {
        e.target.style.transition = 'opacity .55s ease, transform .55s cubic-bezier(.22,1,.36,1)';
        e.target.style.opacity    = '1';
        e.target.style.transform  = 'translateY(0)';
      }, i * 100);
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.icard, .result-block, .mcard').forEach(el => io.observe(el));

// ── Kategori deskripsi & chip ─────────────────────────────────────────────────
const KATEGORI = {
  "Sangat Layak":  { desc: "Profil akademik, ekonomi, dan prestasi sangat mendukung. Kamu adalah kandidat terkuat.", chips: ["IPK Unggul","Ekonomi Lemah","Prestasi Tinggi"] },
  "Layak":         { desc: "Kamu memenuhi kriteria kelayakan dengan baik. Persiapkan berkas lengkap untuk meningkatkan peluang.", chips: ["Memenuhi Kriteria","Siap Daftar"] },
  "Cukup Layak":   { desc: "Cukup memenuhi kriteria. Pertimbangkan meningkatkan prestasi atau melengkapi dokumen pendukung.", chips: ["Perlu Optimasi","Tambah Prestasi"] },
  "Kurang Layak":  { desc: "Beberapa variabel belum optimal. Fokus pada peningkatan IPK dan catat setiap pencapaian non-akademik.", chips: ["IPK Perlu Naik","Kumpulkan Prestasi"] },
  "Tidak Layak":   { desc: "Kombinasi saat ini belum memenuhi kriteria. Jangan menyerah — tingkatkan dan coba kembali.", chips: ["Perlu Peningkatan","Tetap Semangat"] },
};

// ── Prestasi state ────────────────────────────────────────────────────────────
let prestasiCount = 0;
const MAX_PR = 3;

function tambahPrestasi() {
  if (prestasiCount >= MAX_PR) return;
  prestasiCount++;
  const idx = prestasiCount;
  const div = document.createElement('div');
  div.className = 'pentry';
  div.id = `pe-${idx}`;
  div.innerHTML = `
    <div class="pentry-head">
      <span class="pentry-num">Prestasi ${idx}</span>
      <button class="btn-remove" onclick="hapusPrestasi(${idx})">✕ Hapus</button>
    </div>
    <div class="pentry-fields">
      <div class="pf" style="grid-column:1/-1">
        <label>Nama Kejuaraan / Lomba</label>
        <input type="text" id="pr-nama-${idx}" placeholder="Contoh: Olimpiade Fisika Nasional"/>
      </div>
      <div class="pf">
        <label>Tingkat</label>
        <div class="sel-wrap">
          <select id="pr-tingkat-${idx}">
            <option value="">— Pilih —</option>
            <option value="lokal">Lokal / Kampus</option>
            <option value="provinsi">Provinsi / Regional</option>
            <option value="nasional">Nasional</option>
            <option value="internasional">Internasional</option>
          </select>
        </div>
      </div>
      <div class="pf">
        <label>Juara / Posisi</label>
        <div class="sel-wrap">
          <select id="pr-juara-${idx}">
            <option value="">— Pilih —</option>
            <option value="1">Juara 1</option>
            <option value="2">Juara 2</option>
            <option value="3">Juara 3</option>
            <option value="harapan">Juara Harapan</option>
          </select>
        </div>
      </div>
    </div>`;
  document.getElementById('prestasi-container').appendChild(div);
  updateBtnAdd();
}

function hapusPrestasi(idx) {
  const el = document.getElementById(`pe-${idx}`);
  if (!el) return;
  el.style.transition = 'opacity .2s ease, transform .2s ease';
  el.style.opacity = '0';
  el.style.transform = 'scale(.96) translateY(-6px)';
  setTimeout(() => {
    el.remove();
    prestasiCount = document.querySelectorAll('.pentry').length;
    document.querySelectorAll('.pentry-num').forEach((e, i) => e.textContent = `Prestasi ${i + 1}`);
    updateBtnAdd();
  }, 220);
}

function updateBtnAdd() {
  const btn = document.getElementById('btn-add');
  const c   = document.querySelectorAll('.pentry').length;
  prestasiCount = c;
  btn.disabled  = c >= MAX_PR;
  btn.innerHTML = c >= MAX_PR
    ? 'Maks. 3 prestasi tercapai'
    : '<span class="btn-add-plus">＋</span> Tambah Prestasi';
}

function kumpulkanPrestasi() {
  return [...document.querySelectorAll('.pentry')].map(el => {
    const idx     = el.id.replace('pe-', '');
    const nama    = (document.getElementById(`pr-nama-${idx}`)?.value || '').trim();
    const tingkat = document.getElementById(`pr-tingkat-${idx}`)?.value || '';
    const juara   = document.getElementById(`pr-juara-${idx}`)?.value || '';
    return (tingkat && juara) ? { nama: nama || '(tanpa nama)', tingkat, juara } : null;
  }).filter(Boolean);
}

// ── Slider ↔ Input sync ───────────────────────────────────────────────────────
function syncSlider(id, fmtFn) {
  const slider = document.getElementById(id + '-slider');
  const input  = document.getElementById(id === 'penghasilan' ? 'penghasilan' : id);
  const val    = document.getElementById(id + '-val');
  input.value  = slider.value;
  if (val) val.textContent = fmtFn(slider.value);
  clearErr(id === 'penghasilan' ? 'pgh' : id);
}

function syncInput(id) {
  const input  = document.getElementById(id);
  const slider = document.getElementById(id + '-slider');
  const val    = document.getElementById(id + '-val');
  const n      = parseFloat(input.value);
  if (!isNaN(n)) {
    slider.value = Math.min(n, parseFloat(slider.max));
    if (val) val.textContent = id === 'ipk'
      ? parseFloat(n).toFixed(2)
      : id === 'penghasilan'
        ? 'Rp ' + parseInt(n).toLocaleString('id-ID')
        : parseInt(n) + ' orang';
  } else if (val) { val.textContent = '—'; }
  clearErr(id === 'penghasilan' ? 'pgh' : id);
}

// ── Validation ────────────────────────────────────────────────────────────────
function showErr(id, msg) {
  const fe = document.getElementById('fe-' + id);
  const iw = document.getElementById('iw-' + id);
  if (fe) { fe.textContent = msg; fe.className = 'ferror show'; }
  if (iw) iw.classList.add('error');
}
function clearErr(id) {
  const fe = document.getElementById('fe-' + id);
  const iw = document.getElementById('iw-' + id);
  if (fe) { fe.textContent = ''; fe.className = 'ferror'; }
  if (iw) iw.classList.remove('error');
}

function validateIPK() {
  const v = document.getElementById('ipk').value.trim();
  if (!v) { showErr('ipk', '⚠ IPK wajib diisi.'); return false; }
  const n = parseFloat(v);
  if (isNaN(n) || n < 0 || n > 4) { showErr('ipk', '⚠ IPK harus antara 0.00 – 4.00.'); return false; }
  clearErr('ipk'); return true;
}
function validatePenghasilan() {
  const v = document.getElementById('penghasilan').value.trim();
  if (!v) { showErr('pgh', '⚠ Penghasilan wajib diisi.'); return false; }
  const n = parseFloat(v);
  if (isNaN(n) || n < 0) { showErr('pgh', '⚠ Masukkan nominal yang valid.'); return false; }
  clearErr('pgh'); return true;
}
function validateTanggungan() {
  const v = document.getElementById('tanggungan').value.trim();
  if (!v) { showErr('tg', '⚠ Jumlah tanggungan wajib diisi.'); return false; }
  const n = parseInt(v);
  if (isNaN(n) || n < 0) { showErr('tg', '⚠ Masukkan angka tanggungan yang valid.'); return false; }
  clearErr('tg'); return true;
}

// ── Hitung ────────────────────────────────────────────────────────────────────
async function hitungKelayakan() {
  const v1 = validateIPK(), v2 = validatePenghasilan(), v3 = validateTanggungan();
  if (!v1 || !v2 || !v3) {
    document.querySelector('.ferror.show')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }
  const ipk         = parseFloat(document.getElementById('ipk').value);
  const penghasilan = parseFloat(document.getElementById('penghasilan').value);
  const tanggungan  = parseInt(document.getElementById('tanggungan').value);
  const prestasi    = kumpulkanPrestasi();

  setState('loading');
  document.getElementById('resultCol').scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const res  = await fetch('/hitung', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ipk, penghasilan, tanggungan, prestasi })
    });
    const data = await res.json();
    if (data.error) { alert('Error: ' + data.error); setState('idle'); return; }
    tampilkan(data, { ipk, penghasilan, tanggungan, prestasi });
  } catch { alert('Tidak dapat terhubung ke server.'); setState('idle'); }
}

// ── Render ────────────────────────────────────────────────────────────────────
function tampilkan(data, input) {
  setState('result');
  const { skor, kategori, warna, skor_prestasi } = data;

  // Gauge
  const circumference = 2 * Math.PI * 82;
  const offset = circumference - (skor / 100) * circumference;
  const arc = document.getElementById('gauge-arc');
  // Reset then animate
  arc.style.transition = 'none';
  arc.style.strokeDashoffset = circumference;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      arc.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(.22,1,.36,1), stroke .4s';
      arc.style.strokeDashoffset = offset;
    });
  });

  const colors = {
    "Sangat Layak":  ['#34d399','#059669'],
    "Layak":         ['#6ee7b7','#10b981'],
    "Cukup Layak":   ['#fde047','#ca8a04'],
    "Kurang Layak":  ['#fb923c','#ea580c'],
    "Tidak Layak":   ['#f87171','#dc2626'],
  };
  const [c1, c2] = colors[kategori] || ['#34d399','#059669'];
  document.getElementById('grad-stop-1').setAttribute('stop-color', c1);
  document.getElementById('grad-stop-2').setAttribute('stop-color', c2);

  // Animated number count-up
  const numEl = document.getElementById('gauge-num');
  numEl.style.fill = c1;
  let start = 0, end = Math.round(skor), duration = 1200;
  const step = (ts) => {
    if (!start) start = ts;
    const progress = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 4);
    numEl.textContent = Math.round(ease * end);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);

  // Kategori & desc
  const lbl = document.getElementById('result-kategori');
  lbl.textContent = kategori;
  lbl.style.color = c1;

  const rh = document.getElementById('result-header');
  rh.style.borderColor     = c1 + '44';
  rh.style.background      = `linear-gradient(135deg, color-mix(in srgb, ${c1} 8%, #0d1714) 0%, #091f17 100%)`;

  document.getElementById('result-desc').textContent = KATEGORI[kategori]?.desc || '';
  const chips = KATEGORI[kategori]?.chips || [];
  document.getElementById('result-chips').innerHTML = chips.map(c =>
    `<span class="chip" style="border-color:${c1}44;color:${c1};background:${c1}15">${c}</span>`
  ).join('');

  // Prestasi
  const prBlock = document.getElementById('pr-used-block');
  const prList  = document.getElementById('pr-used-list');
  const TL = { lokal:'Lokal', provinsi:'Provinsi', nasional:'Nasional', internasional:'Internasional' };
  const JL = { '1':'Juara 1', '2':'Juara 2', '3':'Juara 3', harapan:'Juara Harapan' };
  if (input.prestasi?.length) {
    prBlock.style.display = 'block';
    prList.innerHTML = input.prestasi.map(p =>
      `<span class="pr-tag">🏅 ${p.nama} · ${TL[p.tingkat]||p.tingkat} · ${JL[String(p.juara)]||p.juara}</span>`
    ).join('');
  } else { prBlock.style.display = 'none'; }

  // Membership bars
  const pghN = Math.min(input.penghasilan, 10_000_000);
  const tgN  = Math.min(input.tanggungan, 10);
  const bars = [
    { lbl:'IPK Rendah',  val:trimf(input.ipk,0,0,2.75),         color:'#f87171' },
    { lbl:'IPK Sedang',  val:trimf(input.ipk,2.25,3.0,3.5),      color:'#fbbf24' },
    { lbl:'IPK Tinggi',  val:trimf(input.ipk,3.0,4,4),            color:'#34d399' },
    { lbl:'Pgh. Rendah', val:trimf(pghN,0,0,2.5e6),              color:'#34d399' },
    { lbl:'Pgh. Sedang', val:trimf(pghN,1.5e6,4e6,6.5e6),        color:'#fbbf24' },
    { lbl:'Pgh. Tinggi', val:trimf(pghN,5e6,10e6,10e6),          color:'#f87171' },
    { lbl:'Tg. Sedikit', val:trimf(tgN,0,0,3),                   color:'#f87171' },
    { lbl:'Tg. Sedang',  val:trimf(tgN,2,5,7),                   color:'#fbbf24' },
    { lbl:'Tg. Banyak',  val:trimf(tgN,5,10,10),                  color:'#34d399' },
    { lbl:'Prs. Rendah', val:trimf(skor_prestasi,0,0,40),         color:'#f87171' },
    { lbl:'Prs. Sedang', val:trimf(skor_prestasi,25,50,75),       color:'#fbbf24' },
    { lbl:'Prs. Tinggi', val:trimf(skor_prestasi,60,100,100),     color:'#34d399' },
  ];
  document.getElementById('mb-bars').innerHTML = bars.map(b => {
    const pct = Math.round(b.val * 100);
    return `<div class="mb-row">
      <span class="mb-lbl">${b.lbl}</span>
      <div class="mb-track"><div class="mb-fill" style="width:0%;background:${b.color}" data-w="${pct}"></div></div>
      <span class="mb-pct">${pct}%</span>
    </div>`;
  }).join('');

  // Stagger bar animations
  setTimeout(() => {
    document.querySelectorAll('.mb-fill').forEach((el, i) => {
      setTimeout(() => { el.style.width = el.dataset.w + '%'; }, i * 60);
    });
  }, 300);
}

function trimf(x, a, b, c) {
  x = parseFloat(x);
  if (x <= a || x >= c) return 0;
  if (x === b) return 1;
  return x < b ? (x - a) / (b - a) : (c - x) / (c - b);
}

function setState(s) {
  document.getElementById('rstate-idle').style.display    = s === 'idle'    ? 'flex'  : 'none';
  document.getElementById('rstate-loading').style.display = s === 'loading' ? 'flex'  : 'none';
  document.getElementById('rstate-result').style.display  = s === 'result'  ? 'block' : 'none';
}