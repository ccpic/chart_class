"""
中国地图热力图绘制模块

基于 GeoPandas 和 Matplotlib，支持省级、地级市、区县三个层级的热力图绘制。
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Literal, List
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib as mpl
from chart.plots.base import Plot


# 省级简称到全称的映射字典（支持"北京"/"北京市"等多种输入）
PROVINCE_NAME_MAP = {
    # 直辖市
    "北京": "北京市",
    "北京市": "北京市",
    "天津": "天津市",
    "天津市": "天津市",
    "上海": "上海市",
    "上海市": "上海市",
    "重庆": "重庆市",
    "重庆市": "重庆市",
    # 省
    "河北": "河北省",
    "河北省": "河北省",
    "山西": "山西省",
    "山西省": "山西省",
    "辽宁": "辽宁省",
    "辽宁省": "辽宁省",
    "吉林": "吉林省",
    "吉林省": "吉林省",
    "黑龙江": "黑龙江省",
    "黑龙江省": "黑龙江省",
    "江苏": "江苏省",
    "江苏省": "江苏省",
    "浙江": "浙江省",
    "浙江省": "浙江省",
    "安徽": "安徽省",
    "安徽省": "安徽省",
    "福建": "福建省",
    "福建省": "福建省",
    "江西": "江西省",
    "江西省": "江西省",
    "山东": "山东省",
    "山东省": "山东省",
    "河南": "河南省",
    "河南省": "河南省",
    "湖北": "湖北省",
    "湖北省": "湖北省",
    "湖南": "湖南省",
    "湖南省": "湖南省",
    "广东": "广东省",
    "广东省": "广东省",
    "海南": "海南省",
    "海南省": "海南省",
    "四川": "四川省",
    "四川省": "四川省",
    "贵州": "贵州省",
    "贵州省": "贵州省",
    "云南": "云南省",
    "云南省": "云南省",
    "陕西": "陕西省",
    "陕西省": "陕西省",
    "甘肃": "甘肃省",
    "甘肃省": "甘肃省",
    "青海": "青海省",
    "青海省": "青海省",
    "台湾": "台湾省",
    "台湾省": "台湾省",
    # 自治区
    "内蒙古": "内蒙古自治区",
    "内蒙古自治区": "内蒙古自治区",
    "广西": "广西壮族自治区",
    "广西壮族自治区": "广西壮族自治区",
    "西藏": "西藏自治区",
    "西藏自治区": "西藏自治区",
    "宁夏": "宁夏回族自治区",
    "宁夏回族自治区": "宁夏回族自治区",
    "新疆": "新疆维吾尔自治区",
    "新疆维吾尔自治区": "新疆维吾尔自治区",
    # 特别行政区
    "香港": "香港特别行政区",
    "香港特别行政区": "香港特别行政区",
    "澳门": "澳门特别行政区",
    "澳门特别行政区": "澳门特别行政区",
}

# 地级市简称到全称的映射字典（支持"昆明"/"昆明市"等多种输入）
CITY_NAME_MAP = {
    # 直辖市（作为地级市出现）
    "北京": "北京市",
    "北京市": "北京市",
    "天津": "天津市",
    "天津市": "天津市",
    "上海": "上海市",
    "上海市": "上海市",
    "重庆": "重庆市",
    "重庆市": "重庆市",
    # 普通地级市（按拼音排序）
    "阿坝": "阿坝藏族羌族自治州",
    "阿坝藏族羌族自治州": "阿坝藏族羌族自治州",
    "阿克苏": "阿克苏地区",
    "阿克苏地区": "阿克苏地区",
    "阿拉尔": "阿拉尔市",
    "阿拉尔市": "阿拉尔市",
    "阿拉善": "阿拉善盟",
    "阿拉善盟": "阿拉善盟",
    "阿勒泰": "阿勒泰地区",
    "阿勒泰地区": "阿勒泰地区",
    "阿里": "阿里地区",
    "阿里地区": "阿里地区",
    "安康": "安康市",
    "安康市": "安康市",
    "安庆": "安庆市",
    "安庆市": "安庆市",
    "安顺": "安顺市",
    "安顺市": "安顺市",
    "安阳": "安阳市",
    "安阳市": "安阳市",
    "鞍山": "鞍山市",
    "鞍山市": "鞍山市",
    "巴彦淖尔": "巴彦淖尔市",
    "巴彦淖尔市": "巴彦淖尔市",
    "巴音郭楞": "巴音郭楞蒙古自治州",
    "巴音郭楞蒙古自治州": "巴音郭楞蒙古自治州",
    "巴中": "巴中市",
    "巴中市": "巴中市",
    "白城": "白城市",
    "白城市": "白城市",
    "白山": "白山市",
    "白山市": "白山市",
    "白银": "白银市",
    "白银市": "白银市",
    "白杨": "白杨市",
    "白杨市": "白杨市",
    "百色": "百色市",
    "百色市": "百色市",
    "蚌埠": "蚌埠市",
    "蚌埠市": "蚌埠市",
    "包头": "包头市",
    "包头市": "包头市",
    "宝鸡": "宝鸡市",
    "宝鸡市": "宝鸡市",
    "保定": "保定市",
    "保定市": "保定市",
    "保山": "保山市",
    "保山市": "保山市",
    "北海": "北海市",
    "北海市": "北海市",
    "北屯": "北屯市",
    "北屯市": "北屯市",
    "本溪": "本溪市",
    "本溪市": "本溪市",
    "毕节": "毕节市",
    "毕节市": "毕节市",
    "滨州": "滨州市",
    "滨州市": "滨州市",
    "博尔塔拉": "博尔塔拉蒙古自治州",
    "博尔塔拉蒙古自治州": "博尔塔拉蒙古自治州",
    "沧州": "沧州市",
    "沧州市": "沧州市",
    "昌都": "昌都市",
    "昌都市": "昌都市",
    "昌吉": "昌吉回族自治州",
    "昌吉回族自治州": "昌吉回族自治州",
    "长春": "长春市",
    "长春市": "长春市",
    "长沙": "长沙市",
    "长沙市": "长沙市",
    "长治": "长治市",
    "长治市": "长治市",
    "常德": "常德市",
    "常德市": "常德市",
    "常州": "常州市",
    "常州市": "常州市",
    "巢湖": "巢湖市",
    "巢湖市": "巢湖市",
    "朝阳": "朝阳市",
    "朝阳市": "朝阳市",
    "潮州": "潮州市",
    "潮州市": "潮州市",
    "郴州": "郴州市",
    "郴州市": "郴州市",
    "成都": "成都市",
    "成都市": "成都市",
    "承德": "承德市",
    "承德市": "承德市",
    "池州": "池州市",
    "池州市": "池州市",
    "赤峰": "赤峰市",
    "赤峰市": "赤峰市",
    "崇左": "崇左市",
    "崇左市": "崇左市",
    "滁州": "滁州市",
    "滁州市": "滁州市",
    "楚雄": "楚雄彝族自治州",
    "楚雄彝族自治州": "楚雄彝族自治州",
    "达州": "达州市",
    "达州市": "达州市",
    "大理": "大理白族自治州",
    "大理白族自治州": "大理白族自治州",
    "大连": "大连市",
    "大连市": "大连市",
    "大庆": "大庆市",
    "大庆市": "大庆市",
    "大同": "大同市",
    "大同市": "大同市",
    "大兴安岭": "大兴安岭地区",
    "大兴安岭地区": "大兴安岭地区",
    "丹东": "丹东市",
    "丹东市": "丹东市",
    "德宏": "德宏傣族景颇族自治州",
    "德宏傣族景颇族自治州": "德宏傣族景颇族自治州",
    "德阳": "德阳市",
    "德阳市": "德阳市",
    "德州": "德州市",
    "德州市": "德州市",
    "迪庆": "迪庆藏族自治州",
    "迪庆藏族自治州": "迪庆藏族自治州",
    "定西": "定西市",
    "定西市": "定西市",
    "东方": "东方市",
    "东方市": "东方市",
    "东莞": "东莞市",
    "东莞市": "东莞市",
    "东营": "东营市",
    "东营市": "东营市",
    "鄂尔多斯": "鄂尔多斯市",
    "鄂尔多斯市": "鄂尔多斯市",
    "鄂州": "鄂州市",
    "鄂州市": "鄂州市",
    "恩施": "恩施土家族苗族自治州",
    "恩施土家族苗族自治州": "恩施土家族苗族自治州",
    "防城港": "防城港市",
    "防城港市": "防城港市",
    "佛山": "佛山市",
    "佛山市": "佛山市",
    "福州": "福州市",
    "福州市": "福州市",
    "抚顺": "抚顺市",
    "抚顺市": "抚顺市",
    "抚州": "抚州市",
    "抚州市": "抚州市",
    "阜新": "阜新市",
    "阜新市": "阜新市",
    "阜阳": "阜阳市",
    "阜阳市": "阜阳市",
    "甘南": "甘南藏族自治州",
    "甘南藏族自治州": "甘南藏族自治州",
    "甘孜": "甘孜藏族自治州",
    "甘孜藏族自治州": "甘孜藏族自治州",
    "赣州": "赣州市",
    "赣州市": "赣州市",
    "固原": "固原市",
    "固原市": "固原市",
    "广安": "广安市",
    "广安市": "广安市",
    "广元": "广元市",
    "广元市": "广元市",
    "广州": "广州市",
    "广州市": "广州市",
    "贵港": "贵港市",
    "贵港市": "贵港市",
    "贵阳": "贵阳市",
    "贵阳市": "贵阳市",
    "桂林": "桂林市",
    "桂林市": "桂林市",
    "果洛": "果洛藏族自治州",
    "果洛藏族自治州": "果洛藏族自治州",
    "哈密": "哈密市",
    "哈密市": "哈密市",
    "哈尔滨": "哈尔滨市",
    "哈尔滨市": "哈尔滨市",
    "海北": "海北藏族自治州",
    "海北藏族自治州": "海北藏族自治州",
    "海东": "海东市",
    "海东市": "海东市",
    "海口": "海口市",
    "海口市": "海口市",
    "海南": "海南藏族自治州",
    "海南藏族自治州": "海南藏族自治州",
    "海西": "海西蒙古族藏族自治州",
    "海西蒙古族藏族自治州": "海西蒙古族藏族自治州",
    "邯郸": "邯郸市",
    "邯郸市": "邯郸市",
    "汉中": "汉中市",
    "汉中市": "汉中市",
    "杭州": "杭州市",
    "杭州市": "杭州市",
    "毫州": "亳州市",
    "亳州": "亳州市",
    "亳州市": "亳州市",
    "合肥": "合肥市",
    "合肥市": "合肥市",
    "和田": "和田地区",
    "和田地区": "和田地区",
    "河池": "河池市",
    "河池市": "河池市",
    "河源": "河源市",
    "河源市": "河源市",
    "贺州": "贺州市",
    "贺州市": "贺州市",
    "鹤壁": "鹤壁市",
    "鹤壁市": "鹤壁市",
    "鹤岗": "鹤岗市",
    "鹤岗市": "鹤岗市",
    "菏泽": "菏泽市",
    "菏泽市": "菏泽市",
    "黑河": "黑河市",
    "黑河市": "黑河市",
    "衡水": "衡水市",
    "衡水市": "衡水市",
    "衡阳": "衡阳市",
    "衡阳市": "衡阳市",
    "红河": "红河哈尼族彝族自治州",
    "红河哈尼族彝族自治州": "红河哈尼族彝族自治州",
    "呼和浩特": "呼和浩特市",
    "呼和浩特市": "呼和浩特市",
    "呼伦贝尔": "呼伦贝尔市",
    "呼伦贝尔市": "呼伦贝尔市",
    "胡杨河": "胡杨河市",
    "胡杨河市": "胡杨河市",
    "葫芦岛": "葫芦岛市",
    "葫芦岛市": "葫芦岛市",
    "湖州": "湖州市",
    "湖州市": "湖州市",
    "怀化": "怀化市",
    "怀化市": "怀化市",
    "淮安": "淮安市",
    "淮安市": "淮安市",
    "淮北": "淮北市",
    "淮北市": "淮北市",
    "淮南": "淮南市",
    "淮南市": "淮南市",
    "黄冈": "黄冈市",
    "黄冈市": "黄冈市",
    "黄南": "黄南藏族自治州",
    "黄南藏族自治州": "黄南藏族自治州",
    "黄山": "黄山市",
    "黄山市": "黄山市",
    "黄石": "黄石市",
    "黄石市": "黄石市",
    "惠州": "惠州市",
    "惠州市": "惠州市",
    "鸡西": "鸡西市",
    "鸡西市": "鸡西市",
    "吉安": "吉安市",
    "吉安市": "吉安市",
    "吉林": "吉林市",
    "吉林市": "吉林市",
    "济南": "济南市",
    "济南市": "济南市",
    "济宁": "济宁市",
    "济宁市": "济宁市",
    "济源": "济源市",
    "济源市": "济源市",
    "佳木斯": "佳木斯市",
    "佳木斯市": "佳木斯市",
    "嘉兴": "嘉兴市",
    "嘉兴市": "嘉兴市",
    "嘉峪关": "嘉峪关市",
    "嘉峪关市": "嘉峪关市",
    "江门": "江门市",
    "江门市": "江门市",
    "焦作": "焦作市",
    "焦作市": "焦作市",
    "揭阳": "揭阳市",
    "揭阳市": "揭阳市",
    "金昌": "金昌市",
    "金昌市": "金昌市",
    "金华": "金华市",
    "金华市": "金华市",
    "锦州": "锦州市",
    "锦州市": "锦州市",
    "晋城": "晋城市",
    "晋城市": "晋城市",
    "晋中": "晋中市",
    "晋中市": "晋中市",
    "荆门": "荆门市",
    "荆门市": "荆门市",
    "荆州": "荆州市",
    "荆州市": "荆州市",
    "景德镇": "景德镇市",
    "景德镇市": "景德镇市",
    "九江": "九江市",
    "九江市": "九江市",
    "酒泉": "酒泉市",
    "酒泉市": "酒泉市",
    "喀什": "喀什地区",
    "喀什地区": "喀什地区",
    "开封": "开封市",
    "开封市": "开封市",
    "可克达拉": "可克达拉市",
    "可克达拉市": "可克达拉市",
    "克拉玛依": "克拉玛依市",
    "克拉玛依市": "克拉玛依市",
    "克孜勒苏": "克孜勒苏柯尔克孜自治州",
    "克孜勒苏柯尔克孜自治州": "克孜勒苏柯尔克孜自治州",
    "昆明": "昆明市",
    "昆明市": "昆明市",
    "昆玉": "昆玉市",
    "昆玉市": "昆玉市",
    "来宾": "来宾市",
    "来宾市": "来宾市",
    "莱芜": "莱芜市",
    "莱芜市": "莱芜市",
    "兰州": "兰州市",
    "兰州市": "兰州市",
    "廊坊": "廊坊市",
    "廊坊市": "廊坊市",
    "拉萨": "拉萨市",
    "拉萨市": "拉萨市",
    "乐山": "乐山市",
    "乐山市": "乐山市",
    "凉山": "凉山彝族自治州",
    "凉山彝族自治州": "凉山彝族自治州",
    "连云港": "连云港市",
    "连云港市": "连云港市",
    "聊城": "聊城市",
    "聊城市": "聊城市",
    "辽源": "辽源市",
    "辽源市": "辽源市",
    "辽阳": "辽阳市",
    "辽阳市": "辽阳市",
    "丽江": "丽江市",
    "丽江市": "丽江市",
    "丽水": "丽水市",
    "丽水市": "丽水市",
    "临沧": "临沧市",
    "临沧市": "临沧市",
    "临汾": "临汾市",
    "临汾市": "临汾市",
    "临夏": "临夏回族自治州",
    "临夏回族自治州": "临夏回族自治州",
    "临沂": "临沂市",
    "临沂市": "临沂市",
    "林芝": "林芝市",
    "林芝市": "林芝市",
    "六安": "六安市",
    "六安市": "六安市",
    "六盘水": "六盘水市",
    "六盘水市": "六盘水市",
    "柳州": "柳州市",
    "柳州市": "柳州市",
    "龙岩": "龙岩市",
    "龙岩市": "龙岩市",
    "陇南": "陇南市",
    "陇南市": "陇南市",
    "娄底": "娄底市",
    "娄底市": "娄底市",
    "泸州": "泸州市",
    "泸州市": "泸州市",
    "洛阳": "洛阳市",
    "洛阳市": "洛阳市",
    "漯河": "漯河市",
    "漯河市": "漯河市",
    "吕梁": "吕梁市",
    "吕梁市": "吕梁市",
    "马鞍山": "马鞍山市",
    "马鞍山市": "马鞍山市",
    "茂名": "茂名市",
    "茂名市": "茂名市",
    "眉山": "眉山市",
    "眉山市": "眉山市",
    "梅州": "梅州市",
    "梅州市": "梅州市",
    "绵阳": "绵阳市",
    "绵阳市": "绵阳市",
    "牡丹江": "牡丹江市",
    "牡丹江市": "牡丹江市",
    "那曲": "那曲市",
    "那曲市": "那曲市",
    "南昌": "南昌市",
    "南昌市": "南昌市",
    "南充": "南充市",
    "南充市": "南充市",
    "南京": "南京市",
    "南京市": "南京市",
    "南宁": "南宁市",
    "南宁市": "南宁市",
    "南平": "南平市",
    "南平市": "南平市",
    "南通": "南通市",
    "南通市": "南通市",
    "南阳": "南阳市",
    "南阳市": "南阳市",
    "内江": "内江市",
    "内江市": "内江市",
    "宁波": "宁波市",
    "宁波市": "宁波市",
    "宁德": "宁德市",
    "宁德市": "宁德市",
    "怒江": "怒江傈僳族自治州",
    "怒江傈僳族自治州": "怒江傈僳族自治州",
    "攀枝花": "攀枝花市",
    "攀枝花市": "攀枝花市",
    "盘锦": "盘锦市",
    "盘锦市": "盘锦市",
    "平顶山": "平顶山市",
    "平顶山市": "平顶山市",
    "平凉": "平凉市",
    "平凉市": "平凉市",
    "萍乡": "萍乡市",
    "萍乡市": "萍乡市",
    "莆田": "莆田市",
    "莆田市": "莆田市",
    "濮阳": "濮阳市",
    "濮阳市": "濮阳市",
    "普洱": "普洱市",
    "普洱市": "普洱市",
    "七台河": "七台河市",
    "七台河市": "七台河市",
    "齐齐哈尔": "齐齐哈尔市",
    "齐齐哈尔市": "齐齐哈尔市",
    "黔东南": "黔东南苗族侗族自治州",
    "黔东南苗族侗族自治州": "黔东南苗族侗族自治州",
    "黔南": "黔南布依族苗族自治州",
    "黔南布依族苗族自治州": "黔南布依族苗族自治州",
    "黔西南": "黔西南布依族苗族自治州",
    "黔西南布依族苗族自治州": "黔西南布依族苗族自治州",
    "潜江": "潜江市",
    "潜江市": "潜江市",
    "钦州": "钦州市",
    "钦州市": "钦州市",
    "秦皇岛": "秦皇岛市",
    "秦皇岛市": "秦皇岛市",
    "青岛": "青岛市",
    "青岛市": "青岛市",
    "清远": "清远市",
    "清远市": "清远市",
    "庆阳": "庆阳市",
    "庆阳市": "庆阳市",
    "琼海": "琼海市",
    "琼海市": "琼海市",
    "曲靖": "曲靖市",
    "曲靖市": "曲靖市",
    "衢州": "衢州市",
    "衢州市": "衢州市",
    "泉州": "泉州市",
    "泉州市": "泉州市",
    "日喀则": "日喀则市",
    "日喀则市": "日喀则市",
    "日照": "日照市",
    "日照市": "日照市",
    "三门峡": "三门峡市",
    "三门峡市": "三门峡市",
    "三明": "三明市",
    "三明市": "三明市",
    "三亚": "三亚市",
    "三亚市": "三亚市",
    "三沙": "三沙市",
    "三沙市": "三沙市",
    "厦门": "厦门市",
    "厦门市": "厦门市",
    "山南": "山南市",
    "山南市": "山南市",
    "汕头": "汕头市",
    "汕头市": "汕头市",
    "汕尾": "汕尾市",
    "汕尾市": "汕尾市",
    "商洛": "商洛市",
    "商洛市": "商洛市",
    "商丘": "商丘市",
    "商丘市": "商丘市",
    "上饶": "上饶市",
    "上饶市": "上饶市",
    "韶关": "韶关市",
    "韶关市": "韶关市",
    "邵阳": "邵阳市",
    "邵阳市": "邵阳市",
    "绍兴": "绍兴市",
    "绍兴市": "绍兴市",
    "神农架": "神农架林区",
    "神农架林区": "神农架林区",
    "沈阳": "沈阳市",
    "沈阳市": "沈阳市",
    "深圳": "深圳市",
    "深圳市": "深圳市",
    "十堰": "十堰市",
    "十堰市": "十堰市",
    "石河子": "石河子市",
    "石河子市": "石河子市",
    "石家庄": "石家庄市",
    "石家庄市": "石家庄市",
    "石嘴山": "石嘴山市",
    "石嘴山市": "石嘴山市",
    "双河": "双河市",
    "双河市": "双河市",
    "双鸭山": "双鸭山市",
    "双鸭山市": "双鸭山市",
    "朔州": "朔州市",
    "朔州市": "朔州市",
    "四平": "四平市",
    "四平市": "四平市",
    "松原": "松原市",
    "松原市": "松原市",
    "苏州": "苏州市",
    "苏州市": "苏州市",
    "宿迁": "宿迁市",
    "宿迁市": "宿迁市",
    "宿州": "宿州市",
    "宿州市": "宿州市",
    "绥化": "绥化市",
    "绥化市": "绥化市",
    "随州": "随州市",
    "随州市": "随州市",
    "遂宁": "遂宁市",
    "遂宁市": "遂宁市",
    "塔城": "塔城地区",
    "塔城地区": "塔城地区",
    "台州": "台州市",
    "台州市": "台州市",
    "太原": "太原市",
    "太原市": "太原市",
    "泰安": "泰安市",
    "泰安市": "泰安市",
    "泰州": "泰州市",
    "泰州市": "泰州市",
    "唐山": "唐山市",
    "唐山市": "唐山市",
    "天门": "天门市",
    "天门市": "天门市",
    "天水": "天水市",
    "天水市": "天水市",
    "铁岭": "铁岭市",
    "铁岭市": "铁岭市",
    "铁门关": "铁门关市",
    "铁门关市": "铁门关市",
    "通化": "通化市",
    "通化市": "通化市",
    "通辽": "通辽市",
    "通辽市": "通辽市",
    "铜川": "铜川市",
    "铜川市": "铜川市",
    "铜陵": "铜陵市",
    "铜陵市": "铜陵市",
    "铜仁": "铜仁市",
    "铜仁市": "铜仁市",
    "图木舒克": "图木舒克市",
    "图木舒克市": "图木舒克市",
    "吐鲁番": "吐鲁番市",
    "吐鲁番市": "吐鲁番市",
    "万宁": "万宁市",
    "万宁市": "万宁市",
    "威海": "威海市",
    "威海市": "威海市",
    "潍坊": "潍坊市",
    "潍坊市": "潍坊市",
    "渭南": "渭南市",
    "渭南市": "渭南市",
    "温州": "温州市",
    "温州市": "温州市",
    "文昌": "文昌市",
    "文昌市": "文昌市",
    "文山": "文山壮族苗族自治州",
    "文山壮族苗族自治州": "文山壮族苗族自治州",
    "乌海": "乌海市",
    "乌海市": "乌海市",
    "乌兰察布": "乌兰察布市",
    "乌兰察布市": "乌兰察布市",
    "乌鲁木齐": "乌鲁木齐市",
    "乌鲁木齐市": "乌鲁木齐市",
    "无锡": "无锡市",
    "无锡市": "无锡市",
    "吴忠": "吴忠市",
    "吴忠市": "吴忠市",
    "芜湖": "芜湖市",
    "芜湖市": "芜湖市",
    "梧州": "梧州市",
    "梧州市": "梧州市",
    "五家渠": "五家渠市",
    "五家渠市": "五家渠市",
    "五指山": "五指山市",
    "五指山市": "五指山市",
    "武汉": "武汉市",
    "武汉市": "武汉市",
    "武威": "武威市",
    "武威市": "武威市",
    "西安": "西安市",
    "西安市": "西安市",
    "西宁": "西宁市",
    "西宁市": "西宁市",
    "西双版纳": "西双版纳傣族自治州",
    "西双版纳傣族自治州": "西双版纳傣族自治州",
    "锡林郭勒": "锡林郭勒盟",
    "锡林郭勒盟": "锡林郭勒盟",
    "仙桃": "仙桃市",
    "仙桃市": "仙桃市",
    "咸宁": "咸宁市",
    "咸宁市": "咸宁市",
    "咸阳": "咸阳市",
    "咸阳市": "咸阳市",
    "湘潭": "湘潭市",
    "湘潭市": "湘潭市",
    "湘西": "湘西土家族苗族自治州",
    "湘西土家族苗族自治州": "湘西土家族苗族自治州",
    "襄阳": "襄阳市",
    "襄阳市": "襄阳市",
    "孝感": "孝感市",
    "孝感市": "孝感市",
    "忻州": "忻州市",
    "忻州市": "忻州市",
    "新乡": "新乡市",
    "新乡市": "新乡市",
    "新余": "新余市",
    "新余市": "新余市",
    "新星": "新星市",
    "新星市": "新星市",
    "信阳": "信阳市",
    "信阳市": "信阳市",
    "兴安": "兴安盟",
    "兴安盟": "兴安盟",
    "邢台": "邢台市",
    "邢台市": "邢台市",
    "宣城": "宣城市",
    "宣城市": "宣城市",
    "许昌": "许昌市",
    "许昌市": "许昌市",
    "徐州": "徐州市",
    "徐州市": "徐州市",
    "雅安": "雅安市",
    "雅安市": "雅安市",
    "烟台": "烟台市",
    "烟台市": "烟台市",
    "延安": "延安市",
    "延安市": "延安市",
    "延边": "延边朝鲜族自治州",
    "延边朝鲜族自治州": "延边朝鲜族自治州",
    "盐城": "盐城市",
    "盐城市": "盐城市",
    "扬州": "扬州市",
    "扬州市": "扬州市",
    "阳江": "阳江市",
    "阳江市": "阳江市",
    "阳泉": "阳泉市",
    "阳泉市": "阳泉市",
    "伊春": "伊春市",
    "伊春市": "伊春市",
    "伊犁": "伊犁哈萨克自治州",
    "伊犁哈萨克自治州": "伊犁哈萨克自治州",
    "宜宾": "宜宾市",
    "宜宾市": "宜宾市",
    "宜昌": "宜昌市",
    "宜昌市": "宜昌市",
    "宜春": "宜春市",
    "宜春市": "宜春市",
    "益阳": "益阳市",
    "益阳市": "益阳市",
    "银川": "银川市",
    "银川市": "银川市",
    "鹰潭": "鹰潭市",
    "鹰潭市": "鹰潭市",
    "营口": "营口市",
    "营口市": "营口市",
    "永州": "永州市",
    "永州市": "永州市",
    "榆林": "榆林市",
    "榆林市": "榆林市",
    "玉林": "玉林市",
    "玉林市": "玉林市",
    "玉树": "玉树藏族自治州",
    "玉树藏族自治州": "玉树藏族自治州",
    "玉溪": "玉溪市",
    "玉溪市": "玉溪市",
    "岳阳": "岳阳市",
    "岳阳市": "岳阳市",
    "云浮": "云浮市",
    "云浮市": "云浮市",
    "运城": "运城市",
    "运城市": "运城市",
    "枣庄": "枣庄市",
    "枣庄市": "枣庄市",
    "湛江": "湛江市",
    "湛江市": "湛江市",
    "张家界": "张家界市",
    "张家界市": "张家界市",
    "张家口": "张家口市",
    "张家口市": "张家口市",
    "张掖": "张掖市",
    "张掖市": "张掖市",
    "漳州": "漳州市",
    "漳州市": "漳州市",
    "昭通": "昭通市",
    "昭通市": "昭通市",
    "肇庆": "肇庆市",
    "肇庆市": "肇庆市",
    "镇江": "镇江市",
    "镇江市": "镇江市",
    "郑州": "郑州市",
    "郑州市": "郑州市",
    "中山": "中山市",
    "中山市": "中山市",
    "中卫": "中卫市",
    "中卫市": "中卫市",
    "周口": "周口市",
    "周口市": "周口市",
    "舟山": "舟山市",
    "舟山市": "舟山市",
    "株洲": "株洲市",
    "株洲市": "株洲市",
    "珠海": "珠海市",
    "珠海市": "珠海市",
    "驻马店": "驻马店市",
    "驻马店市": "驻马店市",
    "资阳": "资阳市",
    "资阳市": "资阳市",
    "淄博": "淄博市",
    "淄博市": "淄博市",
    "自贡": "自贡市",
    "自贡市": "自贡市",
    "遵义": "遵义市",
    "遵义市": "遵义市",
    "儋州": "儋州市",
    "儋州市": "儋州市",
    # 特别行政区
    "香港": "香港特别行政区",
    "香港特别行政区": "香港特别行政区",
    "澳门": "澳门特别行政区",
    "澳门特别行政区": "澳门特别行政区",
    # 省直管县级市（海南省）
    "临高": "临高县",
    "临高县": "临高县",
    "定安": "定安县",
    "定安县": "定安县",
    "屯昌": "屯昌县",
    "屯昌县": "屯昌县",
    "澄迈": "澄迈县",
    "澄迈县": "澄迈县",
    "乐东": "乐东黎族自治县",
    "乐东黎族自治县": "乐东黎族自治县",
    "保亭": "保亭黎族苗族自治县",
    "保亭黎族苗族自治县": "保亭黎族苗族自治县",
    "昌江": "昌江黎族自治县",
    "昌江黎族自治县": "昌江黎族自治县",
    "白沙": "白沙黎族自治县",
    "白沙黎族自治县": "白沙黎族自治县",
    "陵水": "陵水黎族自治县",
    "陵水黎族自治县": "陵水黎族自治县",
    "琼中": "琼中黎族苗族自治县",
    "琼中黎族苗族自治县": "琼中黎族苗族自治县",
}


# 无下属区县的地级市列表（这些城市没有区县，直接作为地级市显示）
CITIES_WITHOUT_COUNTIES = ["东莞市", "中山市", "嘉峪关市", "儋州市"]

# 区县简称字典（用于标签显示）
COUNTY_ABBR_MAP = {
    # 云南省
    "巍山彝族回族自治县": "巍山县",
    "南涧彝族自治县": "南涧县",
    "漾濞彝族自治县": "漾濞县",
    "维西傈僳族自治县": "维西县",
    "河口瑶族自治县": "河口县",
    "金平苗族瑶族傣族自治县": "金平县",
    "屏边苗族自治县": "屏边县",
    "禄劝彝族苗族自治县": "禄劝县",
    "寻甸回族彝族自治县": "寻甸县",
    "石林彝族自治县": "石林县",
    "玉龙纳西族自治县": "玉龙县",
    "宁蒗彝族自治县": "宁蒗县",
    "耿马傣族佤族自治县": "耿马县",
    "双江拉祜族佤族布朗族傣族自治县": "双江县",
    "沧源佤族自治县": "沧源县",
    "兰坪白族普米族自治县": "兰坪县",
    "贡山独龙族怒族自治县": "贡山县",
    "澜沧拉祜族自治县": "澜沧县",
    "景谷傣族彝族自治县": "景谷县",
    "景东彝族自治县": "景东县",
    "墨江哈尼族自治县": "墨江县",
    "镇沅彝族哈尼族拉祜族自治县": "镇沅县",
    "宁洱哈尼族彝族自治县": "宁洱县",
    "江城哈尼族彝族自治县": "江城县",
    "孟连傣族拉祜族佤族自治县": "孟连县",
    "西盟佤族自治县": "西盟县",
    "新平彝族傣族自治县": "新平县",
    "元江哈尼族彝族傣族自治县": "元江县",
    "峨山彝族自治县": "峨山县",
    # 青海省
    "门源回族自治县": "门源县",
    "互助土族自治县": "互助县",
    "民和回族土族自治县": "民和县",
    "化隆回族自治县": "化隆县",
    "循化撒拉族自治县": "循化县",
    "大柴旦行政委员会": "大柴旦",
    "河南蒙古族自治县": "河南县",
    "大通回族土族自治县": "大通县",
    # 贵州省
    "镇宁布依族苗族自治县": "镇宁县",
    "关岭布依族苗族自治县": "关岭县",
    "紫云苗族布依族自治县": "紫云县",
    "威宁彝族回族苗族自治县": "威宁县",
    "三都水族自治县": "三都县",
    "松桃苗族自治县": "松桃县",
    "沿河土家族自治县": "沿河县",
    "印江土家族苗族自治县": "印江县",
    "玉屏侗族自治县": "玉屏县",
    "道真仡佬族苗族自治县": "道真县",
    "务川仡佬族苗族自治县": "务川县",
    # 甘肃省
    "肃北蒙古族自治县": "肃北县",
    "阿克塞哈萨克族自治县": "阿克塞县",
    "积石山保安族东乡族撒拉族自治县": "积石山县",
    "张家川回族自治县": "张家川",
    "天祝藏族自治县": "天祝县",
    "肃南裕固族自治县": "肃南县",
    # 新疆维吾尔自治区
    "焉耆回族自治县": "焉耆县",
    "木垒哈萨克自治县": "木垒县",
    "巴里坤哈萨克自治县": "巴里坤县",
    "塔什库尔干塔吉克自治县": "塔什库尔干县",
    "和布克赛尔蒙古自治县": "和布克赛尔县",
    "察布查尔锡伯自治县": "察布查尔县",
    # 内蒙古自治区
    "鄂温克族自治旗": "鄂温克旗",
    "莫力达瓦达斡尔族自治旗": "莫力达瓦旗",
    # 吉林省
    "伊通满族自治县": "伊通县",
    "长白朝鲜族自治县": "长白县",
    "前郭尔罗斯蒙古族自治县": "前郭县",
    # 辽宁省
    "岫岩满族自治县": "岫岩县",
    "本溪满族自治县": "本溪县",
    "桓仁满族自治县": "桓仁县",
    "喀喇沁左翼蒙古族自治县": "喀喇沁左翼县",
    "宽甸满族自治县": "宽甸县",
    "清原满族自治县": "清原县",
    "新宾满族自治县": "新宾县",
    "阜新蒙古族自治县": "阜新县",
    # 广西壮族自治区
    "隆林各族自治县": "隆林县",
    "恭城瑶族自治县": "恭城县",
    "龙胜各族自治县": "龙胜县",
    "巴马瑶族自治县": "巴马县",
    "都安瑶族自治县": "都安县",
    "环江毛南族自治县": "环江县",
    "大化瑶族自治县": "大化县",
    "罗城仫佬族自治县": "罗城县",
    "富川瑶族自治县": "富川县",
    "金秀瑶族自治县": "金秀县",
    "融水苗族自治县": "融水县",
    "三江侗族自治县": "三江县",
    # 河北省
    "孟村回族自治县": "孟村县",
    "围场满族蒙古族自治县": "围场县",
    "丰宁满族自治县": "丰宁县",
    "宽城满族自治县": "宽城县",
    "青龙满族自治县": "青龙县",
    "大厂回族自治县": "大厂县",
    # 黑龙江省
    "杜尔伯特蒙古族自治县": "杜尔伯特县",
    # 海南省
    "陵水黎族自治县": "陵水县",
    "乐东黎族自治县": "乐东县",
    "昌江黎族自治县": "昌江县",
    "琼中黎族苗族自治县": "琼中县",
    "保亭黎族苗族自治县": "保亭县",
    "白沙黎族自治县": "白沙县",
    # 湖南省
    "芷江侗族自治县": "芷江县",
    "麻阳苗族自治县": "麻阳县",
    "靖州苗族侗族自治县": "靖州县",
    "新晃侗族自治县": "新晃县",
    "通道侗族自治县": "通道县",
    "城步苗族自治县": "城步县",
    "江华瑶族自治县": "江华县",
    # 四川省
    "峨边彝族自治县": "峨边县",
    "马边彝族自治县": "马边县",
    "木里藏族自治县": "木里县",
    "北川羌族自治县": "北川县",
    # 浙江省
    "景宁畲族自治县": "景宁县",
    # 广东省
    "连南瑶族自治县": "连南县",
    "连山壮族瑶族自治县": "连山县",
    "乳源瑶族自治县": "乳源县",
    # 湖北省
    "长阳土家族自治县": "长阳县",
    "五峰土家族自治县": "五峰县",
    # 重庆市
    "秀山土家族苗族自治县": "秀山县",
    "彭水苗族土家族自治县": "彭水县",
    "酉阳土家族苗族自治县": "酉阳县",
    "石柱土家族自治县": "石柱县",
}


class PlotMap(Plot):
    """中国地图热力图绘制类

    支持三个层级的热力图绘制：
    - 省级：全国范围的省级行政区划热力图
    - 地级市：指定省份的地级市热力图
    - 区县：指定地级市的区县热力图

    数据要求：
    - 省级/地级市：DataFrame 的索引应为行政区划名称（如"北京"、"上海"、"昆明市"等）
    - 区县层级：由于区县名有重复，必须提供省市区县四级数据
      - 方式1（推荐）：提供 province_column, city_column, county_column 三列
      - 方式2（兼容）：仅提供 region_column（区县名），但可能匹配错误
    - 至少包含一列数值数据用于热力图着色

    特殊处理：
    - 东莞、中山、嘉峪关、儋州这4个地级市无下属区县，会自动降级为地级市显示

    示例：
        >>> # 省级热力图
        >>> f = plt.figure(FigureClass=GridFigure)
        >>> f.plot(kind='map', data=df, value_column='GDP', level='province')

        >>> # 地级市热力图
        >>> f.plot(kind='map', data=df, value_column='人口',
        ...        level='prefecture', province='云南')

        >>> # 区县热力图（推荐：使用省市区县四级匹配）
        >>> f.plot(kind='map', data=df, value_column='销售额',
        ...        level='county', scope='cities', regions=['昆明市'],
        ...        province_column='省份', city_column='地级市', county_column='区县')
    """

    def __init__(
        self,
        data: pd.DataFrame,
        ax: Optional[mpl.axes.Axes] = None,
        fontsize: int = 14,
        fmt: str = "{:,.0f}",
        style: Dict[str, Any] = {},
        color_dict: Optional[Dict[str, str]] = None,
        cmap_qual: Optional[mpl.colors.Colormap] = None,
        cmap_norm: Optional[mpl.colors.Colormap] = None,
        hue: Optional[str] = None,
        focus: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            data=data,
            ax=ax,
            fontsize=fontsize,
            fmt=fmt,
            style=style,
            color_dict=color_dict,
            cmap_qual=cmap_qual,
            cmap_norm=cmap_norm,
            hue=hue,
            focus=focus,
            *args,
            **kwargs,
        )

        # 地图数据缓存
        self.map_data = None
        self.map_data_regional = None
        self.plot_data = None
        self.map_level = None
        self.data_mapper = None

    def plot(
        self,
        value_column: Optional[str] = None,
        level: Literal["province", "prefecture", "county"] = "province",
        scope: Literal["national", "provinces", "cities", "counties"] = "national",
        regions: Optional[List[str]] = None,
        exclude_regions: Optional[List[str]] = None,
        region_column: Optional[str] = None,
        province_column: Optional[str] = None,
        city_column: Optional[str] = None,
        county_column: Optional[str] = None,
        label_column: Optional[str] = None,
        label_format: Optional[str] = None,
        label_value_format: str = "{:,.0f}",
        label_fontsize: Optional[float] = None,
        use_abbr: bool = False,
        cmap: str = "PiYG",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        edgecolor: str = "black",
        linewidth: float = 0.5,
        national_border_width: Optional[float] = None,
        province_border_width: Optional[float] = None,
        city_border_width: Optional[float] = None,
        show_colorbar: bool = True,
        dissolve_urban: bool = False,
        shapefile_dir: Optional[str] = None,
        color_mapping: Optional[Dict[str, Any]] = None,
        hatch_mapping: Optional[Dict[str, Any]] = None,
        color_mapping_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> PlotMap:
        """绘制中国地图热力图

        Args:
            value_column: 用于着色的数值列名，如不指定则使用第一列
            level: 数据粒度 ('province'=省级数据, 'prefecture'=地级市数据, 'county'=区县数据)
            scope: 地图范围 ('national'=全国, 'provinces'=指定省份集合,
                          'cities'=指定地级市集合, 'counties'=指定区县集合)
            regions: 指定区域列表（当 scope 不为 'national' 时使用）
                    例如：['云南省', '四川省'] 或 ['昆明市', '成都市']
            exclude_regions: 排除的区域列表（全国省级地图时默认自动排除三沙市以避免地图变形，
                           展示海南省或三沙市本身时会保留）
            region_column: 数据中的行政区划列名，如不指定则使用索引
                          （区县层级时，如果提供了 province_column/city_column/county_column，
                          则 region_column 可省略）
            province_column: 省级数据列名（仅 level='county' 时使用，用于省市区县四级匹配）
            city_column: 地级市数据列名（仅 level='county' 时使用，用于省市区县四级匹配）
            county_column: 区县数据列名（仅 level='county' 时使用，用于省市区县四级匹配）
                         如果未指定，则使用 region_column 作为区县列
            label_column: 用于标注的列名（可选）
            label_format: 标签格式化字符串，支持占位符：
                         {index} - 区域名称
                         {value} - label_column的值（已格式化）
                         例如："{index}\n{value}"
                         如不指定，直接显示label_column的值
            label_value_format: 数值格式化字符串，用于格式化 {value} 占位符
                               默认 "{:,.0f}" (千分位分隔的整数)
                               例如："{:.1f}" (一位小数), "{:,.2f}" (千分位+两位小数)
            label_fontsize: 标签字体大小（可选，默认根据层级自动调整）
                         例如："{index}\n{value}" 显示区域名和数值
                         如不指定，直接显示label_column的值
            label_fontsize: 标签字体大小，如不指定则根据层级自动调整
            use_abbr: 是否在标签中使用简称（True=显示简称，False=显示全称）
                     简称包括省/市/县的缩写形式，例如"琼中黎族苗族自治县"显示为"琼中县"
            cmap: colormap 名称
            vmin: 颜色范围最小值
            vmax: 颜色范围最大值
            edgecolor: 边界颜色
            linewidth: 边界线宽（基础线宽，用于区县边界等）
            national_border_width: 国界线宽（如不指定则使用 linewidth）
            province_border_width: 省界线宽（如不指定则使用 linewidth）
            city_border_width: 地级市边界线宽（如不指定则使用 linewidth）
            show_colorbar: 是否显示颜色条
            dissolve_urban: 是否合并市区轮廓（仅 county 层级且 scope='cities' 时有效）
            shapefile_dir: shapefile 文件目录，默认为项目 data/map 目录
            color_mapping: 分类映射字典，格式为 {值: 颜色}，如 {"自营": "#FF0000", "招商": "#0000FF"}
                         如果提供此参数，将使用分类映射而不是 colormap
                         数值列的值如果匹配上映射中的键，则显示对应颜色；否则不上色（透明）
                         支持向后兼容：如果值是字典格式 {color: string}，会提取 color 字段
            **kwargs: 其他样式参数

        Returns:
            self: 返回实例以支持方法链

        示例：
            >>> # 全国省级热力图
            >>> f.plot(kind='map', data=df, level='province', scope='national')

            >>> # 全国地级市热力图
            >>> f.plot(kind='map', data=df, level='prefecture', scope='national')

            >>> # 指定省份的地级市热力图
            >>> f.plot(kind='map', data=df, level='prefecture',
            ...        scope='provinces', regions=['云南省', '四川省'])

            >>> # 指定地级市的区县热力图
            >>> f.plot(kind='map', data=df, level='county',
            ...        scope='cities', regions=['昆明市', '成都市'])
        """

        # 默认排除三沙市（避免南海区域导致地图变形）
        if exclude_regions is None:
            exclude_regions = ["三沙市"]

        # 确定默认值
        if value_column is None:
            value_column = self.data.columns[0]

        # 处理区县层级的省市区县列
        if level == "county":
            # 区县层级：检查是否提供了省市区县列
            if province_column or city_column or county_column:
                # 使用省市区县四级匹配
                plot_data = self.data.copy()
                # 如果未指定 county_column，使用 region_column 或默认列名
                if county_column is None:
                    if region_column is None:
                        region_column = self.data.index.name or "county"
                        plot_data = self.data.reset_index()
                        plot_data.rename(
                            columns={plot_data.columns[0]: region_column}, inplace=True
                        )
                    county_column = region_column
            else:
                # 兼容旧方式：只使用 region_column
                if region_column is None:
                    region_column = self.data.index.name or "region"
                    plot_data = self.data.reset_index()
                    plot_data.rename(
                        columns={plot_data.columns[0]: region_column}, inplace=True
                    )
                else:
                    plot_data = self.data.copy()
        else:
            # 省级或地级市层级：使用 region_column
            if region_column is None:
                region_column = self.data.index.name or "region"
                plot_data = self.data.reset_index()
                plot_data.rename(
                    columns={plot_data.columns[0]: region_column}, inplace=True
                )
            else:
                plot_data = self.data.copy()

        # 加载 shapefile
        self._load_shapefile(level, shapefile_dir)

        # 准备数据（筛选范围）
        self._prepare_data(
            plot_data,
            region_column,
            scope,
            regions,
            exclude_regions,
            province_column,
            city_column,
            county_column,
        )

        # 检查合并后的数据是否为空
        if self.plot_data.empty:
            raise ValueError(
                "合并后的数据为空。请检查：\n"
                "1. 数据中的省市区县名称是否与地图数据匹配\n"
                "2. 选择的区域范围是否正确\n"
                "3. 省市区县列名是否正确"
            )

        # 验证 value_column 是否存在
        if value_column not in self.plot_data.columns:
            raise ValueError(
                f"数值列 '{value_column}' 在合并后的数据中不存在。\n"
                f"可用列: {list(self.plot_data.columns)}\n"
                f"请检查数据列名是否正确，或者是否在合并过程中丢失。"
            )

        # 过滤掉 value_column 为 NaN 的行（只保留有数据的区域）
        initial_count = len(self.plot_data)
        self.plot_data = self.plot_data[self.plot_data[value_column].notna()].copy()

        if self.plot_data.empty:
            raise ValueError(
                f"所有区域的数值列 '{value_column}' 都是 NaN。\n"
                "请检查数据是否正确匹配。"
            )

        if len(self.plot_data) < initial_count:
            # 有部分区域没有数据，这是正常的（只显示有数据的区域）
            pass

        # 设置边界线宽（如未指定则使用基础线宽）
        if national_border_width is None:
            national_border_width = linewidth
        if province_border_width is None:
            province_border_width = linewidth
        if city_border_width is None:
            city_border_width = linewidth

        # 绘制底图
        self._plot_base_map(edgecolor=edgecolor, linewidth=linewidth)

        # 判断是否使用分类映射
        # 如果明确指定了 color_mapping_mode == "categorical"，即使 color_mapping 为空也使用分类映射模式
        # 这种情况下所有区域都会显示透明（"none"）
        if color_mapping_mode == "categorical":
            use_categorical = True
            # 如果 color_mapping 为空，设置为空字典
            if color_mapping is None:
                color_mapping = {}
        else:
            # 否则，只有当 color_mapping 不为空时才使用分类映射
            use_categorical = color_mapping is not None and len(color_mapping) > 0

        # 判断是否使用纹理映射
        use_hatch_mapping = hatch_mapping is not None and len(hatch_mapping) > 0

        # 准备纹理参数（如果使用纹理映射）
        # 为每个区域计算 hatch_str 和 hatch_color，添加到临时列中
        if use_hatch_mapping and value_column and hatch_mapping:
            hatch_strs = []
            hatch_colors_list = []

            for idx, row in self.plot_data.iterrows():
                value = row[value_column]

                # 处理 NaN 和 None 值
                try:
                    is_na = pd.isna(value)
                    # 确保 is_na 是布尔值，而不是数组
                    if isinstance(is_na, (pd.Series, pd.DataFrame, np.ndarray)):
                        is_na = bool(
                            is_na.any() if hasattr(is_na, "any") else bool(is_na)
                        )
                    elif not isinstance(is_na, bool):
                        is_na = bool(is_na)
                except (TypeError, ValueError):
                    is_na = value is None

                # 确保 value is None 的判断不会与数组产生冲突
                value_is_none = value is None
                if is_na or value_is_none:
                    hatch_str = ""  # 默认无纹理
                    hatch_color = edgecolor  # 默认使用边界颜色
                else:
                    # 尝试多种匹配方式以提高匹配成功率
                    value_str = (
                        str(value).strip() if isinstance(value, str) else str(value)
                    )

                    # 先尝试精确匹配（去除空格后的字符串）
                    mapping = hatch_mapping.get(value_str, None)

                    # 如果精确匹配失败，尝试匹配原始值（如果是字符串类型）
                    if mapping is None and isinstance(value, str):
                        mapping = hatch_mapping.get(value, None)

                    # 如果还是失败，尝试匹配去除空格后的值
                    if mapping is None and isinstance(value, str):
                        mapping = hatch_mapping.get(value.strip(), None)

                    # 应用纹理映射
                    if mapping is not None:
                        # 提取纹理参数
                        if isinstance(mapping, dict):
                            hatch_pattern = mapping.get("hatch", "")
                            density = mapping.get("density", 5)
                            hatch_color = mapping.get("color", edgecolor)
                        else:
                            # 向后兼容：如果是字符串，当作 hatch 模式
                            hatch_pattern = mapping
                            density = 5
                            hatch_color = edgecolor

                        # 根据密度生成 hatch 字符串（重复 hatch 模式）
                        hatch_str = hatch_pattern * max(1, int(density))
                    else:
                        hatch_str = ""  # 默认无纹理
                        hatch_color = edgecolor  # 默认使用边界颜色

                hatch_strs.append(hatch_str)
                hatch_colors_list.append(hatch_color)

            # 将 hatch 信息添加到 plot_data 的临时列中
            self.plot_data["_hatch_str"] = hatch_strs
            self.plot_data["_hatch_color"] = hatch_colors_list

        if use_categorical:
            # 分类映射模式：为每个区域根据值查找对应颜色
            # 创建一个颜色列表，用于存储每个区域的颜色
            colors = []
            for idx, row in self.plot_data.iterrows():
                value = row[value_column]

                # 处理 NaN 和 None 值
                try:
                    is_na = pd.isna(value)
                    # 确保 is_na 是布尔值，而不是数组
                    if isinstance(is_na, (pd.Series, pd.DataFrame, np.ndarray)):
                        is_na = bool(
                            is_na.any() if hasattr(is_na, "any") else bool(is_na)
                        )
                    elif not isinstance(is_na, bool):
                        is_na = bool(is_na)
                except (TypeError, ValueError):
                    is_na = value is None

                # 确保 value is None 的判断不会与数组产生冲突
                value_is_none = value is None
                if is_na or value_is_none:
                    color = None
                else:
                    # 尝试多种匹配方式以提高匹配成功率
                    # 1. 直接使用原始值（如果是字符串）
                    # 2. 转换为字符串
                    # 3. 去除首尾空格（如果是字符串）
                    value_str = (
                        str(value).strip() if isinstance(value, str) else str(value)
                    )

                    # 先尝试精确匹配（去除空格后的字符串）
                    mapping = color_mapping.get(value_str, None)

                    # 如果精确匹配失败，尝试匹配原始值（如果是字符串类型）
                    if mapping is None and isinstance(value, str):
                        mapping = color_mapping.get(value, None)

                    # 如果还是失败，尝试匹配去除空格后的值（再次尝试，以防万一）
                    if mapping is None and isinstance(value, str):
                        mapping = color_mapping.get(value.strip(), None)

                    # 处理映射值：支持字符串格式（颜色）和字典格式（向后兼容）
                    if mapping is not None:
                        if isinstance(mapping, dict):
                            # 字典格式：提取 color（忽略其他字段）
                            color = mapping.get("color", None)
                        else:
                            # 字符串格式：直接是颜色
                            color = mapping
                    else:
                        color = None

                colors.append(color if color else "none")  # None 转换为 "none"（透明）

            # 将颜色添加到 plot_data 的临时列中
            self.plot_data["_color"] = colors

            # 如果使用纹理映射，按 hatch 分组绘制
            if use_hatch_mapping and "_hatch_str" in self.plot_data.columns:
                # 按 hatch_str 分组
                for hatch_str, group_data in self.plot_data.groupby("_hatch_str"):
                    # 获取该组的颜色列表
                    group_colors = group_data["_color"].tolist()
                    # 获取该组的 hatch_color（用于 edgecolor）
                    group_hatch_colors = (
                        group_data["_hatch_color"].tolist()
                        if "_hatch_color" in group_data.columns
                        else [edgecolor] * len(group_data)
                    )

                    # 绘制该组数据
                    plot_kwargs = {
                        "ax": self.ax,
                        "color": group_colors,
                        "edgecolor": (
                            group_hatch_colors[0] if group_hatch_colors else edgecolor
                        ),  # 使用第一个 hatch_color 作为 edgecolor
                        "linewidth": linewidth,
                        "legend": False,
                    }

                    # 如果 hatch_str 不为空，添加 hatch 参数
                    if hatch_str:
                        plot_kwargs["hatch"] = hatch_str

                    group_data.plot(**plot_kwargs)

                    # 如果该组有多个不同的 hatch_color，需要单独设置每个 patch 的 edgecolor
                    if len(set(group_hatch_colors)) > 1:
                        patches = self.ax.patches
                        patches_before = len(patches) - len(group_data)
                        for i, hatch_color in enumerate(group_hatch_colors):
                            patch_idx = patches_before + i
                            if patch_idx < len(patches):
                                patches[patch_idx].set_edgecolor(hatch_color)
            else:
                # 不使用纹理映射，直接绘制
                plot_kwargs = {
                    "ax": self.ax,
                    "color": colors,
                    "edgecolor": edgecolor,
                    "linewidth": linewidth,
                    "legend": False,
                }
                self.plot_data.plot(**plot_kwargs)
        else:
            # Colormap 模式：使用原有的颜色渐变方案
            # 如果使用纹理映射，按 hatch 分组绘制
            if use_hatch_mapping and "_hatch_str" in self.plot_data.columns:
                # 按 hatch_str 分组
                for hatch_str, group_data in self.plot_data.groupby("_hatch_str"):
                    # 获取该组的 hatch_color（用于 edgecolor）
                    group_hatch_colors = (
                        group_data["_hatch_color"].tolist()
                        if "_hatch_color" in group_data.columns
                        else [edgecolor] * len(group_data)
                    )

                    # 绘制该组数据
                    plot_kwargs = {
                        "column": value_column,
                        "cmap": cmap,
                        "legend": (
                            show_colorbar
                            if hatch_str == self.plot_data["_hatch_str"].iloc[0]
                            else False
                        ),  # 只在第一组显示 colorbar
                        "ax": self.ax,
                        "edgecolor": (
                            group_hatch_colors[0] if group_hatch_colors else edgecolor
                        ),  # 使用第一个 hatch_color 作为 edgecolor
                        "linewidth": linewidth,
                        "vmin": vmin,
                        "vmax": vmax,
                    }

                    # 如果 hatch_str 不为空，添加 hatch 参数
                    if hatch_str:
                        plot_kwargs["hatch"] = hatch_str

                    group_data.plot(**plot_kwargs)

                    # 如果该组有多个不同的 hatch_color，需要单独设置每个 patch 的 edgecolor
                    if len(set(group_hatch_colors)) > 1:
                        patches = self.ax.patches
                        patches_before = len(patches) - len(group_data)
                        for i, hatch_color in enumerate(group_hatch_colors):
                            patch_idx = patches_before + i
                            if patch_idx < len(patches):
                                patches[patch_idx].set_edgecolor(hatch_color)

                # 格式化 colorbar 刻度标签（使用与数据标签相同的格式）
                if show_colorbar:
                    self._format_colorbar(label_value_format)
            else:
                # 不使用纹理映射，直接绘制
                plot_kwargs = {
                    "column": value_column,
                    "cmap": cmap,
                    "legend": show_colorbar,
                    "ax": self.ax,
                    "edgecolor": edgecolor,
                    "linewidth": linewidth,
                    "vmin": vmin,
                    "vmax": vmax,
                }
                self.plot_data.plot(**plot_kwargs)

                # 格式化 colorbar 刻度标签（使用与数据标签相同的格式）
                if show_colorbar:
                    self._format_colorbar(label_value_format)

        # 绘制不同层级的边界
        self._draw_hierarchical_borders(
            level=level,
            scope=scope,
            edgecolor=edgecolor,
            national_border_width=national_border_width,
            province_border_width=province_border_width,
            city_border_width=city_border_width,
        )

        # 特殊处理：区县层级的地级市轮廓
        if level == "county" and scope == "cities":
            if dissolve_urban:
                self._highlight_urban_area()

        # 添加标签
        if label_column:
            # 如果未指定 label_format，默认使用 '{index}'（与前端一致）
            if label_format is None:
                label_format = "{index}"

            self._add_labels(
                label_column,
                level,
                label_format,
                label_value_format,
                label_fontsize,
                use_abbr,
            )

        # 清理临时列
        if hasattr(self.plot_data, "columns"):
            columns_to_drop = []
            if "_hatch_str" in self.plot_data.columns:
                columns_to_drop.append("_hatch_str")
            if "_hatch_color" in self.plot_data.columns:
                columns_to_drop.append("_hatch_color")
            if "_color" in self.plot_data.columns:
                columns_to_drop.append("_color")
            if columns_to_drop:
                self.plot_data.drop(columns=columns_to_drop, inplace=True)

        # 应用样式
        self.apply_style()

        return self

    def _load_shapefile(self, level: str, shapefile_dir: Optional[str] = None) -> None:
        """加载对应层级的 shapefile

        Args:
            level: 地图层级
            shapefile_dir: shapefile 目录路径
        """
        if shapefile_dir is None:
            # 默认使用项目的 data/map 目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            shapefile_dir = os.path.join(project_root, "data", "map")

        # 根据层级选择文件
        level_map = {
            "province": "省级/2024年省级.shp",
            "prefecture": "地级/T2024年初地级.shp",
            "county": "县级/T2024年初县级.shp",
        }

        shapefile_path = os.path.join(shapefile_dir, level_map[level])

        # 标准化路径以避免兼容性问题
        shapefile_path = os.path.normpath(os.path.abspath(shapefile_path))

        if not os.path.exists(shapefile_path):
            raise FileNotFoundError(
                f"Shapefile 未找到: {shapefile_path}\n"
                f"请确保地图数据文件存在于 {shapefile_dir}"
            )

        # 使用标准化的路径读取 shapefile
        self.map_data = gpd.read_file(shapefile_path, encoding="utf-8")

        # 转换到适合中国的投影坐标系（EPSG:2343 - Pulkovo 1942 / 3-degree Gauss-Kruger CM 120E）
        # 这样可以避免地图变形，保持正确的地理比例
        if self.map_data.crs is not None:
            self.map_data = self.map_data.to_crs(epsg=2343)

        self.map_level = level

        # 设置数据映射字段（根据不同层级使用不同的列名）
        if level == "province":
            self.data_mapper = "省"  # 省级 shapefile 使用 '省' 列
        elif level == "prefecture":
            self.data_mapper = "地名"  # 地级市 shapefile 使用 '地名' 列
            # 地级市 shapefile 中的 '省级' 列已经是完整名称（如"云南省"），无需映射
            if "省级" in self.map_data.columns:
                self.map_data["省份"] = self.map_data["省级"]
            # 过滤三沙市（默认在 _prepare_data 中处理）
        elif level == "county":
            self.data_mapper = "地名"  # 区县 shapefile 使用 '地名' 列
            # 区县 shapefile 中的 '省级' 列已经是完整名称（如"云南省"），无需映射
            if "省级" in self.map_data.columns:
                self.map_data["省份"] = self.map_data["省级"]
            # 处理直辖县级行政区划
            for prov in ["湖北省", "海南省", "河南省", "新疆维吾尔自治区"]:
                mask = (self.map_data["地级"] == "不统计") & (
                    self.map_data["省份"] == prov
                )
                prov_short = prov.replace("省", "").replace("维吾尔自治区", "")
                if prov == "新疆维吾尔自治区":
                    self.map_data.loc[mask, "地级"] = (
                        f"{prov_short}自治区直辖县级行政区划"
                    )
                else:
                    self.map_data.loc[mask, "地级"] = f"{prov_short}省直辖县级行政区划"

    def _prepare_data(
        self,
        data: pd.DataFrame,
        region_column: str,
        scope: str = "national",
        regions: Optional[List[str]] = None,
        exclude_regions: Optional[List[str]] = None,
        province_column: Optional[str] = None,
        city_column: Optional[str] = None,
        county_column: Optional[str] = None,
    ) -> None:
        """准备绘图数据

        Args:
            data: 包含行政区划和数值的数据
            region_column: 行政区划列名
            scope: 地图范围类型
            regions: 指定区域列表
            exclude_regions: 排除的区域列表
            province_column: 省级数据列名（仅 level='county' 时使用）
            city_column: 地级市数据列名（仅 level='county' 时使用）
            county_column: 区县数据列名（仅 level='county' 时使用）
        """
        # 保存scope参数，用于后续边界设置
        self.map_scope = scope
        # 归一化区域名称（根据 scope 而不是 level）
        if regions is not None:
            normalized_regions = []
            for region in regions:
                if scope == "provinces":
                    # 省份范围：使用省份映射
                    normalized_regions.append(PROVINCE_NAME_MAP.get(region, region))
                elif scope in ["cities", "counties"]:
                    # 城市/区县范围：使用城市映射
                    normalized_regions.append(CITY_NAME_MAP.get(region, region))
                else:  # national
                    normalized_regions.append(region)
            regions = normalized_regions

        if exclude_regions is not None:
            normalized_exclude = []
            for region in exclude_regions:
                # exclude_regions 根据 level 映射
                if self.map_level == "province":
                    normalized_exclude.append(PROVINCE_NAME_MAP.get(region, region))
                else:
                    normalized_exclude.append(CITY_NAME_MAP.get(region, region))
            exclude_regions = normalized_exclude

        # 归一化用户数据的区域名称
        normalized_data = data.copy()

        # 处理无下属区县的地级市：检测并降级处理
        cities_without_counties_normalized = [
            CITY_NAME_MAP.get(city, city) for city in CITIES_WITHOUT_COUNTIES
        ]

        if self.map_level == "province":
            # 省级数据：使用PROVINCE_NAME_MAP归一化
            normalized_data[region_column] = normalized_data[region_column].map(
                lambda x: PROVINCE_NAME_MAP.get(x, x)
            )
        elif self.map_level == "county" and (
            province_column or city_column or county_column
        ):
            # 区县数据：使用省市区县四级匹配
            # 归一化省市区县列
            if province_column and province_column in normalized_data.columns:
                normalized_data[province_column] = normalized_data[province_column].map(
                    lambda x: PROVINCE_NAME_MAP.get(x, x)
                )
            if city_column and city_column in normalized_data.columns:
                normalized_data[city_column] = normalized_data[city_column].map(
                    lambda x: CITY_NAME_MAP.get(x, x)
                )
            if county_column and county_column in normalized_data.columns:
                # 区县名不需要映射，直接使用
                pass
        else:
            # 地级市数据或区县数据（旧方式）：使用CITY_NAME_MAP归一化
            normalized_data[region_column] = normalized_data[region_column].map(
                lambda x: CITY_NAME_MAP.get(x, x)
            )

        # 根据 scope 筛选地图数据
        self.map_data_regional = self.map_data.copy()

        if scope == "national":
            # 全国范围：仅排除 exclude_regions
            # 自动排除三沙市（除非用户明确要求保留）
            if exclude_regions is None:
                exclude_regions = ["三沙市"]

            if exclude_regions:
                self.map_data_regional = self.map_data_regional[
                    ~self.map_data_regional[self.data_mapper].isin(exclude_regions)
                ].copy()

        elif scope == "provinces":
            # 指定省份范围
            if not regions:
                raise ValueError("scope='provinces' 时必须指定 regions 参数")

            if self.map_level == "province":
                # 省级数据：直接筛选省份
                self.map_data_regional = self.map_data_regional[
                    self.map_data_regional["省"].isin(regions)
                ].copy()

                # 三沙市处理：只在展示海南省或三沙市自身时保留
                has_hainan = any(r in ["海南省", "海南"] for r in regions)
                has_sansha = any(r in ["三沙市", "三沙"] for r in regions)
                if not has_hainan and not has_sansha:
                    # 既不展示海南也不展示三沙，排除三沙市
                    self.map_data_regional = self.map_data_regional[
                        self.map_data_regional["省"] != "三沙市"
                    ].copy()
            else:
                # 地级市/区县数据：根据省份筛选
                # 优先使用"省级"列，其次使用"省份"列
                prov_col = (
                    "省级" if "省级" in self.map_data_regional.columns else "省份"
                )
                if prov_col not in self.map_data_regional.columns:
                    raise ValueError(f"{self.map_level} 层级数据缺少省份列")

                self.map_data_regional = self.map_data_regional[
                    self.map_data_regional[prov_col].isin(regions)
                ].copy()

        elif scope == "cities":
            # 指定地级市范围
            if not regions:
                raise ValueError("scope='cities' 时必须指定 regions 参数")

            if self.map_level == "province":
                raise ValueError("省级数据 (level='province') 不支持 scope='cities'")
            elif self.map_level == "prefecture":
                # 地级市数据：直接筛选
                self.map_data_regional = self.map_data_regional[
                    self.map_data_regional["地名"].isin(regions)
                ].copy()
            else:  # county
                # 区县数据：根据地级市筛选
                if "地级" not in self.map_data_regional.columns:
                    raise ValueError("县级数据缺少地级市列")

                # 检查是否有无下属区县的地级市
                cities_without_counties_normalized = [
                    CITY_NAME_MAP.get(city, city) for city in CITIES_WITHOUT_COUNTIES
                ]
                regions_normalized = [
                    CITY_NAME_MAP.get(region, region) for region in regions
                ]
                cities_without_counties_in_regions = [
                    city
                    for city in regions_normalized
                    if city in cities_without_counties_normalized
                ]

                # 筛选有区县的地级市
                if cities_without_counties_in_regions:
                    # 分离有区县和无区县的地级市
                    cities_with_counties = [
                        city
                        for city in regions_normalized
                        if city not in cities_without_counties_normalized
                    ]
                    if cities_with_counties:
                        # 只筛选有区县的地级市
                        self.map_data_regional = self.map_data_regional[
                            self.map_data_regional["地级"].isin(cities_with_counties)
                        ].copy()
                    else:
                        # 如果所有选择的地级市都无区县，map_data_regional为空
                        # 后续会在合并数据时处理
                        self.map_data_regional = self.map_data_regional[
                            self.map_data_regional["地级"].isin([])
                        ].copy()
                else:
                    # 所有地级市都有区县，正常筛选
                    self.map_data_regional = self.map_data_regional[
                        self.map_data_regional["地级"].isin(regions_normalized)
                    ].copy()

        elif scope == "counties":
            # 指定区县范围
            if not regions:
                raise ValueError("scope='counties' 时必须指定 regions 参数")

            if self.map_level != "county":
                raise ValueError("只有区县数据 (level='county') 支持 scope='counties'")

            self.map_data_regional = self.map_data_regional[
                self.map_data_regional["地名"].isin(regions)
            ].copy()

        # 应用排除列表（仅在全国范围时自动排除）
        # 在其他scope中，用户已经明确指定了区域，不应自动排除
        # 如果用户需要排除某些区域，可以在regions参数中不包含它们

        # 合并用户数据和地图数据
        if (
            self.map_level == "county"
            and province_column
            and city_column
            and county_column
            and province_column in normalized_data.columns
            and city_column in normalized_data.columns
            and county_column in normalized_data.columns
        ):
            # 区县层级：使用省市区县四级匹配
            # 检查是否有无下属区县的地级市
            cities_in_data = normalized_data[city_column].unique()
            cities_without_counties_in_data = [
                city
                for city in cities_in_data
                if city in cities_without_counties_normalized
            ]

            if cities_without_counties_in_data:
                # 分离有区县的地级市和无区县的地级市
                data_with_counties = normalized_data[
                    ~normalized_data[city_column].isin(cities_without_counties_in_data)
                ].copy()
                data_without_counties = normalized_data[
                    normalized_data[city_column].isin(cities_without_counties_in_data)
                ].copy()

                # 如果 scope == "provinces"，需要根据省份范围过滤无区县的地级市数据
                if (
                    scope == "provinces"
                    and regions
                    and province_column in normalized_data.columns
                ):
                    # 只保留属于选择省份的这些城市
                    data_without_counties = data_without_counties[
                        data_without_counties[province_column].isin(regions)
                    ].copy()

                # 有区县的地级市：使用省市区县四级匹配
                plot_data_with_counties = None
                if not data_with_counties.empty:
                    # 处理直辖市：直辖市的省份和地级市名称相同
                    municipalities = ["北京市", "天津市", "上海市", "重庆市"]
                    is_municipality = data_with_counties[province_column].isin(
                        municipalities
                    ) & (
                        data_with_counties[province_column]
                        == data_with_counties[city_column]
                    )
                    municipalities_data = data_with_counties[is_municipality].copy()
                    non_municipalities_data = data_with_counties[
                        ~is_municipality
                    ].copy()

                    plot_data_list = []

                    # 非直辖市：使用标准匹配
                    if not non_municipalities_data.empty:
                        plot_data_non_municipality = self.map_data_regional.merge(
                            non_municipalities_data,
                            left_on=["省份", "地级", "地名"],
                            right_on=[province_column, city_column, county_column],
                            how="inner",
                        )
                        if not plot_data_non_municipality.empty:
                            plot_data_list.append(plot_data_non_municipality)

                    # 直辖市：尝试多种匹配方式
                    if not municipalities_data.empty:
                        map_data_municipality = self.map_data_regional[
                            self.map_data_regional["省份"].isin(municipalities)
                        ].copy()

                        # 方式1：标准匹配
                        plot_data_municipality_1 = map_data_municipality.merge(
                            municipalities_data,
                            left_on=["省份", "地级", "地名"],
                            right_on=[province_column, city_column, county_column],
                            how="inner",
                        )

                        if not plot_data_municipality_1.empty:
                            plot_data_list.append(plot_data_municipality_1)
                        else:
                            # 方式2：只匹配省份和区县（忽略地级列）
                            plot_data_municipality_2 = map_data_municipality.merge(
                                municipalities_data,
                                left_on=["省份", "地名"],
                                right_on=[province_column, county_column],
                                how="inner",
                            )
                            if not plot_data_municipality_2.empty:
                                plot_data_list.append(plot_data_municipality_2)

                    # 合并所有匹配结果
                    if plot_data_list:
                        plot_data_with_counties = pd.concat(
                            plot_data_list, ignore_index=True
                        )

                # 无区县的地级市：降级为地级市显示
                # 需要加载地级市 shapefile 来显示这些城市
                plot_data_without_counties = None
                if not data_without_counties.empty:
                    # 对于无下属区县的地级市，如果有多条记录，只取第一条
                    # （因为这些城市实际上没有区县，多条记录可能是错误数据）
                    data_without_counties_dedup = (
                        data_without_counties.groupby(city_column).first().reset_index()
                    )

                    # 临时加载地级市 shapefile
                    project_root = os.path.dirname(
                        os.path.dirname(os.path.dirname(__file__))
                    )
                    shapefile_dir = os.path.join(project_root, "data", "map")
                    prefecture_shapefile = os.path.join(
                        shapefile_dir, "地级/T2024年初地级.shp"
                    )
                    if os.path.exists(prefecture_shapefile):
                        prefecture_data = gpd.read_file(
                            prefecture_shapefile, encoding="utf-8"
                        )
                        if prefecture_data.crs is not None:
                            prefecture_data = prefecture_data.to_crs(epsg=2343)

                        # 筛选无区县的地级市
                        prefecture_data_filtered = prefecture_data[
                            prefecture_data["地名"].isin(
                                cities_without_counties_in_data
                            )
                        ].copy()

                        # 根据当前范围（scope）进一步筛选
                        if scope == "provinces" and regions:
                            # 省份范围：只显示属于选择省份的这些城市
                            prov_col = (
                                "省级"
                                if "省级" in prefecture_data_filtered.columns
                                else "省份"
                            )
                            if prov_col in prefecture_data_filtered.columns:
                                prefecture_data_filtered = prefecture_data_filtered[
                                    prefecture_data_filtered[prov_col].isin(regions)
                                ].copy()
                        elif scope == "cities" and regions:
                            # 城市范围：只显示在regions中的这些城市
                            regions_normalized = [
                                CITY_NAME_MAP.get(region, region) for region in regions
                            ]
                            prefecture_data_filtered = prefecture_data_filtered[
                                prefecture_data_filtered["地名"].isin(
                                    regions_normalized
                                )
                            ].copy()
                        # scope == "national" 或 "counties" 时，显示所有匹配的城市

                        # 合并数据（使用地级市名称匹配）
                        plot_data_without_counties = prefecture_data_filtered.merge(
                            data_without_counties_dedup,
                            left_on="地名",
                            right_on=city_column,
                            how="inner",  # 只保留有匹配数据的区域
                        )

                # 合并两部分数据
                if (
                    plot_data_with_counties is not None
                    and not plot_data_with_counties.empty
                ):
                    if (
                        plot_data_without_counties is not None
                        and not plot_data_without_counties.empty
                    ):
                        self.plot_data = pd.concat(
                            [plot_data_with_counties, plot_data_without_counties],
                            ignore_index=True,
                        )
                    else:
                        self.plot_data = plot_data_with_counties
                elif (
                    plot_data_without_counties is not None
                    and not plot_data_without_counties.empty
                ):
                    self.plot_data = plot_data_without_counties
                else:
                    # 如果两部分都为空，使用空数据
                    self.plot_data = self.map_data_regional.copy()
            else:
                # 所有地级市都有区县，使用省市区县四级匹配
                # 处理直辖市：直辖市的省份和地级市名称相同
                # 在shapefile中，直辖市的"地级"列可能是省份名称或其他值
                # 需要特殊处理

                municipalities = ["北京市", "天津市", "上海市", "重庆市"]

                # 分离直辖市数据和非直辖市数据
                is_municipality = normalized_data[province_column].isin(
                    municipalities
                ) & (normalized_data[province_column] == normalized_data[city_column])
                municipalities_data = normalized_data[is_municipality].copy()
                non_municipalities_data = normalized_data[~is_municipality].copy()

                plot_data_list = []

                # 非直辖市：使用标准匹配（省份、地级、区县）
                if not non_municipalities_data.empty:
                    plot_data_non_municipality = self.map_data_regional.merge(
                        non_municipalities_data,
                        left_on=["省份", "地级", "地名"],
                        right_on=[province_column, city_column, county_column],
                        how="inner",
                    )
                    if not plot_data_non_municipality.empty:
                        plot_data_list.append(plot_data_non_municipality)

                # 直辖市：尝试多种匹配方式
                if not municipalities_data.empty:
                    # 筛选直辖市的区县数据
                    map_data_municipality = self.map_data_regional[
                        self.map_data_regional["省份"].isin(municipalities)
                    ].copy()

                    # 方式1：标准匹配（省份、地级、区县）
                    plot_data_municipality_1 = map_data_municipality.merge(
                        municipalities_data,
                        left_on=["省份", "地级", "地名"],
                        right_on=[province_column, city_column, county_column],
                        how="inner",
                    )

                    if not plot_data_municipality_1.empty:
                        plot_data_list.append(plot_data_municipality_1)
                    else:
                        # 方式2：如果方式1失败，尝试只匹配省份和区县（忽略地级列）
                        # 在shapefile中，直辖市的"地级"列可能不是省份名称
                        plot_data_municipality_2 = map_data_municipality.merge(
                            municipalities_data,
                            left_on=["省份", "地名"],
                            right_on=[province_column, county_column],
                            how="inner",
                        )
                        if not plot_data_municipality_2.empty:
                            plot_data_list.append(plot_data_municipality_2)

                # 合并所有匹配结果
                if plot_data_list:
                    self.plot_data = pd.concat(plot_data_list, ignore_index=True)
                else:
                    # 如果所有匹配都失败，创建空数据
                    self.plot_data = self.map_data_regional.head(0).copy()
        else:
            # 其他情况：使用单列匹配（兼容旧方式）
            self.plot_data = self.map_data_regional.merge(
                normalized_data,
                left_on=self.data_mapper,
                right_on=region_column,
                how="left",
            )

    def _plot_base_map(self, edgecolor: str = "black", linewidth: float = 0.1) -> None:
        """绘制底图边界"""
        self.map_data_regional.boundary.plot(
            ax=self.ax, color=edgecolor, linewidth=linewidth
        )

        # 全国范围地图时，设置边界裁剪南海区域（三沙市）
        # 海南岛最南端约为北纬18度，三沙市主要在北纬4-18度之间
        # 设置南边界为北纬17度，可以保留海南岛主体，排除三沙市
        if hasattr(self, "map_scope") and self.map_scope == "national":
            bounds = self.map_data_regional.total_bounds  # [minx, miny, maxx, maxy]
            # 投影坐标系下，需要转换纬度限制
            # 对于EPSG:2343，大致北纬17度对应的y坐标约为1900000
            # 这里设置一个合理的南边界，保留海南岛主体
            south_limit = 1900000  # 对应约北纬17度
            if bounds[1] < south_limit:  # 如果数据范围超出南边界
                self.ax.set_ylim(bottom=south_limit)

        # 移除坐标轴
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlabel("")
        self.ax.set_ylabel("")

    def _draw_hierarchical_borders(
        self,
        level: str,
        scope: str,
        edgecolor: str,
        national_border_width: float,
        province_border_width: float,
        city_border_width: float,
    ) -> None:
        """绘制不同层级的边界线

        Args:
            level: 数据层级
            scope: 地图范围
            edgecolor: 边界颜色
            national_border_width: 国界线宽
            province_border_width: 省界线宽
            city_border_width: 地级市边界线宽
        """
        # 国界（全国范围时绘制）
        if scope == "national" and national_border_width > 0:
            # 绘制全国外边界
            # 使用 map_data_regional 而不是 plot_data，因为 plot_data 只包含有数据的区域
            # 而国界应该基于完整的地图区域
            national_boundary = self.map_data_regional.geometry.union_all()
            if national_boundary.geom_type == "MultiPolygon":
                for geom in national_boundary.geoms:
                    gpd.GeoSeries([geom]).boundary.plot(
                        ax=self.ax, color=edgecolor, linewidth=national_border_width
                    )
            else:
                gpd.GeoSeries([national_boundary]).boundary.plot(
                    ax=self.ax, color=edgecolor, linewidth=national_border_width
                )

        # 省界
        if province_border_width > 0:
            if level == "province":
                # 省级数据：绘制省边界
                self.plot_data.boundary.plot(
                    ax=self.ax, color=edgecolor, linewidth=province_border_width
                )
            elif level in ["prefecture", "county"]:
                # 地级市/区县数据：按省份分组绘制省界
                prov_col = "省级" if "省级" in self.plot_data.columns else "省份"
                if prov_col in self.plot_data.columns:
                    province_boundaries = self.plot_data.dissolve(by=prov_col).geometry
                    gpd.GeoSeries(province_boundaries).boundary.plot(
                        ax=self.ax, color=edgecolor, linewidth=province_border_width
                    )

        # 市界（地级市层级或区县层级）
        if city_border_width > 0:
            if level == "prefecture":
                # 地级市数据：绘制地级市边界
                self.plot_data.boundary.plot(
                    ax=self.ax, color=edgecolor, linewidth=city_border_width
                )
            elif level == "county" and "地级" in self.plot_data.columns:
                # 区县数据：按地级市分组绘制市界
                city_boundaries = self.plot_data.dissolve(by="地级").geometry
                gpd.GeoSeries(city_boundaries).boundary.plot(
                    ax=self.ax, color=edgecolor, linewidth=city_border_width
                )

    def _dissolve_prefecture(self, edgecolor: str = "black") -> None:
        """绘制地级市轮廓（仅区县层级使用）"""
        # 此方法已被 _draw_hierarchical_borders 替代，保留用于向后兼容
        pass

    def _highlight_urban_area(self) -> None:
        """高亮显示市区（仅区县层级使用）"""
        if self.map_level == "county" and "市区/县域" in self.plot_data.columns:
            urban_areas = self.plot_data[self.plot_data["市区/县域"] == "市区"]
            if not urban_areas.empty:
                urban_area = urban_areas.dissolve(by="地级").geometry.union_all()
                gpd.GeoSeries([urban_area]).plot(
                    ax=self.ax,
                    color="deepskyblue",
                    edgecolor="black",
                    linewidth=0,
                    alpha=0.3,
                )

    def _format_colorbar(self, label_value_format: str = "{:,.0f}") -> None:
        """格式化 colorbar 的刻度标签

        Args:
            label_value_format: 数值格式化字符串（如 '{:,.0f}', '{:.1f}', '{:.2%}' 等）
        """
        # 获取当前 figure 中的所有 axes，找到 colorbar
        for ax in self.ax.figure.get_axes():
            # colorbar 通常是一个独立的 axes
            if ax != self.ax and hasattr(ax, "yaxis"):
                # 获取当前刻度值
                ticklabels = ax.get_yticklabels()
                if ticklabels:
                    # 获取刻度位置（数值）
                    ticks = ax.get_yticks()

                    # 格式化刻度标签
                    formatted_labels = []
                    for tick in ticks:
                        try:
                            # 去掉格式字符串的外层花括号，提取内部格式
                            # '{:,.0f}' -> ':,.0f'
                            format_spec = label_value_format.strip("{}")
                            if format_spec.startswith(":"):
                                format_spec = format_spec[1:]

                            # 使用 Python 格式化
                            formatted = f"{tick:{format_spec}}"
                            formatted_labels.append(formatted)
                        except (ValueError, KeyError):
                            # 格式化失败时保持原样
                            formatted_labels.append(str(tick))

                    # 设置格式化后的标签
                    ax.set_yticklabels(formatted_labels)
                    break

    def _add_labels(
        self,
        label_column: str,
        level: str,
        label_format: str = "{index}",
        label_value_format: str = "{:,.0f}",
        label_fontsize: Optional[float] = None,
        use_abbr: bool = False,
    ) -> None:
        """在地图上添加文字标签

        Args:
            label_column: 标签列名
            level: 地图层级
            label_format: 标签格式化字符串，支持 {index} 和 {value} 占位符（默认 '{index}'）
            label_value_format: 数值格式化字符串
            label_fontsize: 自定义字体大小
            use_abbr: 是否使用简称
        """
        # 字体大小：优先使用自定义值，否则根据层级调整
        if label_fontsize is None:
            fontsize_map = {
                "province": self.fontsize * 0.7,
                "prefecture": self.fontsize * 0.6,
                "county": self.fontsize * 0.5,
            }
            label_fontsize = fontsize_map.get(level, self.fontsize * 0.6)

        for _, row in self.plot_data.iterrows():
            if label_column in row and pd.notna(row[label_column]):
                # 获取区域名称（索引）
                region_name = row.get(self.data_mapper, "")

                # 如果启用简称，去掉省市县等后缀
                if use_abbr and region_name:
                    # 优先查找区县简称
                    if region_name in COUNTY_ABBR_MAP:
                        region_name = COUNTY_ABBR_MAP[region_name]
                    else:
                        # 去除常见后缀，得到简称
                        for suffix in [
                            "省",
                            "市",
                            "自治区",
                            "特别行政区",
                            "壮族自治区",
                            "回族自治区",
                            "维吾尔自治区",
                            "藏族羌族自治州",
                            "藏族自治区",
                            "地区",
                            "盟",
                            "自治州",
                            "自治县",
                        ]:
                            if region_name.endswith(suffix):
                                region_name = region_name[: -len(suffix)]
                                break

                # 格式化数值
                value = row[label_column]
                if isinstance(value, (int, float)):
                    formatted_value = label_value_format.format(value)
                else:
                    formatted_value = str(value)

                # 使用格式化字符串替换占位符
                label = label_format.format(index=region_name, value=formatted_value)

                # 跳过空标签
                if not label or label.strip() == "":
                    continue

                centroid = row.geometry.centroid

                self.ax.text(
                    centroid.x,
                    centroid.y,
                    label,
                    fontsize=label_fontsize,
                    ha="center",
                    va="center",
                )
