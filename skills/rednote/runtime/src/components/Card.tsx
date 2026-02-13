import { CARD_HEIGHT, CARD_WIDTH } from "../constants";
import { formatDate, useI18n } from "../i18n";
import type { CoverConfig, StyleOverrides, Template } from "../types";

interface CardProps {
	content: string;
	template: Template;
	styleOverrides: StyleOverrides;
	pageNum: number;
	totalPages: number;
	watermark: string;
	scale?: number;
	coverConfig?: CoverConfig;
}

function AppleNotesHeader({ accentColor }: { accentColor: string }) {
	const { t, locale } = useI18n();
	return (
		<div className="card-chrome apple-notes-header">
			<span className="back-btn" style={{ color: accentColor }}>
				{t("card.memo")}
			</span>
			<span className="date-text">{formatDate(locale)}</span>
			<span className="done-btn" style={{ color: accentColor }}>
				{t("card.done")}
			</span>
		</div>
	);
}

function AccentLineHeader({ accentColor }: { accentColor: string }) {
	return (
		<div className="card-chrome accent-line-header">
			<div className="accent-line" style={{ backgroundColor: accentColor }} />
		</div>
	);
}

function BorderHeader() {
	return (
		<div className="card-chrome border-header">
			<div className="border-line" />
		</div>
	);
}

export default function Card({
	content,
	template,
	styleOverrides,
	pageNum,
	totalPages,
	watermark,
	scale,
	coverConfig,
}: CardProps) {
	const { t } = useI18n();
	const { styles, chrome } = template;
	const bg = styleOverrides.cardBg || styles.cardBg;
	const textColor = styleOverrides.textColor || styles.textColor;
	const accentColor = styleOverrides.accentColor || styles.accentColor;
	const headingColor = styles.headingColor;
	const isGradient = bg.includes("gradient");
	const isCover = !!coverConfig;

	const cardStyle: React.CSSProperties = {
		"--card-bg": bg,
		"--text-color": textColor,
		"--accent-color": accentColor,
		"--heading-color": headingColor,
		"--font-family": styles.fontFamily,
		"--font-size": `${styleOverrides.fontSize}px`,
		"--line-height": `${styleOverrides.lineHeight}`,
		"--letter-spacing": `${styleOverrides.letterSpacing}px`,
		background: isGradient ? bg : undefined,
		backgroundColor: isGradient ? undefined : bg,
	} as React.CSSProperties;

	const wrapperStyle: React.CSSProperties = scale
		? {
				transform: `scale(${scale})`,
				transformOrigin: "top left",
				width: CARD_WIDTH,
				height: CARD_HEIGHT,
			}
		: { width: CARD_WIDTH, height: CARD_HEIGHT };

	const footer = (
		<div className="card-footer">
			{watermark && <span className="card-watermark">{watermark}</span>}
			<span className="card-page-num">
				{pageNum} / {totalPages}
			</span>
		</div>
	);

	if (isCover) {
		return (
			<div style={wrapperStyle}>
				<div className={`card card--${template.id}`} style={cardStyle} data-template={template.id}>
					<div className="card-cover-image">
						{coverConfig.imageDataUrl ? (
							<img src={coverConfig.imageDataUrl} alt="cover" />
						) : (
							<div className="card-cover-placeholder">{t("card.coverPlaceholder")}</div>
						)}
					</div>
					<div
						className="card-cover-title"
						style={{ fontSize: coverConfig.fontSize, color: accentColor }}
					>
						{coverConfig.title || t("card.coverTitleDefault")}
					</div>
					{footer}
				</div>
			</div>
		);
	}

	// biome-ignore lint/security/noDangerouslySetInnerHtml: rendered markdown
	const body = <div className="card-body" dangerouslySetInnerHTML={{ __html: content }} />;
	const contentInner = template.contentWrapper ? (
		<div className={template.contentWrapper}>{body}</div>
	) : (
		body
	);

	return (
		<div style={wrapperStyle}>
			<div className={`card card--${template.id}`} style={cardStyle} data-template={template.id}>
				{chrome === "apple-notes" && <AppleNotesHeader accentColor={accentColor} />}
				{chrome === "accent-line" && <AccentLineHeader accentColor={accentColor} />}
				{chrome === "border" && <BorderHeader />}

				<div className="card-content">{contentInner}</div>

				{footer}
			</div>
		</div>
	);
}
