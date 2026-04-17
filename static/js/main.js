/* ── Tab switching ──────────────────────────────────────────────── */
function switchTab(tab) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.auth-form').forEach(f => f.style.display = 'none');
  document.getElementById('tab-' + tab).classList.add('active');
  const form = document.getElementById('form-' + tab);
  form.style.display = 'block';
  form.style.animation = 'fadeUp 0.3s ease';
}

/* ── Language change ────────────────────────────────────────────── */
function changeLang(val) {
  document.querySelectorAll('.lang-hidden').forEach(i => i.value = val);
}

/* ── File upload preview ────────────────────────────────────────── */
function setupPreview(inputId, previewId) {
  const inp = document.getElementById(inputId);
  const pre = document.getElementById(previewId);
  if (!inp || !pre) return;
  inp.addEventListener('change', function () {
    if (!this.files[0]) return;
    const reader = new FileReader();
    reader.onload = e => {
      pre.innerHTML = `
        <div style="margin-top:10px;border-radius:10px;overflow:hidden;border:1px solid var(--border);">
          <img src="${e.target.result}" style="width:100%;max-height:180px;object-fit:cover;display:block;">
        </div>`;
    };
    reader.readAsDataURL(this.files[0]);
  });
}

/* ── Upload zone interaction ────────────────────────────────────── */
function setupUploadZone(zoneId) {
  const zone = document.getElementById(zoneId);
  if (!zone) return;
  const inp  = zone.querySelector('input[type=file]');
  const hint = zone.querySelector('.upload-zone-hint');

  zone.addEventListener('click', () => inp.click());

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.style.borderColor = 'var(--blue-bright)';
    zone.style.background  = 'rgba(37,99,235,0.06)';
  });
  zone.addEventListener('dragleave', () => {
    zone.style.borderColor = '';
    zone.style.background  = '';
  });
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.style.borderColor = '';
    zone.style.background  = '';
    if (e.dataTransfer.files.length) {
      inp.files = e.dataTransfer.files;
      inp.dispatchEvent(new Event('change'));
    }
  });

  if (inp && hint) {
    inp.addEventListener('change', function () {
      if (this.files.length) {
        hint.textContent = this.files.length > 1
          ? `${this.files.length} files selected`
          : this.files[0].name;
        hint.style.color = 'var(--blue-bright)';
      }
    });
  }
}

/* ── Sidebar mobile toggle ──────────────────────────────────────── */
function toggleSidebar() {
  document.querySelector('.sidebar').classList.toggle('open');
}

/* ── Auto-dismiss flashes ───────────────────────────────────────── */
function setupFlashes() {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-6px)';
    }, 3200);
    setTimeout(() => el.remove(), 3700);
  });
}

/* ── Progress bar animation ─────────────────────────────────────── */
function animateBars() {
  document.querySelectorAll('.bar[data-width]').forEach(bar => {
    setTimeout(() => {
      bar.style.width = bar.dataset.width + '%';
    }, 200);
  });
}

/* ── Stat counter animation ─────────────────────────────────────── */
function animateCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count, 10);
    if (isNaN(target) || target === 0) return;
    let current = 0;
    const step  = Math.ceil(target / 30);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 30);
  });
}

/* ── Init ───────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  setupFlashes();
  animateBars();
  animateCounters();
  setupUploadZone('zone-original');
  setupUploadZone('zone-suspect');
  setupUploadZone('zone-photos');
  setupPreview('original_photo', 'preview-original');
  setupPreview('suspect_photo',  'preview-suspect');
});