// node render.js in.html out.png [#selector]
const { chromium } = require(process.env.PWC);
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME });
  const p = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 1000, height: 800 } });
  await p.goto("file://" + require("path").resolve(process.argv[2]));
  await p.evaluate(() => document.fonts.ready);
  await p.locator(process.argv[4] || "#shot").screenshot({ path: process.argv[3], omitBackground: true });
  await b.close();
})();
