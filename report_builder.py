import os.path
import os.path
import ssl
import os.path
from piecharts import *
from microbiome_builder import *
import pandas as pd
from reportlab.lib.utils import ImageReader
from datetime import datetime
import traceback
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor
import textwrap
import re
import dynamic_builder
from dynamic_builder import place_dynamic_part
ssl._create_default_https_context = ssl._create_unverified_context
import json
import socket
from collections import Counter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT

socket.setdefaulttimeout(18)
import datetime
from reportlab.pdfgen import canvas
import io
import os
from PyPDF2 import PdfReader, PdfWriter
from textwrap import wrap
from color_calculation import *

# path to the config file
config_file = 'config.json'

colors = {'grey': 0xada9a9,
          'green': 0x6ec886,
          'green_text': 0x50bcb4,

          'orange': 0xc00000,
          'red': 0xd75f5a,
          'yellow': 0xffd36b,
          'Beneficial': 0x009985,
          'Variable': 0xeda831,
          'Unfriendly': 0xc00000,
          'Unknown': 0xd8d8d8}


def recreate_log_file():
    """
    recreats LOG.txt file
    :return:
    """
    try:
        # removing LOG file of previous session if exists
        if os.path.exists("LOG.txt"):
            os.remove("LOG.txt")
    except Exception as e:
        print_log("Exception in recreate_log_file: {}".format(str(e)))
        print_log(traceback.format_exc())


def print_log(msg: str):
    """
    print message and wries to LOG.txt
    :param msg:
    :return:
    """
    try:
        print(msg)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("LOG.txt", 'a+') as f:
            f.write('[{}] {}\n'.format(now, msg))
    except Exception as e:
        print("Exception in print_log: {}".format(str(e)))
        print(traceback.format_exc())


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


def get_image_aspect(path):
    """
    get image size and aspect ratio
    :param path:
    :return:
    """
    img = ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return iw, ih, aspect


def register_fonts():
    """
    adding custom fonts to the system
    :return:
    """
    try:
        pdfmetrics.registerFont(TTFont('Montserrat-Bold', 'Montserrat-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('Mons', 'fonts/Montserrat-Medium.ttf'))
        pdfmetrics.registerFont(TTFont('ChelseaMarket', 'fonts/DMSans-Medium.ttf'))
        pdfmetrics.registerFont(TTFont('Montserrat-SemiBoldItalic', 'Montserrat-SemiBoldItalic.ttf'))
        pdfmetrics.registerFont(TTFont('Segoe UI', 'fonts/Montserrat-Medium.ttf'))
        pdfmetrics.registerFont(TTFont('Rob', 'Roboto-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('RobIt', 'Roboto-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('RobB', 'Roboto-Bold.ttf'))

    except Exception as e:
        print_log("Exception in register_fonts: {}".format(str(e)))
        print_log(traceback.format_exc())


def building_pdf_header(can, config):
    """
    filling the header of the PDF
    :param can:
    :param config:
    :return:
    """
    try:
        can.setFont('Rob', 24)

        color = "47b9b2"
        # can.setFillColorRGB(71,185,178, 0)
        can.setFillColor(HexColor(0x47b9b2))

        physician_name = config['Physician Name']
        pat_name = config['Patient Name']
        kit_id = config['Kit ID']
        date = config['Sampling Date']

        print(physician_name)
        can.drawString(230, 457, physician_name)
        can.drawString(230, 412 - 5, pat_name)
        can.drawString(230, 355, kit_id)
        can.drawString(230, 310 - 5, date)

        # can.setFillColorRGB(255,255,255)

        """
        address_wrap = wrap(config['customer_address'], 25)
        lvl = 710
        for part in address_wrap:
            part_w = stringWidth(part, 'Mons', 11)
            can.drawString(540 - part_w, lvl, part)
            lvl -= 15
        can.setFont('Mons', 10)
        can.drawString(110, 685, config['date'])
        can.drawString(110, 670, config['quote_nr'])
        can.drawString(110, 655, config['reference'])
        """
    except Exception as e:
        print_log("Exception in building_pdf_header: {}".format(str(e)))
        print_log(traceback.format_exc())


def building_new_item_row(can, config, item, lvl):
    """
    add new item (row) to the PDF
    :param can:
    :param config:
    :param item:
    :param lvl:
    :return:
    """
    try:
        print_log("adding new row: {}".format(str(item)))
        iw, ih, aspect = get_image_aspect(item['image'])
        target = 40
        aspect_ratio = target / ih
        can.drawImage(item['image'], 15,
                      lvl, iw * aspect_ratio, ih * aspect_ratio, mask='auto')
        description = " | ".join([config['customer_name'], item['description'], item['no']])
        if len(description) > 40:
            description_wrap = wrap(description, 44)
            lvl_descr = lvl + 30
            for part in description_wrap:
                can.drawString(80, lvl_descr, part)
                lvl_descr -= 15
        else:
            lvl_descr = lvl + 16
            can.drawString(80, lvl_descr, description)
        process = " | ".join([item['process1'], item['process2']])
        if len(process) > 40:
            process_wrap = wrap(process, 44)
            lvl_descr = lvl + 30
            for part in process_wrap:
                can.drawString(260, lvl_descr, part)
                lvl_descr -= 15
        else:
            lvl_descr = lvl + 16
            can.drawString(260, lvl_descr, process)
        can.setFont('RobIt', 8)
        qty_w = stringWidth(str(item['qty']), 'Montserrat-SemiBoldItalic', 8)
        can.drawString(460 - qty_w, lvl + 16, str(item['qty']))
        price_w = stringWidth(str('€' + str(item['unit_price'])), 'Montserrat-SemiBoldItalic', 8)
        can.drawString(520 - price_w, lvl + 16, str('€' + str(item['unit_price'])))
        can.setFont('Rob', 7)
    except Exception as e:
        print_log("Exception in building_new_item_row: {}".format(str(e)))
        print_log(traceback.format_exc())


def merge_save_template(can, config, packet):
    """
    save the PDF by merging with the tempalte
    :param can:
    :param config:
    :param packet:
    :return:
    """
    try:
        can.showPage()

        can.save()

        packet.seek(1)
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open('template_new2.pdf', "rb"))

        output = PdfWriter()
        for i in range(4):
            print(i)
            page = existing_pdf.pages[i]
            page.merge_page(new_pdf.pages[i])
            output.add_page(page)

        for i in range(4, len(new_pdf.pages)-3):
            print(i)
            temp_pdf = PdfReader(open('template_new2.pdf', "rb"))

            page = temp_pdf.pages[4]
            page.merge_page(new_pdf.pages[i])
            output.add_page(page)


        page = existing_pdf.pages[5]
        page.merge_page(new_pdf.pages[len(new_pdf.pages)-3])
        output.add_page(page)

        page = existing_pdf.pages[6]
        page.merge_page(new_pdf.pages[len(new_pdf.pages)-2])
        output.add_page(page)


        new_pdf_file_name = os.path.join(config['output_folder'], 'report_TEST' + str(config['Kit ID']) + '.pdf')
        outputStream = open(new_pdf_file_name, "wb")
        output.write(outputStream)
        outputStream.close()
        print_log("Saved to file: {}".format(new_pdf_file_name))
    except Exception as e:
        print_log("Exception in merge_save_template: {}".format(str(e)))
        print_log(traceback.format_exc())

def print_point(can, min, max, y1, min1, max1, value):
    if value == 0:
        value += min1 + 0.001
    if value > max1:
        value = max1 + 0.001
    can.setFont('Montserrat-SemiBoldItalic', 60)
    can.setFillColor(HexColor(0x003e43))
    diff1 = max1 - min1
    value = float(value) - min1
    percent = value / diff1
    x1 = min + ((max - min) * percent)
    can.drawString(x1, y1, '.')
    can.setFont('Montserrat-SemiBoldItalic', 16)


def place_image(can, y, color_map, key):
    """
    place a marker section image
    :param x:
    :param y:
    :param color:
    :return:
    """
    try:
        if key in color_map.keys():
            sign = ImageReader('images/{}.png'.format(color_map[key]))
            can.drawImage(sign, 20, y, 30, 30, mask='auto')

    except Exception as e:
        print_log("Exception in place_image: {}".format(str(e)))
        print_log(traceback.format_exc())


def print_pointed_result(can, df, y, key, postfix, min1, max1):
    min = 272
    max = 477
    print(df[df['name'] == key])
    if len(df[df['name'] == key]) > 0:
        value = df[df['name'] == key].iloc[0]['user_value']
        if postfix == '%':
            value = value * 100
        value = round(value, 2)
        can.setFont('Rob', 9)
        can.drawString(200, y, str(value) + postfix)
        print_point(can, min, max, y, min1, max1, value)


def place_page_no(can, page):
    can.setFont('Rob', 9)
    can.setFillColor(HexColor(0xada9a9))
    can.drawString(545, 37, str(page))


def build_pdf_report(config):
    """
    build a single PDF report
    :param config:
    :return:
    """
    try:
        packet = io.BytesIO()
        can = canvas.Canvas(packet)

        register_fonts()

        min = 60
        max = 535
        diff = 475

        building_pdf_header(can, config)
        can.showPage()
        # PAGE2
        can.setFillColor(HexColor(0x003e43))
        can.setFont('Rob', 12)
        df = pd.read_csv(config['metrics_file'])
        df = df[df['range_lower'].le(df['user_value']) & df['range_upper'].ge(df['user_value'])]
        df.rename({'range_color': 'evaluation_color'}, axis=1, inplace=True)
        df.rename({'evaluation': 'evaluation_text'}, axis=1, inplace=True)

        shan_div = df[df['name'] == "Shannon diversity"]
        can.drawString(240+32, 274, str(shan_div.iloc[0]['user_value']))
        print_point(can, 60, 310, 291, 0, 12, float(shan_div.iloc[0]['user_value']))
        sign = ImageReader('ranges/Microbiome Diversity/Shannon diversity.png')
        can.drawImage(sign, 60, 291-2, 310 - 60, 15, mask='auto')


        can.setFillColor(HexColor(0x003e43))
        can.setFont('Rob', 12)
        host_dna = df[df['name'] == "Host DNA"]
        can.drawString(240+32, 274 - 48, str(host_dna.iloc[0]['user_value']*100) + "%")
        print_point(can, 60, 310, 294 - 50, 0, 55, float(host_dna.iloc[0]['user_value']))
        sign = ImageReader('ranges/Host DNA/Host DNA.png')
        can.drawImage(sign, 60, 294 - 50 - 2, 310 - 60, 15, mask='auto')

        fixed_categories = config.get("fixed_categories", {})

        color_map = get_colormap(
            config['metrics_file'],
            fixed_categories=fixed_categories,
        )

        pd_color = df[df['name'] == "Phocaeicola dorei"].iloc[0]['evaluation_color']
        if pd_color == 'red':
            color_map['Overabundant species'] = 'red'
        elif pd_color == 'orange':
            color_map['Overabundant species'] = 'yellow'
     #   else:
     #       color_map['Overabundant species'] = 'green'
        totals = calculate_values(color_map)
        print(totals)
        print(color_map)
        green_total = totals.get('green', 0)
        red_total = totals.get('red', 0)
        yellow_total = totals.get('yellow', 0)
        can.setFillColor(HexColor(0xffffff))

        green_x = 362 + 5
        yellow_x = 419 + 5
        red_x = 488 + 5
        can.setFont('RobB', 14)

        if len(str(green_total)) > 1:
            green_x -= stringWidth(str(green_total), 'RobB', 14)
        if len(str(red_total)) > 1:
            red_x -= stringWidth(str(red_total), 'RobB', 14)
        if len(str(yellow_total)) > 1:
            yellow_x -= stringWidth(str(yellow_total), 'RobB', 14)

        can.drawString(green_x+17, 283, str(green_total))
        can.drawString(yellow_x+17, 283, str(yellow_total))
        can.drawString(red_x+17, 283, str(red_total))

        Firmicutes = df[df['name'] == "Firmicutes"].iloc[0]['user_value']
        Bacteroides = df[df['name'] == "Bacteroidota"].iloc[0]['user_value']
        print(Firmicutes, Bacteroides)

        fb_ratio = ratioFunction(Firmicutes, Bacteroides)
        can.setFont('Rob', 10)
        can.setFillColor(HexColor(0x003e43))
        can.drawString(145+10, 84, str(fb_ratio))
        build_fb([Firmicutes, Bacteroides])

        Prevotella = df[df['name'] == "Prevotella"].iloc[0]['user_value']
        Bacteroides = df[df['name'] == "Bacteroides"].iloc[0]['user_value']
        print(Prevotella, Bacteroides)
        pb_ratio = ratioFunction(Prevotella, Bacteroides)
        can.setFont('Rob', 10)
        can.setFillColor(HexColor(0x003e43))
        can.drawString(255+10, 84, str(pb_ratio))
        build_pb([Prevotella, Bacteroides])

        sign = ImageReader('images/pb.png')
        can.drawImage(sign, 195, 80, 100, 100, mask='auto')
        sign = ImageReader('images/fb.png')
        can.drawImage(sign, 85, 80, 100, 100, mask='auto')
        print(os.path.exists('images/microbiome.png'))
        sign = ImageReader('images/microbiome.png')
        can.drawImage(sign, 290, 145, 250, 15, mask='auto')

        microbione = build_stats(config['taxa_file'])
        print(microbione)
        can.setFillColor(HexColor(0xd8d8d8))
        can.drawString(395+10, 89, str(microbione['Unfriendly']) + "%")
        can.drawString(495+10, 89, str(microbione['Unknown']) + "%")
        can.drawString(395+10, 110, str(microbione['Beneficial']) + "%")
        can.drawString(495+10, 110, str(microbione['Variable']) + "%")

        add_KIT(can, config)

        can.showPage()
        # PAGE3
        page3(can, df)
        add_KIT(can, config)
        can.showPage()
        # PAGE4
        data = [[[100, 736], 'Major Bacterial Phyla', 'Wingdings-Regular'],
                [[350, 736], 'Potential Fungal Overgrowth', 'Wingdings-Regular'],
                [[100, 724], 'Common Microbiome Members', 'Wingdings-Regular'],
                [[350, 724], 'Potential Stomach Inflammation', 'Wingdings-Regular'],
                [[100, 712], 'Overabundant Species', 'Wingdings-Regular'],
                [[350, 712], 'Parasites and Infection', 'Wingdings-Regular'],
                [[100, 700], 'Common Probiotic Species', 'Wingdings-Regular'],
                [[350, 700], 'Methane Producers', 'Wingdings-Regular'],
                [[100, 688], 'Beneficial Bifidobacterium', 'Wingdings-Regular'],
                [[350, 688], 'Histamine-producing Species', 'Wingdings-Regular'],
                [[100, 676], 'Metabolic Health', 'Wingdings-Regular'],
                [[350, 676], 'Oral Microbes in the Gut', 'Wingdings-Regular'],
                [[100, 664], 'Anti-Inflammatory Markers', 'Wingdings-Regular'],
                [[350, 664], 'Urolithin-producing Species', 'Wingdings-Regular'],
                [[100, 651], 'Opportunistic Pathogens', 'Wingdings-Regular'],
                [[350, 651], 'Microbiome Richness', 'Wingdings-Regular'],
                [[100, 605-20], 'SCFA Production', 'Wingdings-Regular'],
                [[350, 605-20], 'Vitamin Production Capacity', 'Wingdings-Regular'],
                [[100, 592-20], 'Complex Sugar Digestion Capacity', 'Wingdings-Regular'],
                [[350, 592-20], 'Complex Compound Breakdown', 'Wingdings-Regular'],
                [[100, 579-20], 'Fiber Digestion Capacity', 'Wingdings-Regular'],
                [[350, 579-20], 'Microbial GABA Capacity', 'Wingdings-Regular'],
                [[100, 566-20], 'Protein Breakdown Capacity', 'Wingdings-Regular'],
                [[100, 534-40], 'Antibiotic Resistance Signature', 'Wingdings-Regular'],
                [[350, 534-40], 'Mucus Degradation Index', 'Wingdings-Regular'],
                [[100, 521-40], 'Hydrogen Sulphide Index', 'Wingdings-Regular'],
                [[350, 521-40], 'Modified Bile Acid Production Capacity', 'Wingdings-Regular'],
                [[100, 508-40], 'Hexa-LPS Index', 'Wingdings-Regular'],
                [[350, 508-40], 'Gut Resilience Score', 'Wingdings-Regular']
                ]
        for line in data:
            # print(HexColor(colors[color_map[line[1]]]))
            # can.setFillColor(HexColor(colors[color_map[line[1]]]))
            can.setFillColor(HexColor(0x7f7f7f))
            can.setFont('Helvetica', 10)
            can.drawString(line[0][0], line[0][1], '✓ ')
            can.setFont('Rob', 10)

            can.drawString(line[0][0]+10, line[0][1], line[1])

        can.setFillColor(HexColor(0xffffff))
        green_x = 224 + 5
        yellow_x = 241 + 5
        red_x = 269 + 5
        can.setFont('RobB', 14)

        if len(str(green_total)) > 1:
            green_x -= stringWidth(str(green_total), 'RobB', 14)
        if len(str(red_total)) > 1:
            red_x -= stringWidth(str(red_total), 'RobB', 14)
        if len(str(yellow_total)) > 1:
            yellow_x -= stringWidth(str(yellow_total), 'RobB', 14)

        can.drawString(green_x + 17, 803, str(green_total))
        can.drawString(yellow_x + 17, 803, str(yellow_total))
        can.drawString(red_x + 17, 803, str(red_total))

        can, page = place_dynamic_part(can, 4, config)

        place_page_no(can, page)
        add_KIT(can, config)

        can.showPage()

        can.setFillColor(HexColor(0x003e43))
        can.setFont('Rob', 14)
        can.drawString(330, 188, str(pb_ratio))
        can.drawString(330, 398, str(fb_ratio))

        sign = ImageReader('images/pb.png')
        can.drawImage(sign, 230, 178, 220, 220, mask='auto')


        sign = ImageReader('images/fb.png')
        can.drawImage(sign, 230, 385, 220, 220, mask='auto')


        sign = ImageReader('images/microbiome.png')
        can.drawImage(sign, 55, 116, 490, 20, mask='auto')
        can.setFont('Rob', 12)
        can.drawString(162 - 30, 90, str(microbione['Beneficial']) + "%")
        can.drawString(277 - 30, 90, str(microbione['Variable']) + "%")
        can.drawString(410 - 30, 90, str(microbione['Unfriendly']) + "%")
        can.drawString(529 - 30, 90, str(microbione['Unknown']) + "%")

        place_page_no(can, page + 1)
        add_KIT(can, config)

        can.showPage()




        # PAGE8



        df = pd.read_csv(config['taxa_file'])
        df['category_gut'] = df['category_gut'].fillna("Unknown")
        df['about_gut'] = df['about_gut'].fillna("")
        df['classified_relative_abundance'] = round(df['classified_relative_abundance'] * 100, 2)
        df = df[['taxonomy_name',
                 'classified_relative_abundance', 'category_gut', 'about_gut']]
        print(df.columns)
        df = df.sort_values('classified_relative_abundance', ascending=False).head(20)

        current_h = 700

        for index, row in df.iterrows():
            can.setFont('RobIt', 8)
            can.setFillColor(HexColor(0x003e43))
            can.drawString(55, current_h, str(row['taxonomy_name']))
            can.setFont('RobIt', 50)
            can.setFillColor(HexColor(colors[row['category_gut']]))
            can.drawString(35, current_h, '.')
            can.setFont('Rob', 7)
            can.setFillColor(HexColor(0x003e43))
            can.drawString(255 - stringWidth(str(row['classified_relative_abundance']) + "%",
                                             "Rob", 8), current_h,
                           str(row['classified_relative_abundance']) + "%")
            can.setFont('Rob', 5)

            URLless_string = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '',
                                    row['about_gut'].replace('\n', ''))
            URLless_string = URLless_string.replace('(', '').replace('\n', '').replace('\\n', '')
            URLless_string = (URLless_string.replace('[[1]]', '').replace('[[2]]', '').replace('[[3]]', '')
            .replace('[[4]]', '').replace('[[5]]', '').replace('[[6]]', '').replace('[[7]]',
                                                                                    '').replace(
                '[[8]]', ''))
            wrapped_text = textwrap.wrap(URLless_string, 120)
            can.setFont('Rob', 5.2)
            iteration_h = current_h + 3
            for x in wrapped_text:
                can.drawString(275, iteration_h, x)
                iteration_h -= 6
            if not wrapped_text:
                current_h = iteration_h - 20
            else:
                current_h = iteration_h - 10

        add_KIT(can, config)
        place_page_no(can, page + 2)
        can.showPage()

        merge_save_template(can, config, packet)

    except Exception as e:
        print_log("Exception in build_pdf_report: {}".format(str(e)))
        print_log(traceback.format_exc())


def add_KIT(can, config):
    can.setFont('Rob', 7)
    can.setFillColor(HexColor(0x48b8b2))
    can.drawString(270, 33, "Kit ID: {}".format(config['Kit ID']))


def page3(can, df):
    can.setFont('RobIt', 16)
    shan_div = df[df['name'] == "Shannon diversity"]
    part_w = stringWidth("Index {}".format(shan_div.iloc[0]['user_value']),
                         'Montserrat-SemiBoldItalic', 16)
    can.setFillColor(HexColor(colors['grey']))
    can.drawString(545 - part_w, 640, "Index {}".format(
        shan_div.iloc[0]['user_value']))

    print_point(can, 60, 535, 602, 0, 12, float(shan_div.iloc[0]['user_value']))

    sign = ImageReader('ranges/Microbiome Diversity/Shannon diversity.png')
    can.drawImage(sign, 60, 599, 535-60, 15, mask='auto')

    can.setFont('RobIt', 16)
    host_dna = df[df['name'] == "Host DNA"]
    part_w = stringWidth(
        host_dna.iloc[0]['evaluation_text'].upper() + "- {}%".format(host_dna.iloc[0]['user_value']),
        'Montserrat-SemiBoldItalic', 16)
    can.setFillColor(HexColor(colors[host_dna.iloc[0]['evaluation_color']]))
    can.drawString(545 - part_w, 395, host_dna.iloc[0]['evaluation_text'].upper() + "- {}%".format(
        host_dna.iloc[0]['user_value']*100))
    can.setFillColor(HexColor(colors['grey']))
    can.setFont('RobIt', 60)
    print_point(can, 60, 535, 355, 0, 55, float(host_dna.iloc[0]['user_value']))
    sign = ImageReader('ranges/Host DNA/Host DNA.png')
    can.drawImage(sign, 60, 355-2, 535 - 60, 15, mask='auto')

    can.setFont('Rob', 7)

    config = read_json('config_fields.json')
    config_ent = read_json('config.json')

    enterotype = config_ent['enterotype']

    text = [x for x in config if x['category_title'] == "Enterotype" and x['name'].lower() == enterotype.lower()][0]['Comments'].replace('\n', ' ')
    print(text)
    styles = getSampleStyleSheet()
    styleN = ParagraphStyle(
        name='CellStyle',
        parent=styles['Normal'],
        fontName='Rob',
        fontSize=8.5,  # Set the desired font size here for the cells
        textColor=HexColor(colors['green_text']),
        leading=12,
        alignment=TA_JUSTIFY
    )
    register_fonts()
    styles = getSampleStyleSheet()
    can.setFillColor(HexColor(colors['green_text']))
    p = Paragraph(text, style=styleN)
    width, height = p.wrapOn(can, 475, 20)
    print(width)
    print(height)
    p.wrapOn(can, 475, 20)
    p.drawOn(can, 62, 175-height)

    can.setFont('RobIt', 14)
    text_w = stringWidth(enterotype, 'RobIt', 12)
    can.drawString(500-text_w, 190, enterotype.upper())


def main():
    try:
        recreate_log_file()
        config = read_json(config_file)
        if not os.path.exists(config['output_folder']):
            os.mkdir(config['output_folder'])
        build_pdf_report(config)
        print_log("Done and saved")
    except Exception as e:
        print_log("Exception in the main pipeline: {}".format(str(e)))
        print_log(traceback.format_exc())


if __name__ == '__main__':
    main()
