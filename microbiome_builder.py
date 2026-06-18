import os.path

from PIL import Image, ImageDraw
import pandas as pd

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


def build_microbiome(perc1, perc2, perc3, perc4):
    im1 = build_image(perc1, "#009985")
    im2 = build_image(perc2, "#eda831")
    im3 = build_image(perc3, "#c00000")
    im4 = build_image(perc4, "#d8d8d8")

    im = get_concat_h(im1, im2)
    im = get_concat_h(im, im3)
    im = get_concat_h(im, im4)
    im.save(os.path.join('images', 'microbiome.png'))



def build_stats(filepath):
    df = pd.read_csv(filepath)
    df['category_gut'] = df['category_gut'].fillna("Unknown")
    dff = df.groupby(['category_gut']).classified_relative_abundance.sum().reset_index()
    df_dict = dict(zip(dff.category_gut, dff.classified_relative_abundance))


    sum_dict = sum(df_dict.values())
    if sum_dict < 0.99:
        df_dict["Unknown"] += (1-sum_dict)
        print(df_dict["Unknown"])
    for k, v in df_dict.items():
        if v<0.001:
            df_dict[k] = 0
        else:
            df_dict[k] = round( df_dict[k]*100, 2)
    build_microbiome(df_dict['Beneficial'], df_dict['Variable'], df_dict['Unfriendly'], df_dict['Unknown'])
    return df_dict

