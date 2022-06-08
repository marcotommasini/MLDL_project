# -*- coding: utf-8 -*-
"""loss.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AwKR7FZzzD-fnCX-uuZfaLgNZ-4A0MWY
"""

import torch.nn as nn
import torch
import torch.nn.functional as F
from torch.autograd import Variable

def flatten(tensor):
    """Flattens a given tensor such that the channel axis is first.
    The shapes are transformed as follows:
       (N, C, D, H, W) -> (C, N * D * H * W)
    """
    C = tensor.size(1)
    # new axis order
    axis_order = (1, 0) + tuple(range(2, tensor.dim()))
    # Transpose: (N, C, D, H, W) -> (C, N, D, H, W)
    transposed = tensor.permute(axis_order)
    # Flatten: (C, N, D, H, W) -> (C, N * D * H * W)
    return transposed.contiguous().view(C, -1)

class DiceLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.epsilon = 1e-5

    def forward(self, output, target):
        assert output.size() == target.size(), "'input' and 'target' must have the same shape"
        output = F.softmax(output, dim=1)
        output = flatten(output)
        target = flatten(target)
        # intersect = (output * target).sum(-1).sum() + self.epsilon
        # denominator = ((output + target).sum(-1)).sum() + self.epsilon

        intersect = (output * target).sum(-1)
        denominator = (output + target).sum(-1)
        dice = intersect / denominator
        dice = torch.mean(dice)
        return 1 - dice
        # return 1 - 2. * intersect / denominator

class CrossEntropyLoss(nn.Module):
  def __init__(self, backgroud_label_value = 255):
    super().__init__()
    self.backgroud = backgroud_label_value
  
  def forward(self, prediction, target, weight = None):
    
    batch_size, number_classes, height, width = prediction.size()
    target_mask = (target >= 0) * (target != self.background)
    target = target[target_mask]

    if not target.data.dim():
      return Variable(torch.zeros(1))

    prediction = prediction.transpose(1, 2).transpose(2, 3).contiguous()
    prediction = prediction[target_mask.view(batch_size, height, width, 1).repeat(1, 1, 1, number_classes)].view(-1, number_classes)

    loss = F.cross_entropy(prediction, target, weight=weight)
    return loss