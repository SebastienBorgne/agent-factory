---
name: design-systems
description: Use when building UI that must stay visually and structurally consistent with an existing design system or component library.
---

## What I do
I build and extend UI using the project's existing design tokens and shared component library instead of one-off styles, keeping the product visually and structurally consistent.

## How to apply
- Reuse existing shared components (buttons, inputs, layout primitives) before creating a new one; check the component library first.
- Pull colors, spacing, typography, and radii from design tokens/theme variables — never hardcode a raw hex or pixel value that a token already covers.
- When a new UI pattern is genuinely needed, add it to the shared component set rather than inlining it in a single feature.
- Keep component APIs consistent with existing ones (naming of props like `variant`, `size`, `disabled`) so usage stays predictable across the codebase.
- Respect the system's responsive breakpoints instead of introducing ad hoc media queries.
- Document any new shared component's intended usage briefly at the point of definition so other agents/devs reuse it correctly.
