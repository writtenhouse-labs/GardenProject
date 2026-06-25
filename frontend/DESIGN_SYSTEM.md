# GardenProject Frontend Layout Standards

Use these standards for new or changed Streamlit controls so spacing stays consistent across pages.

## Layout Tokens

The shared CSS tokens live in `frontend/ui.py` inside `inject_css()`.

- `--gp-page-max`: max content width.
- `--gp-page-gutter`: left and right page gutter.
- `--gp-section-gap`: vertical gap between major page sections.
- `--gp-panel-padding`: padding inside framed panels.
- `--gp-control-gap`: spacing between controls and columns.
- `--gp-control-radius`: radius for inputs, notes, and small controls.
- `--gp-panel-radius`: radius for panels/cards.

## Page Structure

- Use `configure_page(...)` and `render_nav()` at the top of every page.
- Use a hero or service header first, followed by panels separated by `--gp-section-gap`.
- Keep primary content inside the global `block-container`; do not add page-level negative margins.

## Control Rows

- Use `st.columns(..., gap="medium")` for two- or three-column control rows.
- Keep helper text in `.field-note` or `.field-note-neutral`.
- Do not manually set per-control widths unless Streamlit needs a targeted override.
- Keep labels short and let the note explain context.

## Panels

- For the Crop Intelligence form, keep controls inside the `intelligence-panel-marker` container.
- For repeated result cards, keep the `result-card-marker` marker inside each bordered container.
- Do not nest cards inside cards.

## Visual Checks

Before finishing layout changes, check:

- Hero-to-panel gap is a single `--gp-section-gap`.
- Section headings align to the same gutters as controls.
- Notes and inputs line up across columns.
- No control text is clipped at desktop or mobile widths.
