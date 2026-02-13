import { type Locale, registerTemplateTranslations } from "./i18n";
import type { Template, TemplateStyles } from "./types";

interface TemplateDefinition {
	id: string;
	styles: TemplateStyles;
	chrome: Template["chrome"];
	contentWrapper?: string;
	i18n: Record<Locale, { name: string; desc: string }>;
}

const templateDefs: TemplateDefinition[] = [
	{
		id: "apple-notes",
		styles: {
			cardBg: "#ffffff",
			textColor: "#1d1d1f",
			accentColor: "#FF9500",
			headingColor: "#1d1d1f",
			fontFamily: '-apple-system, "PingFang SC", "Helvetica Neue", sans-serif',
		},
		chrome: "apple-notes",
		i18n: {
			en: {
				name: "Apple Notes",
				desc: "Pixel-perfect iOS 2026 recreation, just like using the real thing",
			},
			zh: {
				name: "\u82F9\u679C\u5907\u5FD8\u5F55",
				desc: "2026\u7248 iOS \u6781\u81F4\u8FD8\u539F\uFF0C\u6BCF\u4E00\u6B21\u8BB0\u5F55\u90FD\u50CF\u5728\u7528\u771F\u673A",
			},
		},
	},
	{
		id: "swiss",
		styles: {
			cardBg: "#fafafa",
			textColor: "#222222",
			accentColor: "#e63946",
			headingColor: "#111111",
			fontFamily: '"Helvetica Neue", Arial, "PingFang SC", sans-serif',
		},
		chrome: "accent-line",
		i18n: {
			en: {
				name: "Zurich Studio",
				desc: "Swiss graphic design style, ultimate order and sophistication",
			},
			zh: {
				name: "\u82CF\u9ECE\u4E16\u5DE5\u4F5C\u5BA4",
				desc: "\u745E\u58EB\u5E73\u9762\u8BBE\u8BA1\u98CE\u683C\uFF0C\u6781\u81F4\u7684\u79E9\u5E8F\u611F\u4E0E\u9AD8\u7EA7\u611F",
			},
		},
	},
	{
		id: "magazine",
		styles: {
			cardBg: "#f5f1eb",
			textColor: "#2d2d2d",
			accentColor: "#8b4513",
			headingColor: "#1a1a1a",
			fontFamily: 'Georgia, "Noto Serif SC", "Songti SC", serif',
		},
		chrome: "border",
		i18n: {
			en: {
				name: "Minimalist Magazine",
				desc: "Modern editorial typography, giving text a print-quality feel",
			},
			zh: {
				name: "\u6781\u7B80\u6742\u5FD7",
				desc: "\u73B0\u4EE3\u793E\u8BBA\u6392\u7248\u7F8E\u5B66\uFF0C\u8BA9\u6587\u5B57\u62E5\u6709\u7EB8\u8D28\u51FA\u7248\u7269\u7684\u8D28\u611F",
			},
		},
	},
	{
		id: "aurora",
		styles: {
			cardBg: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
			textColor: "#333333",
			accentColor: "#667eea",
			headingColor: "#1a1a2e",
			fontFamily: '-apple-system, "PingFang SC", sans-serif',
		},
		chrome: "none",
		contentWrapper: "aurora-inner",
		i18n: {
			en: {
				name: "Aurora",
				desc: "2026 fluid light aesthetics, dreamy and ethereal experience",
			},
			zh: {
				name: "\u5F25\u6563\u6781\u5149",
				desc: "2026 \u6D41\u4F53\u5149\u5F71\u7F8E\u5B66\uFF0C\u8425\u9020\u68A6\u5E7B\u3001\u7A7A\u7075\u7684\u611F\u5B98\u4F53\u9A8C",
			},
		},
	},
	{
		id: "dark",
		styles: {
			cardBg: "#1a1a2e",
			textColor: "#d4d4d8",
			accentColor: "#64ffda",
			headingColor: "#ffffff",
			fontFamily: '-apple-system, "PingFang SC", sans-serif',
		},
		chrome: "accent-line",
		i18n: {
			en: {
				name: "Dark Thoughts",
				desc: "Rational energy at night, immersive deep thinking space",
			},
			zh: {
				name: "\u6697\u591C\u6DF1\u601D",
				desc: "\u6DF1\u591C\u91CC\u7684\u7406\u6027\u80FD\u91CF\uFF0C\u6C89\u6D78\u5F0F\u6DF1\u5EA6\u601D\u8003\u7A7A\u95F4",
			},
		},
	},
	{
		id: "corporate",
		styles: {
			cardBg: "#ffffff",
			textColor: "#374151",
			accentColor: "#2563eb",
			headingColor: "#111827",
			fontFamily: '-apple-system, "PingFang SC", "Helvetica Neue", sans-serif',
		},
		chrome: "accent-line",
		i18n: {
			en: {
				name: "Corporate Docs",
				desc: "Professional technical documentation, authoritative presentation",
			},
			zh: {
				name: "\u5927\u5382\u6587\u6863",
				desc: "\u4E13\u4E1A\u7EA7\u6280\u672F\u6587\u6863\u7F8E\u5B66\uFF0C\u9AD8\u5C42\u7EA7\u4FE1\u606F\u7684\u6743\u5A01\u5448\u73B0",
			},
		},
	},
	{
		id: "blank",
		styles: {
			cardBg: "#ffffff",
			textColor: "#333333",
			accentColor: "#333333",
			headingColor: "#111111",
			fontFamily: '-apple-system, "PingFang SC", sans-serif',
		},
		chrome: "none",
		i18n: {
			en: {
				name: "Blank Template",
				desc: "Pure minimalist background, back to the text itself",
			},
			zh: {
				name: "\u7A7A\u767D\u6A21\u677F",
				desc: "\u7EAF\u51C0\u6781\u7B80\u80CC\u666F\uFF0C\u56DE\u5F52\u6587\u5B57\u672C\u8EAB",
			},
		},
	},
];

// Register template translations into the i18n system
for (const def of templateDefs) {
	for (const locale of Object.keys(def.i18n) as Locale[]) {
		registerTemplateTranslations(locale, {
			[`template.${def.id}.name`]: def.i18n[locale].name,
			[`template.${def.id}.desc`]: def.i18n[locale].desc,
		});
	}
}

// Build runtime Template objects (name/desc use Chinese as default display values)
export const templates: Template[] = templateDefs.map((def) => ({
	id: def.id,
	name: def.i18n.zh.name,
	description: def.i18n.zh.desc,
	styles: def.styles,
	chrome: def.chrome,
	contentWrapper: def.contentWrapper,
}));

export const TEMPLATE_IDS: string[] = templateDefs.map((def) => def.id);

export const defaultTemplate = templates[0];
