import json
import geojson


from src import geo_feature, utility

with open("./data/file_path.json") as f:
    data_path = json.load(f)

default_data_path = data_path["default"]
support = data_path["support"]
target_data_path = data_path["target"]


def nearest_path_feature_collection():
    nearest_feature = geo_feature.Nearest_Feature(default_data_path, support)
    nearest_feature.build()
    exit()

    feature_collection = geojson.FeatureCollection(features["LineString"])

    return feature_collection, center


def default_feature_collection():
    return (
        geo_feature.json_feature(default_data_path),
        geo_feature.center_from_geojson(default_data_path),
    )


def target_feature_collection():
    try:
        nearest_feature = geo_feature.Nearest_Feature(default_data_path, support)
        nearest_feature.build(target_data_path)

        print(target_data_path)
        return (
            geo_feature.json_feature(target_data_path),
            geo_feature.center_from_geojson(target_data_path),
        )
    except Exception as e:
        print(e)
        raise utility.InnerException()


def target_build(): ...


# if __name__ == "__main__":
#     nearest_feature = geo_feature.Nearest_Feature(default_data_path, support)
#     nearest_feature.build(target_data_path)
#     exit()

#     default_feature = geojson.FeatureCollection(
#         geo_feature.json_feature(default_data_path)
#     )
#     feature_collection = geojson.FeatureCollection(features["LineString"])
#     feature_collection_point = geojson.FeatureCollection(features["Point"])
#     feature_collection_point_err = geojson.FeatureCollection(features["Point_err"])
#     folium_map = folium.Map(
#         location=center, zoom_start=17
#     )  # デフォルトの表示緯度経度  # デフォルトの表示倍率

#     style_def = lambda x: {
#         "fillColor": "#000000",
#         "color": "#00ff00",
#         "fillOpacity": 1,
#         "weight": 1,
#     }

#     style = lambda x: {
#         "fillColor": "#000000",
#         "color": "#ff0000",
#         "fillOpacity": 1,
#         "weight": 10,
#     }

#     tooltip = folium.GeoJsonTooltip(fields=["name"])

#     """
#     folium.GeoJson(default_feature, style_function=style_def, tooltip=tooltip).add_to(
#         folium_map
#     )
#     """

#     folium.GeoJson(feature_collection, style_function=style, tooltip=tooltip).add_to(
#         folium_map
#     )

#     # def style_function(feature):
#     #     markup = f"""
#     #             <div style="font-size: 0.8em;">
#     #             <div style="width: 10px;
#     #                         height: 10px;
#     #                         border: 1px solid black;
#     #                         border-radius: 5px;
#     #                         background-color: orange;">
#     #             </div>
#     #         </div>
#     #     """
#     #     return {"html": markup}

#     # def style_function_err(feature):
#     #     markup = f"""
#     #             <div style="font-size: 0.8em;">
#     #             <div style="width: 10px;
#     #                         height: 10px;
#     #                         border: 1px solid black;
#     #                         border-radius: 5px;
#     #                         background-color: blue;">
#     #             </div>
#     #         </div>
#     #     """
#     #     return {"html": markup}

#     # folium.GeoJson(
#     #     feature_collection_point_err,
#     #     marker=folium.Marker(icon=folium.DivIcon()),
#     #     style_function=style_function_err,
#     # ).add_to(folium_map)

#     # folium.GeoJson(
#     #     feature_collection_point,
#     #     marker=folium.Marker(icon=folium.DivIcon()),
#     #     style_function=style_function,
#     # ).add_to(folium_map)

#     folium_map.save(outfile="road_network.html")
