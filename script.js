const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#main-nav");

if (menuButton && navigation) {
  const closeMenu = (returnFocus = false) => {
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Open navigation");
    navigation.classList.remove("is-open");
    if (returnFocus) menuButton.focus();
  };

  menuButton.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!isOpen));
    menuButton.setAttribute("aria-label", isOpen ? "Open navigation" : "Close navigation");
    navigation.classList.toggle("is-open", !isOpen);
  });

  navigation.addEventListener("click", (event) => {
    if (event.target instanceof Element && event.target.closest("a")) closeMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuButton.getAttribute("aria-expanded") === "true") {
      closeMenu(true);
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 1000) closeMenu();
  });
}

const homeHero = document.querySelector(".home-hero");

if (homeHero) {
  const frames = [...homeHero.querySelectorAll(".hero-frame")];
  const firstLine = homeHero.querySelector("[data-hero-first]");
  const secondLine = homeHero.querySelector("[data-hero-second]");
  const highlight = homeHero.querySelector("[data-hero-highlight]");
  const description = homeHero.querySelector("[data-hero-description]");
  const meta = homeHero.querySelector("[data-hero-meta]");
  const slides = [
    {
      first: "Build what",
      second: "takes",
      highlight: "flight.",
      description: "Aircraft, unmanned systems and ideas made real by students who learn with their hands.",
      meta: "Aircraft design"
    },
    {
      first: "Explore",
      second: "UAV",
      highlight: "systems.",
      description: "Explore multirotor development, drone racing and autonomous-flight challenges.",
      meta: "Unmanned systems"
    },
    {
      first: "Made by",
      second: "student",
      highlight: "team.",
      description: "Learn aerospace engineering through designing, making, testing and flying.",
      meta: "The AeroBMSCE team"
    }
  ];

  homeHero.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const control = event.target.closest("[data-hero-target]");
    if (!(control instanceof HTMLButtonElement)) return;

    const index = Number(control.dataset.heroTarget);
    const slide = slides[index];
    if (!slide || !frames[index] || !firstLine || !secondLine || !highlight || !description || !meta) return;

    frames.forEach((frame, frameIndex) => {
      frame.classList.toggle("is-active", frameIndex === index);
    });
    homeHero.querySelectorAll("[data-hero-target]").forEach((item, itemIndex) => {
      item.setAttribute("aria-pressed", String(itemIndex === index));
    });
    firstLine.textContent = slide.first;
    secondLine.textContent = slide.second;
    highlight.textContent = slide.highlight;
    description.textContent = slide.description;
    meta.textContent = slide.meta;
  });
}

const interestForm = document.querySelector("#interest-form");

if (interestForm instanceof HTMLFormElement) {
  const status = document.querySelector("#form-status");
  const submitButton = interestForm.querySelector('button[type="submit"]');

  const clearFieldErrors = () => {
    interestForm.querySelectorAll(".field-error").forEach((error) => error.remove());
    interestForm.querySelectorAll("[aria-invalid='true']").forEach((field) => {
      field.removeAttribute("aria-invalid");
      field.removeAttribute("aria-describedby");
    });
  };

  const showFieldErrors = (fields) => {
    Object.entries(fields).forEach(([name, message]) => {
      const field = interestForm.elements.namedItem(name);
      if (!(field instanceof HTMLElement)) return;
      field.setAttribute("aria-invalid", "true");
      const error = document.createElement("p");
      error.className = "field-error";
      error.id = `${name}-error`;
      error.textContent = message;
      field.setAttribute("aria-describedby", error.id);
      field.insertAdjacentElement("afterend", error);
    });
    interestForm.querySelector("[aria-invalid='true']")?.focus();
  };

  interestForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFieldErrors();
    status.textContent = "Sending your request…";
    status.dataset.state = "loading";
    submitButton.disabled = true;

    const formData = new FormData(interestForm);
    const payload = {
      fullName: formData.get("fullName"),
      email: formData.get("email"),
      department: formData.get("department"),
      studyYear: formData.get("studyYear"),
      interest: formData.get("interest"),
      consent: formData.get("consent") === "on"
    };

    try {
      const response = await fetch(interestForm.action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        credentials: "same-origin"
      });
      const isJson = response.headers.get("content-type")?.includes("application/json");
      const result = isJson ? await response.json() : null;

      if (!response.ok) {
        if (result?.fields) showFieldErrors(result.fields);
        status.textContent = result?.error || "The registration service is unavailable. Please try again or email the club.";
        status.dataset.state = "error";
        return;
      }

      if (response.status !== 201 || !result?.id) {
        status.textContent = "We couldn't confirm that your request was saved. Please email the club before trying again.";
        status.dataset.state = "error";
        return;
      }

      interestForm.reset();
      status.textContent = `Your interest was saved. Reference ${result.id}.`;
      status.dataset.state = "success";
    } catch {
      status.textContent = "We couldn't reach the registration service. Please try again later or email the club.";
      status.dataset.state = "error";
    } finally {
      submitButton.disabled = false;
    }
  });
}
