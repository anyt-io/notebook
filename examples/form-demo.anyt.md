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

<form type="dsl">
fullName: text | Full Name | required, minLength=2, maxLength=100, placeholder="Enter your name"
email: text | Email Address | required, placeholder="you@example.com", pattern="^[^@]+@[^@]+\.[^@]+$"
age: number | Age | min=18, max=120, placeholder="Your age"
bio: textarea | Short Bio | rows=4, placeholder="Tell us about yourself..."
</form>
</input>

<input id="preferences">
## Preferences

Configure your preferences:

<form type="dsl">
theme: select[light,dark,auto] | Theme | required, default=light
notifications: checkbox | Enable Notifications | default=true, description="Receive updates about your tasks"
language: radio[en,es,fr,de] | Preferred Language | required, default=en
features: multiselect[analytics,reports,api,webhooks] | Features to Enable | minItems=1, maxItems=3, description="Select all features you want to use"
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

<form type="dsl">
ticker: select[NVDA,GOOGL,AAPL,MSFT] | Stock Ticker | required
timeframe: radio[1d,1w,1m,1y] | Time Period | required, default=1d
includeChart: checkbox | Generate Price Chart | default=true, description="Create an SVG visualization of the price history"
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
