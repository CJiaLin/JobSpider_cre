# -*- coding: utf-8 -*-
__author__ = 'chenjialin'
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import logging.config
from scrapy.http import Request
from ..allitems.jobitems import AllJobs
from src.main.python.service.scrapy.Job.Job.utils.strUtil import StrUtil
from src.main.python.service.scrapy.Job.Job.utils.FileUtil import FileUtil
logging.config.fileConfig(FileUtil().getLogConfigPath())
logger = logging.getLogger("ahu")

class UNIDOjobLink(scrapy.Spider):
    name = "UNIDOjob"
    start_urls = ["http://www.unido.org/employment/consultancy-opportunities.html",
                  "http://www.unido.org/employment/o518900.html",
                  "http://www.unido.org/overview/employment/internship.html",
                  "http://www.unido.org/internship/internships-in-field-offices.html"]

    def __init__(self):
        self.preurl = 'http://www.unido.org'

    def parse(self, response):
        cnt = 0
        selector = scrapy.Selector(response)
        joburls = selector.xpath('//li[@class="active current activeandsub"]/ul/li/a')

        if response.url == 'http://www.unido.org/internship/internships-in-field-offices.html':
            others = selector.xpath('//div[@class="csc-textpic-text"]/div/table/tbody/tr/td/a')
            for other in others[1:]:
                finalurl = other.xpath('@href').extract()[0]
                if finalurl.endswith('.pdf'):
                    url = self.preurl + finalurl
                    yield Request(url, callback=self.duepdf, dont_filter=True)
                else:
                    pass
        else:
            try:
                for joburl in joburls:
                    url = self.preurl + joburl.xpath('@href').extract()[0]
                    cnt += 1
                    logger.debug('正在抓取<---  ' + url)
                    yield Request(url=url, callback=self.wr)
            except:
                pass
            logger.debug("%s" % response.url + '->>共有'+ str(cnt) + '个招聘信息')

    def wr(self,response):
        selector = scrapy.Selector(response)
        deeps = selector.xpath('//li[@class="active current activeandsub"]/ul/li/a')
        if deeps:
            for deep in deeps:
                url = self.preurl + deep.xpath('@href').extract()[0]
                yield Request(url, callback=self.wr)
            return

        if response.url == 'http://www.unido.org/internship/internships-in-field-offices.html':
            return

        item = self._inititem()
        url = response.url
        item['joburl'] = url
        num = 0

        main_content = selector.xpath('//div[@class="csc-default"]/p')
        itemname = ''
        text = ''
        tips = ''
        totle = 0
        for i in main_content:
            totle += 1

        while num < totle:
            target = ''
            content = main_content[num]
            try:
                target = content.xpath('b/text()').extract()[0]
                text = content.xpath('text()').extract()[0]
            except:
                pass
            num += 1
            if target == 'Duration:' or target == 'Duration: ':
                itemname = 'ExpectedDurationofAssignment'
            elif target == 'Duty Station:' or target == 'Duty Station: ':
                itemname = 'Location'
            elif target == 'Tasks:' or target == 'Tasks: ':
                itemname = 'responsibilities'
                num2 = num
                for content in main_content[num2:]:
                    target = content.xpath('b/text()')
                    if not target:
                        num += 1
                        text += content.xpath('text()').extract()[0]
                    else:
                        break
            elif target == 'Qualification requirements:' or target == 'Qualification requirements: ':
                num2 = num
                for content in main_content[num2:]:
                    test = content.xpath('text()').extract()[0]
                    if 'Education' in test:
                        item['education'] = test
                    elif 'Experience' in test:
                        item['experience'] = test
                    elif 'Language' in test:
                        item['language'] = test
                break
            else:
                try:
                    cont = content.xpath('b')
                    tips += cont.xpath('string(.)').extract()[0]
                except:
                    pass
                continue

            item[itemname] = StrUtil.delWhiteSpace(text)
            logger.debug("UNIDO-->job-->%s" % url+'-->'+itemname+'-->'+item[itemname])

        Work = selector.xpath('//div[@id="header-content"]/div/h1/text()').extract()[0]
        item['work'] = StrUtil.delWhiteSpace(Work)
        logger.debug("UNIDO-->job-->%s" % url+'-->Work-->'+item['work'])

        itemname= 'addition'
        item[itemname] = StrUtil.delWhiteSpace(tips)
        logger.debug("UNIDO-->job-->%s" % url + '-->' + itemname + '-->' + item[itemname])
        print item
        yield item

    def duepdf(self, response):
        url = response.url
        items = self._inititem()
        items['joburl'] = url
        if url.endswith('.pdf'):
            PDF_name = url.split('/')[-1]
            items['work'] = StrUtil.delWhiteSpace(PDF_name)
            logger.debug("UNIDO-->job-->%s" % items['work'])
            yield Request(url, meta={'items': items}, callback=self.savepdf, dont_filter=True)
        else:
            items['addition'] = StrUtil.delWhiteSpace(url)
        yield items

    def savepdf(self, response):
        items = response.meta['items']
        with open('./UNIDOPDF/' + items['work'], 'wb') as f:
            f.write(response.body)

    def _inititem(self):
        '''
        初始化全部字段
        :return: 初始字段
        '''
        item = AllJobs()
        item['englishname'] = 'UNIDO'  # 组织英文缩写
        item['chinesename'] = '联合国工业发展组'  # 组织中文缩写
        item['incontinent'] = '欧洲'  # 组织所属洲
        item['incountry'] = '奥地利'  # 组织所在国家
        item['type'] = '经济'  # 组织类别
        item['url'] = 'www.unido.org'  # 组织主页
        item['alljoburl'] = 'http://www.unido.org/employment.html'
        item['description'] = ''
        item['joburl'] = ''
        item['work'] = ''
        item['reference'] = ''
        item['issuedate'] = ''
        item['ApplicationDeadline'] = ''
        item['responsibilities'] = ''
        item['skill'] = ''
        item['PostLevel'] = ''
        item['belong'] = ''
        item['TypeofContract'] = ''
        item['language'] = ''
        item['contracttime'] = ''
        item['ExpectedDurationofAssignment'] = ''
        item['linkman'] = ''
        item['Location'] = ''
        item['full_time'] = ''
        item['treatment'] = ''
        item['education'] = ''
        item['addition'] = ''
        item['experience'] = ''

        '''item['Work'] = ''         #岗位名称
        item['Duration'] = ''     #工作时长
        item['Duty_Station'] = '' #工作地点
        item['Organizational_Context'] = '' #组织背景
        item['Tasks'] = ''        #岗位描述
        item['Requirements'] = '' #资格要求
        item['Tips'] = ''         #相关信息
        item['joburl'] = ''       #招聘页面
        item['link'] = ''         #申请链接'''
        return item


