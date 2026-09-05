(() => {
  "use strict";

  const scriptUrl = document.currentScript && document.currentScript.src;
  const readyClass = "secure-pages-ready";
  const sessionKeyPrefix = "secure-pages:group:";

  function normalizePath(path) {
    const withLeadingSlash = path.startsWith("/") ? path : `/${path}`;
    return withLeadingSlash.endsWith("/")
      ? withLeadingSlash
      : `${withLeadingSlash}/`;
  }

  function getSiteBasePath() {
    if (!scriptUrl) {
      throw new Error("Unable to determine the secure-page script URL.");
    }

    return normalizePath(new URL("../../", scriptUrl).pathname);
  }

  function getPagePath() {
    const basePath = getSiteBasePath();
    const currentPath = normalizePath(window.location.pathname);

    if (!currentPath.startsWith(basePath)) {
      return currentPath;
    }

    return normalizePath(currentPath.slice(basePath.length));
  }

  function getConfigUrl() {
    return new URL("../config/secure-pages.json", scriptUrl);
  }

  async function loadConfiguration() {
    const response = await fetch(getConfigUrl(), {
      cache: "no-store",
      credentials: "same-origin",
    });

    if (!response.ok) {
      throw new Error(`Secure-page configuration returned ${response.status}.`);
    }

    const configuration = await response.json();
    if (!configuration || !Array.isArray(configuration.secure_pages)) {
      throw new Error("Secure-page configuration has an invalid structure.");
    }

    return configuration.secure_pages;
  }

  function findSecurePage(pages) {
    const currentPath = getPagePath();
    return pages.find((page) => normalizePath(page.path) === currentPath) || null;
  }

  async function hashPassword(password) {
    if (!window.crypto || !window.crypto.subtle) {
      throw new Error("Web Crypto API is unavailable in this browser context.");
    }

    const bytes = new TextEncoder().encode(password);
    const digest = await window.crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), (byte) =>
      byte.toString(16).padStart(2, "0"),
    ).join("");
  }

  function hashesMatch(actual, expected) {
    if (typeof expected !== "string" || actual.length !== expected.length) {
      return false;
    }

    let difference = 0;
    for (let index = 0; index < actual.length; index += 1) {
      difference |= actual.charCodeAt(index) ^ expected.charCodeAt(index);
    }
    return difference === 0;
  }

  function getSessionKey(group) {
    return `${sessionKeyPrefix}${encodeURIComponent(group)}`;
  }

  function isGroupUnlocked(page) {
    try {
      return (
        window.sessionStorage.getItem(getSessionKey(page.group)) ===
        page.password_hash.toLowerCase()
      );
    } catch (cause) {
      console.warn("Unable to read the protected-page session.", cause);
      return false;
    }
  }

  function rememberUnlockedGroup(page) {
    try {
      window.sessionStorage.setItem(
        getSessionKey(page.group),
        page.password_hash.toLowerCase(),
      );
    } catch (cause) {
      console.warn("Unable to save the protected-page session.", cause);
    }
  }

  function detachContent(container) {
    const content = document.createDocumentFragment();
    while (container.firstChild) {
      content.append(container.firstChild);
    }
    return content;
  }

  function createLockScreen() {
    const lock = document.createElement("section");
    lock.className = "secure-lock";
    lock.setAttribute("aria-labelledby", "secure-lock-title");
    lock.innerHTML = `
      <div class="secure-lock__panel">
        <p class="secure-lock__icon" aria-hidden="true">🔒</p>
        <h1 class="secure-lock__title" id="secure-lock-title">Protected Documentation</h1>
        <p class="secure-lock__description">This page requires a password.</p>
        <form class="secure-lock__form" novalidate>
          <label class="secure-lock__field">
            <span class="secure-lock__label">Password</span>
            <input class="secure-lock__input" name="password" type="password" autocomplete="current-password" required>
          </label>
          <button class="secure-lock__button" type="submit">Unlock</button>
          <p class="secure-lock__error" role="alert" aria-live="polite"></p>
        </form>
      </div>`;
    return lock;
  }

  function showConfigurationError(container) {
    const lock = createLockScreen();
    const form = lock.querySelector(".secure-lock__form");
    form.replaceChildren();
    const error = document.createElement("p");
    error.className = "secure-lock__error";
    error.setAttribute("role", "alert");
    error.textContent = "Protected-page configuration is unavailable.";
    form.append(error);
    container.replaceChildren(lock);
    document.documentElement.classList.add(readyClass);
  }

  function protectPage(container, page) {
    const protectedContent = detachContent(container);
    const secondarySidebar = document.querySelector(".md-sidebar--secondary");
    const protectedTableOfContents = secondarySidebar
      ? detachContent(secondarySidebar)
      : null;
    const lock = createLockScreen();
    const form = lock.querySelector(".secure-lock__form");
    const input = lock.querySelector(".secure-lock__input");
    const button = lock.querySelector(".secure-lock__button");
    const error = lock.querySelector(".secure-lock__error");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      error.textContent = "";

      if (!input.value) {
        error.textContent = "Password is required.";
        input.focus();
        return;
      }

      button.disabled = true;
      try {
        const passwordHash = await hashPassword(input.value);
        if (!hashesMatch(passwordHash, page.password_hash.toLowerCase())) {
          input.value = "";
          error.textContent = "Incorrect password.";
          input.focus();
          return;
        }

        rememberUnlockedGroup(page);
        container.replaceChildren(protectedContent);
        if (secondarySidebar && protectedTableOfContents) {
          secondarySidebar.replaceChildren(protectedTableOfContents);
        }
        document.documentElement.classList.remove("secure-page-locked");
      } catch (cause) {
        console.error("Unable to verify protected page password.", cause);
        error.textContent = "Password verification is unavailable.";
        input.focus();
      } finally {
        button.disabled = false;
      }
    });

    container.replaceChildren(lock);
    document.documentElement.classList.add("secure-page-locked");
    document.documentElement.classList.add(readyClass);
    input.focus();
  }

  async function initialize() {
    const container = document.querySelector(".md-content__inner");
    if (!container) {
      document.documentElement.classList.add(readyClass);
      return;
    }

    try {
      const pages = await loadConfiguration();
      const securePage = findSecurePage(pages);
      if (!securePage) {
        document.documentElement.classList.add(readyClass);
        return;
      }

      if (isGroupUnlocked(securePage)) {
        document.documentElement.classList.add(readyClass);
        return;
      }

      protectPage(container, securePage);
    } catch (cause) {
      console.error("Unable to initialize protected pages.", cause);
      detachContent(container);
      showConfigurationError(container);
    }
  }

  initialize();
})();
