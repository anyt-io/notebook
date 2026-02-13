#!/usr/bin/env npx tsx
/**
 * CLI script to generate XHS card images from a markdown file.
 *
 * Usage:
 *   pnpm generate input.md                     # outputs to ./output/
 *   pnpm generate input.md -o ./my-cards       # custom output dir
 *   pnpm generate input.md -t dark             # use "dark" template
 *   pnpm generate input.md --watermark "MyID"  # set watermark
 *   pnpm generate input.md --lang en           # use English UI
 *
 * Prerequisites:
 *   pnpm build                                 # build the app first
 *   pnpm exec playwright install chromium      # install browser
 */

import { createReadStream, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, resolve } from "node:path";
import { chromium } from "playwright";
import { CARD_HEIGHT, CARD_WIDTH } from "../src/constants";
import { TEMPLATE_IDS } from "../src/templates";

// --- CLI args ---
const args = process.argv.slice(2);

function getArg(flags: string[], fallback: string): string {
	for (const flag of flags) {
		const idx = args.indexOf(flag);
		if (idx !== -1 && idx + 1 < args.length) return args[idx + 1];
	}
	return fallback;
}

const inputFile = args.find((a) => !a.startsWith("-"));
if (!inputFile || args.includes("--help") || args.includes("-h")) {
	console.log(`
Usage: pnpm generate <input.md> [options]

Options:
  -o, --output <dir>       Output directory (default: ./output)
  -t, --template <id>      Template: ${TEMPLATE_IDS.join(", ")}
                            (default: apple-notes)
  --watermark <text>       Watermark text (default: AnyT)
  --lang <en|zh>           UI language (default: en)
  -h, --help               Show this help
`);
	process.exit(inputFile ? 0 : 1);
}

const outputDir = resolve(getArg(["-o", "--output"], "./output"));
const templateId = getArg(["-t", "--template"], "apple-notes");
const watermarkText = getArg(["--watermark"], "AnyT");
const lang = getArg(["--lang"], "en");

// --- Validate ---
const mdPath = resolve(inputFile);
if (!existsSync(mdPath)) {
	console.error(`File not found: ${mdPath}`);
	process.exit(1);
}

const distDir = resolve(import.meta.dirname, "..", "dist");
if (!existsSync(resolve(distDir, "index.html"))) {
	console.error("dist/ not found. Run `pnpm build` first.");
	process.exit(1);
}

if (!TEMPLATE_IDS.includes(templateId)) {
	console.error(`Unknown template: ${templateId}`);
	console.error(`Available: ${TEMPLATE_IDS.join(", ")}`);
	process.exit(1);
}

const markdown = readFileSync(mdPath, "utf-8");
mkdirSync(outputDir, { recursive: true });

// --- Helper: serve dist/ over HTTP (ES modules require http://, not file://) ---
const MIME_TYPES: Record<string, string> = {
	".html": "text/html",
	".js": "application/javascript",
	".css": "text/css",
	".json": "application/json",
	".png": "image/png",
	".jpg": "image/jpeg",
	".svg": "image/svg+xml",
	".woff": "font/woff",
	".woff2": "font/woff2",
};

function serveStatic(root: string): Promise<{ url: string; close: () => void }> {
	return new Promise((res) => {
		const server = createServer((req, reply) => {
			const urlPath = req.url === "/" ? "/index.html" : (req.url?.split("?")[0] ?? "/index.html");
			const filePath = resolve(root, `.${urlPath}`);
			if (!existsSync(filePath) || !statSync(filePath).isFile()) {
				// SPA fallback
				const index = resolve(root, "index.html");
				reply.writeHead(200, { "Content-Type": "text/html" });
				createReadStream(index).pipe(reply);
				return;
			}
			const ext = extname(filePath);
			reply.writeHead(200, { "Content-Type": MIME_TYPES[ext] || "application/octet-stream" });
			createReadStream(filePath).pipe(reply);
		});
		server.listen(0, "127.0.0.1", () => {
			const addr = server.address();
			const port = typeof addr === "object" && addr ? addr.port : 0;
			res({ url: `http://127.0.0.1:${port}`, close: () => server.close() });
		});
	});
}

// --- Helper: set a React-controlled input value ---
function setInputScript(selector: string, value: string) {
	return `
    (() => {
      const el = document.querySelector('${selector}');
      if (!el) return;
      const setter = Object.getOwnPropertyDescriptor(
        el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype,
        'value'
      ).set;
      setter.call(el, ${JSON.stringify(value)});
      el.dispatchEvent(new Event('input', { bubbles: true }));
    })();
  `;
}

// --- Main ---
async function main() {
	console.log(`Input:    ${mdPath}`);
	console.log(`Template: ${templateId}`);
	console.log(`Language: ${lang}`);
	console.log(`Output:   ${outputDir}`);
	console.log();

	const server = await serveStatic(distDir);
	console.log(`Dev server: ${server.url}\n`);

	const browser = await chromium.launch();
	const page = await browser.newPage({ viewport: { width: 1920, height: 1200 } });

	// Set locale in localStorage before loading page
	await page.addInitScript((locale: string) => {
		localStorage.setItem("locale", locale);
	}, lang);

	await page.goto(server.url);
	await page.waitForSelector(".markdown-input");

	// 1. Set markdown content
	await page.evaluate(setInputScript(".markdown-input", markdown));
	await page.waitForTimeout(400);

	// 2. Select template by clicking the matching template card
	const templateCards = page.locator(".template-card");
	const count = await templateCards.count();
	for (let i = 0; i < count; i++) {
		const card = templateCards.nth(i);
		const isActive = await card.evaluate((el) => el.classList.contains("template-card--active"));
		// Templates are rendered in order matching TEMPLATE_IDS
		if (TEMPLATE_IDS[i] === templateId && !isActive) {
			await card.click();
			await page.waitForTimeout(300);
			break;
		}
	}

	// 3. Set watermark — switch to cover tab first, then find the input
	const coverTab = page.locator(".style-tab").nth(1);
	await coverTab.click();
	await page.waitForTimeout(100);

	const watermarkInput = page.locator(".style-controls .text-input").last();
	if ((await watermarkInput.count()) > 0) {
		await watermarkInput.evaluate((el: HTMLInputElement, val: string) => {
			const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")!.set!;
			setter.call(el, val);
			el.dispatchEvent(new Event("input", { bubbles: true }));
		}, watermarkText);
	}
	await page.waitForTimeout(300);

	// Switch back to basic tab
	const basicTab = page.locator(".style-tab").nth(0);
	await basicTab.click();
	await page.waitForTimeout(100);

	// 4. Read total page count
	const totalText = await page.locator(".preview-count").textContent();
	const totalMatch = totalText?.match(/(\d+)/);
	const totalPages = totalMatch ? Number.parseInt(totalMatch[1]) : 1;

	console.log(`Generating ${totalPages} card(s)...\n`);

	// 5. For each page, navigate and screenshot the full-size card
	for (let i = 0; i < totalPages; i++) {
		// Click pagination dot
		const dots = page.locator(".dot");
		if ((await dots.count()) > i) {
			await dots.nth(i).click();
			await page.waitForTimeout(300);
		}

		// Clone the card at full size for screenshot
		await page.evaluate(
			({ w, h }) => {
				const wrapper = document.querySelector(".card-viewport");
				if (!wrapper) return;
				const inner = wrapper.firstElementChild as HTMLElement;
				if (!inner) return;

				const clone = inner.cloneNode(true) as HTMLElement;
				clone.style.transform = "none";
				clone.style.width = `${w}px`;
				clone.style.height = `${h}px`;

				const card = clone.querySelector(".card") as HTMLElement;
				if (card) {
					card.style.width = `${w}px`;
					card.style.height = `${h}px`;
				}

				const container = document.createElement("div");
				container.id = "__ss__";
				container.style.cssText = `position:fixed;left:0;top:0;z-index:99999;width:${w}px;height:${h}px;overflow:hidden;`;
				container.appendChild(clone);
				document.body.appendChild(container);
			},
			{ w: CARD_WIDTH, h: CARD_HEIGHT },
		);

		await page.waitForTimeout(200);

		const target = page.locator("#__ss__");
		if ((await target.count()) > 0) {
			const filename = `xhs-card-${i + 1}.png`;
			await target.screenshot({
				path: resolve(outputDir, filename),
				type: "png",
			});
			console.log(`  Saved: ${filename}`);
		}

		// Cleanup
		await page.evaluate(() => document.getElementById("__ss__")?.remove());
	}

	await browser.close();
	server.close();
	console.log(`\nDone! ${totalPages} image(s) saved to ${outputDir}`);
}

main().catch((err) => {
	console.error("Error:", err);
	process.exit(1);
});
