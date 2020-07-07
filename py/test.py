# import wx
# from subprocess import Popen
import os
from bs4 import BeautifulSoup
import html2text  # html转markdown格式的库
from lxml import etree
import requests
# import webbrowser
import json
import time
# import wx.html
import re
import pdfkit
from multiprocessing import Pool

headers = {
    # 'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'Connection': 'keep-alive'
}
cookies = dict(customerToken='f782f8a0-6e43-11e8-9722-a7ceb2ddb814', customerId='5b1fc99a26021e4b80b09317')


class BuyChat:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        # pass
        # self.auto_down()
        # self.auto_buy()

    def auto_buy(self):
        req = requests.session()
        album_pages = 'https://gitbook.cn/gitchat/columns?page=%s&searchKey=&tag='
        for page in range(1, 5):
            album_url = album_pages % str(page)
            album_json = json.loads(req.get(album_url, cookies=cookies).text)
            for course in album_json['columnList']:
                is_updating = course['isUpdating']  # 是否更新中
                is_preSale = course['preSale']  # 是否预售
                course_id = course['_id']
                course_url = 'https://gitbook.cn/gitchat/column/%s' % course_id

                # """
                auto_buy_url = 'https://gitbook.cn/m/mazi/vip/order/column'
                # https://gitbook.cn/gitchat/column/5c0e149eedba1b683458fd5f
                course_id = course['_id']
                course_url = 'https://gitbook.cn/gitchat/column/%s' % course_id
                data = {
                    'columnId': course_id,
                    'requestUrl': 'https://gitbook.cn/gitchat/column/%s' % course_id,
                }
                buy_post = requests.post(auto_buy_url, data=data, cookies=cookies)  # 发送购买请求！！！
                print('id为%s的课程购买成功！！！' % course_id)
                time.sleep(1)

                # """

                print('开始进行一个课程的解析下载！！！')
                self.down_course(course_url, is_updating, is_preSale)

    def auto_buy_column(self, column_url):
        course_id = column_url.split('/')[-1]
        # """
        auto_buy_url = 'https://gitbook.cn/m/mazi/vip/order/column'
        data = {
            'columnId': course_id,
            'requestUrl': column_url,
        }
        buy_post = requests.post(auto_buy_url, data=data, cookies=cookies)  # 发送购买请求！！！
        print('id为%s的课程购买成功！！！' % course_id)
        time.sleep(1)

        print('开始进行一个课程的解析下载！！！')

    def auto_down(self, album_dict):
        """手动下载模式"""
        album_dict2 = {
            # '001JVM 核心技术 22 讲 ': 'https://gitbook.cn/gitchat/column/5de76cc38d374b7721a15cec',
            # '002自然语言处理面试基础': 'https://gitbook.cn/gitchat/column/5e031b6a6b195b5f92fdee0d',
            # '003张亮的运营思维课': 'https://gitbook.cn/gitchat/column/5dd7549779b8c11c31360b55',
            # '004机器学习中的数学：概率统计': 'https://gitbook.cn/gitchat/column/5d9efd3feb954a204f3ab13d',
            # '微积分': 'https://gitbook.cn/gitchat/column/5ddcf0b079b8c11c31370e76',
            # '机器学习中的数学：线性代数': 'https://gitbook.cn/gitchat/column/5daeb1e3669f843a1a4af134',
            # '深入浅出学 Netty': 'https://gitbook.cn/gitchat/column/5daeb1e3669f843a1a4af134',
            'Redis 核心原理与实战': 'https://gitbook.cn/gitchat/column/5e44e9deec8d9033cf94123c',
            # '深入浅出学 Netty': '',
        }
        for course in album_dict:
            course_url = album_dict[course]
            self.auto_buy_column(course_url)
            is_updating = True
            is_preSale = False
            self.down_course(course_url, is_updating, is_preSale)

    def down_course(self, course_url, is_updating, is_preSale):
        dir_path = self.dir_path
        is_choice = 2
        print('is_preSale:%s' % is_preSale)
        if not is_preSale:
            DownCourse(course_url, dir_path, is_choice, is_updating, is_preSale)
        else:
            print('预售课程下载不了！！')


class DownCourse:
    def __init__(self, login_url, dir_path, is_choice, is_updating, is_preSale):
        # 线程实例化时立即启动
        # self.thread = thread
        self.login_url = login_url
        self.dir_path = dir_path
        self.is_choice = is_choice

        self.is_updating = is_updating
        self.is_preSale = is_preSale
        self.cookies = cookies
        # Thread.__init__(self)
        # self.start()
        # print(login_url, dir_path)
        self.run()

    def run(self):
        r = requests.get(self.login_url, cookies=self.cookies, headers=headers).content
        content = etree.HTML(r)
        article_list = content.xpath('//div[ @class="column_categorys"]/a/@onclick')
        chapter_name_list = content.xpath('//div[@class="column_categorys"]/a/div[2]/div/h2/text()')
        if not article_list:  # 恶心的是，有的时候链接是在div下的，一般是a标签下例如：https://gitbook.cn/gitchat/column/5b6d05446b66e3442a2bfa7b
            article_list = content.xpath('//div[@class="column_categorys"]/div/@onclick')
        if not chapter_name_list:  # 恶心的是，有的时候链接是在div下的，一般是a标签下例如：https://gitbook.cn/gitchat/column/5b6d05446b66e3442a2bfa7b
            chapter_name_list = content.xpath('//div[@class="column_categorys"]/div/div[2]/div/h2/text()')

        self.chapter_title = content.xpath('//div[@class="column_infos"]/div/h1/text()')[0]
        # self.chapter_title = content.xpath('//div[@class="catalog_items_head"]/a/text()')[0]
        self.chapter_title = self.format_name(self.chapter_title)
        print('is_updating: %s' % self.is_updating)
        if self.is_updating:
            mid_name = '更新'
        elif not self.is_updating:
            mid_name = '完结'
        else:
            mid_name = '其他'
        self.dir_path = self.dir_path + '/' + mid_name + '/'
        self.dir_path_title = self.dir_path + self.chapter_title  # 生成课程的根目录

        if not os.path.exists(self.dir_path_title):
            os.makedirs(self.dir_path_title)
        index = 1
        print("总共章节数：%s" % len(article_list))
        for u in article_list:
            url_info = re.findall(
                r"clickOnTopic\(\'(?P<blog>.+)\',\'(?P<directory>.+)\',\'(?P<is_free>.+)\',\'(?P<is_done>.+)\'\)", u)[0]
            a_url = 'https://gitbook.cn/gitchat/column/' + url_info[1] + '/topic/' + url_info[0]
            print(a_url)
            # wx.CallAfter(pub.sendMessage, "update", message=a_url + '\n')
            is_free = url_info[2]
            is_done = url_info[3]
            print('is_done:%s' % is_done)
            if is_done == 'false':
                is_done = False
            else:
                is_done = True
            if is_done:
                self.get_md(a_url, index)
                # if self.is_choice == 0:       # 说明下载pdf
                #     self.get_pdf(a_url, index)
                # elif self.is_choice == 1:        # 说明下载md
                #     self.get_md(a_url, index)
                # elif self.is_choice == 2:             # 说明同时下载md和pdf
                #     self.get_pdf(a_url, index)
                #     # wx.CallAfter(pub.sendMessage, "update", message='开始下载markdown格式...' + '\n')
                #     self.get_md(a_url, index)
                # else:
                #     print('>>>已存在 %s' % (self.dir_path + self.chapter_title))
            else:
                is_done_message = '*** %s ***文章正在写作中...'
                print(is_done_message)
            # wx.CallAfter(pub.sendMessage, "update", message=is_done_message + '\n')
            index += 1
        # else:
        #     print('%s已下载过！！！' % self.chapter_title)
        # wx.CallAfter(pub.sendMessage, "update", message='***下载完毕，如果章节不全的话，请添加cookie以及购买相关课程***')

    def get_md(self, a_url, md_index):
        """获取到博客文章的内容部分的html代码"""
        self.dir_path_md = self.dir_path + self.chapter_title + '/' + 'markdown格式'
        self.dir_path_word = self.dir_path + self.chapter_title + '/' + 'word格式'
        self.dir_path_pdf = self.dir_path + self.chapter_title + '/' + 'pdf格式'
        self.dir_path_sound = self.dir_path + self.chapter_title + '/' + '音频'
        if not os.path.exists(self.dir_path_md):
            os.makedirs(self.dir_path_md)
        # if not os.path.exists(self.dir_path_word):
        #     os.makedirs(self.dir_path_word)
        if not os.path.exists(self.dir_path_pdf):
            os.makedirs(self.dir_path_pdf)
        if not os.path.exists(self.dir_path_sound):
            os.makedirs(self.dir_path_sound)

        r = requests.get(a_url, cookies=self.cookies, headers=headers).text
        # print(r)

        soup = BeautifulSoup(r, 'lxml')
        content = soup.find_all('div', class_='topic_content')
        # content = soup.find_all('article', id='topicContainer')
        sound_url = soup.find_all('audio', id='audio')
        print(sound_url)
        if content:
            content = content[0]
            # print(content)
            html_code = str(content)
            title = self.numbers_sort(md_index) + '--' + self.format_name(str(soup.title.string))  # 格式化文件标题
            # print(title)
            if len(sound_url) >= 1:
                print('开始下载音频。。。')
                try:
                    sound_url = sound_url[0]['src']
                    print(sound_url)
                    sound_data = requests.get(sound_url, cookies=self.cookies, headers=headers).content
                    sound_file_path = os.path.join(self.dir_path_sound, title + '.mp3')
                    if not os.path.exists(sound_file_path):
                        with open(sound_file_path, 'wb') as f:
                            f.write(sound_data)
                except Exception as e:
                    print("此章节没有音频")
            else:
                print('无音频！！！')
            title_message = '*** %s ***markdown格式开始下载' % title
            print(title_message)
            # wx.CallAfter(pub.sendMessage, "update", message=title_message + '\n')
            self.get_pdf(html_code, title)
            self.change_md(html_code, title)

        else:
            print("!!!此章节付费章节，请购买后在下载...' + \n")
            # wx.CallAfter(pub.sendMessage, "update", message='!!!此章节付费章节，请购买后在下载...' + '\n')

    # html = open("article.html").read().encode('utf8')

    def change_md(self, txt, title):
        """html代码转markdown"""
        ht = html2text.HTML2Text()
        htmlpage = txt
        text = html2text.html2text(htmlpage)
        # print(text)
        # print(type(text))
        try:
            if os.path.exists(self.dir_path_md + '/' + title + '.md'):  # 判断文件是否存在
                success_already = '*** %s ***已存在、markdown格式下载完毕' % title
                # wx.CallAfter(pub.sendMessage, "update", message=success_already + '\n')
                print(success_already)
            else:
                md_path = self.dir_path_md + '/' + title
                word_path = self.dir_path_word + '/' + title
                # ip_notice = '<h2>本资源由微信公众号：光明顶一号，分享</h2>'
                ip_notice = '# 更多学习交流欢迎关注微信公众号：光明顶一号'
                ip_notice2 = '## 更多资源下载交流请加微信：Morstrong'
                ip_notice3 = '# 本资源由微信公众号：光明顶一号，分享,一个用技术共享精品付费资源的公众号！'
                with open(self.dir_path_md + '/' + title + '.md', 'w', encoding='utf8') as f:
                    f.write(text + ip_notice)
                    # f.write(ip_notice + '\n' + text + '\n' + ip_notice2 + '\n' + ip_notice3)
                    success_message = '*** %s ***、markdown下载完毕' % title
                    # cmd = 'pandoc %s.md -o %s.docx' % (md_path, word_path)
                    # Popen(cmd)
                    # print('%s转成word成功！！！' % title)
                    print(success_message)
        except Exception as e:
            print(e)
            error_down = '***%s下载出错了' % title
            # wx.CallAfter(pub.sendMessage, "update", message=error_down + '\n')
            print(error_down)

    def get_pdf(self, html_code, title):
        ip_notice = '<h2>更多学习交流欢迎关注微信公众号：光明顶一号<h2>'
        html_code += ip_notice
        options = {
            # 'page-size': 'A4',       # A4(default), Letter（书信大小）, A0，A1,B1，etc（等等）.
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'minimum-font-size': '30',  # 页面字体大小
            'encoding': "UTF-8"  # 设定生成pdf文件为utf-8编码，避免生成pdf中文乱码

        }
        pdf_file_path = os.path.join(self.dir_path_pdf, title + '.pdf')
        if not os.path.exists(pdf_file_path):
            column_css = ['column_style.css', ]
            pdfkit.from_string(html_code, pdf_file_path, options=options, css=column_css)
        pass

    def get_pdf02(self, a_url, pdf_index):
        """下载pdf格式操作"""
        self.dir_path_pdf = self.dir_path + self.chapter_title + '/' + 'pdf格式'
        if not os.path.exists(self.dir_path_pdf):
            os.makedirs(self.dir_path_pdf)
        r = requests.get(a_url, cookies=self.cookies, headers=headers).content

        content = etree.HTML(r)
        title = content.xpath('/html/head/title/text()')[0]  # 获取章节标题
        title = self.numbers_sort(pdf_index) + '--' + self.format_name(title)
        # print(chapter_title)

        src_content = content.xpath('//div[@class="column_topic_view"]/script/text()')
        # print(src_content)
        if src_content:
            try:
                href = re.findall('href = \'(.+)\'', src_content[0])[0]  # 解析到pdf的下载路径url
                print(href)
                if os.path.exists(self.dir_path_pdf + '/' + title + '.pdf'):  # 判断文件是否存在
                    success_already = '*** %s ***PDF格式、已存在、下载完毕' % title
                    # wx.CallAfter(pub.sendMessage, "update", message=success_already + '\n')
                    print(success_already)
                else:
                    pdf_content = requests.get(href, cookies=self.cookies,
                                               headers=headers).content  # request 文件pdf的data
                    with open(self.dir_path_pdf + '/' + title + '.pdf', 'wb') as f:
                        f.write(pdf_content)
                    success_message = '*** %s ***PDF格式、下载完毕' % title
                    print(success_message)
            except Exception as e:
                print('pdf下载出错原因%s' % e)
                # wx.CallAfter(pub.sendMessage, "update", message=success_message + '\n')
        else:
            error_down = '***%s ***不支持PDF下载或者下载出错了或者购买后在下载！' % title
            print(error_down)
            # wx.CallAfter(pub.sendMessage, "update", message=error_down + '\n')

    def format_name(self, file_name):
        file_name = file_name.replace(' ', '').replace('|', '-'). \
            replace('：', '').replace(':', '-').replace('/', '').replace('"', ''). \
            replace('=', '').replace('?', '').replace('>', '').replace('<', '').replace('/', '').replace('*',
                                                                                                         '').strip()
        return file_name

    def numbers_sort(self, num):
        if num:
            num = int(num)
            if num < 10:
                num = '00' + str(num)
            elif num < 100:
                num = '0' + str(num)
            # elif num < 1000:
            #     num = '0' + str(num)
            else:
                num = str(num)
            # print(num)
        else:
            num = '0'
        return num


if __name__ == '__main__':
    # dict = {'': ''}
    pool = Pool(processes=4)
    update_column = {
        # 'Netty + JavaFx 实战：仿桌面版微信聊天': 'https://gitbook.cn/gitchat/column/5e5d29ac3fbd2d3f5d05e05f',
        'Dart 入门实践': 'https://gitbook.cn/gitchat/column/5e8eddebf33069503095f54a',
        '全栈工程师实战：从 0 开发云笔记': 'https://gitbook.cn/gitchat/column/5e7d59299bbb1d452bee7a34',
        '重学 Go 语言：进阶篇': 'https://gitbook.cn/gitchat/column/5e7077b2ff3c455d2445827e',
        # '工程师实战方法论核心 12 讲': 'https://gitbook.cn/gitchat/column/5e61b62ed0cbbb4557e7c257',
        # 'Redis 核心原理与实战': 'https://gitbook.cn/gitchat/column/5e44e9deec8d9033cf94123c',
        # 'ElasticSearch 大数据搜索查询分析全指南（）': 'https://gitbook.cn/gitchat/column/5e8553f36a28093c950e1614',
        'Spring Cloud 微服务开发实战': 'https://gitbook.cn/gitchat/column/5eb0d962d57c4106ecc28597',
        '尚老师产品思维 21 讲': 'https://gitbook.cn/gitchat/column/5dde0ec5d78e8e39ca0d4792',
        '互联网分布式系统开发实战（上）': 'https://gitbook.cn/gitchat/column/5ec226afce272616c7bad1d4',
        # '重学 Go 语言：基础篇（完结）': 'https://gitbook.cn/gitchat/column/5dca675eb104917ad887b388',
        # 'Redis 核心原理与实战': 'https://gitbook.cn/gitchat/column/5e44e9deec8d9033cf94123c',
    }
    complete_column = {
        # 'SSM 搭建精美实用的管理系统': 'https://gitbook.cn/gitchat/column/5b4dae389bcda53d07056bc9',
        # 'JVM 核心技术 32 讲(完结)': 'https://gitbook.cn/gitchat/column/5de76cc38d374b7721a15cec',
        # '深入浅出学 Netty（完结）': 'https://gitbook.cn/gitchat/column/5daeb1e3669f843a1a4af134',
        # '张亮的运营思维课（完结）': 'https://gitbook.cn/gitchat/column/5dd7549779b8c11c31360b55',
        # '机器学习中的数学：概率图与随机过程(完结)': 'https://gitbook.cn/gitchat/column/5d9efd3feb954a204f3ab13d',
        # '机器学习中的数学：线性代数': 'https://gitbook.cn/gitchat/column/5dc3d651e740be5a007389fd',
        # '机器学习中的数学：微积分与最优化': 'https://gitbook.cn/gitchat/column/5ddcf0b079b8c11c31370e76',
        # '机器学习中的数学：概率图与随机过程': 'https://gitbook.cn/gitchat/column/5e7d59299bbb1d452bee7a34',
        # '程序员的 MySQL 面试金典': 'https://gitbook.cn/gitchat/column/5d80aea449b2b1063b52990f',
        # '': '',
    }
    dir_path = r'F:\03gitchat(同步更新)\01达人课\更新'
    # dir_path = r'F:\03gitchat(同步更新)\01达人课\更新\完结-更'
    # update_column = complete_column

    chat = BuyChat(dir_path)  # 启动下载！！
    for course in update_column:
        course_url = update_column[course]
        chat.auto_buy_column(course_url)
        is_updating = True
        is_preSale = False
        # pool.apply_async(chat.down_course, args=(course_url, is_updating, is_preSale))
        chat.down_course(course_url, is_updating, is_preSale)

    pool.close()
    pool.join()