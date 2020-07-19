import torch
import numpy as np
import matplotlib.pyplot as plt
import os, math, random
from PIL import Image, ImageDraw
import torch.utils.data as data
import torchvision.transforms as transforms
import matplotlib.patches as patches
from matplotlib.ticker import NullLocator
import random


def center_fix(img, boxes, size):
    w, h = img.size
    size_min = min(w, h)
    size_max = max(w, h)
    sw = sh = float(size) / size_max
    ow = int(w * sw + 0.5)
    oh = int(h * sh + 0.5)
    ofst_w = round((size - ow) / 2.0)
    ofst_h = round((size - oh) / 2.0)
    img = img.resize((ow, oh), Image.BILINEAR)
    img = img.crop((-ofst_w, -ofst_h, size - ofst_w, size - ofst_h))
    if boxes.shape[0] != 0:
        boxes = boxes * torch.FloatTensor([sh, sw, sh, sw])
        boxes += torch.FloatTensor([ofst_h, ofst_w, ofst_h, ofst_w])
    loc = torch.FloatTensor([ofst_h, ofst_w, ofst_h + oh, ofst_w + ow])
    return img, boxes, loc, sw


def show_bbox(img, boxes, labels, labels_p, file_name):
    NAME_TAB = ['background', 'hot area']
    if not isinstance(img, Image.Image):
        img = transforms.ToPILImage()(img)

    img = np.array(img)
    plt.figure()
    fig, ax = plt.subplots(1)
    ax.imshow(img)
    if boxes is None:
        return
    for [y1, x1, y2, x2], cls_conf, cls_pred in zip(boxes, labels_p, labels):
        print("\t+ Label: %s, Conf: %.5f" % (NAME_TAB[int(cls_pred)], cls_conf.item()))

        box_w = x2 - x1
        box_h = y2 - y1

        # Create a Rectangle patch
        bbox = patches.Rectangle((x1, y1), box_w, box_h, linewidth=2, edgecolor='blue', facecolor="none")
        # Add the bbox to the plot
        ax.add_patch(bbox)
        # Add label
        # plt.text(x1, y1, s=NAME_TAB[int(cls_pred)], color="white", verticalalignment="top",
        #          bbox={"color": 'blue', "pad": 0}, fontsize=12)
    plt.axis("off")
    plt.gca().xaxis.set_major_locator(NullLocator())
    plt.gca().yaxis.set_major_locator(NullLocator())

    if file_name is not None:
        if not (file_name.endswith('jpg') or file_name.endswith('png')):
            file_name = f"{file_name}.png"
        plt.savefig(file_name, bbox_inches="tight", pad_inches=0.0)
        plt.close()
