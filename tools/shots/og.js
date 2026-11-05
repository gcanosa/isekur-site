const { chromium } = require(process.env.PWC);
(async () => { const b = await chromium.launch({ executablePath: process.env.CHROME });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto("file://" + require("path").resolve("og.html")); await p.waitForTimeout(300);
  await p.locator("#og").screenshot({ path: "out/og.png" }); await b.close(); })();
