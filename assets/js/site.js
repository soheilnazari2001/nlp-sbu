/* NLP @ SBU — small, dependency-free site scripts */
(function () {
  "use strict";

  var root = document.documentElement;

  /* ---------- theme ---------- */
  function currentTheme() {
    var explicit = root.getAttribute("data-theme");
    if (explicit === "light" || explicit === "dark") return explicit;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function syncThemeButtons() {
    var theme = currentTheme();
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-label", theme === "dark" ? "تغییر به حالت روشن" : "تغییر به حالت تیره");
      btn.setAttribute("title", theme === "dark" ? "حالت روشن" : "حالت تیره");
      var sun = btn.querySelector("[data-icon-sun]");
      var moon = btn.querySelector("[data-icon-moon]");
      if (sun) sun.style.display = theme === "dark" ? "block" : "none";
      if (moon) moon.style.display = theme === "dark" ? "none" : "block";
    });
  }
  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    try { localStorage.setItem("nlp-theme", theme); } catch (e) {}
    syncThemeButtons();
  }
  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setTheme(currentTheme() === "dark" ? "light" : "dark");
    });
  });
  try {
    var requestedTheme = new URLSearchParams(window.location.search).get("theme");
    if (requestedTheme === "dark" || requestedTheme === "light") setTheme(requestedTheme);
    else syncThemeButtons();
  } catch (e) {
    syncThemeButtons();
  }

  /* ---------- mobile nav ---------- */
  var menuBtn = document.querySelector("[data-menu-toggle]");
  var nav = document.querySelector("[data-nav]");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", String(!open));
      menuBtn.setAttribute("aria-expanded", String(!open));
    });
    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        nav.setAttribute("data-open", "false");
        menuBtn.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("click", function (event) {
      if (!nav.contains(event.target) && !menuBtn.contains(event.target)) {
        nav.setAttribute("data-open", "false");
        menuBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- reading progress ---------- */
  var progress = document.querySelector("[data-read-progress] span");
  if (progress) {
    var ticking = false;
    function updateProgress() {
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      var value = max > 0 ? Math.min(100, Math.max(0, (window.scrollY / max) * 100)) : 0;
      progress.style.width = value + "%";
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(updateProgress); }
    }, { passive: true });
    window.addEventListener("resize", updateProgress);
    updateProgress();
  }

  /* ---------- TOC active section ---------- */
  var toc = document.querySelector("[data-toc]");
  if (toc && "IntersectionObserver" in window) {
    var links = Array.prototype.slice.call(toc.querySelectorAll("a[href^='#']"));
    var map = {};
    links.forEach(function (link) {
      var id = decodeURIComponent(link.getAttribute("href").slice(1));
      if (id) map[id] = link;
    });
    var targets = Object.keys(map).map(function (id) { return document.getElementById(id); }).filter(Boolean);
    if (targets.length) {
      var visible = new Set();
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) visible.add(entry.target.id);
          else visible.delete(entry.target.id);
        });
        var activeId = null;
        for (var i = 0; i < targets.length; i++) {
          if (visible.has(targets[i].id)) { activeId = targets[i].id; break; }
        }
        links.forEach(function (link) { link.classList.remove("active"); });
        if (activeId && map[activeId]) map[activeId].classList.add("active");
      }, { rootMargin: "-15% 0px -70% 0px", threshold: 0 });
      targets.forEach(function (target) { observer.observe(target); });
    }
  }

  /* ---------- notes search + filters ---------- */
  var search = document.querySelector("[data-notes-search]");
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-note-card]"));
  var count = document.querySelector("[data-search-count]");
  var empty = document.querySelector("[data-note-empty]");
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-filter]"));
  var activeFilter = "all";

  function faNumber(value) {
    return String(value).replace(/\d/g, function (d) { return "۰۱۲۳۴۵۶۷۸۹".charAt(Number(d)); });
  }
  function normalize(value) {
    return (value || "")
      .toLowerCase()
      .replace(/[يى]/g, "ی")
      .replace(/ك/g, "ک")
      .replace(/[‌‍]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }
  function applyNotesFilter() {
    if (!cards.length) return;
    var q = normalize(search ? search.value : "");
    var shown = 0;
    cards.forEach(function (card) {
      var hay = normalize(card.getAttribute("data-search") || card.textContent);
      var matchText = !q || hay.indexOf(q) !== -1;
      var matchTag = activeFilter === "all" || (card.getAttribute("data-tags") || "").split(",").indexOf(activeFilter) !== -1;
      var show = matchText && matchTag;
      card.style.display = show ? "" : "none";
      if (show) shown++;
    });
    if (count) count.textContent = faNumber(shown) + " جلسه";
    if (empty) empty.style.display = shown ? "none" : "block";
  }
  if (search) {
    var timer = null;
    search.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(applyNotesFilter, 90);
    });
  }
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      activeFilter = chip.getAttribute("data-filter") || "all";
      chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
      applyNotesFilter();
    });
  });
  applyNotesFilter();

  /* ---------- copy code ---------- */
  document.querySelectorAll(".prose pre").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "COPY";
    btn.setAttribute("aria-label", "کپی کد");
    btn.addEventListener("click", function () {
      var code = pre.querySelector("code");
      var text = code ? code.innerText : pre.innerText;
      var done = function () {
        btn.textContent = "COPIED";
        setTimeout(function () { btn.textContent = "COPY"; }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        var area = document.createElement("textarea");
        area.value = text;
        area.style.position = "fixed";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(area);
      }
    });
    pre.appendChild(btn);
  });

  /* ---------- print button ---------- */
  document.querySelectorAll("[data-print]").forEach(function (btn) {
    btn.addEventListener("click", function () { window.print(); });
  });

  /* ---------- reveal on scroll (subtle) ---------- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
  if (reveals.length && "IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    reveals.forEach(function (el) { el.style.opacity = "0"; el.style.transform = "translateY(10px)"; el.style.transition = "opacity .45s ease, transform .45s ease"; });
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "none";
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { revealObserver.observe(el); });
  }

  /* ---------- current year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();

/* ---------- hero slideshow ---------- */
(function () {
  var wrap = document.querySelector("[data-slides]");
  if (!wrap) return;
  var slides = Array.prototype.slice.call(wrap.querySelectorAll(".slide"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".sdot"));
  var count = document.querySelector("[data-slide-count]");
  var idx = 0;
  var timer = null;
  var delay = 4000;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function show(i) {
    idx = (i + slides.length) % slides.length;
    slides.forEach(function (s, k) { s.classList.toggle("is-active", k === idx); });
    dots.forEach(function (d, k) { d.classList.toggle("is-active", k === idx); });
    if (count) count.textContent = faNumber(idx + 1) + " / " + faNumber(slides.length);
  }
  function stop() {
    if (timer) { clearInterval(timer); timer = null; }
  }
  function play() {
    stop();
    if (!reduced) timer = setInterval(function () { show(idx + 1); }, delay);
  }
  dots.forEach(function (d) {
    d.addEventListener("click", function () {
      show(Number(d.getAttribute("data-goto")));
      play();
    });
  });
  wrap.addEventListener("mouseenter", stop);
  wrap.addEventListener("mouseleave", play);
  show(0);
  play();
})();
