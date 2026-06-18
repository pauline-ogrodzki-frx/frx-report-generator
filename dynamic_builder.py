import os.path
import json
from PIL import Image, ImageDraw
import pandas as pd
import random
import ssl
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch

ssl._create_default_https_context = ssl._create_unverified_context
import socket

socket.setdefaulttimeout(18)
from color_calculation import *
from reportlab.pdfgen.canvas import Canvas
import textwrap


def register_fonts():
    """
    adding custom fonts to the system
    :return:
    """
    try:
        pdfmetrics.registerFont(TTFont('Rob', 'Roboto-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('RobIt', 'Roboto-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('RobB', 'Roboto-Bold.ttf'))

    except Exception as e:
        print_log("Exception in register_fonts: {}".format(str(e)))
        print_log(traceback.format_exc())


def place_image(can, y, color):
    """
    place a marker section image
    :param x:
    :param y:
    :param color:
    :return:
    """
    try:
        sign = ImageReader('images/{}.png'.format(color))
        can.drawImage(sign, 20, y+4, 32, 32, mask='auto')

    except Exception as e:
        print_log("Exception in place_image: {}".format(str(e)))
        print_log(traceback.format_exc())


colors = {"green": "#009985",
          "orange": "#eda831",
          "red": "#c00000",
          "grey": "#d8d8d8",
          }


def percent_to_number(percent):
    len = 1760 / 100 * percent
    return len


def build_image(percent, color):
    width = int(percent_to_number(percent))
    # create an image
    im = Image.new("RGBA", (width + 1, 62), (0, 0, 0, 0))
    # get a font
    # get a drawing context
    draw = ImageDraw.Draw(im, "RGBA")
    draw.rounded_rectangle([(0, 0), (width, 62)], radius=29, fill=color, outline=color, width=1, corners=None)
    for x in range(1, 3000):
        if x % 8 == 0:
            draw.line([(-100 + x, 0), (200 + x, 200)], fill=(255, 255, 255, 0), width=3)
    draw.rounded_rectangle([(0, 0), (width, 62)], radius=29, fill=None, outline=color, width=3, corners=None)

    # draw multiline text
    return im


def get_concat_h(im1, im2):
    if im2.width > 2:
        dst = Image.new('RGBA', (im1.width + im2.width, im1.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width, 0))
        return dst
    return im1


def build_graph(res_dict, file_path):
    images = [build_image(k[1], colors[k[0]]) for k in res_dict]
    if len(images) > 1:
        im = get_concat_h(images[0], images[1])
        for x in range(1, len(images) - 1):
            im = get_concat_h(im, images[x + 1])
    else:
        im = images[0]

    im.save(file_path)


def build_stats(colormap, range_values, file_path):
    a_values = []
    for x in range(1, len(range_values)):
        a_values.append(range_values[x] - range_values[x - 1])
    total = sum(a_values)
    res = [round(x / total * 100, 2) for x in a_values]
    res_dict = []
    for x in range(len(res)):
        if len(res_dict) > 0 and res_dict[-1][0] == colormap[x]:
            res_dict[-1][1] += res[x]
        else:
            res_dict.append([colormap[x], res[x]])
    print(res_dict)
    build_graph(res_dict, file_path)


def print_pointed_result(can, df, y, key, postfix, min1, max1, config_row):
    min = 287
    max = 575
    if len(df[df['name'] == key]) > 0:
        value = df[df['name'] == key].iloc[0]['user_value']

        if config_row and config_row['Percentage'] == "TRUE":
            postfix = '%'
        if value > 10:
            value = round(value, 2)
        else:
            value = round(value, 5)
        can.setFont('Rob', 9)
        if config_row and config_row['Percentage'] == "TRUE":
            can.drawString(230, y, str(round(value * 100, 3)) + postfix)
        else:
            can.drawString(230, y, str(value) + postfix)
        print_point(can, min, max, y, min1, max1, value)


def print_point(can, min, max, y1, min1, max1, value):
    if value == 0:
        value += min1 + 0.000000001
    if value > max1:
        value = max1 + 0.000000001
    can.setFont('RobIt', 40)
    can.setFillColor(HexColor(0x003e43))
    diff1 = max1 - min1
    value = float(value) - min1
    percent = value / diff1
    x1 = min + ((max - min) * percent)
    can.drawString(x1, y1, '.')
    can.setFont('RobIt', 16)

def add_KIT(can, config):
    can.setFont('Rob', 7)
    can.setFillColor(HexColor(0x48b8b2))
    can.drawString(270, 33, "Kit ID: {}".format(config['Kit ID']))

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

def place_page_no(can, page):
    can.setFont('Rob', 9)
    can.setFillColor(HexColor(0xada9a9))
    if page != 4:
        can.drawString(545, 37, str(page))


def place_dynamic_part(can, page, config):
    fixes_categories = read_json('fixed_color_categories.json')
    config_data = read_json('сonfig_fields.json')
    register_fonts()
    current_level = 450
    df = pd.read_csv(config['metrics_file'])
    print(df)
    groups = df.groupby('category_title', sort=False)
    processed_categories = []
    for g in groups:
        if g[0] not in ['Microbiome Diversity', 'Host DNA']:
            print(g[0])
            print(g[1])

            group_names = g[1]['name'].tolist()
            super_categories = [x['Super category'] for x in config_data if
                                x['name'] in group_names and x['Super category'] and 'page' not in x['Super category']]
            print(group_names)
            if super_categories:
                super_category = super_categories[0].upper()
                if super_category not in processed_categories:
                    processed_categories.append(super_category)
                    print(super_category)
                    can.setFillColor(HexColor(0x003e43))
                    if current_level < 90:
                        place_page_no(can, page)
                        add_KIT(can, config)
                        page += 1
                        can.showPage()
                        current_level = 770
                    can.setFont('Rob', 13)
                    can.drawString(60, current_level - 10, super_category)
                    can.setFillColor(HexColor(0x48b8b2))
                    can.roundRect(60, current_level - 15, 520, 2, 1, fill=1, stroke=0)
                    can.roundRect(60, current_level - 20, 520, 2, 1, fill=1, stroke=0)

                    can.setFillColor(HexColor(0x003e43))

                    current_level -= 40
            color_df = g[1][g[1]['range_lower'].le(g[1]['user_value']) & g[1]['range_upper'].ge(g[1]['user_value'])][
                'range_color']

            if current_level < 90:
                place_page_no(can, page)
                add_KIT(can, config)
                page+=1
                can.showPage()
                current_level = 770
            if g[0] == 'Gut Ratio':
                continue

            can.setFillColor(HexColor(0x003e43))
            can.setFont('RobB', 12)
            can.drawString(1 * inch, current_level, g[0])
            can.setFillColor(HexColor(0x757070))
            can.rect(60, current_level - 25, 520, 20, fill=1, stroke=0)
            can.setFillColor(HexColor(0x003e43))
            can.setFillColor(HexColor(0xffffff))
            can.setFont('RobB', 10)
            can.drawString(70, current_level - 18, 'METRIC')
            can.drawString(230, current_level - 18, 'RESULT')
            can.drawString(400, current_level - 18, "RANGE")
            current_level -= 20

            if g[0] in fixes_categories.keys():
                color = fixes_categories[g[0]]
            else:
                color = 'green'
                values = color_df.tolist()
                if 'red' in values:
                    color = 'red'
                elif 'orange' in values:
                    color = 'yellow'
            place_image(can, current_level - 14, color)

        folder = os.path.join('ranges', str(g[0]))
        if not os.path.exists(folder):
            os.makedirs(folder)
        group_2 = g[1].groupby('name', sort=False)

        for row in group_2:
            row = (row[0], row[1].sort_values('range_upper'))
            name = row[0]
            row = row[1]
            range1 = row['range_upper'].tolist()
            range2 = row['range_lower'].tolist()
            range1.extend(range2)
            range1 = list(set(range1))

            range1.sort()
            if name == "Shannon diversity":
                range1[-1] = 12
            elif name == "Host DNA":
                print(range1)
                range1[-1] = 0.55
                print(range1)
            elif list(set(row['user_value'].tolist()))[0] < range1[-2]:
                range1[-1] = range1[-2] + range1[-2] * 0.8

            else:
                range1[-1] = list(set(row['user_value'].tolist()))[0] + (range1[-2]) * 0.3

            if g[0] not in ['Microbiome Diversity', 'Host DNA']:
                if current_level < 90:
                    place_page_no(can, page)
                    add_KIT(can, config)
                    page += 1
                    can.showPage()
                    current_level = 770
            else:
                current_level +=20

            config_row = {}
            if name.lower().strip().replace(' ', '') in [x['name'].lower().replace(' ', '') for x in config_data]:
                config_row = \
                    [x for x in config_data if
                     x['name'].lower().replace(' ', '') == name.lower().strip().replace(' ', '')][-1]

            values = [x for x in range1 if str(x) != 'nan']
            color_values = [x for x in row['range_color'].tolist()]
            range_values = [x for x in values]
            if config_row and config_row['Percentage'] == "TRUE":
                range_values = [x * 100 for x in values]
            range_marker = '(' + str(';'.join([str(round(x, 2)) for x in range_values[1:-1]])) + ')'
            range_marker = range_marker.replace('.0;', ';').replace('.0)', ')')
            file_path = os.path.join(folder, "{}.png".format(name))
            build_stats(color_values, range_values, file_path)
            if g[0] in ['Microbiome Diversity', 'Host DNA']:
                continue

            can.setFillColor(HexColor(0x003e43))
            current_level -= 20

            if config_row and config_row['Italics'] == 'TRUE':
                can.setFont('RobIt', 10)
            else:
                can.setFont('Rob', 10)

            res = row['user_value'].tolist()[0]
            indexes = range_marker
            if len(name) > 35:
                wrapped_text = textwrap.wrap(name, 35)
                can.drawString(70, current_level, wrapped_text[0])
                can.drawString(70, current_level - 12, wrapped_text[1])
                delta = 6

            else:
                can.drawString(70, current_level + 3, name)
                delta = -1
            # can.drawString(190, current_level, str(res) + "%")

            sign = ImageReader(file_path)
            can.drawImage(sign, 290, current_level, 290, 10, mask='auto')

            print_pointed_result(can, row, current_level+3, name, '', range1[0], range1[-1], config_row)
            #print_point(can, 257, 575, current_level-1, 0,10, 0)
            #print_point(can, 257, 575, current_level-1, 0,10, 10)

            can.setFillColor(HexColor(0xb4b4b4))
            can.setFont('Rob', 6.2)
            qty_w = stringWidth(indexes, 'Rob', 6.2)
            can.drawString(580 - qty_w, current_level - 5, indexes)
            current_level -= delta

        current_level -= 30
    return can, page



def build_images(config):
    fixes_categories = read_json('fixed_color_categories.json')
    config_data = read_json('сonfig_fields.json')
    df = pd.read_csv(config['metrics_file'])
    print(df)
    groups = df.groupby('category_title', sort=False)
    processed_categories = []
    for g in groups:
        if g[0] not in ['Microbiome Diversity', 'Host DNA']:
            continue

        folder = os.path.join('ranges', str(g[0]))
        if not os.path.exists(folder):
            os.makedirs(folder)
        group_2 = g[1].groupby('name', sort=False)

        for row in group_2:
            row = (row[0], row[1].sort_values('range_upper'))
            name = row[0]
            row = row[1]
            range1 = row['range_upper'].tolist()
            range2 = row['range_lower'].tolist()
            range1.extend(range2)
            range1 = list(set(range1))

            range1.sort()
            if name == "Shannon diversity":
                range1[-1] = 12
            elif name == "Host DNA":
                print(range1)
                range1[-1] = 0.55
                print(range1)
            elif list(set(row['user_value'].tolist()))[0] < range1[-2]:
                range1[-1] = range1[-2] + range1[-2] * 0.8

            else:
                range1[-1] = list(set(row['user_value'].tolist()))[0] + (range1[-2]) * 0.3

            config_row = {}
            if name.lower().strip().replace(' ', '') in [x['name'].lower().replace(' ', '') for x in config_data]:
                config_row = \
                    [x for x in config_data if
                     x['name'].lower().replace(' ', '') == name.lower().strip().replace(' ', '')][-1]

            values = [x for x in range1 if str(x) != 'nan']
            color_values = [x for x in row['range_color'].tolist()]
            range_values = [x for x in values]
            if config_row and config_row['Percentage'] == "TRUE":
                range_values = [x * 100 for x in values]
            range_marker = '(' + str(';'.join([str(round(x, 2)) for x in range_values[1:-1]])) + ')'
            range_marker = range_marker.replace('.0;', ';').replace('.0)', ')')
            file_path = os.path.join(folder, "{}.png".format(name))
            build_stats(color_values, range_values, file_path)



config = read_json('config.json')
build_images(config)