(() => {
  const initChat = () => {
    const chatBox = document.querySelector(".floating-chat");
    if (!chatBox || chatBox.dataset.chatInit === "1") return;
    chatBox.dataset.chatInit = "1";

    const chatPanel = document.getElementById("chatPanel");
    const chatToggle = document.getElementById("chatToggle");
    const chatClose = document.getElementById("chatClose");
    const chatHistory = document.getElementById("chatHistory");
    const chatInput = document.getElementById("chatInput");
    const chatSend = document.getElementById("chatSend");
    const deepThinkToggle = document.getElementById("deepThinkToggle");
    const deepThinkState = document.getElementById("deepThinkState");
    const apiUrl = chatBox.dataset.apiUrl;
    const provider = chatBox.dataset.provider || "deepseek";

    if (!chatPanel || !chatToggle || !chatInput || !chatSend || !chatHistory) return;

    const messages = [];
    let deepThink = localStorage.getItem("deep-think") === "1";
    let dragged = false;

    const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

    const getCookie = (name) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(";").shift();
      return "";
    };

    const appendBubble = (text, role) => {
      const bubble = document.createElement("div");
      bubble.className = `chat-bubble ${role}`;
      bubble.textContent = text;
      chatHistory.appendChild(bubble);
      chatHistory.scrollTop = chatHistory.scrollHeight;
      return bubble;
    };

    const setOpen = (isOpen) => {
      chatBox.classList.toggle("open", isOpen);
      chatPanel.setAttribute("aria-hidden", String(!isOpen));
      if (isOpen) {
        chatInput.focus();
      }
    };

    const setDeepThink = (value) => {
      deepThink = value;
      localStorage.setItem("deep-think", deepThink ? "1" : "0");
      if (deepThinkToggle) {
        deepThinkToggle.classList.toggle("active", deepThink);
        deepThinkToggle.setAttribute("aria-checked", deepThink ? "true" : "false");
      }
      if (deepThinkState) {
        deepThinkState.textContent = deepThink ? "深度思考" : "标准对话";
      }
    };

    const sendMessage = async () => {
      const text = chatInput.value.trim();
      if (!text) return;
      appendBubble(text, "user");
      messages.push({ role: "user", content: text });
      chatInput.value = "";
      chatSend.disabled = true;
      const thinkingBubble = appendBubble("正在思考", "assistant thinking");

      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({
            provider,
            messages,
            deep_think: deepThink,
          }),
        });
        if (response.status === 401) {
          thinkingBubble.textContent = "请先登录后使用 AI 咨询。";
          thinkingBubble.classList.remove("thinking");
          return;
        }
        const data = await response.json();
        const reply = data.reply || "抱歉，暂时无法回应。";
        thinkingBubble.textContent = reply;
        thinkingBubble.classList.remove("thinking");
        messages.push({ role: "assistant", content: reply });
      } catch (error) {
        thinkingBubble.textContent = "网络连接异常，请稍后再试。";
        thinkingBubble.classList.remove("thinking");
      } finally {
        chatSend.disabled = false;
        chatInput.focus();
      }
    };

    chatToggle.addEventListener("click", (event) => {
      if (dragged) {
        dragged = false;
        event.preventDefault();
        return;
      }
      setOpen(true);
    });

    chatClose?.addEventListener("click", (event) => {
      event.preventDefault();
      setOpen(false);
    });

    if (!document.documentElement.dataset.chatEscBound) {
      document.documentElement.dataset.chatEscBound = "1";
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          setOpen(false);
        }
      });
    }

    chatSend.addEventListener("click", sendMessage);
    chatInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });

    if (deepThinkToggle) {
      deepThinkToggle.addEventListener("click", () => {
        setDeepThink(!deepThink);
      });
    }

    chatToggle.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) return;
      const handleRect = chatToggle.getBoundingClientRect();
      const offsetX = event.clientX - handleRect.left;
      const offsetY = event.clientY - handleRect.top;
      let moved = false;

      const onMove = (moveEvent) => {
        const nextLeft = moveEvent.clientX - offsetX;
        const nextTop = moveEvent.clientY - offsetY;
        const minLeft = 12;
        const maxLeft = window.innerWidth - handleRect.width - 12;
        const minTop = 12;
        const maxTop = window.innerHeight - handleRect.height - 12;
        const clampedLeft = clamp(nextLeft, minLeft, maxLeft);
        const clampedTop = clamp(nextTop, minTop, maxTop);

        chatToggle.style.left = `${clampedLeft}px`;
        chatToggle.style.top = `${clampedTop}px`;
        chatToggle.style.right = "auto";
        chatToggle.style.bottom = "auto";

        if (
          !moved &&
          (Math.abs(moveEvent.clientX - event.clientX) > 4 ||
            Math.abs(moveEvent.clientY - event.clientY) > 4)
        ) {
          moved = true;
          dragged = true;
        }
      };

      const onUp = () => {
        window.removeEventListener("pointermove", onMove);
        window.removeEventListener("pointerup", onUp);
        if (moved) {
          const rect = chatToggle.getBoundingClientRect();
          const screenMid = window.innerWidth / 2;
          const targetLeft =
            rect.left + rect.width / 2 < screenMid
              ? 12
              : window.innerWidth - rect.width - 12;
          chatToggle.style.left = `${targetLeft}px`;
        }
      };

      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp, { once: true });
    });

    setDeepThink(deepThink);
    try {
      localStorage.removeItem("chat-open");
      localStorage.removeItem("chat-toggle-position");
    } catch (error) {
      // 忽略
    }
    setOpen(false);
  };

  document.addEventListener("DOMContentLoaded", initChat);
  document.addEventListener("htmx:afterSwap", initChat);
})();
