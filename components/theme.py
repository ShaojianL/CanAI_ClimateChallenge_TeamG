"""
Flurry: shared visual theme for the single-page Streamlit app.

Purpose:
    Style the app after the approved mockup (documents/ui_design/) using the
    Government of Canada design language (design.canada.ca): a full-width
    accent-blue navigation bar containing the brand, the page tabs, and the
    pilot label; a mostly white page; flat white bordered "card" surfaces;
    Lato headings with Noto Sans body text; and Canada.ca link colours.

Inputs and outputs:
    apply_theme() injects one global CSS block and a hidden page heading.
    render_kpi_row() renders statistic cards from (value, label, color) rows.

State and side effects:
    Neither function reads nor writes session state or files. apply_theme()
    causes the browser to load the Lato font family from Google Fonts.

Assumptions and limitations:
    Colour values follow design.canada.ca/styles/colours.html and the
    contextual-alerts pattern; this adapts the design language and is not an
    official Government of Canada page (no FIP signature or wordmark).
    CSS targets Streamlit's data-testid and React Aria attributes, which are
    not a stable public API; selectors may need updates after upgrading
    Streamlit. The brand and pilot labels in the navigation bar are
    decorative CSS content; the hidden heading keeps the page title
    available to assistive technology.
"""

import html

import streamlit as st

# Canada.ca colours (design.canada.ca/styles/colours.html)
GC_ACCENT = "#26374A"         # main accent: navigation bar, strong numbers
GC_ACCENT_HOVER = "#3B4B5C"   # lightened accent for navigation hover
GC_TEXT = "#333333"           # dark-grey body text
GC_LINK = "#284162"           # default link
GC_LINK_ACTIVE = "#0535D2"    # link on hover or focus; focus indicators
GC_LINK_VISITED = "#7834BC"   # visited link
GC_ERROR_RED = "#D3080C"      # form error or required element indicator
GC_WARNING = "#EE7100"        # contextual warning alert accent
GC_BORDER = "#D4D4D4"         # quiet card and widget borders

# Half of the content max-width; aligns navigation content with the page
_CONTENT_MAX_PX = 1360
_CONTENT_HALF_PX = _CONTENT_MAX_PX // 2


def apply_theme():
    """
    Inject the global look: accent navigation bar, white page, flat cards.

    Side effects:
        Add one CSS block and one visually hidden page heading to the page;
        the CSS imports the Lato heading font from Google Fonts.
    Returns:
        None.
    """
    st.html(f"""
        <h1 class="flurry-sr-only">Flurry — St. John's snow-clearing pilot</h1>
        <style>
        /* Canada.ca heading typeface; body text uses Noto Sans from config */
        @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

        /* Keep the page title for assistive technology without showing it */
        .flurry-sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            overflow: hidden;
            clip-path: inset(50%);
            white-space: nowrap;
        }}

        /* The navy tab bar below replaces Streamlit's default header */
        header[data-testid="stHeader"] {{
            display: none;
        }}

        /* Hide the overflow from the full-bleed navigation bar */
        [data-testid="stMain"] {{
            overflow-x: hidden;
        }}

        .stApp {{
            background: #FFFFFF;
        }}

        /* Canada.ca link colours, including hover, focus, and visited */
        [data-testid="stMain"] a {{
            color: {GC_LINK};
        }}
        [data-testid="stMain"] a:visited {{
            color: {GC_LINK_VISITED};
        }}
        [data-testid="stMain"] a:hover,
        [data-testid="stMain"] a:focus {{
            color: {GC_LINK_ACTIVE};
        }}

        .block-container {{
            max-width: {_CONTENT_MAX_PX}px;
            padding-top: 0;
            padding-bottom: 3rem;
        }}

        /* Full-bleed accent bar holding the brand, tabs, and pilot label */
        .stTabs [role="tablist"] {{
            background: {GC_ACCENT};
            margin: 0 calc(50% - 50vw) 1.25rem;
            padding: 0 max(calc(50vw - {_CONTENT_HALF_PX}px), 1.5rem);
            gap: 0;
            align-items: center;
            border-bottom: none;
        }}
        .stTabs [role="tablist"]::before {{
            content: "Flurry";
            color: #FFFFFF;
            font-family: 'Lato', 'Noto Sans', Arial, sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            margin-right: 1.5rem;
        }}
        /* Streamlit uses this pseudo-element as a 2px underline strip;
           restore normal flow so it can hold the pilot label instead */
        .stTabs [role="tablist"]::after {{
            content: "Pilot: St. John\\2019s NL";
            position: static;
            width: auto;
            height: auto;
            background: none;
            color: #FFFFFF;
            margin-left: auto;
        }}
        .stTabs [data-testid="stTab"] {{
            background: transparent;
            padding: 16px;
            border-radius: 0;
            border-bottom: 4px solid transparent;
            transition: background-color 0.15s;
        }}
        .stTabs [data-testid="stTab"] p {{
            color: #FFFFFF !important;
            font-weight: 600;
            font-size: 1rem;
        }}
        .stTabs [data-testid="stTab"]:hover {{
            background: {GC_ACCENT_HOVER};
            border-bottom-color: #FFFFFF;
        }}
        .stTabs [data-testid="stTab"]:focus-visible {{
            outline: 3px solid #99C9FF;
            outline-offset: -3px;
        }}
        /* White underline marking the active tab */
        .stTabs [data-testid="stTab"][aria-selected="true"] {{
            border-bottom-color: #FFFFFF;
        }}
        .stTabs .react-aria-SelectionIndicator {{
            display: none;
        }}

        /* Keyed card containers and forms become flat white bordered cards */
        [data-testid="stVerticalBlock"][class*="st-key-card-"],
        [data-testid="stForm"] {{
            background: #FFFFFF;
            border: 1px solid {GC_BORDER};
            border-radius: 6px;
            padding: 1.25rem;
        }}

        /* Statistic cards: large coloured number over a quiet label */
        .flurry-kpi-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }}
        .flurry-kpi-card {{
            background: #FFFFFF;
            border: 1px solid {GC_BORDER};
            border-radius: 6px;
            padding: 1rem 1.25rem;
        }}
        .flurry-kpi-value {{
            font-family: 'Lato', 'Noto Sans', Arial, sans-serif;
            font-size: 1.875rem;
            font-weight: 700;
            line-height: 1.2;
        }}
        .flurry-kpi-label {{
            color: {GC_TEXT};
        }}
        </style>
    """)


def render_kpi_row(cards: list[tuple[str, str, str]]):
    """
    Render one row of white statistic cards styled after the design.

    Parameters:
        cards: One (value, label, color) entry per card, in display order.
    Returns:
        None. The row is added to the current Streamlit container.
    """
    items = "".join(
        f"<div class='flurry-kpi-card'>"
        f"<div class='flurry-kpi-value' style='color:{html.escape(color)}'>"
        f"{html.escape(str(value))}</div>"
        f"<div class='flurry-kpi-label'>{html.escape(label)}</div></div>"
        for value, label, color in cards
    )
    st.html(f"<div class='flurry-kpi-row'>{items}</div>")
