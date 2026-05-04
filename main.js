(function () {
  "use strict";

  var yearEl = document.querySelector("[data-year]");
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }

  /* Home: mobile nav */
  var navToggle = document.querySelector("[data-nav-toggle]");
  var navMenu = document.querySelector("[data-nav-menu]");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      var open = navToggle.getAttribute("aria-expanded") === "true";
      navToggle.setAttribute("aria-expanded", String(!open));
      navMenu.classList.toggle("is-open", !open);
      document.body.style.overflow = !open ? "hidden" : "";
    });
    navMenu.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        navToggle.setAttribute("aria-expanded", "false");
        navMenu.classList.remove("is-open");
        document.body.style.overflow = "";
      });
    });
  }

  /* Accordion */
  var root = document.querySelector("[data-accordion]");
  if (root) {
    root.querySelectorAll("[data-accordion-item]").forEach(function (item) {
      var trigger = item.querySelector("[data-accordion-trigger]");
      var panel = item.querySelector("[data-accordion-panel]");
      if (!trigger || !panel) return;

      trigger.addEventListener("click", function () {
        var isOpen = item.classList.contains("is-open");
        root.querySelectorAll("[data-accordion-item]").forEach(function (other) {
          var t = other.querySelector("[data-accordion-trigger]");
          var p = other.querySelector("[data-accordion-panel]");
          other.classList.remove("is-open");
          if (t) t.setAttribute("aria-expanded", "false");
          if (p) p.setAttribute("hidden", "");
        });
        if (!isOpen) {
          item.classList.add("is-open");
          trigger.setAttribute("aria-expanded", "true");
          panel.removeAttribute("hidden");
        }
      });
    });
  }

  /* Contact: hamburger overlay */
  var cToggle = document.querySelector("[data-contact-nav-toggle]");
  var cOverlay = document.querySelector("[data-contact-overlay]");
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (cToggle && cOverlay && !cOverlay.hidden) {
      cToggle.setAttribute("aria-expanded", "false");
      cOverlay.hidden = true;
      document.body.style.overflow = "";
    }
    if (navToggle && navMenu && navMenu.classList.contains("is-open")) {
      navToggle.setAttribute("aria-expanded", "false");
      navMenu.classList.remove("is-open");
      document.body.style.overflow = "";
    }
  });

  if (cToggle && cOverlay) {
    cToggle.addEventListener("click", function () {
      var open = cToggle.getAttribute("aria-expanded") === "true";
      cToggle.setAttribute("aria-expanded", String(!open));
      cOverlay.hidden = open;
      document.body.style.overflow = !open ? "hidden" : "";
    });
    cOverlay.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        cToggle.setAttribute("aria-expanded", "false");
        cOverlay.hidden = true;
        document.body.style.overflow = "";
      });
    });
    cOverlay.addEventListener("click", function (e) {
      if (e.target === cOverlay) {
        cToggle.setAttribute("aria-expanded", "false");
        cOverlay.hidden = true;
        document.body.style.overflow = "";
      }
    });
  }

  /* Contact form */
  var form = document.querySelector("[data-contact-form]");
  var feedback = document.querySelector("[data-form-feedback]");
  if (form && feedback) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      feedback.textContent = "";
      feedback.classList.remove("is-ok", "is-err");
      if (!form.checkValidity()) {
        feedback.textContent = "Please complete the required fields.";
        feedback.classList.add("is-err");
        return;
      }
      feedback.textContent = "Message sent — we’ll be in touch soon.";
      feedback.classList.add("is-ok");
      form.reset();
    });
  }
})();
