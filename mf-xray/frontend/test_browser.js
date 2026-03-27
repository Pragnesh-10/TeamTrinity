import puppeteer from 'puppeteer';
import { spawn } from 'child_process';

(async () => {
  console.log("Starting vite server...");
  const server = spawn('npm', ['run', 'dev', '--', '--port', '5173'], { stdio: 'pipe' });
  
  await new Promise(r => setTimeout(r, 3000)); // wait for vite to start

  console.log("Launching browser...");
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));

  console.log("Navigating to http://localhost:5173...");
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });

  await new Promise(r => setTimeout(r, 1000));
  await browser.close();
  server.kill();
  console.log("Done.");
})();
