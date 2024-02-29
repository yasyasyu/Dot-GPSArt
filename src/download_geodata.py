import json
import geojson
import networkx
import osmnx as ox

from src import utility


def query(target_point: tuple[int, int], distance: int = 300):
    try:
        G: networkx.classes.multidigraph.MultiDiGraph = ox.graph_from_point(
            center_point=target_point,
            dist=distance,
            network_type="walk",
        )
    except Exception as e:
        print(e)
        raise utility.AvailableException()

    return G


def build_geodata(G):
    def split_LineString(data) -> dict:
        features = []
        edge_id = 0
        for line_idx, line in enumerate(data["features"]):
            line_string = line["geometry"]["coordinates"]
            for point_idx in range(len(line_string) - 1):
                frm, to = line_string[point_idx], line_string[point_idx + 1]
                features.append(
                    geojson.Feature(
                        id=edge_id,
                        geometry=geojson.LineString([frm, to]),
                        properties={
                            "name": f"{line_idx}-{point_idx}-{edge_id}",
                            "length": utility.distance(frm, to) * 1_000_000,
                        },
                    )
                )

                edge_id += 1
        feature_collection = geojson.FeatureCollection(features=features)
        feature_collection["bbox"] = data["bbox"]
        return feature_collection

    _, e = ox.graph_to_gdfs(G)

    geo_data = split_LineString(e.__geo_interface__)

    return geo_data


def out_geodata(file_path, geo_data):
    with open(file_path, "w") as f:
        geojson.dump(geo_data, f, indent=4)


def download(center, radius):
    with open("./data/file_path.json") as f:
        data_path = json.load(f)
    file_path = data_path["default"]
    try:
        G = query(center, radius)
        geo_data = build_geodata(G)
        out_geodata(file_path, geo_data)
    except utility.AvailableException as e:
        raise e
    except:
        raise utility.InnerException()
