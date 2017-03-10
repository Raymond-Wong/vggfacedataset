# vggfacedataset
多线程下载vgg face dataset的脚本

# Environment
win10/ubuntu14.04 + python2.7

# Usage
```
$ python Downloader.py -i /path/to/input -o /path/to/output -t threads_amount
```

# Args
`-i`:必选，输入文件夹路径，文件夹中包含多个由人名命名的txt，txt中每一行就是这个人物的一张相片

`-o`:必选，输出文件夹路径，会根据输入文件夹中的人名自动创建对应的输出文件夹

`-t`:可选，默认为单线程。线程数大于0且不大于16

# Examples
1.准备输入目录，项目文件中有一个in目录作为参考。该目录下有四个txt文件，分别为四个人的图片信息

![](http://i.imgur.com/2V8wDNF.png)

2.准备输出目录，项目文件中有一个空的out目录作为参考

![](http://i.imgur.com/8EYFVHw.png)

3.执行`$ python Downloader.py -i ./in -o ./out -t 4`

![](http://i.imgur.com/m9N9usz.png)

4.查看输出

![](http://i.imgur.com/9GJXry4.png)
![](http://i.imgur.com/0IUxUo9.png)

# Hint
+ 该脚本只负责图片下载，并不保证每张下载下来的图都是完好的。但是如果是完全access不到的图片，会写入到`./failed.log`日志中
+ `./parseFailed.py`脚本可用于检查输入文件中有哪些图片没有在输出文件中出现，