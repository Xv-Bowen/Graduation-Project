(() => {
  const root = document.documentElement;
  const buttons = document.querySelectorAll(".size-btn");

  const applyScale = (scale) => {
    root.style.setProperty("--font-scale", scale);
    localStorage.setItem("font-scale", scale);
    buttons.forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.size === scale);
    });
  };

  const stored = localStorage.getItem("font-scale");
  if (stored) {
    applyScale(stored);
  }

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      applyScale(btn.dataset.size);
    });
  });
})();
