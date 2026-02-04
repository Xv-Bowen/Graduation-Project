(() => {
  let listenersBound = false;

  const updateReading = () => {
    const article = document.querySelector(".article");
    const content = document.getElementById("articleContent");
    const progress = document.getElementById("readingProgress");
    const timeEl = document.getElementById("readingTime");

    if (!article || !content || !progress || !timeEl) return;

    const text = content.innerText.replace(/\s+/g, "");
    const minutes = Math.max(1, Math.ceil(text.length / 320));
    timeEl.textContent = `预计阅读 ${minutes} 分钟`;

    const start = article.offsetTop;
    const end = start + article.offsetHeight - window.innerHeight;
    const current = window.scrollY;
    const ratio = end > start ? (current - start) / (end - start) : 1;
    const progressValue = Math.min(1, Math.max(0, ratio));
    progress.style.width = `${progressValue * 100}%`;
  };

  const initReading = () => {
    updateReading();
    if (listenersBound) return;
    listenersBound = true;
    window.addEventListener("scroll", updateReading, { passive: true });
    window.addEventListener("resize", updateReading);
  };

  document.addEventListener("DOMContentLoaded", initReading);
  document.addEventListener("htmx:afterSwap", initReading);
})();
