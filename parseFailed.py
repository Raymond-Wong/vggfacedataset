#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-05-04 13:48:10
# @Author  : Raymond Wong (549425036@qq.com)
# @Link    : github/Raymond-Wong

import os
import sys

if __name__ == '__main__':
  f = open(sys.argv[1], 'r')
  outDir = sys.argv[2]
  line = f.readline()
  counter = 0
  while line:
    sys.stdout.write('正在处理 %d 行\r' % counter)
    counter += 1
    fn, pid, url, error = line.split('\t')
    outFile = open(os.path.join(outDir, fn + '.txt'), 'a')
    outFile.write('1 %s %s\n' % (pid, url))
    line = f.readline()
