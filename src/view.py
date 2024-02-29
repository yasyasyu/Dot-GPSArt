import json

from src import geo_feature, utility

with open("./data/file_path.json") as f:
    data_path = json.load(f)

default_data_path = data_path["default"]
support = data_path["support"]
target_data_path = data_path["target"]


def target_feature_collection():
    try:
        nearest_feature = geo_feature.Nearest_Feature(default_data_path, support)
        nearest_feature.build(target_data_path)

        return (
            geo_feature.json_feature(target_data_path),
            geo_feature.center_from_geojson(target_data_path),
        )
    except Exception as e:
        print(e)
        raise utility.InnerException()
