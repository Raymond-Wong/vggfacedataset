#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-04-21 18:28:13
# @Author  : Raymond Wong (549425036@qq.com)
# @Link    : github/Raymond-Wong

import os
import sys
import copy
import urllib
import threading
import time

from optparse import OptionParser

# 设置5秒超时
import socket
socket.setdefaulttimeout(5.0)

reload(sys)
sys.setdefaultencoding('utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'out')
FILE_DIR = os.path.join(BASE_DIR, 'in')
LOG_DIR = os.path.join(BASE_DIR, 'failed.log')

LOCK = threading.Lock()
FILE_LOCK = threading.Lock()
SIZE_LOCK = threading.Lock()
OUTPUT_LOCK = threading.Lock()
FINISH_LOCK = threading.Lock()

SUCCESS_COUNT = [0]
TOTAL_AMOUNT = 0
THREAD_AMOUNT = 4
COST_TIME = [0]
SUCCESS_FILE_SIZE = [0]
FINISH_THREAD_AMOUNT = [0]
DEBUG = True

# 给出待下载的文件名称，将该名称对应的文件内所有的图片下载到IMG_DIR下该名称对应的目录下
class BatchDownloader(threading.Thread):
  # 初始化时将待下载的文件名称传给downloader
  def __init__(self, nm, fl):
    super(BatchDownloader, self).__init__()
    self.name = nm
    self.fileList = copy.deepcopy(fl)

  # 将url指向的文件下载到path中
  def download(self, path, url):
    try:
      urllib.urlretrieve(url, path, process)
      time.sleep(0.5)
      return True, None
    except Exception, e:
      return False, e

  # 以此读取负责的文件中的每一行，并下载该行对应的图片
  # 如果下载失败，则将失败的url写进日志文件中
  def run(self):
    for fn in self.fileList:
      fp = os.path.join(FILE_DIR, fn + ".txt")
      _file = open(fp, 'r')
      line = _file.readline()
      lineNum = 0
      while line:
        lineNum += 1
        # logger('DEBUG', '%s readling the %dth line' % (self.name, lineNum))
        arr = line.split()
        outPath = os.path.join(os.path.join(IMG_DIR, fn), arr[1] + ".jpg")
        res = [True]
        if not os.path.exists(outPath):
          url = arr[2]
          res = self.download(outPath, url)
        # 如果下载成功，则SUCCESS_COUNT自增1
        if LOCK.acquire():
          SUCCESS_COUNT[0] += 1
          LOCK.release()
        if not res[0]:
          if FILE_LOCK.acquire():
            f = open(LOG_DIR, 'a')
            f.write('%s\t%s\t%s\t%s\n' % (fn, arr[1], url, res[1]))
            f.close()
            FILE_LOCK.release()
        line = _file.readline()
      _file.close()
    # logger('DEBUG', self.name + u' 完成')
    if FINISH_LOCK.acquire():
      FINISH_THREAD_AMOUNT[0] += 1
      FINISH_LOCK.release()

def logger(tp, msg):
  if OUTPUT_LOCK.acquire():
    if not DEBUG and tp.upper() == 'DEBUG':
      return
    print u'[%s]\t%s' % (tp, msg)
    OUTPUT_LOCK.release()

# 用于显示已下载文件的平均速度
def downloadSpeed():
  unit = 'B/s'
  speed = float(SUCCESS_FILE_SIZE[0]) / COST_TIME[0]
  if speed < 1024:
    return str(speed) + " " + unit
  speed /= 1024
  unit = "KB/s"
  if speed < 1024:
    return '%.2f %s' % (speed, unit)
  speed /= 1024
  unit = "MB/s"
  return '%.2f %s' % (speed, unit)

# 显示单个下载过程的进度
def process(a, b, c):
  # per = 100 * a * b / c
  # if per > 100:
  #   per = 100
  # print '%.1f%%' % per
  if SIZE_LOCK.acquire():
    SUCCESS_FILE_SIZE[0] += (a * b)
    SIZE_LOCK.release()

# 显示整个下载进度
def showProcess():
  COST_TIME[0] += 1
  per = '%.2f' % (100 * float(SUCCESS_COUNT[0]) / TOTAL_AMOUNT)
  sys.stdout.write(u'\r[INFO]\t' + str(SUCCESS_COUNT[0]) + '/' + str(TOTAL_AMOUNT) + ' 完成 ' + str(per) + '%, 平均下载速度: ' + downloadSpeed() + ' 已耗时: ' + prettyTime(COST_TIME[0]))
  sys.stdout.flush()
  if FINISH_THREAD_AMOUNT[0] < THREAD_AMOUNT:
    global timer
    timer = threading.Timer(1.0, showProcess)
    timer.setDaemon(True)
    timer.start()
timer = threading.Timer(1.0, showProcess)

# 格式化时间
def prettyTime(second):
  hour = 0
  minute = 0
  if second < 60:
    return str(second) + u"秒"
  minute = int(second / 60)
  second = second % 60
  if minute < 60:
    return str(minute) + u"分钟" + str(second) + u"秒"
  hour = int(minute / 60)
  minute = minute % 60
  return str(hour) + u"小时" + str(minute) + u"分钟" + str(second) + u"秒"

# 获取输入参数
def getParams(args):
  params = ' '.join(args).split('-')
  ret = {}
  for param in params:
    if len(param.strip()) > 0:
      key, val = param.split()
      ret[key] = val
  return ret

if __name__ == "__main__":
  # 从输入参数中获取输入文件的路径以及输出文件的路径
  parser = OptionParser()
  parser.add_option('-i', '--input', action="store", dest='input', help=u"输入文件夹路径，文件夹中为多个以人名命名的txt文件")
  parser.add_option('-o', '--output', action='store', dest="output", help="输出文件夹路径")
  parser.add_option('-t', '--threads', action="store", dest='threads_amount', help=u"使用多少个线程下载，线程数大于0小于等于16", default="1")
  (options, args) = parser.parse_args()
  if options.input is None or options.output is None or not options.threads_amount.isdigit() or int(options.threads_amount) < 1 or int(options.threads_amount) > 16:
    parser.print_help()
    exit(1)
  FILE_DIR = options.input
  IMG_DIR = options.output
  THREAD_AMOUNT = int(options.threads_amount)
  if not os.path.exists(FILE_DIR):
    logger('ERROR', u'输入路径不存在！')
    exit(-1)
  logger('INFO', u'初始化...')
  # 清空日志文件
  open(LOG_DIR, 'w').close()
  # 如果输出路径不存在则创建
  if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)
  logger('INFO', u'输入目录的路径为 %s' % FILE_DIR)
  logger('INFO', u'输出目录的路径为 %s' % IMG_DIR)
  logger('INFO', u'共开启 %d 个线程进行下载' % THREAD_AMOUNT)
  logger('INFO', u'获取输入目录下的所有文件，并在输出目录中创建相应储存结果的目录...')
  fileList = []
  for root, dirs, files in os.walk(FILE_DIR):
    for fileName in files:
      fn = fileName.replace('.txt', '')
      fileList.append(fn)
      if not os.path.exists(os.path.join(IMG_DIR, fn)):
        os.makedirs(os.path.join(IMG_DIR, fn))
  logger('INFO', u'一共获取到 %d 个输入文件' % len(fileList))
  logger('INFO', u'获取等待下载的图片链接..')
  for fn in fileList:
    fp = os.path.join(FILE_DIR, fn + ".txt")
    _file = open(fp, 'r')
    line = _file.readline()
    while line:
      TOTAL_AMOUNT += 1
      line = _file.readline()
  logger('INFO', u'共获取到 %d 个待下载的图片链接' % TOTAL_AMOUNT)
  logger('INFO', u'将文件列表均分成 %d 等分，并申明同样数量的downloader' % THREAD_AMOUNT)
  sys.stdout.write(u'\r[INFO]\t0/' + str(TOTAL_AMOUNT) + ' 完成 0.00%, 平均下载速度为 ---kb/s, 已耗时 0秒')
  sys.stdout.flush()
  pool = []
  diff = len(fileList) / THREAD_AMOUNT
  start = 0
  end = 0
  # 申明downloader
  for i in xrange(0, THREAD_AMOUNT):
    start = end
    end = start + diff
    if end > len(fileList):
      end = len(fileList)
    pool.append(BatchDownloader('downloader %d' % i, fileList[start : end]))
    pool[-1].setDaemon(True)
    pool[-1].start()
  # 开始计时
  global timer
  timer.setDaemon(True)
  timer.start()
  try:
    while FINISH_THREAD_AMOUNT[0] < THREAD_AMOUNT:
      time.sleep(1)
      pass
  except KeyboardInterrupt:
    logger('\nWARN', u'强制退出主线程')
    sys.exit()
  # for downloader in pool:
  #   downloader.join()
  logger('\nINFO', '下载完成')
