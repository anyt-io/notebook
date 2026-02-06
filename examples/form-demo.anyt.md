---
schema: "2.0"
name: form-demo
workdir: form_output
---

# Form-Based Inputs Demo

Demonstrates all form field types available in AnyT Notebook input cells.

<note id="intro">
## Form Field Types

AnyT Notebook supports structured form inputs with:
- Text and textarea fields
- Number inputs with validation
- Select dropdowns and radio buttons
- Checkboxes and multi-select options

Click the **edit** button on any input cell to see the visual Field Editor!
</note>

<input id="user-info">
## User Information

Please provide your information:

<form type="json">
{
  "fields": [
    {
      "name": "fullName",
      "type": "text",
      "label": "Full Name",
      "required": true,
      "placeholder": "Enter your name",
      "validation": { "minLength": 2, "maxLength": 100 }
    },
    {
      "name": "email",
      "type": "text",
      "label": "Email Address",
      "required": true,
      "placeholder": "you@example.com",
      "validation": { "pattern": "^[^@]+@[^@]+\\.[^@]+$" }
    },
    {
      "name": "age",
      "type": "number",
      "label": "Age",
      "placeholder": "Your age",
      "validation": { "min": 18, "max": 120 }
    },
    {
      "name": "bio",
      "type": "textarea",
      "label": "Short Bio",
      "rows": 4,
      "placeholder": "Tell us about yourself..."
    }
  ]
}
</form>
</input>

<input id="preferences">
## Preferences

Configure your preferences:

<form type="json">
{
  "fields": [
    {
      "name": "theme",
      "type": "select",
      "label": "Theme",
      "required": true,
      "default": "light",
      "options": [
        { "value": "light", "label": "Light" },
        { "value": "dark", "label": "Dark" },
        { "value": "auto", "label": "Auto" }
      ]
    },
    {
      "name": "notifications",
      "type": "checkbox",
      "label": "Enable Notifications",
      "default": true,
      "description": "Receive updates about your tasks"
    },
    {
      "name": "language",
      "type": "radio",
      "label": "Preferred Language",
      "required": true,
      "default": "en",
      "options": [
        { "value": "en", "label": "English" },
        { "value": "es", "label": "Spanish" },
        { "value": "fr", "label": "French" },
        { "value": "de", "label": "German" }
      ]
    },
    {
      "name": "features",
      "type": "multiselect",
      "label": "Features to Enable",
      "description": "Select all features you want to use",
      "options": [
        { "value": "analytics", "label": "Analytics" },
        { "value": "reports", "label": "Reports" },
        { "value": "api", "label": "API" },
        { "value": "webhooks", "label": "Webhooks" }
      ],
      "validation": { "minItems": 1, "maxItems": 3 }
    }
  ]
}
</form>
</input>

<task id="process-inputs">
Process the user information and preferences from the previous input cells.

Check the responses from:
- `user-info` - User's personal information
- `preferences` - User's preferences

Create a summary document showing what was collected.

**Output:** user_profile.json, summary.md
</task>

<input id="stock-lookup">
## Stock Price Lookup

Select a stock to check:

<form type="json">
{
  "fields": [
    {
      "name": "ticker",
      "type": "select",
      "label": "Stock Ticker",
      "required": true,
      "options": [
        { "value": "NVDA", "label": "NVDA" },
        { "value": "GOOGL", "label": "GOOGL" },
        { "value": "AAPL", "label": "AAPL" },
        { "value": "MSFT", "label": "MSFT" }
      ]
    },
    {
      "name": "timeframe",
      "type": "radio",
      "label": "Time Period",
      "required": true,
      "default": "1d",
      "options": [
        { "value": "1d", "label": "1 Day" },
        { "value": "1w", "label": "1 Week" },
        { "value": "1m", "label": "1 Month" },
        { "value": "1y", "label": "1 Year" }
      ]
    },
    {
      "name": "includeChart",
      "type": "checkbox",
      "label": "Generate Price Chart",
      "default": true,
      "description": "Create an SVG visualization of the price history"
    }
  ]
}
</form>
</input>

<task id="fetch-stock">
Based on the user's selection from the `stock-lookup` input:

1. Display the stock ticker and company name
2. Look up current stock information
3. Show relevant data for the selected timeframe
4. If chart was requested, describe what it would show

**Output:** stock_info.md
</task>

<note id="summary">
## Demo Complete

This demo showcased all form field types:
- **text**: Single-line input with pattern validation
- **textarea**: Multi-line input
- **number**: Numeric input with min/max
- **select**: Dropdown selection
- **radio**: Radio button groups
- **checkbox**: Boolean toggle
- **multiselect**: Multiple selection with item limits

**Tip**: Click the edit button on any input cell to use the visual Field Editor!
</note>
