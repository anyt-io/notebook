import { useRef } from "react";
import { useI18n } from "../i18n";

interface EditorPanelProps {
	markdown: string;
	totalPages: number;
	onChange: (value: string) => void;
}

export default function EditorPanel({ markdown, totalPages, onChange }: EditorPanelProps) {
	const { t } = useI18n();
	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const fileInputRef = useRef<HTMLInputElement>(null);

	const handleInsertImage = (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onloadend = () => {
			const dataUrl = reader.result as string;
			const imgMarkdown = `![image](${dataUrl})`;
			const textarea = textareaRef.current;
			if (textarea) {
				const start = textarea.selectionStart;
				const end = textarea.selectionEnd;
				const newValue = markdown.slice(0, start) + imgMarkdown + markdown.slice(end);
				onChange(newValue);
			} else {
				onChange(`${markdown}\n${imgMarkdown}`);
			}
		};
		reader.readAsDataURL(file);
		// Reset so the same file can be re-selected
		e.target.value = "";
	};

	return (
		<aside className="panel panel-left">
			<div className="panel-header">
				<span className="panel-icon">&#9998;</span>
				<span>{t("editor.title")}</span>
			</div>
			<div className="editor-hint">
				{t("editor.hint.separator")}
				<code>---</code>
				{t("editor.hint.separatorDesc")}&ensp;|&ensp;{t("editor.hint.markdown")}&ensp;|&ensp;
				<code>{t("editor.hint.highlight")}</code>
			</div>
			<div className="editor-toolbar">
				<input
					ref={fileInputRef}
					type="file"
					accept="image/*"
					style={{ display: "none" }}
					onChange={handleInsertImage}
				/>
				<button
					type="button"
					className="btn btn-sm"
					onClick={() => fileInputRef.current?.click()}
					title={t("editor.insertImageTitle")}
				>
					&#128247; {t("editor.insertImage")}
				</button>
			</div>
			<textarea
				ref={textareaRef}
				className="markdown-input"
				value={markdown}
				onChange={(e) => onChange(e.target.value)}
				placeholder={t("editor.placeholder")}
				spellCheck={false}
			/>
			<div
				className="editor-footer"
				// biome-ignore lint/security/noDangerouslySetInnerHtml: trusted i18n string
				dangerouslySetInnerHTML={{ __html: t("editor.pageCount", totalPages) }}
			/>
		</aside>
	);
}
