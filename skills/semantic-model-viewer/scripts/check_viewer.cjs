#!/usr/bin/env node
/*
  Smoke test for a page built with build_viewer.py. Needs Node and Playwright with Chromium.

    NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html

  Checks: no console errors and no model problems; hovering a mapped word focuses the model
  and draws the thread; clicking pins it and opens the details card; Escape releases it;
  every layer (text, chunks, model) and every form (structure, linear, table, summary)
  renders and settles; the story plays to its last step in both orders; nothing overflows
  a phone-width screen. Exits 1 on the first failure.
*/
'use strict';
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) {
  console.error('Playwright is not available. Install it, or set NODE_PATH="$(npm root -g)".');
  process.exit(2);
}

const file = process.argv.slice(2).find(a => !a.startsWith('--'));
if (!file) { console.error('usage: node check_viewer.cjs view.html'); process.exit(2); }

(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  const fail = async msg => { console.error('FAIL ' + msg); await browser.close(); process.exit(1); };
  const ok = msg => console.log('ok   ' + msg);
  const V = fn => page.evaluate(fn);
  const settle = () => page.waitForFunction(() => !window.__semanticViewer.state.flying, null, { timeout: 10000 });

  await page.goto('file://' + path.resolve(file));
  await page.waitForFunction(() => window.__semanticViewer, null, { timeout: 15000 });
  await V(() => window.__semanticViewer.pause());
  await V(() => window.__semanticViewer.explore({ stop: 'model', rep: 'linear' }));
  await settle();
  if (errors.length) return fail('console errors on load: ' + errors.join(' | '));
  const meta = await V(() => ({ problems: window.__semanticViewer.problems, chunks: window.__semanticViewer.order.length }));
  if (meta.problems.length) return fail('model problems: ' + meta.problems.join(' | '));
  ok(`loaded (${meta.chunks} chunks)`);

  // text -> model, with the thread between them
  const seg = page.locator('#text .seg.c').first();
  await seg.scrollIntoViewIfNeeded();
  await seg.hover();
  await page.waitForTimeout(300);
  const hov = await V(() => ({ f: document.querySelectorAll('#rep .f0, #rep .fp').length, thread: document.querySelectorAll('#pointer path').length }));
  if (!hov.f) return fail('hovering a mapped word did not focus anything in the model');
  ok(`hover on the text focuses the model${hov.thread ? ' and draws the thread' : ''}`);

  // pin, release
  const first = await V(() => window.__semanticViewer.order[0].id);
  await page.evaluate(id => window.__semanticViewer.pin(id), first);
  await page.waitForTimeout(300);
  const pinned = await V(() => ({ pinned: window.__semanticViewer.state.pinned, card: !document.querySelector('#details').hidden, lit: document.querySelectorAll('.seg.hn, .seg.hq, .seg.hp').length }));
  if (!pinned.pinned || !pinned.card) return fail('pinning a chunk did not open the details card');
  ok(`pin opens the details card (${pinned.lit} text segments lit)`);
  await page.mouse.move(2, 2);
  await page.keyboard.press('Escape');
  if (await V(() => window.__semanticViewer.state.pinned)) return fail('Escape did not release the pin');
  ok('Escape releases the pin');

  // every layer and every form
  for (const stop of ['text', 'chunks', 'model']) {
    await page.evaluate(stop => window.__semanticViewer.explore({ stop }), stop);
    await settle();
    const st = await V(() => window.__semanticViewer.state.stop);
    if (st !== stop) return fail(`could not reach the ${stop} layer`);
  }
  ok('rises and descends through text, chunks and model');
  for (const rep of ['structure', 'linear', 'table', 'summary']) {
    await page.evaluate(rep => window.__semanticViewer.explore({ rep }), rep);
    await settle();
    const n = await V(() => document.querySelectorAll('#rep [data-key]').length);
    if (!n) return fail(`the ${rep} form shows nothing`);
  }
  ok('transforms into structure, linear, table and summary');

  // the story, both orders
  for (const order of ['notes', 'reading']) {
    await page.selectOption('#orderSel', order);
    await page.selectOption('#speedSel', '2');
    const n = (await V(() => window.__semanticViewer.story())).length;
    await V(() => { window.__semanticViewer.pause(); window.__semanticViewer.play(); });
    try {
      await page.waitForFunction(n => window.__semanticViewer.state.step === n - 1 && !window.__semanticViewer.state.flying, n, { timeout: Math.max(60000, n * 4000) });
    } catch (e) {
      const at = await V(() => window.__semanticViewer.state.step);
      return fail(`the story (${order}) stopped at step ${at + 1} of ${n}`);
    }
    ok(`story in ${order} order plays ${n} steps to the end`);
    await V(() => window.__semanticViewer.pause());
  }

  // phone width
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  if (await V(() => document.documentElement.scrollWidth > innerWidth + 1)) return fail('the page scrolls sideways at phone width');
  ok('no sideways scroll at phone width');

  if (errors.length) return fail('console errors: ' + errors.join(' | '));
  ok('no console errors');
  await browser.close();
})();
