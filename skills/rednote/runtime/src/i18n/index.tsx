import { createContext, type ReactNode, useCallback, useContext, useEffect, useState } from "react";
import type { I18nKey } from "./keys";
import en from "./locales/en";
import zh from "./locales/zh";

const locales = { en, zh } as const;

export type Locale = keyof typeof locales;

const LOCALE_CODES = Object.keys(locales) as Locale[];

// Mutable store for template translations (populated by templates.ts at module load)
const templateTranslations: Record<string, Record<string, string>> = {};
for (const code of LOCALE_CODES) {
	templateTranslations[code] = {};
}

export function registerTemplateTranslations(
	locale: Locale,
	entries: Record<string, string>,
): void {
	Object.assign(templateTranslations[locale], entries);
}

export function formatDate(locale: Locale): string {
	const now = new Date();
	return new Intl.DateTimeFormat(locale === "zh" ? "zh-CN" : "en-US", {
		year: "numeric",
		month: locale === "zh" ? "numeric" : "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
		hour12: false,
	}).format(now);
}

interface I18nContextValue {
	locale: Locale;
	setLocale: (locale: Locale) => void;
	t: (key: I18nKey, ...args: (string | number)[]) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

function detectLocale(): Locale {
	const stored = localStorage.getItem("locale");
	if (stored && LOCALE_CODES.includes(stored as Locale)) return stored as Locale;
	const lang = navigator.language;
	if (lang.startsWith("zh")) return "zh";
	return "en";
}

export function I18nProvider({ children }: { children: ReactNode }) {
	const [locale, setLocaleState] = useState<Locale>(detectLocale);

	const setLocale = useCallback((l: Locale) => {
		setLocaleState(l);
		localStorage.setItem("locale", l);
		document.documentElement.lang = l === "zh" ? "zh-CN" : "en";
		document.title = locales[l]["app.title"];
	}, []);

	useEffect(() => {
		document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
		document.title = locales[locale]["app.title"];
	}, [locale]);

	const t = useCallback(
		(key: I18nKey, ...args: (string | number)[]): string => {
			let str =
				(locales[locale] as Record<string, string>)[key] ??
				templateTranslations[locale]?.[key] ??
				key;
			for (let i = 0; i < args.length; i++) {
				str = str.replace(`{${i}}`, String(args[i]));
			}
			return str;
		},
		[locale],
	);

	return <I18nContext.Provider value={{ locale, setLocale, t }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
	const ctx = useContext(I18nContext);
	if (!ctx) throw new Error("useI18n must be used within I18nProvider");
	return ctx;
}
