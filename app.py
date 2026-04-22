import math
from typing import Optional
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Gaelic Football Pitch Maps", layout="wide")

st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            width: 20% !important;
        }
    </style>
""", unsafe_allow_html=True)

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
    shapes: list[dict] = []
    line = dict(color="#E8E8E8", width=2)
    dashed = dict(color="#E8E8E8", width=2, dash="dash")

    # The original app image has margins left/right of the pitch.
    x_left = 4.0
    x_right = 96.0

    # Real pitch dimensions
    pitch_len = 145.0
    pitch_wid = 80.0

    def sw(m: float) -> float:
        return (m / pitch_wid) * (x_right - x_left)

    def sy(m: float) -> float:
        return (m / pitch_len) * 100.0

    # Horizontal lines from each endline
    y13 = sy(13)
    y20 = sy(20)
    y45 = sy(45)
    y50 = 50.0
    y100_13 = 100.0 - y13
    y100_20 = 100.0 - y20
    y100_45 = 100.0 - y45

    # Widths
    large_w = sw(19.0)   # keep these outer vertical lines 19m apart
    small_w = sw(14.0)
    goal_w = sw(6.5)
    cx = 50.0

    # Outer boundary of the pitch
    shapes.append(dict(type="rect", x0=x_left, y0=0, x1=x_right, y1=100, line=line))

    # Horizontal lines
    for y in [y13, y20, y45, y100_45, y100_20, y100_13]:
        shapes.append(dict(type="line", x0=x_left, y0=y, x1=x_right, y1=y, line=line))

    shapes.append(dict(type="line", x0=x_left, y0=y50, x1=x_right, y1=y50, line=dashed))

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

    def ellipse_arc_path(
        cx0: float,
        cy0: float,
        rx: float,
        ry: float,
        start_deg: float,
        end_deg: float,
        steps: int = 120,
    ) -> str:
        pts = []
        for i in range(steps + 1):
            t = math.radians(start_deg + (end_deg - start_deg) * i / steps)
            x = cx0 + rx * math.cos(t)
            y = cy0 + ry * math.sin(t)
            pts.append((x, y))

        path = f"M {pts[0][0]},{pts[0][1]}"
        for x, y in pts[1:]:
            path += f" L {x},{y}"
        return path

    # 13m semi-circle from 20m line
    rx13 = sw(13.0)
    ry13 = sy(13.0)

    shapes.append(dict(type="path", path=ellipse_arc_path(cx, y20, rx13, ry13, 0, 180), line=line))
    shapes.append(dict(type="path", path=ellipse_arc_path(cx, y100_20, rx13, ry13, 180, 360), line=line))

    # 40m arcs centred on endlines, clipped beyond 20m line
    rx40 = sw(40.0)
    ry40 = sy(40.0)
    theta = math.degrees(math.asin(20.0 / 40.0))

    shapes.append(dict(type="path", path=ellipse_arc_path(cx, 0.0, rx40, ry40, theta, 180 - theta), line=line))
    shapes.append(dict(type="path", path=ellipse_arc_path(cx, 100.0, rx40, ry40, 180 + theta, 360 - theta), line=line))

    return shapes


def add_pitch_labels(fig: go.Figure) -> None:
    fig.add_annotation(
        x=50,
        y=15,
        text="Ballintubber GOAL",
        showarrow=False,
        font=dict(size=24, color="rgba(255,255,255,0.42)"),
    )
    fig.add_annotation(
        x=50,
        y=85,
        text="Opposition GOAL",
        showarrow=False,
        font=dict(size=24, color="rgba(0,0,0,0.42)"),
    )


def make_pitch_figure(title: str = "Pitch Map") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        shapes=build_pitch_shapes(),
        plot_bgcolor="#4A8242",
        paper_bgcolor="#4A8242",
        margin=dict(l=20, r=8, t=40, b=8),
        height=950,
        width=900,
showlegend=False,
    )
    fig.update_xaxes(range=[3.5, 96.5], visible=False, fixedrange=True)
    fig.update_yaxes(range=[100, 0], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
    add_pitch_labels(fig)
    return fig


def normalize_outcome(value):
    if pd.isna(value) or str(value).strip().lower() in ["", "nan", "none"]:
        return None

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
        return "out for 45"
    if "save" in v or "saved" in v:
        return "saved"
    if "short" in v:
        return "short"
    if "turnover won" in v:
        return "turnover won"
    if "turnover lost" in v:
        return "turnover lost"
    if "won" in v:
        return "KO won"
    if "lost" in v:
        return "KO lost"
    if "free/pen conceded" in v:
        return "free conceded"

    return v


def event_palette() -> dict[str, str]:
    return {
        "goal": "#15FF00",
        "point": "#F5A300",
        "2 pointer": "#A39A00",
        "wide": "#FF3B30",
        "off posts": "#A8A8A8",
        "out for 45": "#20D5E8",
        "saved": "#1886F7",
        "short": "#E85BF7",
        "KO won": "#15FF00",
        "KO lost": "#FF3B30",
        "turnover won": "#15FF00",
        "turnover lost": "#FF3B30",
    }

def event_palette_all() -> dict[str, str]:
    return {
        "goal": "#00C853",
        "point": "#FFB300",
        "2 pointer": "#8E24AA",
        "wide": "#F4511E",
        "off posts": "#90A4AE",
        "out for 45": "#00ACC1",
        "saved": "#1E88E5",
        "short": "#D81B60",
        "KO won": "#7CB342",
        "KO lost": "#E53935",
        "turnover won": "#43A047",
        "turnover lost": "#C62828",
        "free conceded": "#212121",
        "free/pen conceded": "#6D4C41",
    }

def classify_shot_result(value: str) -> str | None:
    v = str(value).strip().lower()

    if v in ["goal", "point", "2 pointer"]:
        return "Score"
    if v in ["wide", "short", "off posts", "saved", "out for 45", "out for 45/65"]:
        return "Miss"
    return None
    
def add_numbered_markers(
    fig: go.Figure,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str,
    category_col: str,
) -> None:
    
    palette = event_palette_all() if st.session_state.get("mode") == "All events" else event_palette()
    df = df.copy()
    df[category_col] = df[category_col].map(normalize_outcome)

    for category, group in df.groupby(category_col, dropna=False):
        color = palette.get(str(category), "#000000")
        fig.add_trace(
            go.Scatter(
                x=group[x_col],
                y=group[y_col],
                mode="markers+text",
                name=str(category),
                text=group[label_col].astype(str),
                textposition="middle center",
                textfont=dict(color="white", size=10, family="Arial Black"),
                marker=dict(size=20, color=color, line=dict(color="#E8E8E8", width=2)),
                customdata=group[[label_col]].values,
                hovertemplate="#%{customdata[0]}<br>x=%{x:.1f}<br>y=%{y:.1f}<extra></extra>",
            )
        )


def infer_columns(df: pd.DataFrame) -> dict[str, Optional[str]]:
    return {
        "x": first_existing(df, [["x_posn_%"], ["x_posn"], ["x"]]),
        "y": first_existing(df, [["y_posn_%"], ["y_posn"], ["y"]]),
        "team": first_existing(df, [["team"], ["team_name"], ["club"], ["side"]], required=False),
        "player": first_existing(df, [["player"], ["player_name"], ["name"]], required=False),
        "event": first_existing(df, [["event_type"], ["event"], ["action"]], required=False),
        "outcome": first_existing(df, [["outcome"], ["result"], ["event_outcome"], ["shot_result"], ["status"]], required=False),
        "number": first_existing(df, [["event_no"], ["event_number"], ["number"], ["id"]], required=False),
        "half": first_existing(df, [["half"], ["period"]], required=False),
        "match": first_existing(df, [["match"], ["match_name"], ["fixture"]], required=False),
        "match_no": first_existing(df, [["match_no"], ["match_number"], ["matchnum"], ["game_no"], ["game_number"]], required=False),
        "stat1": first_existing(df, [["Stat_1"], ["stat_1"], ["stat1"]], required=False),
        "stat2": first_existing(df, [["Stat_2"], ["stat_2"], ["stat2"]], required=False),
    }


def build_display_number(df: pd.DataFrame, number_col: Optional[str]) -> pd.Series:
    if number_col and number_col in df.columns:
        return df[number_col].astype(str)
    return pd.Series(range(1, len(df) + 1), index=df.index).astype(str)

def clean_player_name(value: str) -> str:
    text = str(value).strip()
    parts = text.split()
    if len(parts) >= 2 and parts[0].isdigit():
        return " ".join(parts[1:])
    return text
    
st.title("Gaelic Football Pitch Maps")
st.caption("Pitch layout matched to your Scores Stats Plus screenshots. Uses x_posn_% left→right and y_posn_% top→bottom.")

uploaded = st.file_uploader("Upload GAAScores match events CSV", type=["csv"])
if uploaded is None:
    st.warning("Please upload a match CSV file to view the analysis.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except UnicodeDecodeError:
    uploaded.seek(0)
    df = pd.read_csv(uploaded, encoding="latin1")

cols = infer_columns(df)
plot_df = df.copy()
plot_df["__plot_number__"] = build_display_number(plot_df, cols["number"])

if cols["outcome"] is None and cols["stat1"] is not None:
    plot_df["__plot_category__"] = plot_df[cols["stat1"]].astype(str)
    cols["outcome"] = "__plot_category__"
elif cols["outcome"] is None and cols["event"] is not None:
    plot_df["__plot_category__"] = plot_df[cols["event"]].astype(str)
    cols["outcome"] = "__plot_category__"
elif cols["outcome"] is None:
    plot_df["__plot_category__"] = "event"
    cols["outcome"] = "__plot_category__"

st.sidebar.header("Filters")

if cols["match_no"] and cols["team"]:
    match_info = (
        plot_df[[cols["match_no"], cols["team"]]]
        .dropna()
        .astype(str)
        .drop_duplicates()
    )

    match_labels = {}
    for match_no in sorted(match_info[cols["match_no"]].unique(), key=lambda x: int(x) if x.isdigit() else x):
        teams_for_match = sorted(match_info[match_info[cols["match_no"]] == match_no][cols["team"]].unique().tolist())
        opposition = [t for t in teams_for_match if t.lower() != "ballintubber"]
        opp_text = opposition[0] if opposition else "Unknown"
        match_labels[f"{match_no} v {opp_text}"] = match_no

    match_display_choices = st.sidebar.multiselect("Match Number", list(match_labels.keys()))

    if match_display_choices:
        selected_match_nos = [match_labels[label] for label in match_display_choices]
        plot_df = plot_df[plot_df[cols["match_no"]].astype(str).isin(selected_match_nos)]

if cols["team"]:
    teams = sorted([
        t for t in plot_df[cols["team"]].dropna().astype(str).unique().tolist()
        if t.lower() not in ["1st half", "2nd half"]
    ])
    team_choices = st.sidebar.multiselect("Team", teams)
    if team_choices:
        plot_df = plot_df[plot_df[cols["team"]].astype(str).isin(team_choices)]

if cols["player"]:
    plot_df["__player_clean__"] = plot_df[cols["player"]].astype(str).apply(clean_player_name)
    players = sorted(plot_df["__player_clean__"].dropna().unique().tolist())
    player_choices = st.sidebar.multiselect("Player", players)
    if player_choices:
        plot_df = plot_df[plot_df["__player_clean__"].isin(player_choices)]

if cols["half"]:
    halves = ["All"] + sorted(plot_df[cols["half"]].dropna().astype(str).unique().tolist())
    half_choice = st.sidebar.selectbox("Half", halves)
    if half_choice != "All":
        plot_df = plot_df[plot_df[cols["half"]].astype(str) == half_choice]

mode = st.sidebar.radio("Map type", ["All events", "Shots", "Kickouts", "Turnovers"], index=0)
st.session_state["mode"] = mode
shot_type_filter = "All"
if mode == "Shots" and cols["stat1"] and cols["stat2"]:
    shot_type_filter = st.sidebar.selectbox(
        "Shot Type",
        ["All", "From Play", "From Placed"]
    )

if cols["stat1"]:
    stat1_series = plot_df[cols["stat1"]].astype(str).str.lower()

    if mode == "Shots":
        shot_mask = stat1_series.str.contains(
            "goal|point|2 point|wide|short|post|saved",
            na=False
        )
        plot_df = plot_df[shot_mask]

        if cols["stat2"]:
            stat2_filled = plot_df[cols["stat2"]].fillna("").astype(str).str.strip() != ""

            if shot_type_filter == "From Play":
                plot_df = plot_df[~stat2_filled]

            elif shot_type_filter == "From Placed":
                plot_df = plot_df[stat2_filled]

    elif mode == "Kickouts":
        plot_df = plot_df[
            plot_df[cols["stat1"]].astype(str).str.lower().str.contains("kick ?out", na=False)
        ]
        
    elif mode == "Turnovers":
        to_mask = stat1_series.str.contains(
            "turnover",
            na=False
        )
        plot_df = plot_df[to_mask]

outcomes = ["All"] + sorted(plot_df[cols["outcome"]].dropna().map(normalize_outcome).astype(str).unique().tolist())
outcome_choice = st.sidebar.selectbox("Outcome", outcomes)
if outcome_choice != "All":
    plot_df = plot_df[plot_df[cols["outcome"]].map(normalize_outcome) == outcome_choice]

tab1, tab2 = st.tabs(["Pitch Map", "Match Analysis"])

plot_df[cols["x"]] = pd.to_numeric(plot_df[cols["x"]], errors="coerce").fillna(-1)
plot_df[cols["y"]] = pd.to_numeric(plot_df[cols["y"]], errors="coerce").fillna(-1)

plot_df = plot_df[
    (
        (plot_df[cols["x"]] >= 0) & (plot_df[cols["x"]] <= 100) &
        (plot_df[cols["y"]] >= 0) & (plot_df[cols["y"]] <= 100)
    )
    |
    (
        (plot_df[cols["x"]] == -1) & (plot_df[cols["y"]] == -1)
    )
]
# Map x positions inside the sidelines rather than edge-to-edge
# Map x positions inside the sidelines rather than edge-to-edge
x_left = 4.0
x_right = 96.0

plot_df["__x_plot__"] = x_left + (plot_df[cols["x"]] / 100.0) * (x_right - x_left)
plot_df["__y_plot__"] = plot_df[cols["y"]]

# Hide rows with no plotted location
plot_df.loc[
    (plot_df[cols["x"]] == -1) | (plot_df[cols["y"]] == -1),
    ["__x_plot__", "__y_plot__"]
] = pd.NA

c1, c2 = st.columns(2)
c1.metric("Raw events", len(df))
c2.metric("Plotted events", len(plot_df))

with tab1:
    fig = make_pitch_figure()
    if len(plot_df):
        add_numbered_markers(fig, plot_df, "__x_plot__", "__y_plot__", "__plot_number__", cols["outcome"])

    col1, col2 = st.columns([1, 6], vertical_alignment="center")

    with col1:
        st.markdown("### Legend")

        legend_counts = (
            plot_df[cols["outcome"]]
            .map(normalize_outcome)
            .value_counts()
            .reset_index()
        )
        legend_counts.columns = ["category", "count"]

        palette = event_palette_all() if st.session_state.get("mode") == "All events" else event_palette()

        for _, row in legend_counts.iterrows():
            cat = row["category"]
            cnt = row["count"]
            color = palette.get(cat, "#000000")

            st.markdown(
                f"""
                <div style="display:flex; align-items:center; margin-bottom:6px;">
                    <div style="
                        width:14px;
                        height:14px;
                        border-radius:50%;
                        background:{color};
                        border:2px solid #E8E8E8;
                        margin-right:8px;
                        flex-shrink:0;
                    "></div>
                    <div style="font-size:14px;">{cat} ({cnt})</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        st.plotly_chart(fig, use_container_width=False)
    
    st.markdown(
        "<div style='text-align:right; font-size:12px; color:grey;'>Note: Events with x/y = -1 were not plotted on the pitch.</div>",
        unsafe_allow_html=True
    )
    st.subheader("Filtered events being plotted")
    st.markdown(
        "<div style='text-align:right; font-size:12px; color:grey;'>Note: Events with x/y = -1 were not plotted on the pitch.</div>",
        unsafe_allow_html=True
    )

    show_cols = [
        c for c in [
            cols.get("number"),
            cols.get("match_no"),
            cols.get("team"),
            cols.get("player"),
            cols.get("stat1"),
            cols.get("stat2"),
            cols.get("half"),
            cols.get("match"),
        ] if c
    ]

    if "__plot_number__" not in show_cols:
        show_cols = ["__plot_number__"] + show_cols

    st.dataframe(plot_df[show_cols], use_container_width=True)
with tab2:
    def is_in(event_series, values):
        return event_series.isin(values)
    
    st.subheader("Shots / Scores / Misses by Match")
    event_series = plot_df[cols["stat1"]].astype(str).str.lower()

    miss_events = [
        "wide", "wide from free", "short", "out for 45", "saved",
        "short from free", "wide from 45", "off posts from 45", "short from 45", "off posts"
    ]

    score_events = [
        "point", "point from free", "2 pointer", "point from 45",
        "2 pointer from free", "goal", "goal from penalty",
        "goal from free"
    ]
    count_misses = is_in(event_series, miss_events).sum()
    count_scores = is_in(event_series, score_events).sum()
    count_score_attempts = count_misses + count_scores
    shot_efficiency = count_scores / count_score_attempts if count_score_attempts else 0

    miss_events_from_frees = [
        "wide from free", "short from free", "out for 45 from free",
        "saved from free", "wide from 45", "short from 45", "off posts from free"
    ]

    score_events_from_frees = [
        "point from free", "point from 45", "2 pointer from free", "goal from free"
    ]
    count_misses_from_frees = is_in(event_series, miss_events_from_frees).sum()
    count_scores_from_frees = is_in(event_series, score_events_from_frees).sum()
    count_attempts_from_frees = count_misses_from_frees + count_scores_from_frees
    count_misses_from_play = count_misses - count_misses_from_frees
    count_scores_from_play = count_scores - count_scores_from_frees
    count_attempts_from_play = count_misses_from_play + count_scores_from_play

    shot_efficiency_from_play = (
        count_scores_from_play / count_attempts_from_play
        if count_attempts_from_play else 0
    )

    shot_efficiency_from_frees = (
        count_scores_from_frees / count_attempts_from_frees
        if count_attempts_from_frees else 0
    )

    if cols["match_no"] and cols["stat1"] and cols["team"]:
        shot_df = plot_df.copy()
        shot_df = shot_df[shot_df[cols["team"]].astype(str).str.lower() == "ballintubber"]

        event_series = shot_df[cols["stat1"]].astype(str).str.lower()

        miss_mask = is_in(event_series, miss_events)
        score_mask = is_in(event_series, score_events)
        shot_mask = miss_mask | score_mask

        shot_df = shot_df[shot_mask].copy()
        shot_df["measure"] = "Shots"

        scores_df = shot_df[is_in(shot_df[cols["stat1"]].astype(str).str.lower(), score_events)].copy()
        scores_df["measure"] = "Scores"

        misses_df = shot_df[is_in(shot_df[cols["stat1"]].astype(str).str.lower(), miss_events)].copy()
        misses_df["measure"] = "Misses"

        summary_df = pd.concat([shot_df, scores_df, misses_df], ignore_index=True)

        summary = (
            summary_df.groupby([cols["match_no"], "measure"])
            .size()
            .reset_index(name="count")
        )

        fig_summary = px.bar(
            summary,
            x=cols["match_no"],
            y="count",
            color="measure",
            barmode="group",
            category_orders={"measure": ["Shots", "Scores", "Misses"]},
            title="Ballintubber Shots, Scores and Misses per Match"
        )

        st.plotly_chart(fig_summary, use_container_width=True)

