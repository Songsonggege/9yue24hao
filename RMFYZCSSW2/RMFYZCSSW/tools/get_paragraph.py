# -*- coding: utf-8 -*-
# __author__: wangke
# __date__: 2019/8/2  18:00
# __ide__: PyCharm
def get_paragraph(paragraph_list):
    paragraph_list = [i for i in paragraph_list if i.strip() != '']
    paragraph = ""
    for i in paragraph_list:
        paragraph += "<p>" + i.strip().replace("\xa0", "").replace("\n", "").replace(" ", "")+ "</p>"
    return paragraph
