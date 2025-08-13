# ───────────────────────────────
# Graph Container Styles
# ───────────────────────────────
# Styles for the main graph visualization container.
GRAPH_CONTAINER_STYLE = {
    "backgroundColor": "#d1e8ec",
    "padding": "10px",
    "borderRadius": "10px",
    "boxShadow": "2px 2px 10px rgba(0,0,0,0.1)",
    "cursor": "grab",
    "position": "relative",
    "height": "calc(100vh - 120px)",
    "width": "100%"
}

# ───────────────────────────────
# Toolbar Styles
# ───────────────────────────────
# Sticky toolbar at the top of the page for graph controls.
TOOLBAR_STYLE = {
    "position": "sticky",
    "top": 0,
    "zIndex": 999,
    "marginBottom": "10px"
}

# Fixed button height style for uniformity across buttons
BUTTON_FIXED_HEIGHT_STYLE = {"height": "40px"}

# ───────────────────────────────
# Table Container Styles
# ───────────────────────────────
# Styles for the collapsible table at the bottom of the page.
TABLE_CONTAINER_STYLE = {
    "position": "absolute",
    "bottom": 0,
    "left": 0,
    "right": 0,
    "height": 0,
    "zIndex": 998,
    "backgroundColor": "white",
    "overflowY": "auto",
    "padding": "10px",
    "transition": "height 0.3s ease, width 0.3s ease",
}

# Expanded state of the bottom table container
TABLE_CONTAINER_EXPANDED_STYLE = TABLE_CONTAINER_STYLE.copy()
TABLE_CONTAINER_EXPANDED_STYLE.update({
    "height": "300px",
    "marginRight": "400px",
    "width": "calc(100% - 400px)"
})

# ───────────────────────────────
# Side Button Styles
# ───────────────────────────────
# Styles for the side toggle button that expands/collapses the side panel.
SIDE_BUTTON_STYLE = {
    "position": "fixed",
    "top": "50%",
    "right": "-1.75vw",
    "transform": "translateY(-50%) rotate(-90deg)",
    "transformOrigin": "center",
    "zIndex": 1100,
    "backgroundColor": "#28a745",
    "color": "white",
    "border": "none",
    "borderRadius": "5px",
    "boxShadow": "0 2px 5px rgba(0,0,0,0.2)",
    "height": "40px",
    "width": "120px",
    "fontWeight": "bold",
    "cursor": "pointer",
    "textAlign": "center",
    "whiteSpace": "nowrap",
}

# ───────────────────────────────
# Side Panel Styles
# ───────────────────────────────
# Styles for the side panel (collapsed state).
SIDE_PANEL_STYLE = {
    "position": "absolute",
    "top": "0",
    "bottom": "0",
    "right": "0",
    "width": "0px",
    "backgroundColor": "#f5f7f9",
    "borderLeft": "2px solid #ddd",
    "overflowX": "hidden",
    "overflowY": "auto",
    "transition": "width 0.3s ease",
    "zIndex": 1099,
    "padding": "0"
}

# Expanded state of the side panel
SIDE_PANEL_EXPANDED_STYLE = SIDE_PANEL_STYLE.copy()
SIDE_PANEL_EXPANDED_STYLE.update({
    "width": "400px",
    "padding": "0px"
})