import torch
import numpy as np
import os
import json
from PIL import Image
from detector import Detector
from util import show_bbox
import time, datetime
from util import center_fix
from detector import get_pred
import torchvision.transforms as transforms


class Inferencer(object):
    def __init__(self, net):
        self.net = net
        self.normalizer = transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))

    def pred(self, img_pil):
        _boxes = torch.zeros(0, 4)
        img_pil, boxes, loc, scale = center_fix(img_pil, _boxes, self.net.view_size)
        img = transforms.ToTensor()(img_pil)
        img = self.normalizer(img).view(1, img.shape[0], img.shape[1], img.shape[2])
        # img = img.cuda()
        loc = loc.view(1, -1)  # .cuda()
        with torch.no_grad():
            temp = self.net(img, loc)
            cls_i_preds, cls_p_preds, reg_preds = get_pred(temp, self.net.nms_th, self.net.nms_iou)
            reg_preds[0][:, 0::2] -= loc[0, 0]
            reg_preds[0][:, 1::2] -= loc[0, 1]
            reg_preds[0] /= scale
        return cls_i_preds[0], cls_p_preds[0], reg_preds[0]


net = Detector(pretrained=False)

try:
    from torch.hub import load_state_dict_from_url
except ImportError:
    from torch.utils.model_zoo import load_url as load_state_dict_from_url

state_dict = load_state_dict_from_url('https://drive.google.com/file/d/1IgbS2P02XNvCSXO91Qji9KxGrMaOj4PS',
                                      map_location='cpu')
net.load_state_dict(torch.load(state_dict, map_location='cpu'))
net.eval()
inferencer = Inferencer(net)


def detect(img_path, save_path=None, use_gpu=False):
    '''
    Return:
    bool, exist hot area
    float, max prob
    '''
    print('detection:')
    img = Image.open(img_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    prev_t = time.time()
    cls_i_preds, cls_p_preds, reg_preds = inferencer.pred(img)
    cur_t = time.time()
    inference_time = datetime.timedelta(seconds=cur_t - prev_t)
    print("\t+ Inference Time: %s" % (inference_time))

    show_bbox(img, reg_preds.cpu(), cls_i_preds.cpu(), cls_p_preds.cpu(), save_path)
    return cls_i_preds.cpu().shape[0] > 0, cls_p_preds.cpu().max() if cls_p_preds.cpu().shape[0] > 0 else 0
