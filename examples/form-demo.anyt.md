---
name: form-demo
version: 1.0.0
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

```yaml
fields:
  - name: fullName
    type: text
    label: Full Name
    required: true
    placeholder: Enter your name
    validation:
      minLength: 2
      maxLength: 100

  - name: email
    type: text
    label: Email Address
    required: true
    placeholder: you@example.com
    validation:
      pattern: ^[^@]+@[^@]+\.[^@]+$

  - name: age
    type: number
    label: Age
    placeholder: Your age
    validation:
      min: 18
      max: 120

  - name: bio
    type: textarea
    label: Short Bio
    placeholder: Tell us about yourself...
    rows: 4
```
</input>

<input id="preferences">
## Preferences

Configure your preferences:

```yaml
fields:
  - name: theme
    type: select
    label: Theme
    required: true
    default: light
    options:
      - value: light
        label: Light Mode
      - value: dark
        label: Dark Mode
      - value: auto
        label: System Default

  - name: notifications
    type: checkbox
    label: Enable Notifications
    description: Receive updates about your tasks
    default: true

  - name: language
    type: radio
    label: Preferred Language
    required: true
    default: en
    options:
      - value: en
        label: English
      - value: es
        label: Spanish
      - value: fr
        label: French
      - value: de
        label: German

  - name: features
    type: multiselect
    label: Features to Enable
    description: Select all features you want to use
    options:
      - value: analytics
        label: Analytics Dashboard
      - value: reports
        label: Weekly Reports
      - value: api
        label: API Access
      - value: webhooks
        label: Webhooks
    validation:
      minItems: 1
      maxItems: 3
```
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

```yaml
fields:
  - name: ticker
    type: select
    label: Stock Ticker
    required: true
    options:
      - value: NVDA
        label: NVIDIA Corporation
        description: Graphics and AI chips
      - value: GOOGL
        label: Alphabet Inc.
        description: Search and cloud services
      - value: AAPL
        label: Apple Inc.
        description: Consumer electronics
      - value: MSFT
        label: Microsoft Corporation
        description: Software and cloud

  - name: timeframe
    type: radio
    label: Time Period
    required: true
    default: 1d
    options:
      - value: 1d
        label: 1 Day
      - value: 1w
        label: 1 Week
      - value: 1m
        label: 1 Month
      - value: 1y
        label: 1 Year

  - name: includeChart
    type: checkbox
    label: Generate Price Chart
    description: Create an SVG visualization of the price history
    default: true
```
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
