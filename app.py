import math
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Gaelic Football Pitch Maps", layout="wide")


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def safe_col_lookup(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def first_existing(df: pd.DataFrame, groups: list[list[str]], required: bool = True) -> Optional[str]:
    for group in groups:
        found = safe_col_lookup(df, group)
        if found:
            return found
    if required:
        raise KeyError(f"Could not find any of these columns: {groups}")
    return None


import math
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Gaelic Football Pitch Maps", layout="wide")


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def safe_col_lookup(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def first_existing(df: pd.DataFrame, groups: list[list[str]], required: bool = True) -> Optional[str]:
    for group in groups:
        found = safe_col_lookup(df, group)
        if found:
            return found
    if required:
        raise KeyError(f"Could not find any of these columns: {groups}")
    return None


def build_pitch_shapes() -> list[dict]:
    """Build a vertical Gaelic football pitch using the app's 0-100 screen coordinates."""
    shapes: list[dict] = []
    line = dict(color="#E8E8E8", width=2)
    dashed = dict(color="#E8E8E8", width=2, dash="dash")

    # Scale real pitch dimensions into 0..100 image coordinates.
    # We only need consistent proportions to match the screenshot layout.
    pitch_len = 145.0
    pitch_wid = 100.0

    def sx(m: float) -> float:
        return (m / pitch_wid) * 100.0

    def sy(m: float) -> float:
        return (m / pitch_len) * 100.0

    # Key lines from each endline
    y13 = sy(13)
    y20 = sy(20)
    y45 = sy(45)
    y50 = 50.0
    y100_13 = 100.0 - y13
    y100_20 = 100.0 - y20
    y100_45 = 100.0 - y45

    # Goal / rectangle widths (approx GAA dimensions)
    large_w = sx(40.0)
    small_w = sx(14.0)
    goal_w = sx(6.5)
    cx = 50.0

    # Outer boundary
    shapes.append(dict(type="rect", x0=0, y0=0, x1=100, y1=100, line=line))

    # Horizontal lines
    for y in [y13, y20, y45, y100_45, y100_20, y100_13]:
        shapes.append(dict(type="line", x0=0, y0=y, x1=100, y1=y, line=line))
    shapes.append(dict(type="line", x0=0, y0=y50, x1=100, y1=y50, line=dashed))

    # Top rectangles + goal
    shapes.append(dict(type="rect", x0=cx - large_w / 2, y0=0, x1=cx + large_w / 2, y1=y13, line=line))
    shapes.append(dict(type="rect", x0=cx - small_w / 2, y0=0, x1=cx + small_w / 2, y1=sy(4.5), line=line))
    shapes.append(dict(type="line", x0=cx - goal_w / 2, y0=0, x1=cx - goal_w / 2, y1=sy(1.0), line=line))
    shapes.append(dict(type="line", x0=cx + goal_w / 2, y0=0, x1=cx + goal_w / 2, y1=sy(1.0), line=line))

    # Bottom rectangles + goal
    shapes.append(dict(type="rect", x0=cx - large_w / 2, y0=y100_13, x1=cx + large_w / 2, y1=100, line=line))
    shapes.append(dict(type="rect", x0=cx - small_w / 2, y0=100 - sy(4.5), x1=cx + small_w / 2, y1=100, line=line))
    shapes.append(dict(type="line", x0=cx - goal_w / 2, y0=100, x1=cx - goal_w / 2, y1=100 - sy(1.0), line=line))
    shapes.append(dict(type="line", x0=cx + goal_w / 2, y0=100, x1=cx + goal_w / 2, y1=100 - sy(1.0), line=line))

    # Arc helper: semi-circle / clipped circle path using many points.
    def circle_arc_path(cx0: float, cy0: float, r: float, start_deg: float, end_deg: float, steps: int = 120) -> str:
        pts = []
        for i in range(steps + 1):
            t = math.radians(start_deg + (end_deg - start_deg) * i / steps)
            x = cx0 + r * math.cos(t)
            y = cy0 + r * math.sin(t)
            pts.append((x, y))
        path = f"M {pts[0][0]},{pts[0][1]}"
        for x, y in pts[1:]:
            path += f" L {x},{y}"
        return path

    r13 = sy(13)
    r40 = sy(40)

    # 13m semi-circles centred on 20m lines, visible away from the goals.
    shapes.append(dict(type="path", path=circle_arc_path(cx, y20, r13, 0, 180), line=line))
    shapes.append(dict(type="path", path=circle_arc_path(cx, y100_20, r13, 180, 360), line=line))

    # 40m arcs centred on endlines, visible only beyond the 20m lines.
    theta = math.degrees(math.asin(20.0 / 40.0))
    shapes.append(dict(type="path", path=circle_arc_path(cx, 0.0, r40, theta, 180 - theta), line=line))
    shapes.append(dict(type="path", path=circle_arc_path(cx, 100.0, r40, 180 + theta, 360 - theta), line=line))

return shapes


def add_pitch_labels(fig: go.Figure) -> None:
    fig.add_annotation(x=50, y=14.7, text="Ballintubber GOAL", showarrow=False,
                       font=dict(size=28, color="rgba(255,255,255,0.42)"))
    fig.add_annotation(x=50, y=85.3, text="Parke GOAL", showarrow=False,
                       font=dict(size=28, color="rgba(0,0,0,0.42)"))


def make_pitch_figure(title: str = "") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        shapes=build_pitch_shapes(),
        plot_bgcolor="#4A8242",
        paper_bgcolor="#4A8242",
        margin=dict(l=8, r=8, t=50, b=8),
        height=950,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.0)",
            font=dict(size=14),
        ),
    )
    fig.update_xaxes(range=[0, 100], visible=False, fixedrange=True)
    fig.update_yaxes(range=[100, 0], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
    add_pitch_labels(fig)
    return fig


def normalize_outcome(value: str) -> str:
    v = str(value).strip().lower()
    if "goal" in v:
        return "goal"
    if "2" in v and "point" in v:
        return "2 pointer"
    if "point" in v:
        return "point"
    if "wide" in v:
        return "wide"
    if "post" in v:
        return "off posts"
    if "45" in v or "65" in v:
        return "out for 45/65"
    if "save" in v or "saved" in v:
        return "saved"
    if "short" in v:
        return "short"
    if "won" in v:
        return "won"
    if "lost" in v:
        return "lost"
    return str(value)


def event_palette() -> dict[str, str]:
    return {
        "goal": "#15FF00",
        "point": "#F5A300",
        "2 pointer": "#A39A00",
        "wide": "#FF3B30",
        "off posts": "#A8A8A8",
        "out for 45/65": "#20D5E8",
        "saved": "#1886F7",
        "short": "#E85BF7",
        "won": "#15FF00",
        "lost": "#FF3B30",
    }


def add_numbered_markers(
    fig: go.Figure,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str,
    category_col: str,
    placed_ball_col: Optional[str] = None,
) -> None:
    palette = event_palette()

    df = df.copy()
    df[category_col] = df[category_col].map(normalize_outcome)

    for category, group in df.groupby(category_col, dropna=False):
        color = palette.get(str(category), "#000000")
        border_width = 1 if category in {"goal", "won"} else 2

        text_color = []
        for _, row in group.iterrows():
            placed = False
            if placed_ball_col and placed_ball_col in group.columns:
                placed = str(row.get(placed_ball_col, "")).strip().lower() in {"1", "true", "yes", "y", "placed", "free", "penalty", "45", "65", "sideline"}
            text_color.append("white" if placed else "black")

        fig.add_trace(
            go.Scatter(
                x=group[x_col],
                y=group[y_col],
                mode="markers+text",
                name=str(category),
                text=group[label_col].astype(str),
                textposition="middle center",
                textfont=dict(color=text_color, size=13, family="Arial Black"),
                marker=dict(
                    size=26,
                    color=color,
                    line=dict(color="#E8E8E8", width=border_width),
                ),
                hovertemplate=(
                    "#%{text}<br>"
                    + f"{x_col}: %{{x:.1f}}<br>{y_col}: %{{y:.1f}}"
                    + "<extra></extra>"
                ),
            )
        )


def infer_columns(df: pd.DataFrame) -> dict[str, Optional[str]]:
    cols = {
        "x": first_existing(df, [["x_posn_%"], ["x_posn"], ["x"], ["xpos"]]),
        "y": first_existing(df, [["y_posn_%"], ["y_posn"], ["y"], ["ypos"]]),
        "team": first_existing(df, [["team"], ["team_name"], ["club"], ["side"]], required=False),
        "player": first_existing(df, [["player"], ["player_name"], ["name"]], required=False),
        "event": first_existing(df, [["event_type"], ["event"], ["action"]], required=False),
        "outcome": first_existing(df, [["outcome"], ["result"], ["event_outcome"], ["shot_result"], ["status"]], required=False),
        "number": first_existing(df, [["event_no"], ["event_number"], ["number"], ["id"]], required=False),
        "half": first_existing(df, [["half"], ["period"]], required=False),
        "minute": first_existing(df, [["minute"], ["mins"], ["time_minute"]], required=False),
        "match": first_existing(df, [["match"], ["match_name"], ["fixture"]], required=False),
        "placed_ball": first_existing(df, [["placed_ball"], ["dead_ball"], ["is_placed_ball"], ["restart_type"]], required=False),
    }
    return cols


def build_display_number(df: pd.DataFrame, number_col: Optional[str]) -> pd.Series:
    if number_col and number_col in df.columns:
        return df[number_col].astype(str)
    return pd.Series(range(1, len(df) + 1), index=df.index).astype(str)


# ------------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------------

st.title("Gaelic Football Pitch Maps")
st.caption("Pitch layout matched to your Scores Stats Plus screenshots. Uses x_posn_% left→right and y_posn_% top→bottom.")

uploaded = st.file_uploader("Upload GAAScores match events CSV", type=["csv"])

with st.expander("Expected coordinates"):
    st.write(
        """
        - `x_posn_%`: 0 at the left sideline, 100 at the right sideline
        - `y_posn_%`: 0 at the Ballintubber goal end at the top of the image, 100 at the Parke goal end at the bottom
        - This app keeps the same screen-style coordinate system as your Android output
        """
    )

if not uploaded:
    st.info("Upload your CSV to start plotting shots or kickouts.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except UnicodeDecodeError:
    uploaded.seek(0)
    df = pd.read_csv(uploaded, encoding="latin1")

st.subheader("Raw data preview")
st.dataframe(df.head(20), use_container_width=True)

try:
    cols = infer_columns(df)
except KeyError as exc:
    st.error(str(exc))
    st.stop()

# Create helper columns
plot_df = df.copy()
plot_df["__plot_number__"] = build_display_number(plot_df, cols["number"])

if cols["outcome"] is None and cols["event"] is not None:
    plot_df["__plot_category__"] = plot_df[cols["event"]].astype(str)
    cols["outcome"] = "__plot_category__"
elif cols["outcome"] is None:
    plot_df["__plot_category__"] = "event"
    cols["outcome"] = "__plot_category__"

# Sidebar filters
st.sidebar.header("Filters")

if cols["match"]:
    matches = ["All"] + sorted(plot_df[cols["match"]].dropna().astype(str).unique().tolist())
    match_choice = st.sidebar.selectbox("Match", matches)
    if match_choice != "All":
        plot_df = plot_df[plot_df[cols["match"]].astype(str) == match_choice]

if cols["team"]:
    teams = ["All"] + sorted(plot_df[cols["team"]].dropna().astype(str).unique().tolist())
    team_choice = st.sidebar.selectbox("Team", teams)
    if team_choice != "All":
        plot_df = plot_df[plot_df[cols["team"]].astype(str) == team_choice]

if cols["player"]:
    players = ["All"] + sorted(plot_df[cols["player"]].dropna().astype(str).unique().tolist())
    player_choice = st.sidebar.selectbox("Player", players)
    if player_choice != "All":
        plot_df = plot_df[plot_df[cols["player"]].astype(str) == player_choice]

if cols["half"]:
    halves = ["All"] + sorted(plot_df[cols["half"]].dropna().astype(str).unique().tolist())
    half_choice = st.sidebar.selectbox("Half", halves)
    if half_choice != "All":
        plot_df = plot_df[plot_df[cols["half"]].astype(str) == half_choice]

mode = st.sidebar.radio("Map type", ["All events", "Shots", "Kickouts"], index=0)

if cols["event"]:
    event_series = plot_df[cols["event"]].astype(str).str.lower()
    if mode == "Shots":
        shot_mask = event_series.str.contains("shot|score|point|goal|wide|short|saved|post", na=False)
        plot_df = plot_df[shot_mask]
    elif mode == "Kickouts":
        ko_mask = event_series.str.contains("kick ?out|puck ?out", na=False)
        plot_df = plot_df[ko_mask]

outcomes = ["All"] + sorted(plot_df[cols["outcome"]].dropna().map(normalize_outcome).astype(str).unique().tolist())
outcome_choice = st.sidebar.selectbox("Outcome", outcomes)
if outcome_choice != "All":
    plot_df = plot_df[plot_df[cols["outcome"]].map(normalize_outcome) == outcome_choice]

# Numeric cleanup
for c in [cols["x"], cols["y"]]:
    plot_df[c] = pd.to_numeric(plot_df[c], errors="coerce")
plot_df = plot_df.dropna(subset=[cols["x"], cols["y"]])
plot_df = plot_df[(plot_df[cols["x"]] >= 0) & (plot_df[cols["x"]] <= 100) & (plot_df[cols["y"]] >= 0) & (plot_df[cols["y"]] <= 100)]

summary1, summary2, summary3 = st.columns(3)
summary1.metric("Events shown", len(plot_df))
summary2.metric("Unique players", plot_df[cols["player"]].nunique() if cols["player"] else "-")
summary3.metric("Unique outcomes", plot_df[cols["outcome"]].map(normalize_outcome).nunique())

fig = make_pitch_figure(title="Pitch Map")

if len(plot_df):
    add_numbered_markers(
        fig,
        plot_df,
        cols["x"],
        cols["y"],
        "__plot_number__",
        cols["outcome"],
        cols["placed_ball"],
    )
else:
    st.warning("No events left after filtering.")

st.plotly_chart(fig, use_container_width=True)

with st.expander("Filtered events table"):
    visible_cols = [c for c in [cols["match"], cols["team"], cols["player"], cols["event"], cols["outcome"], cols["half"], cols["minute"], cols["x"], cols["y"]] if c]
    st.dataframe(plot_df[visible_cols], use_container_width=True)

st.markdown("### Notes")
st.write(
    """
    This pitch is built to match your app layout visually, not as an exact engineering drawing.
    The important thing is that it uses the same coordinate frame as your CSV, so events land in the same places.
    """
)

st.markdown("### Next upgrades")
st.write(
    """
    - normalize all shots so teams always attack the same goal
    - add arrowed kickout trajectories when a landing-point column exists
    - add player trend views by opponent, half, and outcome
    - add shot-distance and zone summaries
    """
)


    return shapes


def add_pitch_labels(fig: go.Figure) -> None:
    fig.add_annotation(x=50, y=14.7, text="Ballintubber GOAL", showarrow=False,
                       font=dict(size=28, color="rgba(255,255,255,0.42)"))
    fig.add_annotation(x=50, y=85.3, text="Parke GOAL", showarrow=False,
                       font=dict(size=28, color="rgba(0,0,0,0.42)"))


def make_pitch_figure(title: str = "") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        shapes=build_pitch_shapes(),
        plot_bgcolor="#4A8242",
        paper_bgcolor="#4A8242",
        margin=dict(l=8, r=8, t=50, b=8),
        height=950,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.0)",
            font=dict(size=14),
        ),
    )
    fig.update_xaxes(range=[0, 100], visible=False, fixedrange=True)
    fig.update_yaxes(range=[100, 0], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
    add_pitch_labels(fig)
    return fig


def normalize_outcome(value: str) -> str:
    v = str(value).strip().lower()
    if "goal" in v:
        return "goal"
    if "2" in v and "point" in v:
        return "2 pointer"
    if "point" in v:
        return "point"
    if "wide" in v:
        return "wide"
    if "post" in v:
        return "off posts"
    if "45" in v or "65" in v:
        return "out for 45/65"
    if "save" in v or "saved" in v:
        return "saved"
    if "short" in v:
        return "short"
    if "won" in v:
        return "won"
    if "lost" in v:
        return "lost"
    return str(value)


def event_palette() -> dict[str, str]:
    return {
        "goal": "#15FF00",
        "point": "#F5A300",
        "2 pointer": "#A39A00",
        "wide": "#FF3B30",
        "off posts": "#A8A8A8",
        "out for 45/65": "#20D5E8",
        "saved": "#1886F7",
        "short": "#E85BF7",
        "won": "#15FF00",
        "lost": "#FF3B30",
    }


def add_numbered_markers(
    fig: go.Figure,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str,
    category_col: str,
    placed_ball_col: Optional[str] = None,
) -> None:
    palette = event_palette()

    df = df.copy()
    df[category_col] = df[category_col].map(normalize_outcome)

    for category, group in df.groupby(category_col, dropna=False):
        color = palette.get(str(category), "#000000")
        border_width = 1 if category in {"goal", "won"} else 2

        text_color = []
        for _, row in group.iterrows():
            placed = False
            if placed_ball_col and placed_ball_col in group.columns:
                placed = str(row.get(placed_ball_col, "")).strip().lower() in {"1", "true", "yes", "y", "placed", "free", "penalty", "45", "65", "sideline"}
            text_color.append("white" if placed else "black")

        fig.add_trace(
            go.Scatter(
                x=group[x_col],
                y=group[y_col],
                mode="markers+text",
                name=str(category),
                text=group[label_col].astype(str),
                textposition="middle center",
                textfont=dict(color=text_color, size=13, family="Arial Black"),
                marker=dict(
                    size=26,
                    color=color,
                    line=dict(color="#E8E8E8", width=border_width),
                ),
                hovertemplate=(
                    "#%{text}<br>"
                    + f"{x_col}: %{{x:.1f}}<br>{y_col}: %{{y:.1f}}"
                    + "<extra></extra>"
                ),
            )
        )


def infer_columns(df: pd.DataFrame) -> dict[str, Optional[str]]:
    cols = {
        "x": first_existing(df, [["x_posn_%"], ["x_posn"], ["x"], ["xpos"]]),
        "y": first_existing(df, [["y_posn_%"], ["y_posn"], ["y"], ["ypos"]]),
        "team": first_existing(df, [["team"], ["team_name"], ["club"], ["side"]], required=False),
        "player": first_existing(df, [["player"], ["player_name"], ["name"]], required=False),
        "event": first_existing(df, [["event_type"], ["event"], ["action"]], required=False),
        "outcome": first_existing(df, [["outcome"], ["result"], ["event_outcome"], ["shot_result"], ["status"]], required=False),
        "number": first_existing(df, [["event_no"], ["event_number"], ["number"], ["id"]], required=False),
        "half": first_existing(df, [["half"], ["period"]], required=False),
        "minute": first_existing(df, [["minute"], ["mins"], ["time_minute"]], required=False),
        "match": first_existing(df, [["match"], ["match_name"], ["fixture"]], required=False),
        "placed_ball": first_existing(df, [["placed_ball"], ["dead_ball"], ["is_placed_ball"], ["restart_type"]], required=False),
    }
    return cols


def build_display_number(df: pd.DataFrame, number_col: Optional[str]) -> pd.Series:
    if number_col and number_col in df.columns:
        return df[number_col].astype(str)
    return pd.Series(range(1, len(df) + 1), index=df.index).astype(str)


# ------------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------------

st.title("Gaelic Football Pitch Maps")
st.caption("Pitch layout matched to your Scores Stats Plus screenshots. Uses x_posn_% left→right and y_posn_% top→bottom.")

uploaded = st.file_uploader("Upload GAAScores match events CSV", type=["csv"])

with st.expander("Expected coordinates"):
    st.write(
        """
        - `x_posn_%`: 0 at the left sideline, 100 at the right sideline
        - `y_posn_%`: 0 at the Ballintubber goal end at the top of the image, 100 at the Parke goal end at the bottom
        - This app keeps the same screen-style coordinate system as your Android output
        """
    )

if not uploaded:
    st.info("Upload your CSV to start plotting shots or kickouts.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except UnicodeDecodeError:
    uploaded.seek(0)
    df = pd.read_csv(uploaded, encoding="latin1")

st.subheader("Raw data preview")
st.dataframe(df.head(20), use_container_width=True)

try:
    cols = infer_columns(df)
except KeyError as exc:
    st.error(str(exc))
    st.stop()

# Create helper columns
plot_df = df.copy()
plot_df["__plot_number__"] = build_display_number(plot_df, cols["number"])

if cols["outcome"] is None and cols["event"] is not None:
    plot_df["__plot_category__"] = plot_df[cols["event"]].astype(str)
    cols["outcome"] = "__plot_category__"
elif cols["outcome"] is None:
    plot_df["__plot_category__"] = "event"
    cols["outcome"] = "__plot_category__"

# Sidebar filters
st.sidebar.header("Filters")

if cols["match"]:
    matches = ["All"] + sorted(plot_df[cols["match"]].dropna().astype(str).unique().tolist())
    match_choice = st.sidebar.selectbox("Match", matches)
    if match_choice != "All":
        plot_df = plot_df[plot_df[cols["match"]].astype(str) == match_choice]

if cols["team"]:
    teams = ["All"] + sorted(plot_df[cols["team"]].dropna().astype(str).unique().tolist())
    team_choice = st.sidebar.selectbox("Team", teams)
    if team_choice != "All":
        plot_df = plot_df[plot_df[cols["team"]].astype(str) == team_choice]

if cols["player"]:
    players = ["All"] + sorted(plot_df[cols["player"]].dropna().astype(str).unique().tolist())
    player_choice = st.sidebar.selectbox("Player", players)
    if player_choice != "All":
        plot_df = plot_df[plot_df[cols["player"]].astype(str) == player_choice]

if cols["half"]:
    halves = ["All"] + sorted(plot_df[cols["half"]].dropna().astype(str).unique().tolist())
    half_choice = st.sidebar.selectbox("Half", halves)
    if half_choice != "All":
        plot_df = plot_df[plot_df[cols["half"]].astype(str) == half_choice]

mode = st.sidebar.radio("Map type", ["All events", "Shots", "Kickouts"], index=0)

if cols["event"]:
    event_series = plot_df[cols["event"]].astype(str).str.lower()
    if mode == "Shots":
        shot_mask = event_series.str.contains("shot|score|point|goal|wide|short|saved|post", na=False)
        plot_df = plot_df[shot_mask]
    elif mode == "Kickouts":
        ko_mask = event_series.str.contains("kick ?out|puck ?out", na=False)
        plot_df = plot_df[ko_mask]

outcomes = ["All"] + sorted(plot_df[cols["outcome"]].dropna().map(normalize_outcome).astype(str).unique().tolist())
outcome_choice = st.sidebar.selectbox("Outcome", outcomes)
if outcome_choice != "All":
    plot_df = plot_df[plot_df[cols["outcome"]].map(normalize_outcome) == outcome_choice]

# Numeric cleanup
for c in [cols["x"], cols["y"]]:
    plot_df[c] = pd.to_numeric(plot_df[c], errors="coerce")
plot_df = plot_df.dropna(subset=[cols["x"], cols["y"]])
plot_df = plot_df[(plot_df[cols["x"]] >= 0) & (plot_df[cols["x"]] <= 100) & (plot_df[cols["y"]] >= 0) & (plot_df[cols["y"]] <= 100)]

summary1, summary2, summary3 = st.columns(3)
summary1.metric("Events shown", len(plot_df))
summary2.metric("Unique players", plot_df[cols["player"]].nunique() if cols["player"] else "-")
summary3.metric("Unique outcomes", plot_df[cols["outcome"]].map(normalize_outcome).nunique())

fig = make_pitch_figure(title="Pitch Map")

if len(plot_df):
    add_numbered_markers(
        fig,
        plot_df,
        cols["x"],
        cols["y"],
        "__plot_number__",
        cols["outcome"],
        cols["placed_ball"],
    )
else:
    st.warning("No events left after filtering.")

st.plotly_chart(fig, use_container_width=True)

with st.expander("Filtered events table"):
    visible_cols = [c for c in [cols["match"], cols["team"], cols["player"], cols["event"], cols["outcome"], cols["half"], cols["minute"], cols["x"], cols["y"]] if c]
    st.dataframe(plot_df[visible_cols], use_container_width=True)

st.markdown("### Notes")
st.write(
    """
    This pitch is built to match your app layout visually, not as an exact engineering drawing.
    The important thing is that it uses the same coordinate frame as your CSV, so events land in the same places.
    """
)

st.markdown("### Next upgrades")
st.write(
    """
    - normalize all shots so teams always attack the same goal
    - add arrowed kickout trajectories when a landing-point column exists
    - add player trend views by opponent, half, and outcome
    - add shot-distance and zone summaries
    """
)

