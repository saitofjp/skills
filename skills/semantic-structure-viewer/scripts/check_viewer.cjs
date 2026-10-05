#!/usr/bin/env node
/*
  Smoke test for a page built with build_viewer.py. Needs Node and Playwright with Chromium.

    NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html

  Checks: no console errors and no model problems; dragging the gauge's knob moves the page
  continuously from the text to the chunks to the model, and letting go settles it; the structure and the minimap run
  the same way (with the conclusion on the right when they run from it); the columns follow the shape of the text: a
  question branching out runs from the start, reasons gathering into a conclusion run from the conclusion (a chunk with
  no lines does not tip it), and an anchor given in the view options wins; the page plays by itself
  when it opens (unless built with --no-autoplay); each of the model's forms (summary, linear, slides, table)
  renders, with the model as a minimap; ▶ plays from the text to the summary and back to the model, wherever the knob was; hovering a mapped word focuses the model
  and draws the thread, with its details along the bottom, and so does hovering anywhere inside a chunk's frame; Escape clears the focus; at a form the details
  card and the minimap sit side by side without overlapping; the theme switches between dark, light and dopa: in dopa,
  dragging the knob stages nothing, ▶ stages the play as a show (the build-up and the summary's arrival once), even when
  the system asks for less motion, dopa is not remembered, and the show stops with the theme;
  nothing overflows a phone-width screen. Exits 1 on the first failure.
*/
'use strict';
const fs = require('fs');
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
  // the top-level chunks, column by column from the left: in the structure (at the model) and on the minimap
  const structureCols = () => V(() => [...document.querySelectorAll('#rep .cols > .col')].map(c => [...c.children].map(x => x.dataset.node)));
  const minimapCols = p => p.evaluate(() => {
    const at = new Map();
    document.querySelectorAll('#mmSvg .mm-box.unit').forEach(g => {
      const x = Math.round(+g.querySelector('rect').getAttribute('x'));
      if (!at.has(x)) at.set(x, []);
      at.get(x).push(g.dataset.node);
    });
    return [...at.entries()].sort((a, b) => a[0] - b[0]).map(e => e[1]);
  });

  await page.goto('file://' + path.resolve(file));
  await page.waitForFunction(() => window.__semanticViewer, null, { timeout: 15000 });
  if (errors.length) return fail('console errors on load: ' + errors.join(' | '));
  const meta = await V(() => ({ problems: window.__semanticViewer.problems, chunks: window.__semanticViewer.order.length }));
  if (meta.problems.length) return fail('model problems: ' + meta.problems.join(' | '));
  ok(`loaded (${meta.chunks} chunks)`);
  if (await V(() => window.__semanticViewer.autoplay)) {
    try { await page.waitForFunction(() => window.__semanticViewer.state.playing, null, { timeout: 8000 }); }
    catch (e) { return fail('the page did not play by itself when it opened'); }
    ok('plays by itself when it opens');
  }
  await V(() => window.__semanticViewer.goTo('text', { ms: 1 }));
  await still();

  // drag the knob along the gauge: text -> chunks -> model, with stops in between
  const box = await page.locator('#gaugeSvg').boundingBox();
  const G = await V(() => window.__semanticViewer.gauge);
  const at = (x, y) => [box.x + x * box.width / G.w, box.y + y * box.height / G.h];
  const along = (a, b, k) => at(G.at[a][0] + (G.at[b][0] - G.at[a][0]) * k, G.at[a][1] + (G.at[b][1] - G.at[a][1]) * k);
  await page.mouse.move(...along('text', 'chunks', 0));
  await page.mouse.down();
  for (const k of [0.3, 0.6, 0.8]) { await page.mouse.move(...along('text', 'chunks', k), { steps: 3 }); }
  const mid = await state();
  if (!mid.moving || !(mid.u > 0.5 && mid.u < 1)) return fail('dragging the knob does not move the page between text and chunks: ' + JSON.stringify(mid));
  const ghosts = await V(() => document.querySelectorAll('#fly > *').length);
  ok(`dragging stands the page between text and chunks (u=${mid.u.toFixed(2)}, ${ghosts} pieces in flight)`);
  for (const k of [0.3, 0.6, 0.85, 0.96]) { await page.mouse.move(...along('chunks', 'model', k), { steps: 3 }); }
  await page.mouse.up();
  await still();
  let st = await state();
  if (st.stage !== 'model') return fail('letting go near the model did not settle on the model: ' + JSON.stringify(st));
  ok('letting go settles on the model');

  // the structure and the minimap run the same way, and from the conclusion it sits on the right
  const sCols = await structureCols(), mCols = await minimapCols(page);
  const colOf = cols => new Map(cols.flatMap((c, i) => c.map(id => [id, i])));
  const sAt = colOf(sCols), mAt = colOf(mCols);
  const units = [...mAt.keys()];
  if (units.some(a => units.some(b => sAt.get(a) < sAt.get(b) && mAt.get(a) > mAt.get(b))))
    return fail('the structure and the minimap run different ways: ' + JSON.stringify({ structure: sCols, minimap: mCols }));
  const anchor = await V(() => window.__semanticViewer.anchor);
  const concl = await V(() => { const c = document.querySelector('#rep .cols > .col > .card.concl, #rep .cols > .col > .card:has(.concl)'); return c && c.dataset.node; });
  if (anchor === 'end' && concl && (sAt.get(concl) !== sCols.length - 1 || mAt.get(concl) !== mCols.length - 1))
    return fail('the columns run from the conclusion, but it is not on the right: ' + JSON.stringify({ structure: sCols, minimap: mCols }));
  ok(`the structure and the minimap run the same way, from the ${anchor === 'end' ? 'end (the conclusion on the right)' : 'start (on the left)'}`);

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

  // ▶ always plays from the start, the text, to the goal, the summary, wherever the knob is
  await V(() => window.__semanticViewer.goTo('chunks', { ms: 1 }));
  await still();
  await page.click('#gauge .g-play');
  if ((await state()).seg !== 'text-chunks') return fail('▶ did not start from the text: ' + JSON.stringify(await state()));
  try {
    await page.waitForFunction(() => window.__semanticViewer.state.stage === 'summary' && !window.__semanticViewer.state.moving, null, { timeout: 60000 });
  } catch (e) { return fail('▶ did not play to the summary: ' + JSON.stringify(await state())); }
  try {
    await page.waitForFunction(() => { const s = window.__semanticViewer.state; return s.stage === 'model' && !s.moving && !s.playing; }, null, { timeout: 20000 });
  } catch (e) { return fail('▶ did not go back to the model after the summary: ' + JSON.stringify(await state())); }
  ok('▶ plays from the text to the summary and, after a moment there, back to the model');
  await V(() => window.__semanticViewer.goTo('model', { ms: 1 }));
  await still();

  // text -> model, with the thread between them
  const seg = page.locator('#text .seg.c').first();
  await seg.scrollIntoViewIfNeeded();
  await seg.hover();
  await page.waitForTimeout(300);
  const hov = await V(() => ({ f: document.querySelectorAll('#rep .f0, #rep .fp').length, thread: document.querySelectorAll('#pointer path').length, card: !document.querySelector('#details').hidden }));
  if (!hov.f) return fail('hovering a mapped word did not focus anything in the model');
  if (!hov.card) return fail('hovering a mapped word did not show its details');
  ok(`hover on the text focuses the model${hov.thread ? ', draws the thread' : ''} and shows its details`);
  // between the words, anywhere in a chunk's frame, focuses that chunk
  await page.mouse.move(2, 2);
  const spot = await V(() => {
    const slabs = [...document.querySelectorAll('#slabs .sl rect.slab')].map(r => ({ id: r.parentNode.dataset.node, b: r.getBoundingClientRect() }))
      .filter(x => x.b.top > 120 && x.b.bottom < innerHeight - 60 && x.b.height > 30);
    const pane = document.querySelector('#textPane').getBoundingClientRect();
    const s = slabs.find(x => x.b.right < pane.right);
    return s && { id: s.id, x: s.b.right - 3, y: s.b.top + s.b.height / 2 };
  });
  if (spot) {
    await page.mouse.move(spot.x, spot.y);
    await page.waitForTimeout(200);
    const on = await V(() => window.__semanticViewer.state.hover);
    if (!on) return fail('hovering inside a chunk\'s frame, off the words, did not focus it');
    ok('hovering anywhere inside a chunk\'s frame focuses it');
  }
  // at a form, the details card and the minimap line up along the bottom
  await page.mouse.move(2, 2);
  await V(() => window.__semanticViewer.goTo('linear'));
  await page.waitForTimeout(300);
  const first = await V(() => window.__semanticViewer.order[0].id);
  await page.evaluate(id => window.__semanticViewer.hover(id), first);
  await page.waitForTimeout(200);
  const dock = await V(() => {
    const d = document.querySelector('#details'), m = document.querySelector('#minimap');
    if (d.hidden || m.hidden) return { shown: false };
    const a = d.getBoundingClientRect(), b = m.getBoundingClientRect();
    return { shown: true, overlap: a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1, low: a.bottom > innerHeight * 0.6 };
  });
  if (!dock.shown) return fail('at a form, the details card or the minimap is missing');
  if (dock.overlap) return fail('at a form, the details card overlaps the minimap');
  if (!dock.low) return fail('the details card is not along the bottom');
  ok('at a form, the details card and the minimap sit along the bottom');
  await page.keyboard.press('Escape');
  if (await V(() => window.__semanticViewer.state.hover)) return fail('Escape did not clear the focus');
  if (await V(() => !document.querySelector('#details').hidden)) return fail('the details card stayed open after the focus was cleared');
  ok('Escape clears the focus and its details');
  await V(() => window.__semanticViewer.goTo('model'));

  // the light / dark switch
  await page.click('#themeCtl button[data-theme-set="light"]');
  if ((await V(() => document.documentElement.dataset.theme)) !== 'light') return fail('the theme switch did not change to light');
  await page.click('#themeCtl button[data-theme-set="dark"]');
  if ((await V(() => document.documentElement.dataset.theme)) !== 'dark') return fail('the theme switch did not change back to dark');
  ok('switches between dark and light');

  // dopa: the knob, moved by hand, stages nothing; ▶ stages the play as a show
  await page.click('#themeCtl button[data-theme-set="dopa"]');
  if (!(await V(() => document.documentElement.dataset.theme === 'dopa' && getComputedStyle(document.querySelector('#show')).display !== 'none')))
    return fail('the theme switch did not turn on dopa');
  const quiet = await V(() => window.__semanticViewer.fx.count);
  await V(() => { const v = window.__semanticViewer; v.goTo('text', { ms: 1 }); v.scrub('text', 'chunks', 1); v.release(); });
  await still();
  await V(() => { const v = window.__semanticViewer; v.scrub('chunks', 'model', 1); v.release(); });
  await still();
  if (JSON.stringify(await V(() => window.__semanticViewer.fx.count)) !== JSON.stringify(quiet) || await V(() => document.querySelectorAll('#show .dp-band, #show .dp-pop').length))
    return fail('in dopa, moving the knob by hand staged the show');
  ok('in dopa, moving the knob by hand stages nothing');
  await page.click('#gauge .g-play');
  try {
    await page.waitForFunction(() => { const s = window.__semanticViewer.state; return s.stage === 'model' && !s.moving && !s.playing; }, null, { timeout: 60000 });
  } catch (e) { return fail('in dopa, ▶ did not play to the summary and back: ' + JSON.stringify(await state())); }
  const after = await V(() => window.__semanticViewer.fx.count);
  if (!(after.wrap > quiet.wrap && after.aori > quiet.aori && after.summary > quiet.summary)) return fail('in dopa, ▶ did not stage the show: ' + JSON.stringify(after));
  if (after.aori - quiet.aori !== 1) return fail('the build-up before the summary played again on the way back to the model');
  if (await V(() => document.documentElement.hasAttribute('data-show'))) return fail('the dopa show did not stop when the play did');
  ok('in dopa, ▶ stages the play as a show, the build-up and the summary\'s arrival once, and stops with it');
  const kept = await V(() => { try { return localStorage.getItem('semantic-structure-viewer:theme'); } catch (e) { return null; } });
  if (kept === 'dopa') return fail('dopa was remembered as a reading preference');
  await page.click('#themeCtl button[data-theme-set="dark"]');
  if (await V(() => getComputedStyle(document.querySelector('#show')).display !== 'none' || document.querySelectorAll('#show .dp').length))
    return fail('switching back to dark left the dopa show on screen');
  ok('switches to dopa and back, without remembering it');
  // the dopa show plays even when the system asks for less motion
  const calm = await browser.newPage({ viewport: { width: 1280, height: 800 }, reducedMotion: 'reduce' });
  calm.on('pageerror', e => errors.push(e.message));
  await calm.goto('file://' + path.resolve(file));
  await calm.waitForFunction(() => window.__semanticViewer, null, { timeout: 15000 });
  let shown = true;
  try {
    if (await calm.evaluate(() => window.__semanticViewer.autoplay)) await calm.waitForFunction(() => window.__semanticViewer.state.playing, null, { timeout: 8000 });
    await calm.click('#themeCtl button[data-theme-set="dopa"]');
    if (!(await calm.evaluate(() => window.__semanticViewer.state.playing))) await calm.click('#gauge .g-play');
    await calm.waitForFunction(() => Object.values(window.__semanticViewer.fx.count).some(v => v > 0) && document.documentElement.hasAttribute('data-show'), null, { timeout: 15000 });
  } catch (e) { shown = false; }
  await calm.close();
  if (!shown) return fail('with reduced motion, the dopa show did not play');
  ok('the dopa show plays even when the system asks for less motion');

  // and back down
  await V(() => window.__semanticViewer.goTo('text', { ms: 60 }));
  await still();
  if ((await state()).stage !== 'text') return fail('could not descend to the text');
  ok('descends back to the text');

  // the columns follow the shape of the text: this page's code, with small models of the two shapes in it
  const html = fs.readFileSync(path.resolve(file), 'utf8');
  const embed = v => JSON.stringify(v).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
  const withModel = (model, view) => html
    .replace(/(<script type="application\/json" id="semantic-structure">)[\s\S]*?(<\/script>)/, (m, a, b) => a + embed(model) + b)
    .replace(/(<script type="application\/json" id="semantic-view">)[\s\S]*?(<\/script>)/, (m, a, b) => a + embed(view) + b);
  // one chunk per sentence, [id, sentence, role?], and lines [source, target]
  const shape = (chunks, lines) => {
    let text = '';
    const nodes = chunks.map(([id, label, role]) => {
      const start = Array.from(text).length;
      text += label + '。';
      return { id, label, type: 'note', provenance: 'explicit', ...(role ? { role } : {}),
        sourceSpans: [{ start, end: start + Array.from(label).length, text: label }] };
    });
    const relations = lines.map(([a, b]) => ({ id: `${a}-${b}`, source: a, target: b, type: 'leads to', provenance: 'inferred', sourceSpans: [] }));
    return { version: 'semantic-structure/1', sourceText: text, nodes, relations, metadata: { title: 'shape', language: 'ja' } };
  };
  const branching = shape([['q', '問：空き店舗をどう減らすか'], ['plan', '方針：若い店主を呼ぶ'], ['steps', '手順：家賃を半年補助する'],
    ['issue', '課題：補助のあとも続くか'], ['ruling', '結論：まず三店で試す', 'conclusion']],
    [['q', 'plan'], ['plan', 'steps'], ['steps', 'issue'], ['q', 'ruling']]);
  const gathering = shape([['case', '事件：声の似た動画'], ['claim', '請求：動画の削除'], ['standard', '基準：声も人格の象徴'],
    ['gone', '認定：すでに削除済み'], ['ruling', '結論：請求を棄却', 'conclusion']],
    [['standard', 'claim'], ['claim', 'ruling'], ['gone', 'ruling']]);
  for (const [name, model, view, want, cols] of [
    ['a question branching out', branching, {}, 'start', 'q | plan,ruling | steps | issue'],
    ['a question branching out, with anchor end', branching, { anchor: 'end' }, 'end', 'plan,steps,issue | q | ruling'],
    ['reasons gathering into the conclusion, with a chunk that has no lines', gathering, {}, 'end', 'case | standard | claim,gone | ruling'],
    ['reasons gathering into the conclusion, with anchor start', gathering, { anchor: 'start' }, 'start', 'case,standard,gone | claim,ruling'],
  ]) {
    const p = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    p.on('pageerror', e => errors.push(e.message));
    await p.setContent(withModel(model, { ...view, autoplay: false }));
    await p.waitForFunction(() => window.__semanticViewer, null, { timeout: 15000 });
    const got = { anchor: await p.evaluate(() => window.__semanticViewer.anchor), cols: (await minimapCols(p)).map(c => c.join(',')).join(' | ') };
    await p.close();
    if (got.anchor !== want || got.cols !== cols) return fail(`${name}: expected ${want}, ${cols}; got ${got.anchor}, ${got.cols}`);
  }
  ok('the columns follow the shape of the text: a question branching out runs from the start, reasons gathering into a conclusion from it, and the view options win');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  if (await V(() => document.documentElement.scrollWidth > innerWidth + 1)) return fail('the page scrolls sideways at phone width');
  ok('no sideways scroll at phone width');

  if (errors.length) return fail('console errors: ' + errors.join(' | '));
  ok('no console errors');
  await browser.close();
})();
