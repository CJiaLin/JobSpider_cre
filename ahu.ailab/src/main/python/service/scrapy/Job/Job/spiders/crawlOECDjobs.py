# -*- coding: utf-8 -*-

__author__ = 'Liuyang'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
sys.path.append('D:\py_spider')
from src.main.python.service.scrapy.Job.Job.utils.FileUtil import FileUtil
# from src.main.python.dao.jobDao.CsvCao import SaveToCsv
from src.main.python.service.scrapy.Job.Job.utils.strUtil import StrUtil
from selenium import webdriver
from scrapy.http import Request
from scrapy.http import HtmlResponse
from ..allitems.jobitems import AllJobs
import time
import re
import logging.config
logging.config.fileConfig(FileUtil().getLogConfigPath())
logger = logging.getLogger('ahu')
# OECDJobsPath = u"OECD.csv"

class OECDJobSpider(scrapy.Spider):
    name = 'OECDjobs'
    start_urls = ["https://oecd.taleo.net/careersection/ext/joblist.ftl"]

    def __init__(self):
        self.driver = webdriver.PhantomJS(executable_path=r'D:/py_spider/phantomjs-2.1.1-windows/bin/phantomjs.exe')

    def parse(self, response):
        # retrynum = 0
        self.driver.get(response.url)
        main_page = self.driver
        time.sleep(5)
        # self.driver.maximize_window()
        self.driver.implicitly_wait(30)

        # 判断页面是否加载成功
        if "Job" in self.driver.page_source:
            # 进入第一个职位

            #jobs = self.driver.find_elements_by_xpath('//tr[@id="requisitionListInterface.ID2743.row"]')
            jobs = main_page.find_elements_by_xpath('//titlelink')
            while True:
                i = 1
                for job in jobs:
                    item = self._inititem()
                    print job
                    # print job.text
                    title = job.xpath('//a/text()').extract()
                    item['issuedate'] = main_page.find_element_by_id('requisitionListInterface.reqPostingDate.row' + str(i)).text

                    item['ApplicationDeadline'] = main_page.find_element_by_id('requisitionListInterface.reqUnpostingDate.row' + str(i)).text
                    main_page.find_element_by_link_text(title).click()
                    i += 1
                    yield Request(url=response.url, callback=self.details, meta={'item':item, 'page_source':self.driver.page_source}, dont_filter=True)
                    #self.pars(self.driver.page_source.url)

                try:
                    main_page.find_element_by_partial_link_text("Next").click()
                except:
                    break

            self.depose()

            '''click_text = u"Policy Analysts"
            self.driver.find_element_by_partial_link_text(click_text).click()
            item = self.pars(self.driver.page_source)
            #items.append(item)
            time.sleep(3)
            for i in range(0,23,1):
                if "Job" in self.driver.page_source:
                    self.driver.find_element_by_partial_link_text("Next").click()
                    time.sleep(3)
                    #issuedate = self.driver.page_source
                    #item['ApplicationDeadline'] =
                    item = self.pars(self.driver.page_source)
                    #if item not in items:
                        #items.append(item)
                    logger.debug('爬取岗位%s成功'%item['work'])
                else:
                    logger.error("页面加载失败")
        else:
            retrynum += 1
            time.sleep(5)
            if retrynum < 10:
                self.driver.refresh()
                self.start()

        # TODO 保存爬取的数据
        logger.info("OECDJob>>>共爬取岗位数%d"%len(items))

        # saveToCsv = SaveToCsv()
        # saveToCsv.saveOECDjobs(OECDJobsPath,items)'''

    def details(self, response):
        item = response.meta['item']
        res = HtmlResponse(url='my HTML string', body=response.meta['page_source'], encoding="utf-8")
        selector = scrapy.Selector(res)
        # 岗位名称
        workdata = selector.xpath('//div[@class="editablesection"]/div[1]')
        workinfo = workdata.xpath('string(.)').extract()
        item["work"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(workinfo[0]))
        url = response.url
        item['joburl'] = url

        # 其他岗位信息
        otherdata = selector.xpath('//span[@id="requisitionDescriptionInterface.ID1451.row1"]')
        require =   re.sub('\n',' ',otherdata.xpath('string(.)').extract()[0])

        info1 = require.split('Main Responsibilities')
        for i in info1[:-1]:
            item['description'] += i
        item['description'] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(item['description']))

        info2 = info1[-1].split('Ideal Candidate profile')
        for i in info2[:-1]:
            item['responsibilities'] += i
        item['responsibilities'] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(item['responsibilities']))

        info3 = info2[-1].split('Contract Duration')
        for i in info3[:-1]:

            item["IdealCandidateProfile"] += i
        item["contracttime"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(item["IdealCandidateProfile"]))

        if 'What the OECD offers' in info3[-1]:
            info4 = info3[-1].split('What the OECD offers')
            item["contracttime"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(info4[0]))
            item["treatment"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(info4[1]))
        else:
            item["contracttime"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(info3[-1]))
        yield item

    def depose(self):
        self.driver.close()

    def _inititem(self):
        '''
        初始化全部字段
        :return: 初始化字段
        '''
        item = AllJobs()
        item["englishname"] = "OECD"
        item["chinesename"] = "经济合作与发展组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "法国"
        item["type"] = "经济"
        item["url"] = "http://www.oecd.org/"
        item["alljoburl"] = "https://oecd.taleo.net/careersection/ext/joblist.ftl"
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
        return item

if __name__ == "__main__":
    oECDJobSpider = OECDJobSpider()
    oECDJobSpider.depose()
    