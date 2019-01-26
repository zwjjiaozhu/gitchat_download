

# gitchat_download利器
gitchat文章下载器，支持下载pdf格式以及markdown格式。

其中支持免费的课程下载，付费的课程需要自己购买后，在软件添加cookie后才可以下载

#### 软件架构
- python爬虫技术
- wxpython GUI开发界面
- aria2 开源下载利器


##### 1.1添加cookie

请在使用本软件之前，请先添加自己gitchat账户的cookie信息，如过不添加的话，一些免费的课程也下载不了，只可以下载那些试读的课程。

###### 1.1.1添加cookie

到浏览器使用微信登录自己的gitchat账户，然后打开谷歌浏览器的控制台（其他用谷歌内核的浏览器的也是一样的方法：qq、360、百度浏览器），操作看下方的图片：

![02.png](https://upload-images.jianshu.io/upload_images/8828874-64c1590e76088065.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

只需要复制cookie中custumerId以及custumerToken的值，然后到软件中添加cookie

![![02.png](https://upload-images.jianshu.io/upload_images/8828874-f7977cd83e898944.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
](https://upload-images.jianshu.io/upload_images/8828874-22e7203265b284e5.gif?imageMogr2/auto-orient/strip)


##### 1.1.2课程下载


课程链接是课程主页的链接：

以一个免费的课程为例：
![03.png](https://upload-images.jianshu.io/upload_images/8828874-340200a574419a5e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

点击进去主页然后复制链接https://gitbook.cn/gitchat/column/59f7e38160c9361563ebea95

![04.png](https://upload-images.jianshu.io/upload_images/8828874-e7cb71f74dcd2ffd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

一定要注意，如果链接错了的话，课程是下载不了的。而且自己要提前手动的点击学习课程以及购买课程，才可以下载成功。

#####1.2下载课程

复制好课程主页链接，然后开始下载。

![download.gif](https://upload-images.jianshu.io/upload_images/8828874-d8e4f7047677e814.gif?imageMogr2/auto-orient/strip)
下载后的内容和原格式相差不多。

pdf格式：
![05.png](https://upload-images.jianshu.io/upload_images/8828874-c22f3cdf0404a1e9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

markdown格式：
![06.png](https://upload-images.jianshu.io/upload_images/8828874-a49e2cd57f7974ed.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

#### 2.0软件下载

地址：![软件下载](https://github.com/jz46/gitchat_download/tree/master/setup)


> 总结：

还是有很多要优化的地方，欢迎提交bug和意见...


