#!/usr/bin/env node
/*
  Smoke test for a page built with build_viewer.py. Needs Node and Playwright with Chromium.

    NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html

  Checks: no console errors and no model problems; dragging the gauge's knob moves the page
  continuously from the text to the chunks to the model, and letting go settles it; each of the model's
  forms (summary, linear, slides, table) renders, with the model as a minimap; ▶ plays to the summary; hovering a mapped word focuses the model
  and draws the thread; clicking pins it and opens the details card; Escape releases it;
  nothing overflows a phone-width screen. Exits 1 on the first failure.
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
  const state = () => V(() => window.__semanticViewer.state);
  const still = () => page.waitForFunction(() => !window.__semanticViewer.state.moving, null, { timeout: 15000 });

  await page.goto('file://' + path.resolve(file));
  await page.waitForFunction(() => window.__semanticViewer, null, { timeout: 15000 });
  if (errors.length) return fail('console errors on load: ' + errors.join(' | '));
  const meta = await V(() => ({ problems: window.__semanticViewer.problems, chunks: window.__semanticViewer.order.length }));
  if (meta.problems.length) return fail('model problems: ' + meta.problems.join(' | '));
  ok(`loaded (${meta.chunks} chunks)`);
  await V(() => window.__semanticViewer.goTo('text', { ms: 1 }));
  await still();

  // drag the knob along the gauge: text -> chunks -> model, with stops in between
  const box = await page.locator('#gaugeSvg').boundingBox();
  const at = (x, y) => [box.x + x * box.width / 560, box.y + y * box.height / 120];
  await page.mouse.move(...at(44, 50));
  await page.mouse.down();
  for (const x of [80, 120, 150]) { await page.mouse.move(...at(x, 50), { steps: 3 }); }
  const mid = await state();
  if (!mid.moving || !(mid.u > 0.5 && mid.u < 1)) return fail('dragging the knob does not move the page between text and chunks: ' + JSON.stringify(mid));
  const ghosts = await V(() => document.querySelectorAll('#fly > *').length);
  ok(`dragging stands the page between text and chunks (u=${mid.u.toFixed(2)}, ${ghosts} pieces in flight)`);
  for (const x of [200, 260, 300, 324]) { await page.mouse.move(...at(x, 50), { steps: 3 }); }
  await page.mouse.up();
  await still();
  let st = await state();
  if (st.stage !== 'model') return fail('letting go near the model did not settle on the model: ' + JSON.stringify(st));
  ok('letting go settles on the model');

  // each form
  for (const f of ['summary', 'linear', 'slides', 'table', 'model']) {
    await page.evaluate(f => window.__semanticViewer.goTo(f, { ms: 60 }), f);
    await still();
    st = await state();
    const n = await V(() => document.querySelectorAll('#rep [data-key]').length);
    if (st.stage !== f || !n) return fail(`could not show the ${f} form`);
    const mini = await V(() => !document.querySelector('#minimap').hidden && document.querySelectorAll('#mmSvg .mm-box').length);
    if (f !== 'model' && !mini) return fail(`the minimap is missing at the ${f} form`);
  }
  ok('turns into the summary, linear notes, slides and a table, with the model as a minimap, and back');

  // ▶ plays the way to the goal, the summary
  await V(() => window.__semanticViewer.goTo('chunks', { ms: 1 }));
  await still();
  await page.mouse.click(...at(22, 58));
  try {
    await page.waitForFunction(() => window.__semanticViewer.state.stage === 'summary' && !window.__semanticViewer.state.moving, null, { timeout: 30000 });
  } catch (e) { return fail('▶ did not play to the summary: ' + JSON.stringify(await state())); }
  ok('▶ plays from where the knob is to the summary');
  await V(() => window.__semanticViewer.goTo('model', { ms: 1 }));
  await still();

  // text -> model, with the thread between them
  const seg = page.locator('#text .seg.c').first();
  await seg.scrollIntoViewIfNeeded();
  await seg.hover();
  await page.waitForTimeout(300);
  const hov = await V(() => ({ f: document.querySelectorAll('#rep .f0, #rep .fp').length, thread: document.querySelectorAll('#pointer path').length }));
  if (!hov.f) return fail('hovering a mapped word did not focus anything in the model');
  ok(`hover on the text focuses the model${hov.thread ? ' and draws the thread' : ''}`);
  const first = await V(() => window.__semanticViewer.order[0].id);
  await page.evaluate(id => window.__semanticViewer.pin(id), first);
  await page.waitForTimeout(300);
  const pinned = await V(() => ({ pinned: window.__semanticViewer.state.pinned, card: !document.querySelector('#details').hidden }));
  if (!pinned.pinned || !pinned.card) return fail('pinning a chunk did not open the details card');
  ok('pin opens the details card');
  await page.mouse.move(2, 2);
  await page.keyboard.press('Escape');
  if (await V(() => window.__semanticViewer.state.pinned)) return fail('Escape did not release the pin');
  ok('Escape releases the pin');

  // the light / dark switch
  await page.click('#themeCtl button[data-theme-set="dark"]');
  if ((await V(() => document.documentElement.dataset.theme)) !== 'dark') return fail('the theme switch did not change to dark');
  await page.click('#themeCtl button[data-theme-set="light"]');
  if ((await V(() => document.documentElement.dataset.theme)) !== 'light') return fail('the theme switch did not change back to light');
  ok('switches between light and dark');

  // and back down
  await V(() => window.__semanticViewer.goTo('text', { ms: 60 }));
  await still();
  if ((await state()).stage !== 'text') return fail('could not descend to the text');
  ok('descends back to the text');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  if (await V(() => document.documentElement.scrollWidth > innerWidth + 1)) return fail('the page scrolls sideways at phone width');
  ok('no sideways scroll at phone width');

  if (errors.length) return fail('console errors: ' + errors.join(' | '));
  ok('no console errors');
  await browser.close();
})();
