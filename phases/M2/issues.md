# M2 Issues

## 1. Notification vibrate property not in TypeScript types
**Problem**: `vibrate` is part of the Notification API spec but not in TS's `NotificationOptions` type.
**Fix**: Extended the type inline: `NotificationOptions & { vibrate?: number[] }`.

## 2. Playwright strict mode violations
**Problem**: `text=Skip` matched both the label "Skip if you don't care" and the button "Skip". Similarly `text=Rating` matched both the section label and the helper text.
**Fix**: Used `getByRole("button", { name: "Skip" })` and `getByText("Rating", { exact: true })`.

## 3. Crumb/crust sliders use native range inputs
**Problem**: The spec calls for custom gradient-track sliders with an ink knob. Used native `<input type="range">` with `accent-amber` for now.
**Impact**: Functional but not pixel-perfect to the design. Can be replaced with a custom slider component later.

## 4. Photo upload not fully tested in dev mode
**Problem**: R2 presigned URLs return `file://` paths in dev mode. The actual upload flow (camera capture → upload → confirm) requires a real R2 bucket.
**Impact**: Photo DB rows can be created via API, but the camera-to-R2 pipeline needs production testing.
