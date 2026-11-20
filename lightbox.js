// Click a screenshot to see it larger (the full-size file); a click anywhere or Esc closes it.
// Without JS the docs' screenshots are still links to the file.
(function () {
  var sel = "img.shot, figure.shot img, .gal img, .browser img, .phone img", box;
  var st = document.createElement("style");
  st.textContent = sel + "{cursor:zoom-in}.lb{position:fixed;inset:0;z-index:99;display:flex;align-items:center;justify-content:center;padding:2vh 2vw;" +
    "background:#000d;cursor:zoom-out}.lb img{max-width:100%;max-height:100%;border-radius:8px;box-shadow:0 20px 80px #000}";
  document.head.appendChild(st);
  function close() { if (box) box.remove(), box = null; }
  document.addEventListener("click", function (e) {
    if (box) return close();
    var im = e.target.closest && e.target.closest("img");
    if (!im || !im.matches(sel) || e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
    e.preventDefault();
    box = document.createElement("div");
    box.className = "lb", box.setAttribute("role", "dialog"), box.setAttribute("aria-label", im.alt || "Screenshot");
    var big = document.createElement("img");
    big.src = im.currentSrc || im.src, big.alt = im.alt;
    box.appendChild(big), document.body.appendChild(box);
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
})();
