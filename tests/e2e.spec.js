const { chromium } = require('playwright');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8080';

describe('Landing Page E2E Tests', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await chromium.launch();
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  test('homepage loads successfully', async () => {
    const response = await page.goto(BASE_URL);
    expect(response.status()).toBe(200);
  });

  test('page has correct title', async () => {
    await page.goto(BASE_URL);
    const title = await page.title();
    expect(title).toContain('Project');
  });

  test('SEO meta tags are present', async () => {
    await page.goto(BASE_URL);
    
    // Check meta description
    const description = await page.$eval('meta[name="description"]', el => el.content);
    expect(description).toBeTruthy();
    
    // Check meta keywords
    const keywords = await page.$eval('meta[name="keywords"]', el => el.content);
    expect(keywords).toContain('project');
  });

  test('security headers are present', async () => {
    await page.goto(BASE_URL);
    
    const csp = await page.$eval('meta[http-equiv="Content-Security-Policy"]', el => el.content);
    expect(csp).toContain('default-src');
    
    const xcto = await page.$eval('meta[http-equiv="X-Content-Type-Options"]', el => el.content);
    expect(xcto).toBe('nosniff');
  });

  test('main heading is visible', async () => {
    await page.goto(BASE_URL);
    const heading = await page.$eval('h1', el => el.textContent);
    expect(heading).toContain('Welcome');
  });

  test('no console errors', async () => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    
    expect(errors.length).toBe(0);
  });

  test('page is responsive', async () => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL);
    
    const h1 = await page.$('h1');
    expect(h1).toBeTruthy();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(BASE_URL);
    
    const h1Desktop = await page.$('h1');
    expect(h1Desktop).toBeTruthy();
  });

  test('links are valid', async () => {
    await page.goto(BASE_URL);
    const links = await page.$$eval('a', anchors => anchors.map(a => a.href));
    
    // Check all links are valid (not empty and proper format)
    links.forEach(link => {
      if (link) expect(link).toMatch(/^(http|mailto|#)/);
    });
  });
});

// Docker health check test
describe('Docker Health Check', () => {
  test('health endpoint returns OK', async () => {
    const response = await fetch(`${BASE_URL}/health`);
    const text = await response.text();
    expect(text).toBe('OK');
  });
});