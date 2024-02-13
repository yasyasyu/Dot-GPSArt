from collections import defaultdict
import heapq
import json
import random
import time
import geojson

import osmnx as ox
import networkx as nx
import geopandas as gpd

from src import utility


def _connect(data):
    direct = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    W, H = data["size"]
    grid = data["draw"]
    graph: dict[list] = defaultdict(list)
    point = list()
    pq = []
    for i in range(H):
        for j in range(W):
            if not grid[i][j]:
                continue
            cur = i * W + j
            point.append(cur)
            for d in range(4):
                di, dj = direct[d]
                ni, nj = i + di, j + dj
                if not (0 <= ni < H and 0 <= nj < W):
                    continue
                if not grid[ni][nj]:
                    continue

                nxt = ni * W + nj

                heapq.heappush(pq, (random.random(), cur, nxt))
    uf = utility.UnionFind(H * W)
    while pq:
        _, cur, nxt = heapq.heappop(pq)
        if uf.same(cur, nxt):
            continue
        uf.merge(cur, nxt)
        graph[cur].append(nxt)
        graph[nxt].append(cur)

    return graph, point


def json_feature(file_path):
    print("build json feature")
    t = time.perf_counter()
    with open(file_path, encoding="utf_8_sig") as f:
        data = geojson.load(f)
    features = []
    for i, feature in enumerate(data["features"]):
        features.append(
            geojson.Feature(
                id=i,
                geometry=geojson.LineString(feature["geometry"]["coordinates"]),
                properties={"name": i},
            )
        )
    print(time.perf_counter() - t)
    return geojson.FeatureCollection(features)


def center_from_geojson(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    bbox = data["bbox"]
    center = ((bbox[1] + bbox[3]) / 2, (bbox[2] + bbox[0]) / 2)
    return center


def bbox_from_geojson(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    print(data["bbox"])
    return data["bbox"]


def out_geodata(file_path, geo_data):
    print("out")
    t = time.perf_counter()
    with open(file_path, "w") as f:
        geojson.dump(geo_data, f, indent=4)

    print(time.perf_counter() - t)


class Nearest_Feature:

    def __init__(self, default_data_path, draw_data_path) -> None:
        self.default_data_path = default_data_path
        self.draw_data_path = draw_data_path
        self.G: nx.MultiGraph = nx.MultiGraph()
        self.edges_id = defaultdict(lambda: -1)

    def build(self, out_file) -> None:
        self.geojson_to_nx(self.default_data_path)
        features, center = self.nx_to_nearest_edge_feature(self.draw_data_path)
        feature_collection = geojson.FeatureCollection(features["LineString"])
        feature_collection["bbox"] = bbox_from_geojson(self.default_data_path)
        out_geodata(out_file, feature_collection)

    def geojson_to_nx(self, file_path) -> None:
        print("geojson to nx")
        t = time.perf_counter()
        nodes_idx = {}
        edges = []
        node_id = 0
        with open(file=file_path, encoding="utf_8_sig") as f:
            data = geojson.load(f)
        for line in data["features"]:
            coordinates = line["geometry"]["coordinates"]
            frm = utility.round_point(coordinates[0])
            to = utility.round_point(coordinates[1])
            if not frm in nodes_idx:
                nodes_idx[frm] = node_id
                node_id += 1

            if not to in nodes_idx:
                nodes_idx[to] = node_id
                node_id += 1
            u, v = nodes_idx[frm], nodes_idx[to]

            if (u, v) in self.edges_id.keys():
                continue
            edge_cnt = len(self.edges_id.keys())

            self.edges_id[(u, v)] = edge_cnt + 0
            self.edges_id[(v, u)] = edge_cnt + 1

            edge = {
                "id": self.edges_id[(u, v)],
                "u": u,
                "v": v,
                "geometry": geojson.LineString([frm, to]),
                "properties": {
                    "name": str(len(edges)),
                    "length": utility.distance(frm, to),
                },
            }
            edge_r = {
                "id": self.edges_id[(v, u)],
                "u": v,
                "v": u,
                "geometry": geojson.LineString([to, frm]),
                "properties": {
                    "name": str(len(edges) + 1),
                    "length": utility.distance(to, frm),
                },
            }

            edges.append(edge)
            edges.append(edge_r)

        nodes_gdf = gpd.GeoDataFrame(
            {
                "id": list(nodes_idx.values()),
                "x": [point[0] for point in nodes_idx.keys()],
                "y": [point[1] for point in nodes_idx.keys()],
                "geometry": list(nodes_idx.keys()),
                "properties": [{"name": node_id} for node_id in nodes_idx.values()],
            }
        )
        edges_gdf = gpd.GeoDataFrame(edges).set_index(["u", "v", "id"])
        direct_G: nx.MultiDiGraph = ox.graph_from_gdfs(
            nodes_gdf,
            edges_gdf,
        )
        direct_G.graph["crs"] = "EPSG:6680"

        print(time.perf_counter() - t)

        self.G = direct_G.to_undirected()

    def nx_to_nearest_edge_feature(self, file_path) -> tuple[dict, tuple[int, int]]:
        is_dbg = (False, False, True)

        print("nx to nearest feature")
        t = time.perf_counter()

        with open(file=file_path, mode="r", encoding="utf_8_sig") as f:
            data = json.load(f)

        graph, points = _connect(data)
        grid_point: dict[list[int]] = dict()

        for point in points:
            edge = ox.nearest_edges(self.G, *data["grid_point"][point])
            a, b, _ = edge
            edge_name = self.G.edges.get((a, b, self.edges_id[(a, b)]))["properties"][
                "name"
            ].split("_")[0]

            # coordinates
            A = self.G.nodes.get(a)["geometry"]
            B = self.G.nodes.get(b)["geometry"]
            P = data["grid_point"][point]

            # add node Q
            q = self.G.number_of_nodes()
            Q = utility.nearest_point(P, A, B)

            self.G.add_node(
                q,
                id=q,
                x=Q[0],
                y=Q[1],
                geometry=Q,
                properties={"name": str(q)},
            )
            grid_point[point] = q

            def divide_edge(
                prv, prv_coordinate, cur, cur_coordinate, nxt, nxt_coordinate
            ):
                edge_parameter_builder = lambda x, y, edge_id: {
                    "geometry": geojson.LineString([x, y]),
                    "properties": {
                        "name": edge_name + "_add" + str(edge_id),
                        "length": utility.distance(x, y),
                    },
                }

                def add_edge(frm, frm_coordinate, to, to_coordinate):
                    if not (frm, to) in self.edges_id.keys():
                        self.edges_id[(frm, to)] = len(self.edges_id.keys())

                    edge_id = self.edges_id[frm, to]
                    edge_parameter = edge_parameter_builder(
                        frm_coordinate, to_coordinate, edge_id
                    )
                    self.G.add_edge(
                        frm,
                        to,
                        edge_id,
                        geometry=edge_parameter["geometry"],
                        properties=edge_parameter["properties"],
                    )

                # remove edge
                if (prv, nxt) in self.edges_id:
                    self.G.remove_edge(*(prv, nxt, self.edges_id[(prv, nxt)]))

                # add edge
                add_edge(*(prv, prv_coordinate), *(cur, cur_coordinate))
                add_edge(*(cur, cur_coordinate), *(nxt, nxt_coordinate))

            divide_edge(*(a, A), *(q, Q), *(b, B))
            divide_edge(*(b, B), *(q, Q), *(a, A))

        features = dict()
        features["LineString"] = list()
        features["Point"] = list()
        features["Point_err"] = list()

        features_set = set()
        field_edge = list()
        for cur in points:
            for nxt in graph[cur]:
                shortest_path = nx.shortest_path(
                    self.G, grid_point[cur], grid_point[nxt]
                )

                for i in range(len(shortest_path) - 1):
                    u, v = shortest_path[i], shortest_path[i + 1]

                    edge = self.G.get_edge_data(u, v)
                    field_edge.append(edge)
                    for key in edge.keys():
                        feature = key
                        if feature in features_set:
                            continue
                        features_set.add(feature)
                        features["LineString"].append(
                            geojson.Feature(
                                id=key,
                                geometry=edge[key]["geometry"],
                                properties=edge[key]["properties"],
                            )
                        )

        if any(is_dbg):
            if is_dbg[0]:
                for point in grid_point.values():
                    node = self.G.nodes[point]

                    id = node["id"]
                    geometry = [node["x"], node["y"]]
                    properties = {"name": str(node["properties"]["name"])}

                    feature = geojson.Feature(
                        id=id,
                        geometry=geojson.Point(geometry),
                        properties=properties,
                    )
                    features["Point"].append(feature)

            if is_dbg[1]:
                for point in graph.keys():
                    feature = geojson.Feature(
                        id=point,
                        geometry=geojson.Point(data["grid_point"][point]),
                        properties={"name": str(point)},
                    )
                    features["Point"].append(feature)

            if is_dbg[2]:
                for e in field_edge:
                    for key in e.keys():
                        try:
                            for point in e[key]["geometry"]["coordinates"]:
                                feature = geojson.Feature(
                                    id=e[key]["properties"]["name"],
                                    geometry=geojson.Point(point),
                                    properties={"name": e[key]["properties"]["name"]},
                                )
                                features["Point_err"].append(feature)
                        except:
                            coordinates = e[key]["geometry"]
                            for point in coordinates.coords:
                                point = list(point)
                                feature = geojson.Feature(
                                    id=e[key]["properties"]["name"],
                                    geometry=geojson.Point(point),
                                    properties={"name": e[key]["properties"]["name"]},
                                )
                                features["Point_err"].append(feature)

        center = center_from_geojson(self.default_data_path)
        print(time.perf_counter() - t)
        return features, center
