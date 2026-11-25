// Renders icon.svg to the plugin's icon, a 1024 x 1024 PNG: node tools/plugin-icon/render.cjs
// Needs Playwright with Chromium. The icon is not a poster, so the standard-library rule does not apply to it.
const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");
(async () => {
  const svg = fs.readFileSync(path.join(__dirname, "icon.svg"), "utf8");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 1 });
  await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await page.locator("svg").screenshot({
    path: path.join(__dirname, "../../plugins/proof-posters/.claude-plugin/icon.png"),
  });
  await browser.close();
})();
