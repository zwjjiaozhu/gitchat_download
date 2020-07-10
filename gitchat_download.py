import wx
import os
import subprocess
from threading import Thread
# import wx.lib.pubsub.pub
from wx.lib.pubsub import pub
from bs4 import BeautifulSoup
import html2text
from lxml import etree
import requests
import webbrowser
import json
import wx.html
import re
import pdfkit
import sys
# import win32api
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'Connection': 'keep-alive'
}


class ChatDown:    # 专栏下载类 入口
    def __init__(self, column_url, dir_path, is_choice):
        # 线程实例化时立即启动
        # self.thread = thread
        self.column_url = column_url  # 专栏主页url链接
        self.column_title = ''   # 专栏名称
        self.root_file_path = dir_path    # 存放资源的根目录
        self.column_file_path = ''   # 专栏存放路径
        self.markdown_dir_path = ''  # 专栏markdown格式路径
        self.pdf_dir_path = ''  # 专栏pdf格式路径

        self.is_choice = is_choice    # 专栏下载格式
        self.cookies = ''
        self.run()

    def down_log(self, mes: str):
        """   下载日志，用于给 ui 界面发送下载的实时信息，此函数可避免代码冗余以及后期易维护
        :param mes: 发给ui界面的下载更新信息
        :return:
        """
        print(mes)
        wx.CallAfter(pub.sendMessage, "update", message=mes + '\n')
        return ''

    def run(self):
        # match_path = re.findall(r'\$', self.dir_path)
        # if not match_path:           # 判断是输入的文件存放路径的末尾是否加反斜杠
        #     self.dir_path = self.root_file_path + '/'

        if os.path.exists('static/cookie.json'):
            with open('static/cookie.json', 'r') as f:      # 读取配置的cookie文件
                self.cookies = json.load(f)
        else:
            self.down_log('error:cookie.json文件不存在！')

        # 2.获取专栏的主页目录数据list

        r = requests.get(self.column_url, cookies=self.cookies, headers=headers).content
        content = etree.HTML(r)
        article_list = content.xpath('//div[ @class="column_categorys"]/a/@onclick')
        chapter_name_list = content.xpath('//div[@class="column_categorys"]/a/div[2]/div/h2/text()')
        if not article_list:  # 有的时候链接是在div下的，一般是a标签下例如：https://gitbook.cn/gitchat/column/5b6d05446b66e3442a2bfa7b
            article_list = content.xpath('//div[@class="column_categorys"]/div/@onclick')
        if not chapter_name_list:
            chapter_name_list = content.xpath('//div[@class="column_categorys"]/div/div[2]/div/h2/text()')

        self.column_title = self.format_name(content.xpath('//div[@class="column_infos"]/div/h1/text()')[0])  # 获取课程名称
        self.column_file_path = os.path.join(self.root_file_path, self.column_title)  # 生成课程的根目录
        self.down_log(f"专栏存放路径：{self.column_file_path}")
        if not os.path.exists(self.column_file_path):
            os.makedirs(self.column_file_path)

        # 3、遍历专栏所有的章节，进行章节数据的提取

        resource_index = 0   # 目录页章节排列索引序号
        for u in article_list:
            resource_index += 1
            url_info = re.findall(
                r"clickOnTopic\(\'(?P<blog>.+)\',\'(?P<directory>.+)\',\'(?P<is_free>.+)\',\'(?P<is_done>.+)\'\)", u)[0]
            # 上面是使用正则匹配出该章节的配置信息，例如：是否免费、是否完结、 然后拼接出该章节的目标网页url
            chapter_url = 'https://gitbook.cn/gitchat/column/' + url_info[1] + '/topic/' + url_info[0]
            # self.down_log(chapter_url)

            # 3.1 开始进行下载
            is_free = url_info[2]
            is_done = url_info[3]
            if is_done:
                if self.is_choice == 0:       # 说明下载pdf
                    self.get_md(chapter_url, resource_index, 'pdf')
                elif self.is_choice == 1:        # 说明下载md
                    self.get_md(chapter_url, resource_index, 'md')
                elif self.is_choice == 2:             # 说明同时下载md和pdf
                    self.get_md(chapter_url, resource_index, 'pdf_md')
            else:
                self.down_log(f'该章节正在写作中:{chapter_url}')
        self.down_log('***下载完毕，如果章节不全的话，请添加cookie以及购买相关课程***')

    def get_md(self, chapter_url: str, chapter_index: int, down_style: str):
        """   获取到章节的正文部分的html代码
        :param down_style:
        :param chapter_url:
        :param chapter_index:
        :return:
        """
        self.markdown_dir_path = os.path.join(self.column_file_path, 'markdown')  # 存放markdown文件的文件夹路径
        if not os.path.exists(self.markdown_dir_path):
            os.makedirs(self.markdown_dir_path)

        # 1、爬取章节正文html代码
        chapter_content = requests.get(chapter_url, cookies=self.cookies, headers=headers).text
        soup = BeautifulSoup(chapter_content, 'lxml')
        content = soup.find_all('div', class_='topic_content')   # 获取到章节中写作内容
        if content:
            html_code = str(content[0])
            title = self.numbers_sort(chapter_index) + '--' + self.format_name(str(soup.title.string))       # 格式化文件标题
            if down_style == 'pdf':
                self.get_pdf(html_code, title)
            elif down_style == 'md':
                self.html_to_md(html_code, title)
            else:
                self.get_pdf(html_code, title)
                self.html_to_md(html_code, title)

        else:
            self.down_log('!!!此章节未购买，或者是解析出现错误！')

    def html_to_md(self, html_code: str, title: str):
        """  html内容转markdown格式  python库：html2text
        :param html_code:  文章的html字符串内容
        :param title:  章节名称
        :return:
        """

        # 首先判断本地是否已存在
        md_path = os.path.join(self.markdown_dir_path, title + '.md')
        try:
            if os.path.exists(md_path):       # 判断文件是否存在
                self.down_log(f'{title}:markdown格式已存在!')
            else:
                text = html2text.html2text(html_code)
                with open(md_path, 'w', encoding='utf8') as f:
                    f.write(text)
                    self.down_log(f'{title}：markdown格式下载完毕')
        except Exception as e:
            self.down_log(f'{title}:下载出错了，错误为：{e}')

    def get_pdf(self, html_code, title):
        """  html转pdf  生成pdf，这里使用的库是 pdfkit 基于本地 wkhtmltopdf 程序
        :param html_code:
        :param title:
        :return:
        """

        self.pdf_dir_path = os.path.join(self.column_file_path, 'pdf')  # 存放markdown文件的文件夹路径
        if not os.path.exists(self.pdf_dir_path):
            os.makedirs(self.pdf_dir_path)

        options = {
            # 'page-size': 'A4',       # A4(default), Letter（书信大小）, A0，A1,B1，etc（等等）.
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'minimum-font-size': '30',   # 页面字体大小
            'encoding': "UTF-8"  # 设置为utf-8编码，避免生成pdf中文乱码

        }
        options_str = ''
        for each in options:
            options_str += f"--{each} {options[each]} "
        pdf_file_path = os.path.join(self.pdf_dir_path, title + '.pdf')
        try:
            if not os.path.exists(pdf_file_path):
                column_style_file_path = os.path.join(os.getcwd(), 'static', 'column_style.css')
                column_css = [column_style_file_path, ]
                html_code += '博客：http://zwjjiaozhu.top'  # 可以添加自己的ip

                # pdfkit在mac下有点问题，打包后的软件总是提示找不到wxhtmltopdf的程序，然后直接pycharm运行就没问题！
                wkthmltopdf_file_path = os.path.join(os.getcwd(), 'static', 'wkhtmltopdf')
                # if sys.platform == 'win32':
                #     wkthmltopdf_file_path = subprocess.Popen(
                #         ['where', 'wkhtmltopdf'], stdout=subprocess.PIPE).communicate()[0].strip()
                # else:
                #     wkthmltopdf_file_path = subprocess.Popen(
                #         ['which', 'wkhtmltopdf'], stdout=subprocess.PIPE).communicate()[0].strip()
                # self.down_log(wkthmltopdf_file_path)
                if not wkthmltopdf_file_path:
                    self.down_log(f"{title}: 转换pdf失败，原因：未检测到wkhtmltopdf程序，"
                                  f"请到以下网址进行下载安装：https://wkhtmltopdf.org/downloads.html")
                    return ''
                config = pdfkit.configuration(wkhtmltopdf=wkthmltopdf_file_path)
                pdfkit.from_string(html_code, pdf_file_path, options=options, css=column_css, configuration=config)
                self.down_log(f'{title}：pdf格式下载完毕')
            else:
                self.down_log(f'{title}：pdf格式已存在')
        except Exception as e:
            self.down_log(str(e))

    def get_original_pdf(self, a_url):
        """  获取专栏中自带的官方pdf文件（旧版），目前gitchat已不在支持pdf观看了！
        :param a_url:
        :return:
        """

        self.pdf_dir_path = os.path.join(self.column_file_path, 'pdf')  # 存放markdown文件的文件夹路径
        if not os.path.exists(self.pdf_dir_path):
            os.makedirs(self.pdf_dir_path)

        r = requests.get(a_url, cookies=self.cookies, headers=headers).content
        content = etree.HTML(r)
        title = content.xpath('/html/head/title/text()')[0]        # 获取章节标题
        title = title.replace(' ', '').replace('|', '-')
        # print(chapter_title)

        src_content = content.xpath('//div[@class="column_topic_view"]/script/text()')
        if src_content:
            href = re.findall('href = \'(.+)\'', src_content[0])[0]               # 解析到pdf的下载路径url
            if os.path.exists(self.pdf_dir_path + '/' + title + '.pdf'):     # 判断文件是否存在
                success_already = '*** %s ***PDF格式、已存在、下载完毕' % title
                wx.CallAfter(pub.sendMessage, "update", message=success_already + '\n')
            else:
                pdf_content = requests.get(href, cookies=self.cookies, headers=headers).content  # request 文件pdf的data
                with open(self.pdf_dir_path + '/' + title + '.pdf', 'wb') as f:
                    f.write(pdf_content)
                success_message = '*** %s ***PDF格式、下载完毕' % title
                wx.CallAfter(pub.sendMessage, "update", message=success_message + '\n')
        else:
            error_down = '***%s ***不支持PDF下载或者下载出错了或者购买后在下载！' % title
            wx.CallAfter(pub.sendMessage, "update", message=error_down + '\n')

    def format_name(self, file_name):
        file_name = re.sub('[\/:*?"<>|]', '-', file_name)
        return file_name

    def numbers_sort(self, num):
        if num:
            num = int(num)
            if num < 10:
                num = '00' + str(num)
            elif num < 100:
                num = '0' + str(num)
            else:
                num = str(num)
        else:
            num = '0'
        return num


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.SetBackgroundColour('white')
        # self.SetBackgroundStyle()
        self.icon = wx.Icon(name="./static/logo.ico", type=wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        # 创建窗口栏
        # self.statusbar = self.CreateStatusBar()  # 创建位于窗口的底部的状态栏

        # 设置菜单
        filemenu = wx.Menu()

        # wx.ID_ABOUT和wx.ID_EXIT是wxWidgets提供的标准ID
        menuAbout = filemenu.Append(-1, "&关于软件",
                                    " Information about this program")  # (ID, 项目名称, 状态栏信息)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(-1, "E&xit",
                                   " Terminate the program")  # (ID, 项目名称, 状态栏信息)
        self.Bind(wx.EVT_MENU, self.exit, menuExit)

        study_menu = wx.Menu()            # 创建软件使用教程的菜单栏
        study_use = study_menu.Append(wx.ID_NEW, '软件使用教程', 'use study')
        self.Bind(wx.EVT_MENU, self.study_use, study_use)
        study_menu.AppendSeparator()
        add_cookie = study_menu.Append(-1, '添加cookie', 'add cookie')
        self.Bind(wx.EVT_MENU, self.edit_cookie, add_cookie)
        # 创建顶部菜单栏
        menuBar = wx.MenuBar()
        menuBar.Append(study_menu, "&使用攻略")  # 在菜单栏中添加filemenu菜单
        menuBar.Append(filemenu, "&关于")  # 在菜单栏中添加filemenu菜单
        self.SetMenuBar(menuBar)  # 在frame中添加菜单栏
        # 设置events
        # 创建一些Sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=5, vgap=5)    # 行和列的间距是5像素
        hSizer = wx.BoxSizer(wx.VERTICAL)

        self.url = wx.StaticText(self, label='课程链接：', pos=(20, 30))
        # self.Bind(wx.EVT_MOTION, self.show_status, self.url)
        self.url_blog = wx.TextCtrl(self, pos=(100, 20), size=(420, -1))  # style=wx.TE_RICH
        # self.url_blog.SetDefaultStyle(wx.TextAttr(wx.RED))
        # grid.Add((10, 40), pos=(-1, 0))
        grid.Add(self.url, pos=(1, 0))    # 加入GridBagSizer
        grid.Add(self.url_blog, pos=(1, 1))    # 加入GridBagSizer
        self.clear_button = wx.Button(self, -1, "清除")
        grid.Add(self.clear_button, pos=(1, 2))
        self.Bind(wx.EVT_BUTTON, self.clear_url)
        # self.Bind(wx.EVT_ENTER_WINDOW, self.show_status, self.clear_button)

        # 向GridBagSizer中填充空白的空间
        # grid.Add((10, 40), pos=(2, 0))

        # self.button = wx.Button(self, label='Save', pos=(200, 325))
        # self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)

        self.lblname = wx.StaticText(self, label='下载路径：', pos=(20, 20))
        grid.Add(self.lblname, pos=(3, 0))
        self.dir_path = wx.TextCtrl(self, pos=(10, 10), size=(420, -1), )
        grid.Add(self.dir_path, pos=(3, 1))
        self.liulan_button = wx.Button(self, -1, "浏览")
        grid.Add(self.liulan_button, pos=(3, 2))
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.liulan_button)

        grid.Add((10, 20), pos=(4, 0))

        # 选择下载的格式
        self.name_md = wx.StaticText(self, label='下载格式:', pos=(20, 20))
        grid.Add(self.name_md, pos=(5, 0))
        self.is_md_list = ['pdf', 'markdown', 'pdf和markdown']
        self.is_md = wx.ComboBox(self, value='请选择下载格式', pos=wx.DefaultPosition, size=(120, 35), choices=self.is_md_list,
                                 style=wx.CB_DROPDOWN)
        grid.Add(self.is_md, pos=(5, 1))

        # # 向GridBagSizer中填充空白的空间
        grid.Add((10, 20), pos=(6, 0))

        self.download = wx.Button(self, label='download', pos=(10, 15))        # 总的下载按钮
        self.Bind(wx.EVT_BUTTON, self.down, self.download)

        self.d_info = wx.StaticText(self, label='下载输出信息：', pos=(10, 10))
        font = wx.Font(12,  wx.ROMAN, wx.NORMAL, wx.FONTWEIGHT_BOLD)          # 设置字体大小
        self.d_info.SetFont(font)
        self.d_info.SetForegroundColour('red')           # 设置StaticText部件的文本颜色
        self.logger = wx.TextCtrl(self, pos=(100, 20), size=(600, 300), style=wx.TE_MULTILINE | wx.TE_READONLY,
                                  value='下载输出日志\n'
                                  )

        hSizer.Add(grid, 0, wx.ALL, 5)
        # hSizer.Add(self.download)
        mainSizer.Add(hSizer, 0, wx.ALL, 5)
        mainSizer.Add(self.download, 0, wx.CENTER)
        # mainSizer.Add(self.is_md, 0, wx.Left)
        mainSizer.Add((20, 20))                # 添加上下空白间隔
        mainSizer.Add(self.d_info, 0, wx.Left)
        mainSizer.Add((20, 5))  # 添加上下空白间隔
        mainSizer.Add(self.logger, 0, wx.CENTER)
        # 可以把SetSizer()和sizer.Fit()合并成一条SetSizerAndFit()语句
        self.SetSizerAndFit(mainSizer)
        pub.subscribe(self.down_message, "update")  # 获取到子线程中发来的数据
        self.Show(True)

    def OnAbout(self, e):
        """关于软件"""

        """
        wxpython自带关于我模块
        # 创建一个带"OK"按钮的对话框。wx.OK是wxWidgets提供的标准ID
        dlg = wx.MessageDialog(self, "开发者：西园公子\n一个数据分析&图像处理&爬虫钟爱者...",
                               "关于开发者...", wx.OK)  # 语法是(self, 内容, 标题, ID)
        # dlg.WebSite = ("http://www.pythonlibrary.org", "My Home Page")
        dlg.ShowModal()  # 显示对话框
        dlg.Destroy()  # 当结束之后关闭对话框
        """
        AboutDlg(None).Show()

    def OnOpen(self, e):
        """ 打开文件操作 """
        """
        打开文件：wx.FileDialog(self, parent, message, defaultDir, defaultFile,wildcard, style, pos)
        """
        dlg = wx.DirDialog(self, "Choose a file", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            dir_path = dlg.GetPath()
            self.dir_path.SetValue(dir_path)
        dlg.Destroy()

    def clear_url(self, event):
        """清理课程链接"""
        self.url_blog.SetValue('')

    def down(self, event):
        """下载课程"""
        url = self.url_blog.GetValue()        # 获取课程主页链接
        dir_path = self.dir_path.GetValue()    # 获取存放文件的文件夹路径

        is_choice = self.is_md.GetSelection()      # =-1为其他 =0 为pdf下载器，=1位markdown下载器 =2 为两种格式同时下载
        if url and dir_path:             # 判断路径以及博客链接是否为空
            if is_choice == -1:
                alerm = wx.MessageDialog(self, "请选择markdown或者pdf课程格式", u"Error!!!")
                alerm.ShowModal()
            else:
                self.logger.SetValue('')  # 清空下载日志区
                t = Thread(target=ChatDown, args=(url, dir_path, is_choice))
                t.setDaemon(True)
                t.start()
        else:
            self.verify_down()

    def down_message(self, message):
        self.logger.AppendText(message)

    def verify_down(self):
        dlg = wx.MessageDialog(self, "填写信息有误，请检查路径以及博客链接填写是否正确...", u"error!!!", wx.YES_NO | wx.ICON_QUESTION)
        # if dlg.ShowModal() == wx.ID_YES:
        #     self.Close(True)
        dlg.ShowModal()
        dlg.Destroy()

    def exit(self, e):
        is_quit = wx.MessageDialog(None, "要退出gitchat下载吗？", "exit", wx.YES_NO | wx.ICON_QUESTION)
        # is_quit.ShowModal()  # 显示对话框
        if is_quit.ShowModal() == wx.ID_YES:
            self.Close()
        else:
            pass
        is_quit.Destroy()  # 当结束之后关闭对话框

    def study_use(self, e):
        webbrowser.open('https://github.com/jz46/gitchat_download')

    def edit_cookie(self, e):
        """  编辑cookies.json
        :param e:
        :return:
        """
        path = 'static/cookie.json'
        # window用户：就可以在软件直接打开和编辑
        if sys.platform == 'win32':
            import win32api
            win32api.ShellExecute(0, 'open', 'notepad.exe', path, '', 1)
        else:
            pass

        # mac os下


class WxHTML(wx.html.HtmlWindow):
    def OnLinkClicked(self, link):
        webbrowser.open(link.GetHref())


class AboutDlg(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title="关于本软件", size=(400, 400))
        self.icon = wx.Icon(name="./static/logo.ico", type=wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        html = WxHTML(self)

        html.SetPage(
            ''
            "<h3>关于本软件</h3>"
            "<h3>软件版本：6.2.0</h3>"
            "<p><b>开发者：西园公子 </b></p>"
            "<p><b>个人博客：<a href='http://zwjjiaozhu.top' target='_blank'>http://zwjjiaozhu.top</a> 记录点滴技术积累</b></p>"
            '<p>代码开源，欢迎star：<b><a href="https://github.com/jz46/gitchat_download">⭐github⭐</a></b></p>'
            '<p><b>版权声明：软件仅供学习所用，勿做其他，带来的所有问题均与软件无关！</b></p>'
        )


app = wx.App(False)
frame = MainWindow(None, title='Gitchat课程下载By西园公子')
app.MainLoop()
