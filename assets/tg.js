/* XAU.KH inside Telegram (Mini App). Loaded after telegram-web-app.js on every page.
   Outside Telegram (normal browser) this file does nothing, so the website works exactly as before.
   Inside Telegram: open full height, match Telegram's light/dark theme and colours, Khmer by default for Khmer
   Telegram users (until they press the language button), Telegram's back button, small vibration on taps,
   and links open the Telegram way. No data is sent anywhere: the app only reads the public files as before. */
(() => {
  const W = window.Telegram && window.Telegram.WebApp;
  if (!W || !W.initData) return;                       // not opened from Telegram
  const root = document.documentElement;
  const ok = v => { try { return W.isVersionAtLeast(v); } catch (e) { return false; } };
  root.classList.add("in-tg");

  // 1. Khmer first for Khmer Telegram users, only if they never chose a language on this device
  try {
    const code = ((W.initDataUnsafe || {}).user || {}).language_code || "";
    if (!localStorage.getItem("xau-lang") && code.toLowerCase().startsWith("km")) localStorage.setItem("xau-lang", "km");
  } catch (e) {}

  // 1b. Open the part of the app the button asked for: t.me/<bot>/app?startapp=record (once per launch)
  const home = /(^|\/)(index\.html)?$/.test(location.pathname);
  try {
    const sp = ((W.initDataUnsafe || {}).start_param || "").toLowerCase();
    const pages = { scaleup: "scaleup.html", journal: "journal.html", challenge: "challenge.html" };
    if (home && sp && !sessionStorage.getItem("xau-start-done")) {
      sessionStorage.setItem("xau-start-done", "1");
      if (pages[sp]) location.replace(pages[sp]);
      else if (["today", "chart", "record", "guide"].includes(sp)) history.replaceState(null, "", location.pathname + location.search + "#" + sp);
    }
  } catch (e) {}

  // 2. Same light / dark as Telegram, and Telegram's top bar in the page colour
  const paint = () => {
    root.dataset.theme = W.colorScheme === "dark" ? "dark" : "light";
    const bg = getComputedStyle(document.body || root).backgroundColor;
    const m = bg && bg.match(/\d+/g);
    const hex = m && m.length >= 3 ? "#" + m.slice(0, 3).map(n => (+n).toString(16).padStart(2, "0")).join("") : null;
    try { if (hex && ok("6.1")) { W.setHeaderColor(hex); W.setBackgroundColor(hex); } } catch (e) {}
    try { if (hex && ok("7.10")) W.setBottomBarColor(hex); } catch (e) {}
  };
  root.dataset.theme = W.colorScheme === "dark" ? "dark" : "light";
  W.onEvent("themeChanged", paint);

  // 3. Back button: on the home page it returns to "Today"; on other pages it goes back to the home page
  const syncBack = () => {
    if (!ok("6.1")) return;
    const away = home ? !!document.querySelector(".view.on:not(#v-today)") : true;
    away ? W.BackButton.show() : W.BackButton.hide();
  };
  W.BackButton.onClick(() => {
    if (home) { const b = document.querySelector('.tabbar button[data-v="today"]'); if (b) b.click(); syncBack(); }
    else location.href = "./";
  });

  // 4. Links: t.me links open in Telegram, other websites in Telegram's browser; page links stay inside the app
  document.addEventListener("click", e => {
    const a = e.target.closest && e.target.closest("a[href]");
    if (a) {
      const u = new URL(a.href, location.href);
      if (u.host === "t.me" || u.host === "telegram.me") { e.preventDefault(); W.openTelegramLink(u.href); return; }
      if (u.host !== location.host && /^https?:$/.test(u.protocol)) { e.preventDefault(); W.openLink(u.href); return; }
    }
    if (e.target.closest && e.target.closest("button,[data-v],a[href]")) {
      try { if (ok("6.1")) W.HapticFeedback.selectionChanged(); } catch (err) {}
      setTimeout(syncBack, 50);
    }
  }, true);

  const start = () => {
    paint();
    syncBack();
    W.ready();
    W.expand();
    try { if (ok("7.7")) W.disableVerticalSwipes(); } catch (e) {}   // scrolling the chart won't close the app
  };
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", start) : start();
})();
