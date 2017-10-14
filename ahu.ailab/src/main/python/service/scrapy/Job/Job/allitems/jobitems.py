# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AllJob(scrapy.Item):
    英文缩写 = scrapy.Field()
    中文名称 = scrapy.Field()
    所属洲 = scrapy.Field()
    所在地 = scrapy.Field()
    分类 = scrapy.Field()
    主页url = scrapy.Field()
    招聘网址 = scrapy.Field()
    岗位url = scrapy.Field()
    岗位名称 = scrapy.Field()
    工作地点 = scrapy.Field()
    职级 = scrapy.Field()
    发布日期 = scrapy.Field()
    截止日期 = scrapy.Field()
    职位介绍 = scrapy.Field()
    职能 = scrapy.Field()
    技能 = scrapy.Field()
    组织机构 = scrapy.Field()
    包工方式 = scrapy.Field()
    语言 = scrapy.Field()
    初始合同时间 = scrapy.Field()
    预计工作时间  = scrapy.Field()
    联系人 = scrapy.Field()
    是否全职 = scrapy.Field()
    待遇 = scrapy.Field()
    教育背景 = scrapy.Field()
    附加的 = scrapy.Field()
    工作经历 = scrapy.Field()
    参考 = scrapy.Field()