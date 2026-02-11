---
schema: "2.0"
name: Stock Analysis
workdir: stock-analysis
---

# Stock Analysis

<note id="note-rrnw" label="Overview">
Analyzle Stock in last few days and generate visualization
</note>

<input id="input-t0jh" label="Pick Stock">
Select the stock to review 

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "Stock to review",
      "type": "select",
      "label": "Stock",
      "description": "Which Stock to review",
      "default": "Nvidia",
      "options": [
        {
          "value": "Nvidia",
          "label": "Nvidia"
        },
        {
          "value": "Google",
          "label": "Google"
        },
        {
          "value": "Salesforce",
          "label": "Salesforce"
        }
      ]
    },
    {
      "name": "Last days",
      "type": "number",
      "label": "Last days",
      "default": 30,
      "placeholder": "Number of days "
    }
  ]
}
</form>
</input>

<task id="task-b23w" label="Fetch Stock Information">
Fetch the stock based on user selections , store it in csv `stocks.csv`
</task>

<break id="break-zubt" label="Review Data">
review `stocks.csv` whether the output is correct 

&nbsp;
</break>

<task id="task-0fh6" label="Visualization">
Generate data visualization for `stocks.csv` and stock names
</task>

