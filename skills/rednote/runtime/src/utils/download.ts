import { saveAs } from "file-saver";
import JSZip from "jszip";
import { domToBlob } from "modern-screenshot";
import { CARD_HEIGHT, CARD_WIDTH } from "../constants";

function blobToDataUrl(blob: Blob): Promise<string> {
	return new Promise<string>((resolve) => {
		const reader = new FileReader();
		reader.onloadend = () => resolve(reader.result as string);
		reader.readAsDataURL(blob);
	});
}

/**
 * Fetch an image URL and return it as a data URL.
 * Tries direct fetch, Image+canvas, then CORS proxy as fallback.
 */
async function fetchImageAsDataUrl(url: string): Promise<string | null> {
	// Approach 1: direct fetch with CORS
	try {
		const res = await fetch(url, { mode: "cors" });
		if (res.ok) {
			return await blobToDataUrl(await res.blob());
		}
	} catch {
		// CORS or network error, try fallback
	}

	// Approach 2: load via Image with crossOrigin, draw to canvas
	try {
		return await new Promise<string>((resolve, reject) => {
			const img = new Image();
			img.crossOrigin = "anonymous";
			img.onload = () => {
				const canvas = document.createElement("canvas");
				canvas.width = img.naturalWidth;
				canvas.height = img.naturalHeight;
				const ctx = canvas.getContext("2d")!;
				ctx.drawImage(img, 0, 0);
				try {
					resolve(canvas.toDataURL("image/png"));
				} catch {
					reject(new Error("Canvas tainted"));
				}
			};
			img.onerror = () => reject(new Error("Image load failed"));
			img.src = url;
		});
	} catch {
		// Canvas tainted or load failed
	}

	return null;
}

/**
 * Convert all image URLs in an HTML string to embedded data URLs.
 * This must be done BEFORE rendering the Card so the screenshot can capture them.
 */
export async function convertImageUrlsInHtml(html: string): Promise<string> {
	const tempDiv = document.createElement("div");
	tempDiv.innerHTML = html;
	const images = tempDiv.querySelectorAll("img");

	await Promise.all(
		Array.from(images).map(async (img) => {
			const src = img.getAttribute("src");
			if (!src || src.startsWith("data:") || src.startsWith("blob:")) return;
			const dataUrl = await fetchImageAsDataUrl(src);
			if (dataUrl) {
				img.setAttribute("src", dataUrl);
			}
		}),
	);

	return tempDiv.innerHTML;
}

async function renderCardToBlob(cardElement: HTMLElement): Promise<Blob> {
	const blob = await domToBlob(cardElement, {
		width: CARD_WIDTH,
		height: CARD_HEIGHT,
		scale: 2,
		backgroundColor: null,
		fetchFn: async (url) => {
			if (url.startsWith("data:")) return url;
			const dataUrl = await fetchImageAsDataUrl(url);
			return dataUrl || false;
		},
	});
	if (!blob) {
		throw new Error("Failed to render card to blob");
	}
	return blob;
}

export async function downloadSingleCard(cardElement: HTMLElement, pageNum: number): Promise<void> {
	const blob = await renderCardToBlob(cardElement);
	saveAs(blob, `xhs-card-${pageNum}.png`);
}

export async function downloadAllCards(
	renderCard: (pageIndex: number) => Promise<HTMLElement>,
	totalPages: number,
): Promise<void> {
	const zip = new JSZip();

	for (let i = 0; i < totalPages; i++) {
		const cardElement = await renderCard(i);
		const blob = await renderCardToBlob(cardElement);
		zip.file(`xhs-card-${i + 1}.png`, blob);
	}

	const content = await zip.generateAsync({ type: "blob" });
	saveAs(content, "xhs-cards.zip");
}
