export const TRANSLATION_KEYS = [
	// App / Mobile tabs
	"tab.editor",
	"tab.preview",
	"tab.settings",

	// EditorPanel
	"editor.title",
	"editor.hint.separator",
	"editor.hint.separatorDesc",
	"editor.hint.markdown",
	"editor.hint.highlight",
	"editor.insertImage",
	"editor.insertImageTitle",
	"editor.placeholder",
	"editor.pageCount",

	// PreviewPanel
	"preview.title",
	"preview.pageCount",
	"preview.pageInfo",
	"preview.download",
	"preview.downloading",
	"preview.prevPage",
	"preview.nextPage",

	// ControlPanel
	"ctrl.selectTemplate",
	"ctrl.styleAdjust",
	"ctrl.tabBasic",
	"ctrl.tabCover",
	"ctrl.bgColor",
	"ctrl.textColor",
	"ctrl.accentColor",
	"ctrl.fontSize",
	"ctrl.lineHeight",
	"ctrl.letterSpacing",
	"ctrl.resetStyles",
	"ctrl.enableCover",
	"ctrl.coverTitle",
	"ctrl.coverTitlePlaceholder",
	"ctrl.coverImage",
	"ctrl.uploadImage",
	"ctrl.coverFontSize",
	"ctrl.autoPageBreak",
	"ctrl.watermark",
	"ctrl.watermarkPlaceholder",
	"ctrl.downloadAll",

	// Card
	"card.memo",
	"card.done",
	"card.coverPlaceholder",
	"card.coverTitleDefault",

	// Page title
	"app.title",
] as const;

export type TranslationKey = (typeof TRANSLATION_KEYS)[number];
export type TemplateKey = `template.${string}.name` | `template.${string}.desc`;
export type I18nKey = TranslationKey | TemplateKey;
export type TranslationRecord = Record<TranslationKey, string>;
