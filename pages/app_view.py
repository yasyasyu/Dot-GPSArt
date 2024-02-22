import dash
import dash_leaflet as dl
from dash.dependencies import Input, Output, State

from src import view

dash.register_page(__name__, title="Dot-GPSArtRoute Viewer", path="/view")


def get_layout():
    print("load view")
    layout = dash.html.Div(
        [
            dash.html.Div(
                id="view_map",
                children=[],
                style={"padding": 25, "flex": 1},
            ),
            dash.html.Div(
                children=[
                    dash.html.Pre(id="view_Zoom-text", children="Zoom"),
                    dash.dcc.Input(
                        id="view_zoom", type="number", min=0, max=200, value=25
                    ),
                    dash.html.Button(
                        "Set Zoom input field",
                        id="view_Zoom-input-btn",
                        style={"padding": 5, "margin": 5},
                    ),
                    dash.html.Button(
                        "Set Zoom slider",
                        id="view_Zoom-slider-btn",
                        style={"padding": 5, "margin": 5},
                    ),
                    dash.dcc.Slider(
                        id="view_zoom-slider",
                        min=0,
                        max=50,
                        marks={0: f"in", 50: f"out"},
                        value=25,
                    ),
                    dash.html.Hr(),
                    dash.dcc.Loading(
                        id="view_loading",
                        children=[dash.html.Pre(id="view_load-text", children="wait")],
                        style={"margin": "10%"},
                        type="default",
                    ),
                    dash.html.Button(
                        "View Reload", id="view_reload", style={"padding": 20}
                    ),
                    dash.html.Div(id="reload_area", children=[]),
                    dash.html.Br(),
                    dash.html.Button(
                        "Jump Download Page", id="view_download", style={"padding": 20}
                    ),
                    dash.html.Div(id="download_area", children=[]),
                ],
                style={"padding": 30, "flex": 1, "width": "30px"},
            ),
        ],
        style={"display": "flex", "flexDirection": "row"},
    )

    return layout


layout = get_layout()


@dash.callback(
    [
        Output("view_zoom", "value"),
        Output("view_zoom-slider", "value"),
        Output("view_map-view", "zoom"),
    ],
    [
        Input("view_Zoom-input-btn", "n_clicks"),
        Input("view_Zoom-slider-btn", "n_clicks"),
    ],
    [
        State("view_zoom", "value"),
        State("view_zoom-slider", "value"),
    ],
)
def change_zoom(input_btn, slider_btn, zoom, zoom_slider):
    ctx_id = dash.ctx.triggered_id
    print(zoom, zoom_slider, ctx_id)
    if ctx_id is None:
        return 25, 25, 18 - 25 / 12.5

    match ctx_id:
        case "view_Zoom-input-btn":
            ...
            print(18 - zoom / 12.5)
            return zoom, zoom, 18 - zoom / 12.5
        case "view_Zoom-slider-btn":
            return (
                zoom_slider,
                zoom_slider,
                18 - zoom_slider / 12.5,
            )


@dash.callback(
    Output("view_Zoom-text", "children"),
    Input("view_map-view", "zoom"),
)
def change_zoom(zoom_value):
    ctx_id = dash.ctx.triggered_id
    if ctx_id is None:
        return f"Zoom {25}"
    print(zoom_value)
    # v = 18 - z / 12.5
    # z = (18 - v) * 12.5
    zoom = (18 - zoom_value) * 12.5
    return f"Zoom {zoom}"


def get_map_children():
    print("reload")
    default_children = [
        dl.TileLayer(),
        dl.MeasureControl(
            position="topleft",
            primaryLengthUnit="kilometers",
            primaryAreaUnit="hectares",
            activeColor="#214097",
            completedColor="#972158",
        ),
        dl.LocateControl(locateOptions={"enableHighAccuracy": True}),
        dl.GestureHandling(),
    ]

    try:
        target_feature_collection, center = view.target_feature_collection()

    except Exception as e:
        center = (35.6895, 139.6917)

        return default_children, center

    target_feature_style = {
        "fillColor": "#000000",
        "color": "#ff0000",
        "fillOpacity": 1,
        "weight": 10,
    }

    return (
        default_children
        + [dl.GeoJSON(data=target_feature_collection, style=target_feature_style)],
        center,
    )


@dash.callback(
    [Output("view_map", "children"), Output("view_load-text", "children")],
    Input("view_reload", "n_clicks"),
    State("view_zoom", "value"),
)
def reload(_, zoom_value):
    children, center = get_map_children()

    zoom_level = 18 - zoom_value / 12.5
    map_data = (
        dl.Map(
            id="view_map-view",
            center=center,
            zoom=zoom_level,
            children=children,
            style={"width": "70vw", "height": "92.5vh"},
        ),
    )
    return map_data, "Success"


@dash.callback(
    Output("download_area", "children"),
    Input("view_download", "n_clicks"),
    prevent_initial_call=True,
)
def view_redirect(_):
    # print(flask.url_for("/view"))
    return dash.dcc.Location(pathname="/", id="redirect")
