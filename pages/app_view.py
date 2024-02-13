import dash
import dash_leaflet as dl
from dash.dependencies import Input, Output, State

from src import view, geo_feature

dash.register_page(__name__, title="Dot-GPSArtRoute Viewer", path="/view")


def get_layout():
    print("load view")
    center = geo_feature.center_from_geojson(view.target_data_path)
    layout = dash.html.Div(
        [
            dash.html.Div(
                id="view_map",
                children=[
                    dl.Map(
                        id="view_map-view",
                        center=center,
                        zoom=15,
                        children=[
                            dl.TileLayer(),
                            dl.MeasureControl(
                                position="topleft",
                                primaryLengthUnit="kilometers",
                                primaryAreaUnit="hectares",
                                activeColor="#214097",
                                completedColor="#972158",
                            ),
                            dl.LocateControl(
                                locateOptions={"enableHighAccuracy": True}
                            ),
                            dl.GestureHandling(),
                        ],
                        style={"width": "70vw", "height": "92.5vh"},
                    )
                ],
                style={"padding": 25, "flex": 1},
            ),
            dash.html.Div(
                children=[
                    dash.html.Pre(id="view_zoom-text", children="Zoom"),
                    dash.dcc.Input(
                        id="view_zoom", type="number", min=0, max=200, value=25
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
        Input("view_zoom", "value"),
        Input("view_zoom-slider", "value"),
        Input("view_map-view", "zoom"),
    ],
)
def change_zoom(zoom, zoom_slider, zoom_value):
    ctx_id = dash.ctx.triggered_id
    print(zoom, zoom_slider, ctx_id)
    if ctx_id is None:
        zoom = (18 - 15) * 12.5
        return zoom, zoom, 15

    if ctx_id == "view_zoom":
        print(18 - zoom / 12.5)
        return zoom, zoom, 18 - zoom / 12.5
    elif ctx_id == "view_zoom-slider":
        print(18 - zoom_slider / 12.5)
        return zoom_slider, zoom_slider, 18 - zoom_slider / 12.5
    else:
        # v = 18 - z / 12.5
        # z = (18 - v) * 12.5
        zoom = (18 - zoom_value) * 12.5
        return zoom, zoom, zoom_value


@dash.callback(
    [Output("view_map", "children"), Output("view_load-text", "children")],
    Input("view_reload", "n_clicks"),
    State("view_zoom", "value"),
    # prevent_initial_call=True,
)
def reload(_, zoom_value):
    print("reload")

    try:
        target_feature_collection, center = view.target_feature_collection()

    except Exception as e:
        default_map_data = dl.Map(
            id="view_map-view",
            center=center,
            zoom=15,
            children=[
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
            ],
            style={"width": "70vw", "height": "92.5vh"},
        )

        return default_map_data, f"Failed {e}"

    target_feature_style = {
        "fillColor": "#000000",
        "color": "#ff0000",
        "fillOpacity": 1,
        "weight": 10,
    }
    map_data = (
        dl.Map(
            id="view_map-view",
            center=center,
            zoom=18 - zoom_value / 12.5,
            children=[
                dl.TileLayer(),
                dl.GeoJSON(data=target_feature_collection, style=target_feature_style),
                dl.MeasureControl(
                    position="topleft",
                    primaryLengthUnit="kilometers",
                    primaryAreaUnit="hectares",
                    activeColor="#214097",
                    completedColor="#972158",
                ),
                dl.LocateControl(locateOptions={"enableHighAccuracy": True}),
                dl.GestureHandling(),
            ],
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
