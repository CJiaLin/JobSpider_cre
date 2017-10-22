# -*- coding: utf-8 -*-
__author__ = 'liuyang'
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import re
from scrapy.http import Request
from ..allitems.jobitems import AllJobs
from src.main.python.service.scrapy.Job.Job.utils.strUtil import StrUtil
import logging.config
from src.main.python.service.scrapy.Job.Job.utils.FileUtil import FileUtil

logging.config.fileConfig(FileUtil().getLogConfigPath())
logger = logging.getLogger('ahu')

class UNDPjobSpider(scrapy.Spider):

    name = "UNDPjob"

    start_urls = ["https://jobs.undp.org/cj_view_jobs.cfm"]

    def __init__(self):
    
        self.noidziduan = ['Location :','Application Deadline :','Additional  Category :',
                       'Type of Contract :','Post Level :','Languages Required :','Duration of Initial Contract :',
                       'Expected Duration of Assignment :']

        self.ITE = ['Location','ApplicationDeadline','TypeofContract','PostLevel','LanguagesRequired',
                    'DurationofInitialContract','ExpectedDurationofAssignment','AdditionalCategory']

        self.textnfo_noid = ['Background','Duties and Responsibilities','Competencies','Required Skills and Experience']

        self.id2field = ['Agency', 'Title', 'Job ID', 'Practice Area - Job Family', 'Vacancy End Date', 'Time Left', 
                        'Duty Station', 'Education & Work Experience', 'Languages', 'Grade', 'Vacancy Type', 'Posting Type',
                        'Bureau', 'Contract Duration', 'Background', 'Duties and Responsibilities', 'Competencies', 'Required Skills and Experience', 
                        'Disclaimer']

        self.preurl = "https://jobs.undp.org/"

        # 用来存储第二种页面信息的容器
        self.items = []

    def parse(self, response):
        selector = scrapy.Selector(response)
        logger.debug("开始解析UNDP(联合国开发计划蜀)的连接信息")
        table = selector.xpath('//div[@id="content-main"]/table[@class="table-sortable"]')
        for evertable in table:
            tbody = evertable.xpath('tr')
            for everlink in tbody[:-1]:
                # 提取具体岗位连接
                link = everlink.xpath('td[1]/a/@href').extract()
                if len(link):
                    if link[0].startswith('c'):
                        LINK = self.preurl + link[0]
                    else:
                        LINK = link[0]
                else:
                    continue
                # print LINK

                # 提取岗位描述信息
                describe = everlink.xpath('td[1]/a/text()').extract()
                DESERIBE = describe[0] if len(describe) else ""
                # print DESERIBE

                # 提取所属系统(第二列)
                suoshu = everlink.xpath('td[2]/text()').extract()
                SUOSHU = suoshu[0] if len(suoshu) else ""
                # print SUOSHU

                # 提取岗位名称
                work = everlink.xpath('td[3]/text()').extract()
                WORK = work[0].strip() if len(work) else ""
                # print WORK

                # 提取岗位申请时间
                applytime = everlink.xpath('td[4]/text()').extract()
                APPLYTIME = applytime[1] if len(applytime) else ""
                # print APPLYTIME

                # 提取岗位联系人
                linkman = everlink.xpath('td[5]/text()').extract()
                LINKMAN = linkman[0] if len(linkman) else ""
                # print LINKMAN

                if LINK.endswith('id=2'):
                    logger.debug("开始爬取链接%s"%LINK)
                    yield Request(url=LINK,
                                    callback=self._crawlhaveid,
                                    meta={"describe":DESERIBE,
                                            "suoshu":SUOSHU,
                                            "applytime":APPLYTIME,
                                            "linkman":LINKMAN})

                else:
                    logger.debug("开始爬取链接%s" % LINK)
                    yield Request(url=LINK,
                                    callback=self._UNDPprase,
                                    meta={"describe":DESERIBE,
                                                "suoshu":SUOSHU,
                                                "work":WORK,
                                                "applytime":APPLYTIME,
                                                "linkman":LINKMAN}
                                          )

    def _UNDPprase(self, response):
        '''
       使用scrapy框架解析岗位信息（第一种页面形式）
       '''
        logger.debug('crawl noid!') 
        work_or_PostLevel = response.meta["work"]

        job = scrapy.Selector(response)
        item = self._setitem_noid(response)

        try:
            self._crawlnoid(job,item,work_or_PostLevel)
        except:
            logger.warning("未能爬取到页面%s的相关数据"%response.url)

        yield item

    def _crawlnoid(self,job,item,work_or_PostLevel):

        '''
        对第一种形式页面进行字段解析
        '''
        item["work"] = work_or_PostLevel
        #TODO  提取基本信息
        trs1 = job.xpath('//div[@id="content-main"]/table[1]//tr')
        #trs2 = job.xpath('//div[@id="content-main"]/table[1]/tr')

        try:
            item['work'] = trs1.xpath('td/h3/text()').extract()[0]
            for i in trs1:
                try:
                    tag = i.xpath('td/strong/text()').extract()
                    if tag != []:
                        tag = tag[0]
                    else:
                        continue

                    text = i.xpath('td[2]/text()').extract()
                    if text != []:
                        text = text[0]
                    else:
                        continue

                    if 'Location' in tag:
                        item['Location'] = text
                    elif 'Application Deadline' in tag:
                        item['ApplicationDeadline'] = text
                    #elif 'Additional Category' in tag:
                        #item['type'] = text
                    elif 'Type of Contract' in tag:
                        item['TypeofContract'] = text
                    elif 'Post Level' in tag:
                        item['PostLevel'] = text
                    #elif 'Languages Required' in tag:
                        #item['language'] = text
                    elif 'Duration of Initial Contract' in tag:
                        item['contracttime'] = text
                except:
                    continue
        except:
            pass
        '''for tr in trs2:
            ziduanming = tr.xpath('td[1]/strong/text()').extract()
            if ziduanming:
                if ziduanming[0] in self.noidziduan:
                    context = tr.xpath('td[2]/text()').extract()
                    if context:
                        if StrUtil.delWhite(ziduanming[0].strip(':')) == "LanguagesRequired":
                            item[StrUtil.delWhite(ziduanming[0].strip(':'))] = re.sub('\W',' ',StrUtil.delWhite(context[0]))
                        else:
                            item[StrUtil.delWhite(ziduanming[0].strip(':'))] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(context[0]))
        '''

        # TODO  提取技能经历等数据
        skilldatas = job.xpath('//div[@id="content-main"]/table[2]//tr')

        count = len(skilldatas)
        i = 0
        while i < count:
            try:
                tag = skilldatas[i].xpath('td[@class="field"]/h5/text()').extract()[0]
            except:
                i += 1
                continue
            i += 1
            if 'Background' in tag:
                text = ' '.join(skilldatas[i].xpath('td[@class="text"]').xpath('string(.)').extract()[0].split())
                i += 1
                item['description'] = text
            elif 'Responsibilities' in tag:
                text = ' '.join(skilldatas[i].xpath('td[@class="text"]').xpath('string(.)').extract()[0].split())
                i += 1
                item['responsibilities'] = text
            elif 'Competencies' in tag:
                text = ' '.join(skilldatas[i].xpath('td[@class="text"]').xpath('string(.)').extract()[0].split())
                i += 1
                item['skill'] += text
            elif 'Skills and Experience' in tag:
                try:
                    text = ' '.join(skilldatas[i].xpath('td[@class="text"]').xpath('string(.)').extract()[0].split())
                    i += 1
                    info = []
                except:
                    print '获取信息错误2'

                if 'Education' in text:
                    info = text.split('Education')
                    down = ''
                    length = len(info)
                    for x in info[1:]:
                        down += x
                    info[1] = down
                    while length > 2:
                        info.pop()
                        length -= 1
                elif 'enrolment' in text:
                    info[0] = text.split('enrolment')[-1]
                    if 'skills' in text:
                        info1 = info[-1].split('skills')
                        item['education'] = info1[0]
                        down = ''
                        length = len(info1)
                        for x in info1[1:]:
                            down += x
                        info1[1] = down
                        while length > 2:
                            info1.pop()
                            length -= 1
                        if 'eligibility' in info1[-1]:
                            info2 = info1[-1].split('eligibility')
                            item['skill'] = info2[0]
                            item['addition'] = info2[-1]
                        break
                    else:
                        info[0] = text

                if 'Experience' in info[-1]:
                    info1 = info[-1].split('Experience')
                    item['education'] = info1[0]
                    down = ''
                    length = len(info1)
                    for x in info1[1:]:
                        down += x
                    info1[1] = down
                    while length > 2:
                        info1.pop()
                        length -= 1
                elif 'Expérience' in info[-1]:
                    info1 = info[-1].split('Expérience')
                    item['education'] = info1[0]
                    down = ''
                    length = len(info1)
                    for x in info1[1:]:
                        down += x
                    info1[1] = down
                    while length > 2:
                        info1.pop()
                        length -= 1
                else:
                    info1 = info

                if 'Language' in info1[-1]:
                    info2 = info1[-1].split('Language requirements')
                    item['experience'] = info2[0]
                    down = ''
                    length = len(info1)
                    for x in info2[1:]:
                        down += x
                    info2[1] = down
                    while length > 2:
                        info2.pop()
                        length -= 1
                else:
                    info2 = info1

                if 'Consultant' in info2[-1]:
                    info3 = info2[-1].split('Consultant')
                    item['language'] = info3[0]
                    item['addition'] = info3[-1]
                else:
                    info3 = info2

                item['addition'] = info3[-1]


    def _crawlhaveid(self,response):
        '''
        打开第二种形式页面并进行页面提取
        '''
        item = self. _setitem_noid(response)
        item['joburl'] = response.url

        try:
            self.crawlinfohaveid(item,response)
        except:
            logger.error("crawl failed!")
        yield item

    def crawlinfohaveid(self, item, response):

        '''
        对第二种页面进行字段提取
        '''
        logger.debug('crawl haveid!')

        selector = scrapy.Selector(response)
        table = selector.xpath("//table[@id='ACE_$ICField30$0']/tbody/tr/td")
        tds = [t.strip() for t in table.xpath("string(.)").extract()]
        count = len(tds)
        i = 0
        while i < count:
            if 'Title' in tds[i]:
                i += 1
                j = i
                for td in tds[j:]:
                    i += 1
                    if td:
                        item['work'] = td
                        break
            elif 'Vacancy End Date' in tds[i]:
                i += 1
                j = i
                for td in tds[j:]:
                    i += 1
                    if re.match('.*\d*/\d*/\d*.*',td):
                        item['ApplicationDeadline'] = td
                        break
            elif 'Duty Station' in tds[i]:
                i += 1
                j = i
                for td in tds[j:]:
                    i += 1
                    if td:
                        item['Location'] = td
                        break
            elif 'Education & Work Experience' in tds[i]:
                i += 1
                j = i
                for td in tds[j:]:
                    i += 1
                    if td:
                        content = re.match(r'(.*)-(.*)', td)
                        item['education'] = content.group(1)
                        item['experience'] = content.group(2)
                        break
            elif 'Languages' in tds[i]:
                i += 1
                j = i
                for td in tds[j:]:
                    i += 1
                    if td:
                        if 'Grade' in td:
                            break
                        else:
                            item['language'] += td
            elif 'Grade' in tds[i]:
                i += 1
                j = i
                for td in tds[j:]:
                    i +=1
                    if td:
                        item['PostLevel'] = td
                        break
            elif 'Contract Duration' in tds[i]:
                i += 1
                j = i
                for td in tds[j:]:
                    i += 1
                    if td:
                        item['contracttime'] = td
                        break
            else:
                i += 1

        table2 = selector.xpath("//table[@id='ACE_HRS_JO_PST_DSCR$0']/tbody/tr/td")
        tds2 = [t.strip() for t in table2.xpath("string(.)").extract()]
        count = len(tds2)
        i = 0
        while i < count:
            if 'Duties and Responsibilities' in tds2[i]:
                i += 1
                j = i
                for td in tds2[j:]:
                    i += 1
                    if td:
                        item['responsibilities'] = td
                        break
            else:
                i += 1


    def _setitem_noid(self,response):
        '''
        初始化第一种页面全部字段
        '''
        item = AllJobs()
        item["work"] = ""
        item["englishname"] = "UNDP"
        item["chinesename"] = "联合国开发计划署"
        item["incontinent"] = "北美洲"
        item["incountry"] = "美国"
        item["type"] = "科学研究"
        item["url"] = "http://www.undp.org/"
        item["alljoburl"] = "https://jobs.undp.org/cj_view_jobs.cfm"
        item["joburl"] = response.url
        item["description"] = response.meta["describe"]
        item["belong"] = response.meta["suoshu"]
        item["issuedate"] = response.meta["applytime"]
        item["linkman"] = response.meta["linkman"]
        item["ApplicationDeadline"] = ''
        item["Location"] = ''
        item["PostLevel"] = ''
        item['reference'] = ''
        item['responsibilities'] = ''
        item['skill'] = ''
        item['TypeofContract'] = ''
        item['language'] = ''
        item['contracttime'] = ''
        item['ExpectedDurationofAssignment'] = ''
        item['full_time'] = ''
        item['treatment'] = ''
        item['education'] = ''
        item['addition'] = ''
        item['experience'] = ''
        return item