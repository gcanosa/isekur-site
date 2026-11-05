const { chromium } = require(process.env.PWC);
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME });
  const ctx = await b.newContext({ ignoreHTTPSErrors: true, deviceScaleFactor: 2, viewport: { width: 1240, height: 520 } });
  const p = await ctx.newPage();
  let url = "https://127.0.0.1:18443/";
  try { await p.goto(url); } catch (e) { url = "http://127.0.0.1:18443/"; await p.goto(url); }
  await p.fill("#lu", "me"); await p.fill("#lp", "shot"); await p.press("#lp", "Enter");
  await p.waitForSelector("#msgs >> text=see you in", { timeout: 15000 });
  await p.waitForTimeout(1500);
  await p.screenshot({ path: "out/web-rose.png" });
  const ph = await b.newContext({ ignoreHTTPSErrors: true, deviceScaleFactor: 2, viewport: { width: 390, height: 760 }, isMobile: true, hasTouch: true });
  const q = await ph.newPage(); await q.goto(url);
  await q.fill("#lu", "me"); await q.fill("#lp", "shot"); await q.press("#lp", "Enter");
  await q.waitForSelector("#msgs >> text=see you in", { timeout: 15000 }); await q.waitForTimeout(1500);
  await q.screenshot({ path: "out/web-phone.png" });
  await p.setViewportSize({ width: 1280, height: 760 });
  await p.fill("#line", "/theme mirc"); await p.press("#line", "Enter");
  await p.waitForTimeout(2000);
  await p.screenshot({ path: "out/web-mirc.png" });
  await p.click("#setbtn"); await p.waitForTimeout(1500);
  await p.screenshot({ path: "out/web-set.png" });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
