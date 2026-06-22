import pandas as pd
import traceback
from collections import Counter
import json


def print_log(msg: str):
    try:
        print(msg)
    except Exception as e:
        print("Exception in print_log: {}".format(str(e)))

def read_json(config_file):
    """
    reads json files
    :param config_file:
    :return:
    """
    try:
        print(config_file)
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print_log("Exception in read_json: {}".format(str(e)))
        print_log(traceback.format_exc())



def get_colormap(file_path, fixed_categories=None):
    """
    Build a colormap.

    fixed_categories allows Django to override specific report metric colours,
    replacing the old fixed_color_categories.json workflow.
    """
    try:
        fixes_categories = fixed_categories or {}

        df = pd.read_csv(file_path)
        df = df[df['range_lower'].le(df['user_value']) & df['range_upper'].ge(df['user_value'])]
        df.rename({'range_color': 'evaluation_color'}, axis=1, inplace=True)
        df.rename({'evaluation': 'evaluation_text'}, axis=1, inplace=True)

        df = df[df["category_title"] != "Microbiome Diversity"]
        df = df[df["category_title"] != "Host DNA"]
        df = df[df["category_title"] != "Gut Ratio"]

        results = {}

        for i in df.groupby('category_title')["evaluation_color"]:
            key = i[0]
            color = 'green'
            values = list(set(i[1].values.tolist()))

            if 'red' in values:
                color = 'red'
            elif 'orange' in values:
                color = 'yellow'

            results[key] = color

        for k, v in fixes_categories.items():
            if k in results.keys() and v:
                results[k] = v
                print("Color changed for {} to {}".format(k, v))

        return results

    except Exception as e:
        print("Exception in get_colormap: {}".format(str(e)))
        print(traceback.format_exc())


def calculate_values(results):
    values = list(results.values())
    values = Counter(values)
    return dict(values)


