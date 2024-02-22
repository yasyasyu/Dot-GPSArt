from typing import Union
import subprocess
import json

import dash
import dash_leaflet as dl
from dash.dependencies import Input, Output, State

from src import download_geodata, view, geo_feature

dash.register_page(__name__, title="Dot-GPSArtRoute", path="/")

icon = dict(
    html=f"""
            <div style="width: 10px;
                        height: 10px;
                        border: 1px solid black;
                        border-radius: 5px;
                        background-color: blue;">
            </div>
    """,
)


def get_layout():
    try:
        center = geo_feature.center_from_geojson(view.target_data_path)
    except:
        center = (35.6895, 139.6917)
    layout = dash.html.Div(
        [
            dash.html.Div(
                id="map",
                children=[
                    dl.Map(
                        id="map-view",
                        center=center,
                        zoom=13,
                        children=[
                            dl.TileLayer(),
                            dl.MeasureControl(
                                position="topleft",
                                primaryLengthUnit="kilometers",
                                primaryAreaUnit="hectares",
                                activeColor="#214097",
                                completedColor="#972158",
                            ),
                            dl.DivMarker(
                                id="map-marker", position=center, iconOptions=icon
                            ),
                            dl.Circle(id="map-circle", center=center, radius=100),
                            dl.LocateControl(
                                locateOptions={"enableHighAccuracy": True}
                            ),
                            dl.GestureHandling(),
                        ],
                        style={"width": "70vw", "height": "92.5vh"},
                    ),
                ],
                style={"padding": 25, "flex": 1},
            ),
            dash.html.Div(
                children=[
                    dash.dcc.ConfirmDialog(
                        id="download-success",
                        message="ダウンロードが完了しました．\n描画アプリケーションを起動しますか",
                    ),
                    dash.dcc.ConfirmDialog(
                        id="download-failed",
                        message="ダウンロードに失敗しました．",
                    ),
                    dash.html.Pre(id="Zoom-text", children="Zoom"),
                    dash.dcc.Input(id="zoom", type="number", min=0, max=200, value=25),
                    dash.html.Button(
                        "Set Zoom input field",
                        id="Zoom-input-btn",
                        style={"padding": 5, "margin": 5},
                    ),
                    dash.html.Button(
                        "Set Zoom slider",
                        id="Zoom-slider-btn",
                        style={"padding": 5, "margin": 5},
                    ),
                    dash.dcc.Slider(
                        id="zoom-slider",
                        min=0,
                        max=50,
                        marks={0: f"in", 50: f"out"},
                        value=25,
                    ),
                    dash.html.Hr(),
                    dash.html.Pre(id="center-text", children="Center"),
                    dash.dcc.Input(id="center-lat", type="number", value=0),
                    dash.dcc.Input(id="center-lng", type="number", value=0),
                    dash.html.Button(
                        "Set Center",
                        id="center-btn",
                        style={"padding": 5, "margin": 5},
                    ),
                    dash.html.Pre(id="radius-text", children="Circle Radius"),
                    dash.dcc.Input(
                        id="radius", type="number", min=100, max=5000, value=500
                    ),
                    dash.dcc.Slider(
                        id="radius-slider",
                        min=100,
                        max=5000,
                        marks={
                            100: "min:100",
                            1000: "1000",
                            2500: "2500",
                            5000: "max:5000",
                        },
                        value=500,
                    ),
                    dash.html.Hr(),
                    dash.html.Button("Download", id="download", style={"padding": 10}),
                    dash.dcc.Loading(
                        id="loading",
                        children=[
                            dash.html.Pre(id="download-text", children="Not Download")
                        ],
                        style={"margin": "10%"},
                        type="default",
                    ),
                    dash.html.Button("Draw", id="draw", style={"padding": 20}),
                    dash.html.Div(),
                    dash.html.Br(),
                    dash.html.Div(
                        dash.html.Button(
                            "Jump View Page",
                            id="view",
                            style={
                                "width": "20vw",
                                "height": "20vh",
                            },
                        ),
                        style={
                            "position": "absolute",
                            "bottom": 50,
                        },
                    ),
                    dash.html.Div(id="view_area", children=[]),
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
        Output("download-text", "children"),
        Output("download-success", "displayed"),
        Output("download-failed", "displayed"),
        Output("download-failed", "message"),
    ],
    Input("download", "n_clicks"),
    [State("map-view", "center"), State("radius", "value")],
    prevent_initial_call=True,
)
def download_geo(_, center, radius):
    if type(center) is dict:
        center = (center["lat"], center["lng"])
    else:
        center = tuple(center)
    try:
        download_geodata.download(center, radius)
    except Exception as e:
        print(e)
        return (
            f'Download Failed "{e}"',
            False,
            True,
            f"ダウンロードに失敗しました．\n {e}",
        )

    return f"Download Success", True, False, ""


@dash.callback(
    [
        Output("map-circle", "radius"),
        Output("radius", "value"),
        Output("radius-slider", "value"),
    ],
    [Input("radius", "value"), Input("radius-slider", "value")],
)
def change_radius(radius, radius_slider):
    ctx_id = dash.ctx.triggered_id
    print(radius, radius_slider, ctx_id)
    if ctx_id is None:
        return [radius] * 3

    if ctx_id == "radius":
        return [radius] * 3
    else:
        return [radius_slider] * 3


@dash.callback(
    [
        Output("map-view", "center"),
        Output("map-circle", "center"),
        Output("map-marker", "position"),
        Output("center-lat", "value"),
        Output("center-lng", "value"),
    ],
    [Input("center-btn", "n_clicks"), Input("map-view", "center")],
    [State("center-lat", "value"), State("center-lng", "value")],
)
def change_center(_, center: Union[list, dict], lat, lng):
    ctx_id = dash.ctx.triggered_id
    if ctx_id is None:
        if type(center) is dict:
            center = (center["lat"], center["lng"])

        return center, center, center, *center

    if ctx_id == "map-view":
        if type(center) is dict:
            center = (center["lat"], center["lng"])

        return center, center, center, *center
    else:
        return (lat, lng), (lat, lng), (lat, lng), lat, lng


@dash.callback(
    [
        Output("zoom", "value"),
        Output("zoom-slider", "value"),
        Output("map-view", "zoom"),
    ],
    [
        Input("Zoom-input-btn", "n_clicks"),
        Input("Zoom-slider-btn", "n_clicks"),
    ],
    [State("zoom", "value"), State("zoom-slider", "value")],
)
def change_zoom(input_btn, slider_btn, zoom, zoom_slider):
    ctx_id = dash.ctx.triggered_id
    print(zoom, zoom_slider, ctx_id)
    if ctx_id is None:
        return 25, 25, 18 - 25 / 12.5

    match ctx_id:
        case "Zoom-input-btn":
            return zoom, zoom, 18 - zoom / 12.5
        case "Zoom-slider-btn":
            return (
                zoom_slider,
                zoom_slider,
                18 - zoom_slider / 12.5,
            )


@dash.callback(
    Output("Zoom-text", "children"),
    Input("map-view", "zoom"),
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


@dash.callback(
    Output("draw", "style"),
    [Input("draw", "n_clicks"), Input("download-success", "submit_n_clicks")],
    prevent_initial_call=True,
)
def draw_app(*_):
    with open("./data/file_path.json") as f:
        draw_app_path = json.load(f)["App"]
    subprocess.run(draw_app_path)

    return {"padding": 20}


@dash.callback(
    Output("view_area", "children"),
    Input("view", "n_clicks"),
    prevent_initial_call=True,
)
def view_redirect(_):
    # print(flask.url_for("/view"))
    return dash.dcc.Location(pathname="/view", id="redirect")
