// AgroAid – Main JavaScript

document.addEventListener('DOMContentLoaded', () => {

  // ── Symptom checkboxes ──────────────────────────────────────────
  const symptoms = document.querySelectorAll('.symptom-item input[type="checkbox"]');
  const counter  = document.getElementById('selected-count');
  const submitBtn = document.getElementById('diagnose-btn');

  function updateCounter() {
    const checked = document.querySelectorAll('.symptom-item input[type="checkbox"]:checked').length;
    if (counter) counter.textContent = checked;
    // Toggle checked class on parent
    symptoms.forEach(cb => {
      const item = cb.closest('.symptom-item');
      if (item) item.classList.toggle('checked', cb.checked);
    });
    // Update button state
    if (submitBtn) {
      if (checked === 0) {
        submitBtn.setAttribute('disabled', 'disabled');
        submitBtn.style.opacity = '0.5';
        submitBtn.style.cursor = 'not-allowed';
      } else {
        submitBtn.removeAttribute('disabled');
        submitBtn.style.opacity = '1';
        submitBtn.style.cursor = 'pointer';
      }
    }
  }

  symptoms.forEach(cb => {
    cb.addEventListener('change', updateCounter);
  });

  updateCounter();

  // ── Confidence bars animate on load ────────────────────────────
  const bars = document.querySelectorAll('.confidence-bar-fill');
  setTimeout(() => {
    bars.forEach(bar => {
      const target = bar.dataset.width;
      bar.style.width = target + '%';
    });
  }, 200);

  // ── Flash auto-dismiss ──────────────────────────────────────────
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(30px)';
      flash.style.transition = 'all 0.4s ease';
      setTimeout(() => flash.remove(), 400);
    }, 4000);
  });

  // ── Admin: Dynamic symptom filter by disease ────────────────────
  const diseaseSelect = document.getElementById('admin-disease-select');
  const symptomCheckboxes = document.getElementById('admin-symptom-checkboxes');

  if (diseaseSelect && symptomCheckboxes) {
    diseaseSelect.addEventListener('change', async () => {
      const did = diseaseSelect.value;
      if (!did) { symptomCheckboxes.innerHTML = '<span style="color:var(--text-dim)">Select a disease first</span>'; return; }
      symptomCheckboxes.innerHTML = '<span style="color:var(--text-muted)">Loading symptoms...</span>';
      const res = await fetch(`/api/admin/symptoms_by_disease/${did}`);
      const syms = await res.json();
      if (!syms.length) {
        symptomCheckboxes.innerHTML = '<span style="color:var(--text-dim)">No symptoms found for this disease\'s crop</span>';
        return;
      }
      symptomCheckboxes.innerHTML = syms.map(s => `
        <label class="checkbox-item">
          <input type="checkbox" name="symptom_ids" value="${s.id}">
          ${s.name}
        </label>
      `).join('');
    });
  }

  // ── Stagger animation on crop cards ────────────────────────────
  const cropCards = document.querySelectorAll('.crop-card');
  cropCards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = `opacity 0.5s ease ${i * 0.07}s, transform 0.5s ease ${i * 0.07}s`;
    setTimeout(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 50);
  });

  // ── Global Sidebar Toggle ────────────────────────────────────────
  const menuToggle = document.getElementById('menu-toggle');
  const globalSidebar = document.getElementById('global-sidebar');
  const sidebarOverlay = document.getElementById('sidebar-overlay');
  const closeSidebarBtn = document.getElementById('close-sidebar');

  function openSidebar() {
    if(globalSidebar) globalSidebar.classList.add('open');
    if(sidebarOverlay) sidebarOverlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent scrolling
  }

  function closeSidebar() {
    if(globalSidebar) globalSidebar.classList.remove('open');
    if(sidebarOverlay) sidebarOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (menuToggle) menuToggle.addEventListener('click', openSidebar);
  if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', closeSidebar);
  if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

  // ── Select All / Clear All for symptoms ────────────────────────
  const selectAllBtn = document.getElementById('select-all-btn');
  const clearAllBtn  = document.getElementById('clear-all-btn');

  if (selectAllBtn) {
    selectAllBtn.addEventListener('click', () => {
      symptoms.forEach(cb => cb.checked = true);
      updateCounter();
    });
  }
  if (clearAllBtn) {
    clearAllBtn.addEventListener('click', () => {
      symptoms.forEach(cb => cb.checked = false);
      updateCounter();
    });
  }

});
