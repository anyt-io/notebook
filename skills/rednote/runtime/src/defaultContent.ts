import type { Locale } from "./i18n";

const defaultMarkdownZh = `# \u5C0F\u7EA2\u4E66\u56FE\u7247\u751F\u6210\u5668

\u6B22\u8FCE\u4F7F\u7528\uFF01\u5728\u5DE6\u4FA7\u8F93\u5165 Markdown \u6587\u672C\uFF0C\u53F3\u4FA7\u9009\u62E9\u6A21\u677F\u6837\u5F0F\uFF0C\u5373\u53EF\u751F\u6210\u7CBE\u7F8E\u7684\u5C0F\u7EA2\u4E66\u914D\u56FE\u3002

\u7528 **---** \u5206\u5272\u7EBF\u6765\u624B\u52A8\u5206\u9875\uFF0C\u6BCF\u4E00\u9875\u90FD\u4F1A\u81EA\u52A8\u9002\u914D\u5361\u7247\u5927\u5C0F\u3002

---

## \u652F\u6301\u7684\u8BED\u6CD5

**\u52A0\u7C97\u6587\u5B57**\u3001*\u659C\u4F53\u6587\u5B57*\u3001~~\u5220\u9664\u7EBF~~

==\u9AD8\u4EAE\u6587\u5B57== \u7528\u53CC\u7B49\u53F7\u5305\u88F9

> \u5F15\u7528\u5185\u5BB9\u53EF\u4EE5\u8FD9\u6837\u5199

- \u65E0\u5E8F\u5217\u8868\u9879 A
- \u65E0\u5E8F\u5217\u8868\u9879 B

1. \u6709\u5E8F\u5217\u8868\u9879
2. \u6709\u5E8F\u5217\u8868\u9879

\`\u884C\u5185\u4EE3\u7801\` \u4E5F\u53EF\u4EE5\u4F7F\u7528

---

## \u4E09\u4E2A\u4F7F\u7528\u6280\u5DE7

**\u7B2C\u4E00**\uFF0C\u5148\u628A\u5185\u5BB9\u5199\u597D\uFF0C\u518D\u9009\u6A21\u677F\u3002\u4E0D\u540C\u6A21\u677F\u7684\u6392\u7248\u98CE\u683C\u5DEE\u5F02\u5F88\u5927\uFF0C\u9009\u5BF9\u6A21\u677F\u80FD\u8BA9\u5185\u5BB9\u66F4\u51FA\u5F69\u3002

**\u7B2C\u4E8C**\uFF0C\u5584\u7528\u5206\u9875\u7B26\u3002\u7528 \`---\` \u63A7\u5236\u6BCF\u9875\u663E\u793A\u7684\u5185\u5BB9\u91CF\uFF0C\u907F\u514D\u5355\u9875\u5185\u5BB9\u8FC7\u591A\u3002

**\u7B2C\u4E09**\uFF0C\u8C03\u6574\u53F3\u4FA7\u7684\u5B57\u53F7\u548C\u884C\u9AD8\uFF0C\u627E\u5230\u6700\u8212\u670D\u7684\u9605\u8BFB\u4F53\u9A8C\u3002

---

## \u5F00\u59CB\u521B\u4F5C\u5427

\u5220\u6389\u8FD9\u4E9B\u793A\u4F8B\u6587\u5B57\uFF0C\u8F93\u5165\u4F60\u81EA\u5DF1\u7684\u5185\u5BB9\u3002

\u652F\u6301\u4E00\u952E\u4E0B\u8F7D\u5355\u5F20\u56FE\u7247\uFF0C\u4E5F\u53EF\u4EE5\u6253\u5305\u4E0B\u8F7D\u5168\u90E8\u3002
`;

const defaultMarkdownEn = `# Card Image Generator

Welcome! Enter Markdown text on the left, choose a template on the right, and generate beautiful card images.

Use **---** dividers to manually paginate. Each page auto-fits the card size.

---

## Supported Syntax

**Bold text**, *italic text*, ~~strikethrough~~

==Highlighted text== wrapped with double equals

> Blockquotes look like this

- Unordered list item A
- Unordered list item B

1. Ordered list item
2. Ordered list item

\`Inline code\` is also supported

---

## Three Tips

**First**, write your content before choosing a template. Different templates have very different layouts \u2014 picking the right one makes your content shine.

**Second**, use page breaks wisely. Use \`---\` to control how much content appears on each page. Avoid cramming too much into a single page.

**Third**, adjust the font size and line height on the right panel to find the most comfortable reading experience.

---

## Start Creating

Delete this sample text and enter your own content.

You can download a single image or batch download all pages.
`;

const defaults: Record<string, string> = { en: defaultMarkdownEn, zh: defaultMarkdownZh };

export function getDefaultMarkdown(locale: Locale): string {
	return defaults[locale] ?? defaults.en;
}
