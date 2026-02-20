import { useEffect, useRef, useState } from "react";
import type { ColorResult } from "react-color";
import { CompactPicker } from "react-color";
import {
	COVER_FONT_SIZE_RANGE,
	DEFAULT_FONT_SIZE,
	DEFAULT_LETTER_SPACING,
	DEFAULT_LINE_HEIGHT,
	FONT_SIZE_RANGE,
	LETTER_SPACING_RANGE,
	LINE_HEIGHT_RANGE,
} from "../constants";
import { useI18n } from "../i18n";
import { templates } from "../templates";
import type { CoverConfig, StyleOverrides, Template } from "../types";

interface ControlPanelProps {
	selectedTemplate: Template;
	styleOverrides: StyleOverrides;
	watermark: string;
	coverConfig: CoverConfig;
	autoPageBreak: boolean;
	onSelectTemplate: (t: Template) => void;
	onStyleChange: (overrides: StyleOverrides) => void;
	onWatermarkChange: (w: string) => void;
	onCoverChange: (config: CoverConfig) => void;
	onAutoPageBreakChange: (v: boolean) => void;
	onDownloadAll?: () => void;
}

type Tab = "basic" | "cover";

function ColorField({
	label,
	value,
	onChange,
}: {
	label: string;
	value: string;
	onChange: (color: string) => void;
}) {
	const [open, setOpen] = useState(false);
	const ref = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (!open) return;
		const handleClick = (e: MouseEvent) => {
			if (ref.current && !ref.current.contains(e.target as Node)) {
				setOpen(false);
			}
		};
		document.addEventListener("mousedown", handleClick);
		return () => document.removeEventListener("mousedown", handleClick);
	}, [open]);

	return (
		<div className="control-group">
			<div className="control-header">
				<span className="control-label">{label}</span>
				<button
					type="button"
					className="color-swatch-btn"
					style={{ backgroundColor: value }}
					onClick={() => setOpen(!open)}
					title={value}
				/>
			</div>
			{open && (
				<div className="color-picker-popover" ref={ref}>
					<CompactPicker color={value} onChangeComplete={(c: ColorResult) => onChange(c.hex)} />
				</div>
			)}
		</div>
	);
}

export default function ControlPanel({
	selectedTemplate,
	styleOverrides,
	watermark,
	coverConfig,
	autoPageBreak,
	onSelectTemplate,
	onStyleChange,
	onWatermarkChange,
	onCoverChange,
	onAutoPageBreakChange,
	onDownloadAll,
}: ControlPanelProps) {
	const { t } = useI18n();
	const [tab, setTab] = useState<Tab>("basic");
	const coverFileRef = useRef<HTMLInputElement>(null);
	const [coverFileName, setCoverFileName] = useState<string>("");

	const handleCoverImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;
		setCoverFileName(file.name);
		const reader = new FileReader();
		reader.onloadend = () => {
			onCoverChange({ ...coverConfig, imageDataUrl: reader.result as string });
		};
		reader.readAsDataURL(file);
	};

	const updateStyle = (key: keyof StyleOverrides, value: number | string | undefined) => {
		onStyleChange({ ...styleOverrides, [key]: value });
	};

	const resetStyles = () => {
		onStyleChange({
			cardBg: undefined,
			textColor: undefined,
			accentColor: undefined,
			fontSize: DEFAULT_FONT_SIZE,
			lineHeight: DEFAULT_LINE_HEIGHT,
			letterSpacing: DEFAULT_LETTER_SPACING,
		});
	};

	return (
		<aside className="panel panel-right">
			<div className="right-columns">
				{/* Template Selection Column */}
				<div className="right-col template-col">
					<h3 className="col-title">
						<span className="col-icon">&#10024;</span> {t("ctrl.selectTemplate")}
					</h3>
					<div className="template-list">
						{templates.map((tmpl) => (
							<button
								type="button"
								key={tmpl.id}
								className={`template-card ${tmpl.id === selectedTemplate.id ? "template-card--active" : ""}`}
								onClick={() => onSelectTemplate(tmpl)}
							>
								<div className="template-card-name">{t(`template.${tmpl.id}.name`)}</div>
								<div className="template-card-desc">{t(`template.${tmpl.id}.desc`)}</div>
							</button>
						))}
					</div>
				</div>

				{/* Style Adjustment Column */}
				<div className="right-col style-col">
					<h3 className="col-title">
						<span className="col-icon">&#9881;</span> {t("ctrl.styleAdjust")}
					</h3>

					<div className="style-tabs">
						<button
							type="button"
							className={`style-tab ${tab === "basic" ? "style-tab--active" : ""}`}
							onClick={() => setTab("basic")}
						>
							&#9998; {t("ctrl.tabBasic")}
						</button>
						<button
							type="button"
							className={`style-tab ${tab === "cover" ? "style-tab--active" : ""}`}
							onClick={() => setTab("cover")}
						>
							&#128444; {t("ctrl.tabCover")}
						</button>
					</div>

					{tab === "basic" && (
						<div className="style-controls">
							<ColorField
								label={t("ctrl.bgColor")}
								value={styleOverrides.cardBg || selectedTemplate.styles.cardBg}
								onChange={(c) => updateStyle("cardBg", c)}
							/>

							<ColorField
								label={t("ctrl.textColor")}
								value={styleOverrides.textColor || selectedTemplate.styles.textColor}
								onChange={(c) => updateStyle("textColor", c)}
							/>

							<ColorField
								label={t("ctrl.accentColor")}
								value={styleOverrides.accentColor || selectedTemplate.styles.accentColor}
								onChange={(c) => updateStyle("accentColor", c)}
							/>

							{/* Font Size */}
							<div className="control-group">
								<div className="control-header">
									<span className="control-label">{t("ctrl.fontSize")}</span>
									<span className="control-value">{styleOverrides.fontSize}px</span>
								</div>
								<input
									type="range"
									min={FONT_SIZE_RANGE.min}
									max={FONT_SIZE_RANGE.max}
									step={FONT_SIZE_RANGE.step}
									value={styleOverrides.fontSize}
									onChange={(e) => updateStyle("fontSize", Number(e.target.value))}
								/>
							</div>

							{/* Line Height */}
							<div className="control-group">
								<div className="control-header">
									<span className="control-label">{t("ctrl.lineHeight")}</span>
									<span className="control-value">{styleOverrides.lineHeight.toFixed(1)}</span>
								</div>
								<input
									type="range"
									min={LINE_HEIGHT_RANGE.min}
									max={LINE_HEIGHT_RANGE.max}
									step={LINE_HEIGHT_RANGE.step}
									value={styleOverrides.lineHeight}
									onChange={(e) => updateStyle("lineHeight", Number(e.target.value))}
								/>
							</div>

							{/* Letter Spacing */}
							<div className="control-group">
								<div className="control-header">
									<span className="control-label">{t("ctrl.letterSpacing")}</span>
									<span className="control-value">{styleOverrides.letterSpacing}px</span>
								</div>
								<input
									type="range"
									min={LETTER_SPACING_RANGE.min}
									max={LETTER_SPACING_RANGE.max}
									step={LETTER_SPACING_RANGE.step}
									value={styleOverrides.letterSpacing}
									onChange={(e) => updateStyle("letterSpacing", Number(e.target.value))}
								/>
							</div>

							{/* Auto Page Break */}
							<div className="control-group">
								<label className="cover-toggle">
									<span>{t("ctrl.autoPageBreak")}</span>
									<input
										type="checkbox"
										checked={autoPageBreak}
										onChange={(e) => onAutoPageBreakChange(e.target.checked)}
									/>
								</label>
							</div>

							{/* Reset */}
							<button type="button" className="btn btn-reset" onClick={resetStyles}>
								&#8635; {t("ctrl.resetStyles")}
							</button>
						</div>
					)}

					{tab === "cover" && (
						<div className="style-controls">
							{/* Cover Toggle */}
							<div className="control-group">
								<label className="cover-toggle">
									<span>&#128444; {t("ctrl.enableCover")}</span>
									<input
										type="checkbox"
										checked={coverConfig.enabled}
										onChange={(e) => onCoverChange({ ...coverConfig, enabled: e.target.checked })}
									/>
								</label>
							</div>

							{coverConfig.enabled && (
								<>
									{/* Cover Title */}
									<div className="control-group">
										<span className="control-label">{t("ctrl.coverTitle")}</span>
										<input
											type="text"
											className="text-input"
											value={coverConfig.title}
											onChange={(e) => onCoverChange({ ...coverConfig, title: e.target.value })}
											placeholder={t("ctrl.coverTitlePlaceholder")}
										/>
									</div>

									{/* Cover Image Upload */}
									<div className="control-group">
										<span className="control-label">{t("ctrl.coverImage")}</span>
										<input
											ref={coverFileRef}
											type="file"
											accept="image/*"
											style={{ display: "none" }}
											onChange={handleCoverImageUpload}
										/>
										<button
											type="button"
											className="btn cover-upload-btn"
											onClick={() => coverFileRef.current?.click()}
										>
											&#8682; {t("ctrl.uploadImage")}
										</button>
										{coverFileName && <span className="cover-file-hint">{coverFileName}</span>}
									</div>

									{/* Cover Font Size */}
									<div className="control-group">
										<div className="control-header">
											<span className="control-label">{t("ctrl.coverFontSize")}</span>
											<span className="control-value">{coverConfig.fontSize}px</span>
										</div>
										<input
											type="range"
											min={COVER_FONT_SIZE_RANGE.min}
											max={COVER_FONT_SIZE_RANGE.max}
											step={COVER_FONT_SIZE_RANGE.step}
											value={coverConfig.fontSize}
											onChange={(e) =>
												onCoverChange({
													...coverConfig,
													fontSize: Number(e.target.value),
												})
											}
										/>
									</div>
								</>
							)}

							{/* Watermark - always shown */}
							<div className="control-group">
								<span className="control-label">{t("ctrl.watermark")}</span>
								<input
									type="text"
									className="text-input"
									value={watermark}
									onChange={(e) => onWatermarkChange(e.target.value)}
									placeholder={t("ctrl.watermarkPlaceholder")}
								/>
							</div>
						</div>
					)}
				</div>
			</div>
			<div className="download-section">
				<button type="button" className="btn btn-primary download-all-btn" onClick={onDownloadAll}>
					{t("ctrl.downloadAll")}
				</button>
			</div>
		</aside>
	);
}
