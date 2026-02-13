export const CARD_WIDTH = 1080;
export const CARD_HEIGHT = 1440;

// Layout — must match CSS in index.css (.card-content, .card-footer, etc.)
export const CARD_PADDING_X = 70;
export const CARD_PADDING_Y = 24;
export const HEADER_HEIGHT = 120;
export const FOOTER_HEIGHT = 80;
export const CONTENT_WIDTH = CARD_WIDTH - CARD_PADDING_X * 2;
export const MAX_CONTENT_HEIGHT = CARD_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT - CARD_PADDING_Y * 2;

// Default style values (used in App.tsx state init + ControlPanel reset)
export const DEFAULT_FONT_SIZE = 35;
export const DEFAULT_LINE_HEIGHT = 1.8;
export const DEFAULT_LETTER_SPACING = 1;
export const DEFAULT_COVER_FONT_SIZE = 104;

// Slider ranges (used in ControlPanel)
export const FONT_SIZE_RANGE = { min: 24, max: 56, step: 1 } as const;
export const LINE_HEIGHT_RANGE = { min: 1.2, max: 2.4, step: 0.1 } as const;
export const LETTER_SPACING_RANGE = { min: -2, max: 10, step: 0.5 } as const;
export const COVER_FONT_SIZE_RANGE = { min: 48, max: 200, step: 2 } as const;
