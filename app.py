import math
from typing import Optional

import pandas as pd
import plotly.express as px
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

    x_left = 4.0
    x_right = 96.0

    pitch_len = 145.0
    pitch_wid = 80.0

    def sw(m: float) -> float:
        return (m / pitch_wid) * (x_right - x_left)

    def sy(m: float) -> float:
        return (m / pitch_len) * 100.0

    y13 = sy(13)
    y20 = sy(20)
    y45 = sy(45)
    y50 = 50.0
    y100_13 = 100.0 - y13
    y100_20 = 100.0 - y20
    y100_45 = 100.0 - y45

    large_w = sw(19.0)
    small_w = sw(14.0)
    goal_w = sw(6.5)
    cx = 50.0

    shapes.append(dict(type="rect", x0=x_left, y0=0, x1=x_right, y1=100, line=line))
    # --- Channel lines ---
    x_ch1 = x_left + (1/3) * (x_right - x_left)
    x_ch2 = x_left + (2/3) * (x_right - x_left)

    shapes.append(dict(
        type="line",
        x0=x_ch1, y0=0,
        x1=x_ch1, y1=100,
        line=dict(color="rgba(200,200,200,0.4)", width=2, dash="dash")
    ))

    shapes.append(dict(
        type="line",
        x0=x_ch2, y0=0,
        x1=x_ch2, y1=100,
        line=dict(color="rgba(200,200,200,0.4)", width=2, dash="dash")
    ))

    for y in [y13, y20, y45, y100_45, y100_20, y100_13]:
        shapes.append(dict(type="line", x0=x_left, y0=y, x1=x_right, y1=y, line=line))

    shapes.append(dict(type="line", x0=x_left, y0=y50, x1=x_right, y1=y50, line=dashed))

    shapes.append(dict(type="rect", x0=cx - large_w / 2, y0=0, x1=cx + large_w / 2, y1=y13, line=line))
    shapes.append(dict(type="rect", x0=cx - small_w / 2, y0=0, x1=cx + small_w / 2, y1=sy(4.5), line=line))
    shapes.append(dict(type="line", x0=cx - goal_w / 2, y0=0, x1=cx - goal_w / 2, y1=sy(1.0), line=line))
    shapes.append(dict(type="line", x0=cx + goal_w / 2, y0=0, x1=cx + goal_w / 2, y1=sy(1.0), line=line))

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

    rx13 = sw(13.0)
    ry13 = sy(13.0)

    shapes.append(dict(type="path", path=ellipse_arc_path(cx, y20, rx13, ry13, 0, 180), line=line))
    shapes.append(dict(type="path", path=ellipse_arc_path(cx, y100_20, rx13, ry13, 180, 360), line=line))

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
    # Channel labels
    for x, label in [(19.33, "1"), (50, "2"), (80.67, "3")]:
        fig.add_annotation(
            x=x,
            y=3,
            text=label,
            showarrow=False,
            font=dict(size=22, color="rgba(220,220,220,0.45)"),
        )

        fig.add_annotation(
            x=x,
            y=97,
            text=label,
            showarrow=False,
            font=dict(size=22, color="rgba(220,220,220,0.45)"),
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


def add_numbered_markers(
    fig: go.Figure,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str,
    category_col: str,
    player_col: Optional[str] = None,
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
                mode="markers",
                name=str(category),
                marker=dict(
                    size=12,
                    sizemode="diameter",
                    sizemin=6,
                    color=color,
                    opacity=0.7,
                    line=dict(
                        color=group[cols["stat2"]].apply(
                            lambda x: "#000000" if pd.notna(x) and str(x).strip() != "" else "#FFFFFF"
                        ),
                        width=group[cols["stat2"]].apply(
                            lambda x: 2 if pd.notna(x) and str(x).strip() != "" else 2
                        )
                    )
                ),
                hoverinfo="text",
                hoverlabel=dict(font_size=14),
                customdata=group[
                    [label_col] + ([player_col] if player_col and player_col in group.columns else [])
                ].values,
                hovertemplate="Player=%{customdata[1]}<extra></extra>"
                if player_col and player_col in group.columns
                else "<extra></extra>",
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


def build_player_scoring_table(
    plot_df: pd.DataFrame,
    cols: dict[str, Optional[str]],
    score_events: list[str],
    miss_events: list[str],
) -> Optional[pd.DataFrame]:
    if not (cols["player"] and cols["stat1"] and cols["team"]):
        return None

    player_scoring_df = plot_df.copy()
    player_scoring_df = player_scoring_df[
        player_scoring_df[cols["team"]].astype(str).str.lower() == "ballintubber"
    ].copy()

    if player_scoring_df.empty:
        return None

    player_scoring_df["__player_clean__"] = player_scoring_df[cols["player"]].astype(str).apply(clean_player_name)
    player_scoring_df["__stat1_lower__"] = player_scoring_df[cols["stat1"]].astype(str).str.lower()

    shot_event_list = score_events + miss_events

    player_scoring_df = player_scoring_df[
        player_scoring_df["__stat1_lower__"].isin(shot_event_list)
    ].copy()

    if player_scoring_df.empty:
        return None

    player_summary = (
        player_scoring_df.groupby(["__player_clean__", "__stat1_lower__"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    if player_summary.empty:
        return None

    for col_name in shot_event_list:
        if col_name not in player_summary.columns:
            player_summary[col_name] = 0

    player_summary["Shots"] = player_summary[shot_event_list].sum(axis=1)
    player_summary["Scores"] = player_summary[score_events].sum(axis=1)

    player_summary["Shot Efficiency"] = (
        player_summary["Scores"] / player_summary["Shots"].replace(0, pd.NA)
    ).fillna(0)

    player_summary["Shot Efficiency"] = (
        (player_summary["Shot Efficiency"] * 100).round(0).astype(int).astype(str) + "%"
    )

    player_summary = player_summary.sort_values(
        by=["Shots", "Scores"],
        ascending=[False, False]
    )

    player_summary = player_summary.rename(columns={
        "__player_clean__": "Player"
    })

    keep_cols = ["Player", "Shots", "Scores", "Shot Efficiency"]

    non_zero_cols = [
        col for col in player_summary.columns
        if col in keep_cols or player_summary[col].sum() > 0
    ]
    player_summary = player_summary[non_zero_cols]

    summary_cols = ["Shots", "Scores", "Shot Efficiency"]
    score_cols = [c for c in ["goal", "2 pointer", "point"] if c in player_summary.columns]
    miss_cols = [c for c in ["wide", "short", "off posts", "saved", "out for 45"] if c in player_summary.columns]

    ordered_cols = ["Player"] + summary_cols + score_cols + miss_cols
    ordered_cols = [c for c in ordered_cols if c in player_summary.columns]
    player_summary = player_summary[ordered_cols]

    player_summary["Player"] = (
        player_summary["Player"]
        .replace("nan", pd.NA)
        .fillna("Not Allocated")
    )

    return player_summary


# st.title("Gaelic Football Pitch Maps")
# st.caption("Pitch layout matched to your Scores Stats Plus screenshots. Uses x_posn_% left→right and y_posn_% top→bottom.")

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
plot_df["__original_event_number__"] = build_display_number(plot_df, cols["number"])


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

mode = st.sidebar.radio("Map type", ["All events", "Shots", "Kickouts", "Turnovers"], index=0)
st.session_state["mode"] = mode

if cols["player"]:
    plot_df["__player_clean__"] = plot_df[cols["player"]].astype(str).apply(clean_player_name)

    player_source_df = plot_df.copy()

    if cols["stat1"]:
        stat1_for_players = player_source_df[cols["stat1"]].astype(str).str.lower()

        if mode == "Shots":
            player_source_df = player_source_df[
                stat1_for_players.str.contains(
                    "goal|point|2 point|wide|short|post|saved",
                    na=False
                )
            ]
        elif mode == "Kickouts":
            player_source_df = player_source_df[
                stat1_for_players.str.contains("kick ?out", na=False)
            ]
        elif mode == "Turnovers":
            player_source_df = player_source_df[
                stat1_for_players.str.contains("turnover", na=False)
            ]

    players = sorted(
        player_source_df["__player_clean__"]
        .dropna()
        .loc[lambda s: s.astype(str).str.strip() != ""]
        .unique()
        .tolist()
    )

    st.sidebar.caption("Only players with events matching current filters are shown")
    player_choices = st.sidebar.multiselect("Player", players)

    if player_choices:
        plot_df = plot_df[plot_df["__player_clean__"].isin(player_choices)]

if cols["half"]:
    halves = ["All"] + sorted(plot_df[cols["half"]].dropna().astype(str).unique().tolist())
    half_choice = st.sidebar.selectbox("Half", halves)
    if half_choice != "All":
        plot_df = plot_df[plot_df[cols["half"]].astype(str) == half_choice]

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
        to_mask = stat1_series.str.contains("turnover", na=False)
        plot_df = plot_df[to_mask]

outcomes = ["All"] + sorted(plot_df[cols["outcome"]].dropna().map(normalize_outcome).astype(str).unique().tolist())
outcome_choice = st.sidebar.selectbox("Outcome", outcomes)
if outcome_choice != "All":
    plot_df = plot_df[plot_df[cols["outcome"]].map(normalize_outcome) == outcome_choice]
filters_applied = (
    len(match_display_choices) > 0 or
    len(team_choices) > 0 or
    len(player_choices) > 0 or
    half_choice != "All" or
    shot_type_filter != "All"
)

plot_df["__plot_number__"] = range(1, len(plot_df) + 1)
tab1, tab2, tab3 = st.tabs(["Pitch Map", "Scoring Analysis", "Non-Scoring Analysis"])

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

x_left = 4.0
x_right = 96.0

plot_df["__x_plot__"] = x_left + (plot_df[cols["x"]] / 100.0) * (x_right - x_left)
plot_df["__y_plot__"] = plot_df[cols["y"]]

plot_df.loc[
    (plot_df[cols["x"]] == -1) | (plot_df[cols["y"]] == -1),
    ["__x_plot__", "__y_plot__"]

] = pd.NA

plot_df["__plot_number__"] = range(1, len(plot_df) + 1)
# c1, c2 = st.columns(2)
# c1.metric("Raw events", len(df))
# c2.metric("Plotted events", len(plot_df))

with tab1:
    fig = make_pitch_figure()

    marker_df = plot_df.copy()

    if len(marker_df):
        add_numbered_markers(
            fig,
            marker_df,
            "__x_plot__",
            "__y_plot__",
            "__plot_number__",
            cols["outcome"],
            cols["player"]
        )

    col1, col2 = st.columns([2, 5], vertical_alignment="center")

    with col1:
        st.markdown("### Legend")

        legend_counts = (
            marker_df[cols["outcome"]]
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
    # --- Channel breakdown (1 = left, 3 = right) ---
        st.markdown("<h4 style='margin-bottom:4px;'>Channel breakdown</h4>", unsafe_allow_html=True)

        channel_df = plot_df.copy()

        # Only keep plotted points
        channel_df = channel_df[
            (channel_df["__x_plot__"].notna()) & (channel_df["__y_plot__"].notna())
        ]

        # Use original % positions for clean split
        x_series = channel_df[cols["x"]]

        channel_df["Channel"] = pd.cut(
            x_series,
            bins=[-0.01, 33.33, 66.66, 100.01],
            labels=["1", "2", "3"]
        )

        channel_df["Outcome"] = channel_df[cols["outcome"]].map(normalize_outcome)

        channel_table = (
            channel_df.groupby(["Outcome", "Channel"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        st.markdown("""
        <style>
        /* Center align headers */
        div[data-testid="stDataFrame"] [role="columnheader"] div {
            justify-content: center !important;
            text-align: center !important;
        }

        /* Center align values */
        div[data-testid="stDataFrame"] [role="gridcell"] div {
            justify-content: center !important;
            text-align: center !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            channel_table,
            use_container_width=False,
            hide_index=True,
            column_config={
                "Outcome": st.column_config.TextColumn(width="small"),
                "1(L)": st.column_config.NumberColumn(width=50),
                "2(M)": st.column_config.NumberColumn(width=50),
                "3(R)": st.column_config.NumberColumn(width=50),
            }
        )

    with col2:
        st.plotly_chart(fig, use_container_width=False)

    st.markdown(
        "<div style='text-align:right; font-size:12px; color:grey;'>Note: Events with x/y = -1 were not plotted on the pitch.</div>",
        unsafe_allow_html=True
    )

with tab2:
    def is_in(event_series, values):
        return event_series.isin(values)

    st.subheader("Shots / Scores / Misses by Match")

    miss_events = [
        "wide", "wide from free", "short", "out for 45", "saved",
        "short from free", "wide from 45", "off posts from 45", "short from 45", "off posts"
    ]

    score_events = [
        "point", "point from free", "2 pointer", "point from 45",
        "2 pointer from free", "goal", "goal from penalty",
        "goal from free"
    ]

    scoring_df = plot_df.copy()

    scoring_df = scoring_df[
        scoring_df[cols["team"]].astype(str).str.lower().isin(
            ["ballintubber"] + [
                t.lower()
                for t in df[cols["team"]].dropna().astype(str).unique().tolist()
                if t.lower() != "ballintubber" and t.lower() not in ["1st half", "2nd half"]
            ]
        )
    ].copy()

    scoring_df["__team_group__"] = scoring_df[cols["team"]].astype(str).str.lower().apply(
        lambda x: "Ballintubber" if x == "ballintubber" else "Opposition"
    )

    scoring_event_series = scoring_df[cols["stat1"]].astype(str).str.lower()
    score_mask = scoring_event_series.isin(score_events)
    miss_mask = scoring_event_series.isin(miss_events)
    shot_mask = score_mask | miss_mask

    scoring_df = scoring_df[shot_mask].copy()
    scoring_df["__is_score__"] = scoring_df[cols["stat1"]].astype(str).str.lower().isin(score_events)
    scoring_df["__is_miss__"] = scoring_df[cols["stat1"]].astype(str).str.lower().isin(miss_events)

    overall_summary = (
        scoring_df.groupby("__team_group__")
        .agg(
            Shots=("__team_group__", "size"),
            Scores=("__is_score__", "sum"),
            Misses=("__is_miss__", "sum")
        )
        .reset_index()
    )

    if not overall_summary.empty:
        overall_summary["Efficiency"] = overall_summary["Scores"] / overall_summary["Shots"]
        y_max = overall_summary[["Shots", "Scores", "Misses"]].max().max()
    else:
        overall_summary["Efficiency"] = pd.Series(dtype=float)
        y_max = 1

    has_ball = (overall_summary["__team_group__"] == "Ballintubber").any()
    has_opp = (overall_summary["__team_group__"] == "Opposition").any()

    col1, col2 = st.columns(2)

    if not has_ball and not has_opp:
        st.info("No scoring data available for the current filters.")

    with col1:
        if has_ball:
            ballintubber_summary = overall_summary[
                overall_summary["__team_group__"] == "Ballintubber"
            ].melt(
                id_vars="__team_group__",
                value_vars=["Shots", "Scores", "Misses"],
                var_name="Metric",
                value_name="Count"
            )

            fig_ball = px.bar(
                ballintubber_summary,
                x="Metric",
                y="Count",
                text="Count",
                title="Ballintubber Scoring Summary",
                color="Metric",
                color_discrete_map={
                    "Shots": "#1f77b4",
                    "Scores": "#90EE90",
                    "Misses": "#FF3B30"
                }
            )

            ball_eff = overall_summary.loc[
                overall_summary["__team_group__"] == "Ballintubber", "Efficiency"
            ].iloc[0]

            fig_ball.add_annotation(
                x=0.5,
                y=1.12,
                xref="paper",
                yref="paper",
                text=f"Efficiency: {ball_eff:.0%}",
                showarrow=False,
                font=dict(size=16)
            )

            fig_ball.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                shapes=[
                    dict(
                        type="rect",
                        xref="paper", yref="paper",
                        x0=0, y0=0, x1=1, y1=1,
                        line=dict(color="#FF7F7F", width=2)
                    )
                ],
                margin=dict(t=60),
                yaxis=dict(range=[0, y_max]),
                showlegend=False
            )

            st.plotly_chart(fig_ball, use_container_width=True)

    with col2:
        if has_opp:
            opp_summary = overall_summary[
                overall_summary["__team_group__"] == "Opposition"
            ].melt(
                id_vars="__team_group__",
                value_vars=["Shots", "Scores", "Misses"],
                var_name="Metric",
                value_name="Count"
            )

            fig_opp = px.bar(
                opp_summary,
                x="Metric",
                y="Count",
                text="Count",
                title="Opposition Scoring Summary",
                color="Metric",
                color_discrete_map={
                    "Shots": "#1f77b4",
                    "Scores": "#90EE90",
                    "Misses": "#FF3B30"
                }
            )

            opp_eff = overall_summary.loc[
                overall_summary["__team_group__"] == "Opposition", "Efficiency"
            ].iloc[0]

            fig_opp.add_annotation(
                x=0.5,
                y=1.12,
                xref="paper",
                yref="paper",
                text=f"Efficiency: {opp_eff:.0%}",
                showarrow=False,
                font=dict(size=16)
            )

            fig_opp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                shapes=[
                    dict(
                        type="rect",
                        xref="paper", yref="paper",
                        x0=0, y0=0, x1=1, y1=1,
                        line=dict(color="#333333", width=2)
                    )
                ],
                margin=dict(t=60),
                yaxis=dict(range=[0, y_max]),
                showlegend=False
            )

            st.plotly_chart(fig_opp, use_container_width=True)

    event_series = plot_df[cols["stat1"]].astype(str).str.lower()

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

        scores_df = shot_df[
            is_in(shot_df[cols["stat1"]].astype(str).str.lower(), score_events)
        ].copy()
        scores_df["measure"] = "Scores"

        misses_df = shot_df[
            is_in(shot_df[cols["stat1"]].astype(str).str.lower(), miss_events)
        ].copy()
        misses_df["measure"] = "Misses"

        summary_df = pd.concat([shot_df, scores_df, misses_df], ignore_index=True)

        summary = (
            summary_df.groupby([cols["match_no"], "measure"])
            .size()
            .reset_index(name="count")
        )

        efficiency_summary = (
            summary.pivot(index=cols["match_no"], columns="measure", values="count")
            .fillna(0)
            .reset_index()
        )

        if "Scores" not in efficiency_summary.columns:
            efficiency_summary["Scores"] = 0
        if "Shots" not in efficiency_summary.columns:
            efficiency_summary["Shots"] = 0

        efficiency_summary["Shot Efficiency"] = (
            efficiency_summary["Scores"] / efficiency_summary["Shots"].replace(0, pd.NA)
        ).fillna(0)

        summary["match_label"] = summary[cols["match_no"]].astype(str).map(
            lambda x: next((label for label, num in match_labels.items() if num == x), x)
        )

        fig_summary = px.bar(
            summary,
            x="match_label",
            y="count",
            text="count",
            color="measure",
            barmode="group",
            category_orders={"measure": ["Shots", "Scores", "Misses"]},
            title="Ballintubber Shots, Scores and Misses per Match",
            color_discrete_map={
                "Shots": "#1f77b4",
                "Scores": "#90EE90",
                "Misses": "#FF3B30"
            }
        )

        fig_summary.update_xaxes(
            categoryorder="array",
            categoryarray=summary["match_label"].unique()
        )

        efficiency_summary["match_label"] = efficiency_summary[cols["match_no"]].astype(str).map(
            lambda x: next((label for label, num in match_labels.items() if str(num) == x), x)
        )

        if not summary.empty:
            fig_summary.add_scatter(
                x=efficiency_summary["match_label"],
                y=efficiency_summary["Shot Efficiency"] * summary["count"].max(),
                mode="lines+markers+text",
                text=[f"{round(v * 100)}%" for v in efficiency_summary["Shot Efficiency"]],
                textposition="top center",
                name="Shot Efficiency",
                showlegend=False
            )

        fig_summary.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_summary, use_container_width=True)

        player_summary_display = build_player_scoring_table(
            plot_df=plot_df,
            cols=cols,
            score_events=score_events,
            miss_events=miss_events,
        )

        if player_summary_display is not None and not player_summary_display.empty:
            st.markdown("### Player scoring breakdown")
            st.dataframe(player_summary_display, use_container_width=True)
        else:
            st.info("No player scoring data for current filters.")

with tab3:
    st.markdown("### Kickout Analysis")

    if cols["stat1"] and cols["team"]:
        ko_df = plot_df.copy()

        ko_df["__stat1_lower__"] = ko_df[cols["stat1"]].astype(str).str.lower()
        ko_df = ko_df[ko_df["__stat1_lower__"].str.contains("kick ?out", na=False)]

        if not ko_df.empty:
            ko_df["__team_lower__"] = ko_df[cols["team"]].astype(str).str.lower()
            ko_df["__is_ball__"] = ko_df["__team_lower__"] == "ballintubber"
            ko_df["__is_won__"] = ko_df["__stat1_lower__"].str.contains("won", na=False)
            ko_df["__is_lost__"] = ko_df["__stat1_lower__"].str.contains("lost", na=False)

            summary = (
                ko_df.groupby(cols["match_no"])
                .agg(
                    Own_KO_Won=("__is_won__", lambda x: ((ko_df.loc[x.index, "__is_ball__"]) & x).sum()),
                    Own_KO_Lost=("__is_lost__", lambda x: ((ko_df.loc[x.index, "__is_ball__"]) & x).sum()),
                    Opp_KO_Won=("__is_won__", lambda x: ((~ko_df.loc[x.index, "__is_ball__"]) & x).sum()),
                    Opp_KO_Lost=("__is_lost__", lambda x: ((~ko_df.loc[x.index, "__is_ball__"]) & x).sum()),
                )
                .reset_index()
            )
    
            summary["match_label"] = summary[cols["match_no"]].astype(str).map(
                lambda x: next((label for label, num in match_labels.items() if str(num) == x), x)
            )
    
            summary = summary.drop(columns=[cols["match_no"]])
            summary = summary.rename(columns={"match_label": "Match"})  
            summary["Own KO Index +/-"] = summary["Own_KO_Won"] - summary["Own_KO_Lost"]
            summary["Opp KO Index +/-"] = summary["Opp_KO_Won"] - summary["Opp_KO_Lost"]
            summary["Overall KO Index +/-"] = summary["Own KO Index +/-"] + summary["Opp KO Index +/-"]

            summary = summary.rename(columns={cols["team"]: "Opposition"})
            
            summary = summary[[
                "Match",
                "Own_KO_Won",
                "Own_KO_Lost",
                "Own KO Index +/-",
                "Opp_KO_Won",
                "Opp_KO_Lost",
                "Opp KO Index +/-",
                "Overall KO Index +/-"
            ]]
            
            st.table(summary)
            # --- Player Non-Scoring Stats ---
            st.markdown("### Player Non-scoring Stats")
    
            non_score_df = plot_df.copy()
            non_score_df = non_score_df[
            non_score_df[cols["team"]].astype(str).str.lower() == "ballintubber"
            ]
            non_score_df["__stat1_lower__"] = non_score_df[cols["stat1"]].astype(str).str.lower()
    
            # Exclude all shot-related events
            exclude_events = score_events + miss_events + ["out for 45", "out for 45/65"]
            non_score_df = non_score_df[
                ~non_score_df["__stat1_lower__"].isin(exclude_events)
            ]
    
            if not non_score_df.empty:
    
                non_score_df["__player_clean__"] = non_score_df[cols["player"]].astype(str).apply(clean_player_name)
    
                player_table = (
                    non_score_df.groupby(["__player_clean__", "__stat1_lower__"])
                    .size()
                    .unstack(fill_value=0)
                    .reset_index()
                )
    
                player_table = player_table[
                    player_table["__player_clean__"].notna() &
                    (player_table["__player_clean__"].astype(str).str.lower() != "nan")
                ]

                player_table["Total"] = player_table.drop(columns="__player_clean__").sum(axis=1)
    
                player_table = player_table.sort_values(by="Total", ascending=False)
    
                player_table = player_table.rename(columns={"__player_clean__": "Player"})
                # Drop unwanted columns if present
                drop_cols = ["own kick out lost", "out for 45", "out for 45/65"]
                player_table = player_table.drop(columns=[c for c in drop_cols if c in player_table.columns])
    
                st.dataframe(
                    player_table.style.set_properties(**{"text-align": "left"}),
                    use_container_width=True
                )
    
            else:
                st.info("No non-scoring events for current filters.")
            
        else:
            st.info("No kickout data for current filters.")
