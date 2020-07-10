

# gitchat下载软件
gitchat文章下载器，支持下载pdf格式以及markdown格式。

其中支持免费的课程下载，付费的课程需要自己购买后，在软件添加cookie后才可以下载——————2020.7.8号更新——————————

旧版是采用window系统进行开发的，由于现在切换到mac下进行开发了，所以下面的教程会以 Mac 下进行操作，其中项目代码中我会注释那些是window 下的，那些是 Mac 下的。

<iframe src="//player.bilibili.com/player.html?aid=668763519&bvid=BV1Xa4y1h7g9&cid=210919160&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

#### 软件组成：

- python
- wxpython GUI开发界面
- aria2 开源下载利器

#### 开发平台：

- os：Mac os 10.15/window10
- python version：python3.8
- wxpython
- IDE：Pycharm 2020



# 1.首先配置

## 1.添加cookie：

请在使用本软件之前，请先添加自己gitchat账户的cookie信息，如过不添加的话，一些免费的课程也下载不了，只可以下载那些试读的课程。

到浏览器打开gitchat的网站，使用微信登录自己的gitchat账户，然后打开谷歌浏览器的控制台（其他用谷歌内核的浏览器的也是一样的方法：qq、360、百度浏览器），操作看下方的图片：

![02.png](https://upload-images.jianshu.io/upload_images/8828874-64c1590e76088065.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

只需要复制cookie中custumerId以及custumerToken的值，然后到软件中添加cookie

![![02.png](https://upload-images.jianshu.io/upload_images/8828874-f7977cd83e898944.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
](https://upload-images.jianshu.io/upload_images/8828874-22e7203265b284e5.gif?imageMogr2/auto-orient/strip)



## 2. 下载组件：

软件需要用到 wkhtmlpdf 程序，用于将html转pdf 

# 2.下载教程



## 1.复制链接


课程链接是课程主页的链接：以一个免费的课程为例：

![03.png](https://upload-images.jianshu.io/upload_images/8828874-340200a574419a5e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

点击进去主页然后复制链接https://gitbook.cn/gitchat/column/59f7e38160c9361563ebea95

![04.png](https://upload-images.jianshu.io/upload_images/8828874-e7cb71f74dcd2ffd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

一定要注意，如果链接错了的话，课程是下载不了的。而且自己要提前手动的点击学习课程以及购买课程，才可以下载成功。



复制好课程主页链接，然后开始下载。

![download.gif](https://upload-images.jianshu.io/upload_images/8828874-d8e4f7047677e814.gif?imageMogr2/auto-orient/strip)
下载后的内容和原格式相差不多。

**pdf格式：**
![05.png](https://upload-images.jianshu.io/upload_images/8828874-c22f3cdf0404a1e9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

markdown格式：
![06.png](https://upload-images.jianshu.io/upload_images/8828874-a49e2cd57f7974ed.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

# 3. 软件下载

地址：[软件下载](https://github.com/zwjjiaozhu/gitchat_download/releases)

# TODO：

- chat文章下载
- 设计更好看的界面（有会UI的可以issue一下）
- 支持添加多个链接同时下载

- 其他

# 使用说明：

> 版权说明：本软件仅供学习所用，勿要拿来做违法事情，后果自负！

