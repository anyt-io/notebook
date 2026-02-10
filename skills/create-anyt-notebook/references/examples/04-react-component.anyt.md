---
schema: "2.0"
name: react-component
workdir: components
---

# React Component Generator

Create a reusable React component with tests and Storybook stories.

<input id="component-config">
What component should we build?

<form type="json">
{
  "fields": [
    {
      "name": "componentName",
      "type": "text",
      "label": "Component Name",
      "required": true,
      "placeholder": "e.g., Button, Card, Modal"
    },
    {
      "name": "variant",
      "type": "select",
      "label": "Complexity",
      "options": [
        { "value": "simple", "label": "Simple" },
        { "value": "with-state", "label": "With State" },
        { "value": "with-api", "label": "With Api" }
      ]
    },
    {
      "name": "styling",
      "type": "select",
      "label": "Styling Approach",
      "options": [
        { "value": "tailwind", "label": "Tailwind" },
        { "value": "css-modules", "label": "Css Modules" },
        { "value": "styled-components", "label": "Styled Components" }
      ]
    }
  ]
}
</form>
</input>

<task id="component">
Create a React component based on the user's config:
- Name it according to componentName input
- Use TypeScript with proper prop types
- Apply the selected styling approach
- If variant is "with-state", add useState for internal state
- If variant is "with-api", add a useEffect that fetches from a mock API
- Include proper accessibility attributes (aria labels, roles)
- Export both default and named exports
</task>

<task id="tests">
Create comprehensive tests for the component:
- Use React Testing Library
- Test rendering with different props
- Test user interactions (clicks, input)
- Test accessibility basics
- If variant is "with-api", mock the API call
</task>

<task id="storybook">
Create a Storybook story file for the component:
- Include a default story
- Add stories for different prop variations
- Include a story showing the component in different states
- Add argTypes for interactive controls
</task>

<note id="done">
## Component Ready!

Created:
- `{componentName}.tsx` - The component
- `{componentName}.test.tsx` - Test suite
- `{componentName}.stories.tsx` - Storybook stories

Preview in Storybook:
```bash
npm run storybook
```
</note>
