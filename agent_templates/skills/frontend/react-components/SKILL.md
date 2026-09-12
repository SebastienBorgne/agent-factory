---
name: react-components
description: Component-structure conventions for React projects — apply when the project's frontend framework is React, covering composition, hooks, and choosing between local and shared state. Not applicable if the project uses a different frontend framework.
---

## What I do
I structure React UIs as small, composable components with state placed at the right level — local when only one component needs it, lifted or shared only when several genuinely do.

## How to apply
- Default to local `useState`/`useReducer`; lift state up only when a sibling or parent actually needs it.
- Extract repeated logic into custom hooks (`useX`) rather than duplicating `useEffect` blocks across components.
- Keep components small and single-purpose; split a component once its JSX or state handling covers more than one concern.
- Memoize expensive derived values (`useMemo`) and stable callbacks passed to children (`useCallback`) only where profiling shows a real re-render cost — don't do it reflexively.
- Handle loading, error, and empty states explicitly in any component that fetches data.
- Type props explicitly (TypeScript or PropTypes, matching the project's existing convention) rather than leaving them implicit.
- Prefer composition (children, render props) over deeply nested conditional prop configuration.
