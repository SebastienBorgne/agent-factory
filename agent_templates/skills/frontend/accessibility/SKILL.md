---
name: accessibility
description: Use when building or reviewing any interactive UI to ensure it is usable via keyboard and assistive technology, not just a mouse and sighted use.
---

## What I do
I make interactive UI accessible by default: semantic HTML, correct ARIA usage, full keyboard operability, and sufficient color contrast, so the product works for assistive-technology users as well as everyone else.

## How to apply
- Use semantic elements (`button`, `nav`, `label`, `table`) instead of generic `div`/`span` with click handlers bolted on.
- Ensure every interactive element is reachable and operable by keyboard alone (`Tab`, `Enter`, `Space`, arrow keys where conventional) with a visible focus state.
- Add ARIA roles/attributes (`aria-label`, `aria-expanded`, `aria-live`) only to fill gaps semantic HTML can't cover — don't use ARIA to override native semantics unnecessarily.
- Associate every form input with a `label` (explicit `for`/`id` or wrapping) and surface validation errors in a way screen readers announce.
- Check color contrast against WCAG AA (4.5:1 for normal text) for text and meaningful UI elements, not just decorative ones.
- Manage focus explicitly on route changes, modals opening/closing, and dynamic content insertion.
- Test with keyboard-only navigation before considering an interactive component done.
