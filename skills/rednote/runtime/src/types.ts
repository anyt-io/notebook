export interface Template {
	id: string;
	name: string;
	description: string;
	styles: TemplateStyles;
	chrome: "apple-notes" | "accent-line" | "border" | "none";
	contentWrapper?: string;
}

export interface TemplateStyles {
	cardBg: string;
	textColor: string;
	accentColor: string;
	headingColor: string;
	fontFamily: string;
}

/** Color overrides are optional (fall back to template), typography overrides are required. */
export interface StyleOverrides {
	cardBg?: string;
	textColor?: string;
	accentColor?: string;
	fontSize: number;
	lineHeight: number;
	letterSpacing: number;
}

export interface CardPage {
	html: string;
	pageNum: number;
}

export interface CoverConfig {
	enabled: boolean;
	title: string;
	imageDataUrl: string | null;
	fontSize: number;
}

export interface AppState {
	markdown: string;
	pages: CardPage[];
	currentPage: number;
	selectedTemplate: Template;
	styleOverrides: StyleOverrides;
	watermark: string;
}
