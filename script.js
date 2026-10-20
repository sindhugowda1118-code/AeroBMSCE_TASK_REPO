(function () {
  "use strict";

  var menuButton = document.querySelector(".menu-toggle");
  var navigation = document.querySelector(".site-nav");

  function setMenuOpen(open) {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    navigation.classList.toggle("is-open", open);
    document.body.classList.toggle("menu-open", open);
  }

  if (menuButton && navigation) {
    menuButton.addEventListener("click", function () {
      setMenuOpen(menuButton.getAttribute("aria-expanded") !== "true");
    });
    navigation.addEventListener("click", function (event) {
      if (event.target.closest("a")) setMenuOpen(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 760) setMenuOpen(false);
    });
  }

  var lightbox = document.querySelector(".lightbox");
  if (lightbox && typeof lightbox.showModal === "function") {
    var lightboxImage = lightbox.querySelector("img");
    var lightboxCaption = lightbox.querySelector("p");
    var closeButton = lightbox.querySelector(".lightbox-close");
    var previousFocus;

    document.querySelectorAll(".archive-frame[data-image]").forEach(function (frame) {
      frame.addEventListener("click", function () {
        var thumbnail = frame.querySelector("img");
        previousFocus = frame;
        lightboxImage.src = frame.dataset.image;
        lightboxImage.alt = thumbnail ? thumbnail.alt : "";
        lightboxCaption.textContent = frame.dataset.caption || "";
        lightbox.showModal();
        closeButton.focus();
      });
    });

    closeButton.addEventListener("click", function () {
      lightbox.close();
    });
    lightbox.addEventListener("click", function (event) {
      if (event.target === lightbox) lightbox.close();
    });
    lightbox.addEventListener("close", function () {
      if (previousFocus) previousFocus.focus();
    });
  }

  var payloadButton = document.querySelector(".payload-button");
  var payloadStatus = document.getElementById("payload-status");
  var payloadTimer;
  if (payloadButton && payloadStatus) {
    payloadButton.addEventListener("click", function () {
      var isArmed = payloadButton.getAttribute("aria-pressed") === "true";
      window.clearTimeout(payloadTimer);
      payloadButton.setAttribute("aria-pressed", String(!isArmed));
      if (isArmed) {
        payloadStatus.textContent = "Simulation disarmed. This control does not operate an aircraft.";
        return;
      }
      payloadButton.querySelector("span:nth-child(2)").textContent = "Simulation running…";
      payloadStatus.textContent = "Illustrative payload sequence started. No aircraft control is connected.";
      payloadTimer = window.setTimeout(function () {
        payloadButton.setAttribute("aria-pressed", "false");
        payloadButton.querySelector("span:nth-child(2)").textContent = "Run payload drop simulation";
        payloadStatus.textContent = "Simulation complete. This control does not operate an aircraft.";
      }, 1800);
    });
  }

  var form = document.getElementById("recruitment-form");
  var status = document.getElementById("form-status");
  if (form && status) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!form.reportValidity()) return;
      var data = new FormData(form);
      var name = String(data.get("name") || "").trim();
      var email = String(data.get("email") || "").trim();
      var division = String(data.get("division") || "").trim();
      var message = String(data.get("message") || "").trim();
      var subject = "AeroBMSCE 2026-27 crew application - " + name;
      var body = [
        "Name: " + name,
        "Email: " + email,
        "Division: " + division,
        "",
        "Mission brief:",
        message || "(Not provided)"
      ].join("\n");
      var mailto = "mailto:aerobmsce@bmsce.ac.in?subject=" +
        encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      status.textContent = "";
      var link = document.createElement("a");
      link.href = mailto;
      link.textContent = "Open your email app";
      status.append("A draft is ready. It is not submitted until you send it. ", link, ".");
      window.location.href = mailto;
    });
  }

  var year = document.getElementById("current-year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
