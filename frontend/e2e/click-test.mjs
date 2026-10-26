// Real-browser click test for Receipts.
// Start the backend on a COPY of the database first (it creates accounts and posts), e.g.
//   cp backend/receipts.db /tmp/receipts-test.db
//   DATABASE_URL=sqlite:////tmp/receipts-test.db RATE_LIMIT_ENABLED=false venv/bin/python -m uvicorn app.main:app --port 8000
// then `npm run dev` and `npm run test:click`. Set BASE_URL to test another address.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = process.env.BASE_URL || 'http://localhost:3000';
const OUT = new URL('./screenshots/', import.meta.url).pathname;
fs.mkdirSync(OUT, { recursive: true });

const results = [];
const badRequests = [];
const consoleErrors = [];
let step = 0;

const stamp = Date.now().toString().slice(-6);
const user = { email: `ct${stamp}@example.com`, handle: `ct${stamp}`, name: 'Click Tester', pw: 'Testpass123!' };

async function check(name, fn, page) {
  step++;
  try {
    await fn();
    results.push({ step, name, ok: true });
  } catch (e) {
    results.push({ step, name, ok: false, err: String(e.message).split('\n')[0] });
  }
  if (page) await page.screenshot({ path: `${OUT}${String(step).padStart(2, '0')}-${name.replace(/\W+/g, '_')}.png`, fullPage: true }).catch(() => {});
}

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: BASE });
const page = await ctx.newPage();
page.on('response', r => { if (r.status() >= 400 && !r.url().includes('_next')) badRequests.push(`${r.status()} ${r.request().method()} ${r.url().replace(BASE, '')}`); });
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 200)); });
page.on('pageerror', e => consoleErrors.push('PAGEERROR ' + e.message.slice(0, 200)));

const expectVisible = async (loc, t = 8000) => { await loc.first().waitFor({ state: 'visible', timeout: t }); };

// --- Logged out browsing
await check('home loads', async () => { await page.goto(BASE); await expectVisible(page.getByText('Latest Receipts')); }, page);
for (const [label, path] of [['Trending', '/trending'], ['Topics', '/topics'], ['Newsrooms', '/newsroom']]) {
  await check(`nav ${label}`, async () => {
    await page.getByRole('navigation').getByRole('link', { name: label, exact: true }).click();
    await page.waitForURL(`**${path}`);
    await page.waitForLoadState('networkidle');
  }, page);
}
await check('search', async () => {
  await page.getByPlaceholder('Search receipts...').first().fill('test');
  await page.keyboard.press('Enter');
  await page.waitForURL('**/search?q=test');
  await page.waitForLoadState('networkidle');
}, page);
await check('create while logged out redirects to login', async () => {
  await page.goto(`${BASE}/create`);
  await page.waitForURL('**/login**', { timeout: 8000 });
}, page);

// --- Sign up
await check('sign up', async () => {
  await page.goto(BASE);
  await page.locator('header').getByRole('link', { name: 'Sign Up' }).click();
  await page.waitForURL('**/register');
  await page.getByPlaceholder('Display Name').fill(user.name);
  await page.getByPlaceholder('Handle (username)').fill(user.handle);
  await page.getByPlaceholder('Email').fill(user.email);
  await page.getByPlaceholder('Password (min 8 chars)').fill(user.pw);
  await page.locator('form').getByRole('button', { name: 'Sign Up' }).click();
  await expectVisible(page.getByRole('link', { name: /New Receipt/ }), 10000);
}, page);

// --- Logout + login
await check('logout', async () => {
  await page.locator('header button').filter({ hasText: /^CT$/ }).click();
  await page.getByRole('button', { name: 'Logout' }).click();
  await expectVisible(page.getByRole('link', { name: 'Login' }));
}, page);
await check('log in', async () => {
  await page.locator('header').getByRole('link', { name: 'Login' }).click();
  await page.waitForURL('**/login');
  await page.locator('input[type=email]').fill(user.email);
  await page.locator('input[type=password]').fill(user.pw);
  await page.locator('form').getByRole('button').last().click();
  await expectVisible(page.getByRole('link', { name: /New Receipt/ }), 10000);
}, page);

// --- Create: empty evidence row should be blocked with a clear message
await check('create with blank evidence row shows a clear error', async () => {
  await page.goto(`${BASE}/create`);
  await page.getByLabel('Claim').fill('Click test claim with a blank evidence row');
  await page.getByRole('button', { name: 'Link', exact: true }).click();
  await page.getByRole('button', { name: 'Post Receipt' }).click();
  await page.waitForTimeout(1500);
  const txt = await page.locator('main form, form:has(textarea)').first().innerText();
  if (/status code/i.test(txt)) throw new Error('Shows raw error: ' + txt.split('\n')[0]);
  if (!/evidence/i.test(txt) || page.url().includes('/receipt/')) throw new Error('No clear evidence error (url ' + page.url().replace(BASE, '') + ')');
}, page);

// --- Create real receipt with link + quote
let receiptUrl = '';
await check('create receipt with link + quote evidence', async () => {
  await page.goto(`${BASE}/create`);
  await page.getByLabel('Claim').fill('The city council voted 5-2 to approve the new bike lanes on Main St.');
  await page.getByLabel(/Why it matters/).fill('Construction starts next spring.');
  await page.getByRole('button', { name: 'Link', exact: true }).click();
  await page.getByPlaceholder('https://...').fill('https://example.com/council-minutes');
  await page.getByRole('button', { name: 'Quote', exact: true }).click();
  await page.getByPlaceholder(/Exact words/).fill('"Motion carries five to two." — Clerk');
  await page.getByPlaceholder(/Where is this from/).fill('https://example.com/clerk-video');
  await page.getByRole('button', { name: 'Politics' }).click();
  await page.getByRole('button', { name: 'Post Receipt' }).click();
  await page.waitForURL('**/receipt/**', { timeout: 10000 });
  receiptUrl = page.url();
  await expectVisible(page.getByText('bike lanes'));
  if (await page.getByRole('link', { name: /Source/ }).count() !== 1) throw new Error('quote source link should appear exactly once');
  if (await page.getByText(/^in /).count()) throw new Error('timestamp is in the future (time zone bug)');
  const q = await page.locator('blockquote').innerText();
  if (q.includes('""')) throw new Error('doubled quote marks: ' + q);
}, page);

// --- Image upload
await check('upload image evidence', async () => {
  await page.goto(`${BASE}/create`);
  await page.getByLabel('Claim').fill('Screenshot proof of the posted notice.');
  await page.getByRole('button', { name: 'Screenshot / photo', exact: true }).click();
  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
  await page.locator('input[type=file]').setInputFiles({ name: 'proof.png', mimeType: 'image/png', buffer: png });
  await expectVisible(page.locator('img[alt="Preview"]'), 10000);
  await page.getByRole('button', { name: 'Post Receipt' }).click();
  await page.waitForURL('**/receipt/**', { timeout: 10000 });
}, page);

// --- Receipt detail actions
await check('support reaction toggles', async () => {
  await page.goto(receiptUrl);
  const btn = page.locator('button:has(svg.lucide-thumbs-up)').first();
  await btn.click();
  await page.waitForTimeout(800);
  if (!(await btn.innerText()).includes('1')) throw new Error('count did not go to 1: ' + (await btn.innerText()));
}, page);
await check('share copies link', async () => {
  await page.locator('button:has(svg.lucide-share2), button:has(svg.lucide-share-2)').first().click();
  await expectVisible(page.getByText('Copied!'), 3000);
}, page);
await check('report modal opens and submits', async () => {
  await page.locator('button:has(svg.lucide-flag)').first().click();
  await page.waitForTimeout(400);
  const modal = page.locator('.fixed').last();
  await modal.locator('button').filter({ hasText: /spam|misinfo|harass|other/i }).first().click();
  await modal.getByRole('button', { name: /submit|report/i }).last().click();
  await expectVisible(page.getByText(/thank|submitted|received/i), 5000);
  await page.getByRole('button', { name: 'Close' }).click().catch(() => {});
}, page);
await check('counter-receipt (fork)', async () => {
  await page.goto(receiptUrl);
  await page.getByRole('button', { name: 'Counter with proof' }).click();
  await page.waitForURL('**/create?fork=**');
  await expectVisible(page.getByText('Countering @'));
  await page.getByLabel('Claim').fill('Actually the vote was 4-3 per the official minutes.');
  await page.getByRole('button', { name: 'Link', exact: true }).click();
  await page.getByPlaceholder('https://...').fill('https://example.com/official-minutes');
  await page.getByRole('button', { name: 'Post counter-receipt' }).click();
  await page.waitForURL(u => u.pathname.startsWith('/receipt/') && u.href !== receiptUrl, { timeout: 10000 });
}, page);
await check('counter-receipt shows what it answers', async () => {
  await expectVisible(page.getByText('Responding to:'), 5000);
  await expectVisible(page.getByRole('link', { name: /bike lanes/ }), 5000);
}, page);
await check('original shows the counter-receipt', async () => {
  await page.goto(receiptUrl);
  await page.waitForLoadState('networkidle');
  await expectVisible(page.getByText('4-3'), 5000).catch(() => { throw new Error('Counter-receipts are counted but never listed on the original'); });
}, page);

// --- Feed shows new receipt
await check('new receipt appears in home feed', async () => {
  await page.goto(BASE);
  await expectVisible(page.getByText('bike lanes'), 8000);
}, page);

// --- Profile
await check('profile page + edit bio', async () => {
  await page.goto(`${BASE}/u/${user.handle}`);
  await page.getByRole('button', { name: 'Edit' }).click();
  await page.getByPlaceholder('Tell us about yourself...').fill('I check facts.');
  await page.getByRole('button', { name: 'Save Changes' }).click();
  await expectVisible(page.getByText('I check facts.'), 5000);
}, page);
await check('profile lists my receipts', async () => {
  await page.reload();
  await expectVisible(page.getByText('bike lanes'), 8000);
}, page);

// --- Notifications + topics detail
await check('topic page lists the tagged receipt', async () => {
  await page.goto(`${BASE}/topics/politics`);
  await expectVisible(page.getByText('bike lanes'), 8000);
}, page);
await check('iPhone Home Screen icon and app settings', async () => {
  const r = await page.request.get(`${BASE}/apple-icon`);
  if (r.status() !== 200 || !(r.headers()['content-type'] || '').includes('image/png')) throw new Error('apple-icon status ' + r.status());
  await page.goto(BASE);
  if (await page.locator('link[rel="apple-touch-icon"]').count() !== 1) throw new Error('no apple-touch-icon link');
  const t = await page.locator('meta[name="apple-mobile-web-app-title"]').getAttribute('content');
  if (t !== 'Receipts') throw new Error('Home Screen title is ' + t);
}, null);
await check('logged-out home explains the app', async () => {
  const c = await browser.newContext();
  const p2 = await c.newPage();
  await p2.goto(BASE);
  await expectVisible(p2.getByText('Claims with proof.'));
  await c.close();
}, null);
await check('newsroom page opens from the directory', async () => {
  await page.goto(`${BASE}/newsroom`);
  await page.waitForLoadState('networkidle');
  const card = page.locator('a[href^="/newsroom/"]').filter({ hasNotText: /dashboard|drafts|settings|team|analytics/i }).first();
  if (await card.count() === 0) throw new Error('No newsroom in the directory to open');
  await card.click();
  await page.waitForURL(/\/newsroom\/[^/]+$/);
  await page.waitForLoadState('networkidle');
  if (await page.getByText(/not found/i).count()) throw new Error('Newsroom page says not found');
}, page);
await check('notifications page', async () => { await page.goto(`${BASE}/notifications`); await page.waitForLoadState('networkidle'); }, page);
await check('open first topic', async () => {
  await page.goto(`${BASE}/topics`);
  await page.waitForLoadState('networkidle');
  const n = await page.locator('a[href^="/topics/"]').count();
  if (n === 0) throw new Error('Topics page is blank: no topics and no empty-state message');
  await page.locator('a[href^="/topics/"]').first().click();
  await page.waitForURL('**/topics/**');
  await page.waitForLoadState('networkidle');
}, page);

// --- Phone size
const phone = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
const mp = await phone.newPage();
mp.on('pageerror', e => consoleErrors.push('PHONE PAGEERROR ' + e.message.slice(0, 200)));
await check('phone: home + menu', async () => {
  await mp.goto(BASE);
  await expectVisible(mp.getByText('Latest Receipts'));
  await mp.locator('header button.md\\:hidden').click();
  await expectVisible(mp.getByRole('link', { name: 'Trending' }));
  const w = await mp.evaluate(() => document.documentElement.scrollWidth);
  if (w > 392) throw new Error('page scrolls sideways, width ' + w);
}, mp);
await check('phone: receipt detail fits', async () => {
  await mp.goto(receiptUrl);
  await mp.waitForLoadState('networkidle');
  await expectVisible(mp.getByText('bike lanes'));
  const w = await mp.evaluate(() => document.documentElement.scrollWidth);
  if (w > 392) throw new Error('page scrolls sideways, width ' + w);
}, mp);

await check('no crash errors in the browser', async () => {
  const bad = consoleErrors.filter(e => /PAGEERROR|cannot be a descendant/.test(e));
  if (bad.length) throw new Error(bad[0]);
}, null);

await browser.close();
process.exitCode = results.every(r => r.ok) ? 0 : 1;

const passed = results.filter(r => r.ok).length;
console.log(`\n${passed}/${results.length} passed\n`);
for (const r of results) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${String(r.step).padStart(2)} ${r.name}${r.ok ? '' : '  -> ' + r.err}`);
console.log('\nFailed requests:'); [...new Set(badRequests)].forEach(x => console.log('  ' + x));
console.log('\nConsole errors:'); [...new Set(consoleErrors)].slice(0, 25).forEach(x => console.log('  ' + x));
