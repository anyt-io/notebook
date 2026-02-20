import { useCallback, useEffect, useRef, useState } from "react";
import ControlPanel from "./components/ControlPanel";
import EditorPanel from "./components/EditorPanel";
import type { PreviewPanelHandle } from "./components/PreviewPanel";
import PreviewPanel from "./components/PreviewPanel";
import {
	DEFAULT_COVER_FONT_SIZE,
	DEFAULT_FONT_SIZE,
	DEFAULT_LETTER_SPACING,
	DEFAULT_LINE_HEIGHT,
} from "./constants";
import { getDefaultMarkdown } from "./defaultContent";
import { I18nProvider, useI18n } from "./i18n";
import { defaultTemplate } from "./templates";
import type { CoverConfig, StyleOverrides, Template } from "./types";
import { splitContentIntoPages } from "./utils/pageSplitter";

type MobileTab = "editor" | "preview" | "settings";

const DEFAULT_OVERRIDES: StyleOverrides = {
	fontSize: DEFAULT_FONT_SIZE,
	lineHeight: DEFAULT_LINE_HEIGHT,
	letterSpacing: DEFAULT_LETTER_SPACING,
};

const DEFAULT_COVER: CoverConfig = {
	enabled: false,
	title: "",
	imageDataUrl: null,
	fontSize: DEFAULT_COVER_FONT_SIZE,
};

function AppContent() {
	const { t, locale, setLocale } = useI18n();
	const [markdown, setMarkdown] = useState(() => getDefaultMarkdown(locale));
	const [template, setTemplate] = useState<Template>(defaultTemplate);
	const [styleOverrides, setStyleOverrides] = useState<StyleOverrides>(DEFAULT_OVERRIDES);
	const [watermark, setWatermark] = useState("AnyT");
	const [coverConfig, setCoverConfig] = useState<CoverConfig>(DEFAULT_COVER);
	const [autoPageBreak, setAutoPageBreak] = useState(true);
	const [pages, setPages] = useState<string[]>([""]);
	const [mobileTab, setMobileTab] = useState<MobileTab>("preview");
	const previewRef = useRef<PreviewPanelHandle>(null);
	const prevLocaleRef = useRef(locale);

	const recomputePages = useCallback(() => {
		const result = splitContentIntoPages(markdown, template, styleOverrides, autoPageBreak);
		setPages(result);
	}, [markdown, template, styleOverrides, autoPageBreak]);

	useEffect(() => {
		const timer = setTimeout(recomputePages, 200);
		return () => clearTimeout(timer);
	}, [recomputePages]);

	// Update default content when locale changes (only if content is still the default)
	useEffect(() => {
		if (prevLocaleRef.current !== locale) {
			const prevDefault = getDefaultMarkdown(prevLocaleRef.current);
			if (markdown === prevDefault) {
				setMarkdown(getDefaultMarkdown(locale));
			}
			prevLocaleRef.current = locale;
		}
	}, [locale, markdown]);

	const handleTemplateSelect = (t: Template) => {
		setTemplate(t);
		setStyleOverrides((prev) => ({
			...prev,
			cardBg: undefined,
			textColor: undefined,
			accentColor: undefined,
		}));
	};

	return (
		<div className="app">
			<div className={`mobile-panel-wrapper${mobileTab === "editor" ? " mobile-active" : ""}`}>
				<EditorPanel markdown={markdown} totalPages={pages.length} onChange={setMarkdown} />
			</div>
			<div className={`mobile-panel-wrapper${mobileTab === "preview" ? " mobile-active" : ""}`}>
				<PreviewPanel
					ref={previewRef}
					pages={pages}
					template={template}
					styleOverrides={styleOverrides}
					watermark={watermark}
					coverConfig={coverConfig}
				/>
			</div>
			<div className={`mobile-panel-wrapper${mobileTab === "settings" ? " mobile-active" : ""}`}>
				<ControlPanel
					selectedTemplate={template}
					styleOverrides={styleOverrides}
					watermark={watermark}
					coverConfig={coverConfig}
					autoPageBreak={autoPageBreak}
					onSelectTemplate={handleTemplateSelect}
					onStyleChange={setStyleOverrides}
					onWatermarkChange={setWatermark}
					onCoverChange={setCoverConfig}
					onAutoPageBreakChange={setAutoPageBreak}
					onDownloadAll={() => previewRef.current?.downloadAll()}
				/>
			</div>
			<nav className="mobile-tab-bar">
				<button
					type="button"
					className={`mobile-tab-btn${mobileTab === "editor" ? " mobile-tab-btn--active" : ""}`}
					onClick={() => setMobileTab("editor")}
				>
					<span className="mobile-tab-icon">&#9998;</span>
					<span className="mobile-tab-label">{t("tab.editor")}</span>
				</button>
				<button
					type="button"
					className={`mobile-tab-btn${mobileTab === "preview" ? " mobile-tab-btn--active" : ""}`}
					onClick={() => setMobileTab("preview")}
				>
					<span className="mobile-tab-icon">&#128065;</span>
					<span className="mobile-tab-label">{t("tab.preview")}</span>
				</button>
				<button
					type="button"
					className={`mobile-tab-btn${mobileTab === "settings" ? " mobile-tab-btn--active" : ""}`}
					onClick={() => setMobileTab("settings")}
				>
					<span className="mobile-tab-icon">&#9881;</span>
					<span className="mobile-tab-label">{t("tab.settings")}</span>
				</button>
			</nav>
			<button
				type="button"
				className="lang-toggle"
				onClick={() => setLocale(locale === "zh" ? "en" : "zh")}
			>
				{locale === "zh" ? "EN" : "\u4E2D"}
			</button>
		</div>
	);
}

export default function App() {
	return (
		<I18nProvider>
			<AppContent />
		</I18nProvider>
	);
}
