import type { ReactElement } from "react";
import { forwardRef, useCallback, useEffect, useImperativeHandle, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { CARD_HEIGHT, CARD_WIDTH } from "../constants";
import { useI18n } from "../i18n";
import type { CoverConfig, StyleOverrides, Template } from "../types";
import { convertImageUrlsInHtml, downloadAllCards, downloadSingleCard } from "../utils/download";
import Card from "./Card";

interface PreviewPanelProps {
	pages: string[];
	template: Template;
	styleOverrides: StyleOverrides;
	watermark: string;
	coverConfig: CoverConfig;
}

export interface PreviewPanelHandle {
	downloadAll: () => Promise<void>;
	downloading: boolean;
}

const DEFAULT_SCALE = 0.42;
const PREVIEW_PADDING = 32;

const PreviewPanel = forwardRef<PreviewPanelHandle, PreviewPanelProps>(
	({ pages, template, styleOverrides, watermark, coverConfig }, ref) => {
		const { t } = useI18n();
		const [currentPage, setCurrentPage] = useState(0);
		const [downloading, setDownloading] = useState(false);
		const [previewScale, setPreviewScale] = useState(DEFAULT_SCALE);
		const renderRef = useRef<HTMLDivElement>(null);
		const previewAreaRef = useRef<HTMLDivElement>(null);

		useEffect(() => {
			const el = previewAreaRef.current;
			if (!el) return;

			const updateScale = () => {
				const availableWidth = el.clientWidth - PREVIEW_PADDING;
				const availableHeight = el.clientHeight - 120;
				const scaleW = availableWidth / CARD_WIDTH;
				const scaleH = availableHeight > 0 ? availableHeight / CARD_HEIGHT : scaleW;
				setPreviewScale(Math.min(scaleW, scaleH, 1));
			};

			const observer = new ResizeObserver(updateScale);
			observer.observe(el);
			updateScale();

			return () => observer.disconnect();
		}, []);

		const hasCover = coverConfig.enabled;
		const totalPages = (hasCover ? 1 : 0) + pages.length;
		const safePage = Math.min(currentPage, totalPages - 1);

		const renderFullSizeCard = useCallback(
			async (displayIndex: number): Promise<HTMLElement> => {
				const container = renderRef.current!;
				container.style.display = "block";

				const isCoverPage = hasCover && displayIndex === 0;
				const contentIndex = hasCover ? displayIndex - 1 : displayIndex;

				let cardElement: ReactElement;

				if (isCoverPage) {
					cardElement = (
						<Card
							content=""
							template={template}
							styleOverrides={styleOverrides}
							pageNum={1}
							totalPages={totalPages}
							watermark={watermark}
							coverConfig={coverConfig}
						/>
					);
				} else {
					const processedContent = await convertImageUrlsInHtml(pages[contentIndex]);
					cardElement = (
						<Card
							content={processedContent}
							template={template}
							styleOverrides={styleOverrides}
							pageNum={displayIndex + 1}
							totalPages={totalPages}
							watermark={watermark}
						/>
					);
				}

				const cardEl = await new Promise<HTMLElement>((resolve) => {
					const wrapper = document.createElement("div");
					container.innerHTML = "";
					container.appendChild(wrapper);

					const root = createRoot(wrapper);
					root.render(cardElement);

					requestAnimationFrame(() => {
						requestAnimationFrame(() => {
							resolve(container.querySelector(".card") as HTMLElement);
						});
					});
				});

				const images = Array.from(cardEl.querySelectorAll("img"));
				await Promise.all(
					images
						.filter((img) => !img.complete)
						.map(
							(img) =>
								new Promise<void>((resolve) => {
									img.onload = () => resolve();
									img.onerror = () => resolve();
								}),
						),
				);

				return cardEl;
			},
			[pages, template, styleOverrides, watermark, hasCover, coverConfig, totalPages],
		);

		const handleDownloadCurrent = async () => {
			if (downloading) return;
			setDownloading(true);
			try {
				const cardEl = await renderFullSizeCard(safePage);
				await downloadSingleCard(cardEl, safePage + 1);
			} finally {
				if (renderRef.current) renderRef.current.style.display = "none";
				setDownloading(false);
			}
		};

		const handleDownloadAll = async () => {
			if (downloading) return;
			setDownloading(true);
			try {
				await downloadAllCards(async (i) => {
					return renderFullSizeCard(i);
				}, totalPages);
			} catch {
				for (let i = 0; i < totalPages; i++) {
					const el = await renderFullSizeCard(i);
					await downloadSingleCard(el, i + 1);
				}
			} finally {
				if (renderRef.current) renderRef.current.style.display = "none";
				setDownloading(false);
			}
		};

		useImperativeHandle(ref, () => ({
			downloadAll: handleDownloadAll,
			downloading,
		}));

		const goPrev = () => setCurrentPage((p) => Math.max(0, p - 1));
		const goNext = () => setCurrentPage((p) => Math.min(totalPages - 1, p + 1));

		const isCoverPreview = hasCover && safePage === 0;
		const contentPageIndex = hasCover ? safePage - 1 : safePage;

		return (
			<main className="panel panel-center">
				<div className="preview-header">
					<span className="preview-title">{t("preview.title")}</span>
					<span className="preview-count">{t("preview.pageCount", totalPages)}</span>
				</div>

				<div className="preview-area" ref={previewAreaRef}>
					<div className="page-info">
						<span>{t("preview.pageInfo", safePage + 1, totalPages)}</span>
						<button
							type="button"
							className="btn btn-sm"
							onClick={handleDownloadCurrent}
							disabled={downloading}
						>
							{downloading ? t("preview.downloading") : t("preview.download")}
						</button>
					</div>

					<div className="preview-carousel">
						<button
							type="button"
							className="preview-nav preview-nav--prev"
							onClick={goPrev}
							disabled={safePage === 0}
							aria-label={t("preview.prevPage")}
						>
							&#8249;
						</button>

						<div
							className="card-viewport"
							style={{
								width: CARD_WIDTH * previewScale,
								height: CARD_HEIGHT * previewScale,
							}}
						>
							{isCoverPreview ? (
								<Card
									content=""
									template={template}
									styleOverrides={styleOverrides}
									pageNum={1}
									totalPages={totalPages}
									watermark={watermark}
									coverConfig={coverConfig}
									scale={previewScale}
								/>
							) : (
								<Card
									content={pages[contentPageIndex] || ""}
									template={template}
									styleOverrides={styleOverrides}
									pageNum={safePage + 1}
									totalPages={totalPages}
									watermark={watermark}
									scale={previewScale}
								/>
							)}
						</div>

						<button
							type="button"
							className="preview-nav preview-nav--next"
							onClick={goNext}
							disabled={safePage >= totalPages - 1}
							aria-label={t("preview.nextPage")}
						>
							&#8250;
						</button>
					</div>

					{totalPages > 1 && (
						<div className="pagination">
							{Array.from({ length: totalPages }, (_, i) => (
								<button
									type="button"
									key={`page-${
										// biome-ignore lint/suspicious/noArrayIndexKey: pages are index-based
										i
									}`}
									className={`dot ${i === safePage ? "dot--active" : ""}`}
									onClick={() => setCurrentPage(i)}
									aria-label={`Page ${i + 1}`}
								/>
							))}
						</div>
					)}
				</div>

				{/* Hidden full-size render container */}
				<div ref={renderRef} className="render-container" style={{ display: "none" }} />
			</main>
		);
	},
);

PreviewPanel.displayName = "PreviewPanel";

export default PreviewPanel;
