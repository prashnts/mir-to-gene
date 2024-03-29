#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# fh = logging.FileHandler('spam.log')
# fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# fh.setFormatter(formatter)

logger.addHandler(ch)
# logger.addHandler(fh)
