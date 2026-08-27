#!/usr/bin/env python3
# Frozen production YOLOX-tiny experiment for AeroGuard FOD-A.
from __future__ import annotations

import os
from pathlib import Path

from yolox.exp import Exp as YOLOXExp


YOLOX_SOURCE_COMMIT = "6ddff4824372906469a7fae2dc3206c7aa4bbaee"


class Exp(YOLOXExp):
    def __init__(self):
        super().__init__()
        self.depth = 0.33
        self.width = 0.375
        self.exp_name = Path(__file__).stem

        self.data_dir = os.environ.get("AEROGUARD_COCO_DIR", "artifacts/foda_yolox")
        self.train_ann = "instances_train2017.json"
        self.val_ann = "instances_val2017.json"
        self.num_classes = 31

        # FOD-A source images are 300x300 and the dataset has a meaningful small-object tail.
        # Keep the first competition baseline at 640 throughout instead of random downscaling.
        self.input_size = (640, 640)
        self.test_size = (640, 640)
        self.random_size = (20, 20)
        self.mosaic_scale = (0.5, 1.5)
        self.enable_mixup = False

        self.max_epoch = 100
        self.warmup_epochs = 5
        self.no_aug_epochs = 10
        self.eval_interval = 5
        self.data_num_workers = 4
        self.print_interval = 20
        self.seed = 20260826
