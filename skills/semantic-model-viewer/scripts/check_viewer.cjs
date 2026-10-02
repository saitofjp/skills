#!/usr/bin/env node
/*
  Smoke test for a page built with build_viewer.py. Needs Node and Playwright with Chromium.

    NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html [--all-scales]

  Checks: no console errors; hovering a mapped word focuses a node; clicking pins it and
  opens the details card; Escape releases it; Formation runs to the end in both orders
  at the coarsest and the finest scale (every scale with --all-scales). Exits 1 on the
  first failure.
*/
'use strict';
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) {
  console.error('Playwright is not available. Install it, or set NODE_PATH="$(npm root -g)".');
  process.exit(2);
}

const file = process.argv.slice(2).find(a => !a.startsWith('--'));
const allScales = process.argv.includes('--all-scales');
if (!file) { console.error('usage: node check_viewer.cjs view.html'); process.exit(2); }

(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  const fail = async msg => { console.error('FAIL ' + msg); await browser.close(); process.exit(1); };
  const ok = msg => console.log('ok   ' + msg);

  await page.goto('file://' + path.resolve(file));
  await page.waitForFunction(() => window.__semanticViewer, null, { timeout: 15000 });
  if (errors.length) return fail('console errors on load: ' + errors.join(' | '));
  const meta = await page.evaluate(() => ({ problems: window.__semanticViewer.problems, levels: document.querySelectorAll('#levelCtl button').length || 1 }));
  if (meta.problems.length) return fail('model problems: ' + meta.problems.join(' | '));
  ok(`loaded (${meta.levels} scale${meta.levels > 1 ? 's' : ''})`);

  // text -> model
  const seg = page.locator('.seg').first();
  await seg.scrollIntoViewIfNeeded();
  await seg.hover();
  await page.waitForTimeout(250);
  const focused = await page.evaluate(() => document.querySelectorAll('.node.is-focus, .edge.is-focus').length);
  if (!focused) return fail('hovering a mapped word did not focus anything in the graph');
  ok('hover on the text focuses the graph');

  // model -> text, pin, release
  const vid = await page.evaluate(() => window.__semanticViewer.graph().nodes[0].id);
  await page.evaluate(id => window.__semanticViewer.setPinned(id, null), vid);
  await page.waitForTimeout(300);
  const pinned = await page.evaluate(() => ({ pinned: !!window.__semanticViewer.pinned, card: !document.querySelector('#details').hidden, lit: document.querySelectorAll('.seg.lit, .seg.hot').length }));
  if (!pinned.pinned || !pinned.card) return fail('pinning a node did not open the details card');
  ok(`pin opens the details card (${pinned.lit} text segments lit)`);
  await page.keyboard.press('Escape');
  if (await page.evaluate(() => window.__semanticViewer.pinned)) return fail('Escape did not release the pin');
  ok('Escape releases the pin');

  // Formation, both orders, every scale, at 4x
  await page.click('#modeCtl button[data-mode="formation"]');
  const scales = allScales ? [...Array(meta.levels).keys()] : [...new Set([0, meta.levels - 1])];
  for (const L of scales) {
    for (const order of ['focus', 'reading']) {
      await page.evaluate(L => window.__semanticViewer.setLevel(L), L);
      await page.selectOption('#strategySel', order);
      await page.selectOption('#speedSel', '4');
      await page.evaluate(() => { window.__semanticViewer.pause(); window.__semanticViewer.showStep(-1); window.__semanticViewer.play(); });
      const n = await page.evaluate(() => window.__semanticViewer.steps.length);
      try {
        await page.waitForFunction(n => window.__semanticViewer.step === n - 1, n, { timeout: Math.max(30000, n * 3000) });
      } catch (e) {
        const at = await page.evaluate(() => window.__semanticViewer.step);
        return fail(`Formation (${order}, scale ${L}) stopped at step ${at + 1} of ${n}`);
      }
      ok(`Formation ${order} at scale ${L}: ${n} steps to the end`);
    }
  }
  if (errors.length) return fail('console errors: ' + errors.join(' | '));
  ok('no console errors');
  await browser.close();
})();
