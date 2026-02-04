(() => {
  const initTts = () => {
    const content = document.getElementById("articleContent");
    const playBtn = document.getElementById("ttsPlay");
    const pauseBtn = document.getElementById("ttsPause");
    const stopBtn = document.getElementById("ttsStop");
    const statusEl = document.getElementById("ttsStatus");

    if (!content || !playBtn || !pauseBtn || !stopBtn || !statusEl) return;
    if (playBtn.dataset.ttsInit === "1") return;
    playBtn.dataset.ttsInit = "1";

    if (!("speechSynthesis" in window)) {
      statusEl.textContent = "当前浏览器不支持语音朗读。";
      playBtn.disabled = true;
      pauseBtn.disabled = true;
      stopBtn.disabled = true;
      return;
    }

    let utterance = null;
    let isPaused = false;

    const buildUtterance = () => {
      const text = content.innerText.replace(/\s+/g, " ").trim();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = "zh-CN";
      utter.rate = 0.95;
      utter.onend = () => {
        statusEl.textContent = "朗读结束。";
        isPaused = false;
      };
      utter.onerror = () => {
        statusEl.textContent = "朗读出现问题，请稍后再试。";
        isPaused = false;
      };
      return utter;
    };

    const startSpeak = () => {
      window.speechSynthesis.cancel();
      utterance = buildUtterance();
      window.speechSynthesis.speak(utterance);
      statusEl.textContent = "正在朗读中...";
      isPaused = false;
    };

    playBtn.addEventListener("click", () => {
      startSpeak();
    });

    pauseBtn.addEventListener("click", () => {
      if (!utterance) {
        startSpeak();
        return;
      }
      if (window.speechSynthesis.speaking && !isPaused) {
        window.speechSynthesis.pause();
        statusEl.textContent = "已暂停，可点击继续。";
        isPaused = true;
      } else if (isPaused) {
        window.speechSynthesis.resume();
        statusEl.textContent = "继续朗读中...";
        isPaused = false;
      } else {
        startSpeak();
      }
    });

    stopBtn.addEventListener("click", () => {
      window.speechSynthesis.cancel();
      utterance = null;
      isPaused = false;
      statusEl.textContent = "已停止朗读。";
    });
  };

  document.addEventListener("DOMContentLoaded", initTts);
  document.addEventListener("htmx:afterSwap", initTts);
})();
