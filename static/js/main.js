(function () {
  "use strict";

  // ---------- nav toggle (mobile) ----------
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.querySelector(".nav-links");
  if (navToggle) {
    navToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    navLinks.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        navLinks.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      })
    );
  }

  // ---------- dropzone ----------
  const dropzone = document.getElementById("dropzone");
  const resumeInput = document.getElementById("resumeInput");
  const dropzoneContent = document.getElementById("dropzoneContent");
  const dropzoneFile = document.getElementById("dropzoneFile");
  const fileNameEl = document.getElementById("fileName");
  const removeFileBtn = document.getElementById("removeFile");

  function showSelectedFile(file) {
    fileNameEl.textContent = `${file.name} · ${(file.size / 1024).toFixed(0)} KB`;
    dropzoneContent.hidden = true;
    dropzoneFile.hidden = false;
  }

  function clearSelectedFile() {
    resumeInput.value = "";
    dropzoneContent.hidden = false;
    dropzoneFile.hidden = true;
  }

  dropzone.addEventListener("click", () => resumeInput.click());
  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      resumeInput.click();
    }
  });
  resumeInput.addEventListener("change", () => {
    if (resumeInput.files[0]) showSelectedFile(resumeInput.files[0]);
  });
  removeFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    clearSelectedFile();
  });

  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    })
  );
  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
      resumeInput.files = e.dataTransfer.files;
      showSelectedFile(file);
    }
  });

  // ---------- form submit ----------
  const form = document.getElementById("analyzeForm");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const errorMsg = document.getElementById("errorMsg");
  const resultsSection = document.getElementById("results");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorMsg.hidden = true;
    errorMsg.textContent = "";

    if (!resumeInput.files[0]) {
      errorMsg.textContent = "Please choose a resume file first.";
      errorMsg.hidden = false;
      return;
    }

    const formData = new FormData(form);
    analyzeBtn.classList.add("scanning");
    analyzeBtn.disabled = true;

    try {
      const res = await fetch("/api/analyze", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong analyzing that file.");
      renderResults(data);
    } catch (err) {
      errorMsg.textContent = err.message;
      errorMsg.hidden = false;
    } finally {
      analyzeBtn.classList.remove("scanning");
      analyzeBtn.disabled = false;
    }
  });

  document.getElementById("resetBtn").addEventListener("click", () => {
    resultsSection.hidden = true;
    clearSelectedFile();
    document.getElementById("jdInput").value = "";
    document.getElementById("analyze").scrollIntoView({ behavior: "smooth" });
  });

  document.getElementById("printBtn").addEventListener("click", () => window.print());

  // ---------- render results ----------
  const GAUGE_CIRCUMFERENCE = 540.35;

  function renderResults(data) {
    document.getElementById("resultFileName").textContent = data.filename || "";

    animateScore(data.overall_score);
    renderBreakdown(data.score_breakdown);
    renderChecklist("sectionChecklist", data.sections);
    renderChecklist("contactChecklist", data.contact_info, true);
    renderSkills(data.skills_found, data.skills_found_count);
    renderJdMatch(data.job_match);
    renderSuggestions(data.suggestions);

    resultsSection.hidden = false;
    resultsSection.setAttribute("data-reveal", "");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function scoreColor(score) {
    if (score >= 75) return "#3FC7B8";
    if (score >= 50) return "#F5A623";
    return "#E2665A";
  }

  function animateScore(score) {
    const gaugeFill = document.getElementById("gaugeFill");
    const valueEl = document.getElementById("scoreValue");
    const color = scoreColor(score);
    gaugeFill.style.stroke = color;

    const offset = GAUGE_CIRCUMFERENCE * (1 - score / 100);
    requestAnimationFrame(() => {
      gaugeFill.style.strokeDashoffset = offset;
    });

    const duration = 900;
    const start = performance.now();
    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      valueEl.textContent = Math.round(progress * score);
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function renderBreakdown(breakdown) {
    const wrap = document.getElementById("breakdownList");
    wrap.innerHTML = "";
    Object.entries(breakdown).forEach(([label, value]) => {
      const row = document.createElement("div");
      row.className = "breakdown-row";
      row.innerHTML = `
        <div class="breakdown-row-top"><span>${label}</span><span>${value}/100</span></div>
        <div class="bar-track"><div class="bar-fill" style="background:${scoreColor(value)}"></div></div>
      `;
      wrap.appendChild(row);
      requestAnimationFrame(() => {
        row.querySelector(".bar-fill").style.width = value + "%";
      });
    });
  }

  function renderChecklist(elementId, obj, isContact) {
    const list = document.getElementById(elementId);
    list.innerHTML = "";
    const labels = isContact
      ? { email: "Email address", phone: "Phone number", linkedin: "LinkedIn link", github: "GitHub link" }
      : null;
    Object.entries(obj).forEach(([key, present]) => {
      const li = document.createElement("li");
      const label = labels ? labels[key] : key;
      li.innerHTML = `<span class="check-icon ${present ? "yes" : "no"}">${present ? "✓" : "✕"}</span> ${label}`;
      list.appendChild(li);
    });
  }

  function renderSkills(skillsFound, count) {
    document.getElementById("skillsCount").textContent = count ? `(${count} found)` : "";
    const wrap = document.getElementById("skillsFound");
    wrap.innerHTML = "";
    const entries = Object.entries(skillsFound || {});
    if (entries.length === 0) {
      wrap.innerHTML = `<p style="color:var(--text-muted); font-size:0.9rem;">No known skill keywords were detected. Consider adding a dedicated Skills section.</p>`;
      return;
    }
    entries.forEach(([category, skills]) => {
      const group = document.createElement("div");
      group.className = "skill-group";
      group.innerHTML = `<h4>${category}</h4><div class="chip-row">${skills
        .map((s) => `<span class="chip">${s}</span>`)
        .join("")}</div>`;
      wrap.appendChild(group);
    });
  }

  function renderJdMatch(jd) {
    const card = document.getElementById("jdMatchCard");
    if (!jd) {
      card.hidden = true;
      return;
    }
    card.hidden = false;
    const scoresWrap = document.getElementById("jdScores");
    scoresWrap.innerHTML = "";
    if (jd.skill_match_percent !== null) {
      scoresWrap.innerHTML += `<div class="jd-score-item"><div class="val">${jd.skill_match_percent}%</div><div class="lbl">Keyword overlap</div></div>`;
    }
    if (jd.text_similarity_percent !== null) {
      scoresWrap.innerHTML += `<div class="jd-score-item"><div class="val">${jd.text_similarity_percent}%</div><div class="lbl">Text similarity (TF-IDF)</div></div>`;
    }

    document.getElementById("matchedChips").innerHTML =
      jd.matched_skills.length > 0
        ? jd.matched_skills.map((s) => `<span class="chip">${s}</span>`).join("")
        : `<span style="color:var(--text-muted); font-size:0.85rem;">None found</span>`;

    document.getElementById("missingChips").innerHTML =
      jd.missing_skills.length > 0
        ? jd.missing_skills.map((s) => `<span class="chip">${s}</span>`).join("")
        : `<span style="color:var(--text-muted); font-size:0.85rem;">Nothing missing — great match!</span>`;
  }

  function renderSuggestions(suggestions) {
    const list = document.getElementById("suggestionsList");
    list.innerHTML = "";
    (suggestions || []).forEach((s) => {
      const li = document.createElement("li");
      li.textContent = s;
      list.appendChild(li);
    });
  }
})();