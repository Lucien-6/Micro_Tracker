#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Micro Tracker - 显微视频目标分割和追踪工具
=========================================

基于SAM2 (Segment Anything Model 2)的显微视频目标分割和追踪工具。

作者: Lucien
版权所有 © 2025 Lucien. 保留所有权利。
"""

import sys
import os

# 确保当前目录在搜索路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from micro_tracker.app import main

if __name__ == "__main__":
    main() 