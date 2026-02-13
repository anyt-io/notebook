import { CONTENT_WIDTH, MAX_CONTENT_HEIGHT } from "../constants";
import type { StyleOverrides, Template } from "../types";
import { parseMarkdown, splitByPageBreaks } from "./markdown";

function buildMeasurerStyles(template: Template, overrides: StyleOverrides): string {
	const fontFamily = template.styles.fontFamily;
	const fontSize = overrides.fontSize;
	const lineHeight = overrides.lineHeight;
	const letterSpacing = overrides.letterSpacing;

	return [
		`position:fixed`,
		`left:-9999px`,
		`top:0`,
		`width:${CONTENT_WIDTH}px`,
		`font-family:${fontFamily}`,
		`font-size:${fontSize}px`,
		`line-height:${lineHeight}`,
		`letter-spacing:${letterSpacing}px`,
		`color:#333`,
		`overflow:hidden`,
	].join(";");
}

function measureAndSplit(html: string, template: Template, overrides: StyleOverrides): string[] {
	const container = document.createElement("div");
	container.setAttribute("style", buildMeasurerStyles(template, overrides));
	container.className = "card-body";
	container.innerHTML = html;
	document.body.appendChild(container);

	const elements = Array.from(container.children) as HTMLElement[];

	if (elements.length === 0) {
		document.body.removeChild(container);
		return html.trim() ? [html] : [];
	}

	const pages: string[] = [];
	let currentElements: string[] = [];
	let currentHeight = 0;

	for (const el of elements) {
		const style = window.getComputedStyle(el);
		const marginTop = Number.parseFloat(style.marginTop) || 0;
		const marginBottom = Number.parseFloat(style.marginBottom) || 0;
		const elHeight = el.offsetHeight + marginTop + marginBottom;

		if (currentHeight + elHeight > MAX_CONTENT_HEIGHT && currentElements.length > 0) {
			pages.push(currentElements.join(""));
			currentElements = [el.outerHTML];
			currentHeight = elHeight;
		} else {
			currentElements.push(el.outerHTML);
			currentHeight += elHeight;
		}
	}

	if (currentElements.length > 0) {
		pages.push(currentElements.join(""));
	}

	document.body.removeChild(container);
	return pages;
}

export function splitContentIntoPages(
	markdown: string,
	template: Template,
	overrides: StyleOverrides,
): string[] {
	const sections = splitByPageBreaks(markdown);
	const allPages: string[] = [];

	for (const section of sections) {
		const html = parseMarkdown(section);
		const sectionPages = measureAndSplit(html, template, overrides);
		allPages.push(...sectionPages);
	}

	return allPages.length > 0 ? allPages : ["<p></p>"];
}
