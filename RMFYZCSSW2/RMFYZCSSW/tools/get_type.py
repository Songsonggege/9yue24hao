# -*- coding: utf-8 -*-
#__author__: wangke
#__date__: 2019/7/25  15:35
#__ide__: PyCharm
import re


def transfrom(text):
    pat_dict = {'.*经.*信.*': 'econoAndInforCommittee', '.*工.*业.*': 'industrialBureau',
                '.*公.*路.*': 'highwayAdministration', '.*地.*震.*': 'seismologicalBureau',
                '.*金.*融.*': 'localFinanceSafety', '.*园.*林.*': 'gardenBureau', '.*食.*药.*': 'fdadministrative',
                '.*市.*场.*监督.*': 'saows', '.*国.*科.*': 'nationalDefense', '.*广.*电.*': 'playBureau',
                '.*卫.*生.*': 'healthinspection', '.*科.*(学|技).*': 'science', '.*文.*旅.*': 'cttourism',
                '.*工.*信.*': 'boii', '.*文.*物.*': 'sach', '.*畜.*牧.*': 'husbandry', '.*无.*线.*电.*': 'radio',
                '.*烟.*草.*': 'tobacco', '.*邮.*政.*': 'postOffice', '.*审.*计.*': 'auditing', '.*公.*安.*': 'police',
                '.*农.*林.*': 'agriculture', '.*海.*事.*': 'msa', '.*经.*济.*': 'economic', '.*民.*政.*': 'civilaffairs',
                '.*统.*计.*': 'statistical', '.*教.*育.*': 'bfeducation', '.*文.*体.*新.*': 'boc', '.*海.*渔.*': 'mfbureau',
                '.*体.*育.*': 'sport', '.*民.*局.*': 'civilDefence', '.*文.*体.*广.*新.*': 'snb', '.*房.*管.*': 'hpm',
                '.*物.*价.*': 'priceBureau', '.*水.*(利|务).*': 'water', '.*农.*(业|委|牧).*': 'geoponics',
                '.*规.*划.*': 'planning', '.*发.*改.*': 'ndrc', '.*人.*力.*': 'hr', '.*建.*设.*': 'construction',
                '.*商.*务.*': 'commercial', '.*旅.*游.*': 'tourism', '.*国.*税.*': 'nationalTax',
                '.*粮.*食.*': 'foodBureau', '.*司.*法.*': 'judiciary', '.*环.*保.*': 'environmental', '.*税.*务.*': 'tax',
                '.*工.*商.*': 'business', '.*安.*监.*': 'safety', '.*交.*通.*': 'traffic', '.*国.*土.*': 'land',
                '.*财.*政.*': 'finance', '.*文.*化.*': 'culture', '.*城.*管.*': 'urban', '.*林.*业.*': 'forestry',
                '.*住.*建.*': 'housing', '.*海.*关.*': 'customs', '.*卫.*计.*': 'health', '.*人.*民.*银.*行.*': 'CNbank'}
    for key in pat_dict.keys():
        if (re.match("{}".format(key), text)):
            type = pat_dict[key]
            return type

type = transfrom("迪庆州医疗保障局")
print(type)