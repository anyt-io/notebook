import { Marked } from "marked";

const marked = new Marked();

marked.use({
	gfm: true,
	breaks: true,
	extensions: [
		{
			name: "highlight",
			level: "inline",
			start(src: string) {
				return src.match(/==/)?.index;
			},
			tokenizer(src: string) {
				const match = src.match(/^==(.*?)==/);
				if (match) {
					return {
						type: "highlight",
						raw: match[0],
						text: match[1],
					};
				}
				return undefined;
			},
			renderer(token) {
				const text = (token as unknown as { text: string }).text;
				return `<mark>${text}</mark>`;
			},
		},
	],
});

export function parseMarkdown(text: string): string {
	return marked.parse(text, { async: false }) as string;
}

export function splitByPageBreaks(markdown: string): string[] {
	// Split on lines that are exactly "---" (with optional surrounding blank lines)
	// This avoids consuming setext-style h2 headings (text\n---)
	return markdown
		.split(/\n(?:\s*\n)?---(?:\s*\n)?\n/)
		.map((s) => s.trim())
		.filter((s) => s.length > 0);
}
