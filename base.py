from re import T
from matplotlib import axes
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from matplotlib.gridspec import GridSpec
import os
from numpy.core.arrayprint import str_format
from numpy.lib.function_base import iterable
import pandas as pd
from typing import Union, List
import matplotlib.font_manager as fm
import matplotlib as mpl
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import textwrap
import math
import matplotlib.dates as mdates
import scipy.stats as stats
from adjustText import adjust_text
from itertools import cycle


mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["font.serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams.update({"font.size": 16})
mpl.rcParams["hatch.linewidth"] = 0.5
mpl.rcParams["hatch.color"] = "grey"

# sns.set_theme(style="whitegrid")
MYFONT = fm.FontProperties(fname="C:/Windows/Fonts/SimHei.ttf")
NUM_FONT = {"fontname": "Calibri"}

COLOR_DICT = {
    "100MG * 1": "#6F8DB9",
    "100MG * 2": "#6F8DB9",
    "10MG": "slateblue",
    "15MG": "rebeccapurple",
    "200MG * 1": "#44546A",
    "20MG": "indigo",
    "250MG": "navy",
    "25MG10片装": "darkgreen",
    "25MG20片装": "olivedrab",
    "500MG": "crimson",
    "50MG * 2": "#BD2843",
    "75MG7片装": "darkorange",
    "A+C": "navy",
    "A+D": "darkorange",
    "ACEI": "#6F8DB9",
    "ACEI": "crimson",
    "ARB": "#44546A",
    "ARB": "teal",
    "ARNI": "#BD2843",
    "B03A 补血药，铁剂": "navy",
    "B03C 红细胞生成素": "crimson",
    "B03D HIF-PH抑制剂": "teal",
    "Beta Blocker": "olivedrab",
    "Bottom20%": "crimson",
    "CCB": "navy",
    "D1-D2": "deepskyblue",
    "D3-D5": "dodgerblue",
    "D6-D8": "royalblue",
    "D9-D10": "navy",
    "Diuretics": "darkgreen",
    "G03J0\n选择性雌激素\n受体调节剂": "navy",
    "H04A0\n降钙素": "crimson",
    "H04E0\n甲状旁腺激素\n及类似物": "darkorange",
    "LABA+ICS固定复方制剂": "purple",
    "M05B3\n治疗骨质疏松\n和骨钙失调\n的二膦酸盐类": "darkgreen",
    "Mid-Bottom20%": "pink",
    "Mid20%": "darkorange",
    "PTH": "darkorange",
    "RAAS FDC": "darkorange",
    "SAMA+SABA固定复方制剂": "deepskyblue",
    "SERM": "navy",
    "Top-Mid20%": "olivedrab",
    "Top20%": "darkgreen",
    "一线城市": "navy",
    "万脉舒（H2C）": "navy",
    "三线城市": "teal",
    "丙卡特罗": "navy",
    "丙戊酸钠": "navy",
    "丙酸倍氯米松": "crimson",
    "丙酸氟替卡松": "darkorange",
    "中标仿制": "crimson",
    "中等的20%（50分）": "darkorange",
    "二线城市": "crimson",
    "二羟丙茶碱": "tomato",
    "二羟丙茶碱氯化钠": "teal",
    "五线城市": "darkorange",
    "京可新": "darkgreen",
    "京可新（ZXJ）": "darkgreen",
    "京必舒新（ZXJ）": "darkorange",
    "京诺": "olivedrab",
    "京诺（ZXJ）": "pink",
    "代文": "navy",
    "代文（NVR）": "navy",
    "代文（NVU）": "navy",
    "伊疏（S.I）": "saddlebrown",
    "伊达力": "olive",
    "伊达力（ZHI）": "olive",
    "伊达力（ZUP）": "olive",
    "伏格列波糖": "teal",
    "优力平": "gold",
    "优力平（ZLU）": "saddlebrown",
    "依固": "crimson",
    "依固（C2T）": "crimson",
    "依固（CTA）": "crimson",
    "依度沙班": "deepskyblue",
    "依替膦酸二钠": "teal",
    "依苏": "coral",
    "依那普利": "saddlebrown",
    "依那普利拉": "olivedrab",
    "依那普利（JJJ）": "saddlebrown",
    "依那普利（YAZ）": "saddlebrown",
    "依降钙素": "olivedrab",
    "信立坦": "purple",
    "信立坦（SI6）": "teal",
    "信立明": "teal",
    "信立明（SI6）": "teal",
    "倍利舒": "purple",
    "倍博特": "maroon",
    "倍怡": "pink",
    "倍怡（ZJ5）": "pink",
    "倍悦": "purple",
    "倍林达": "darkorange",
    "傲坦": "deepskyblue",
    "傲坦（DCG）": "navy",
    "傲坦（DSC）": "navy",
    "克赛（AVS）": "crimson",
    "兰沙": "c",
    "兰沙（B4W）": "crimson",
    "其他": "Deepskyblue",
    "其他": "grey",
    "其他品种": "grey",
    "其他科室": "grey",
    "内分泌科": "#FAA53A",
    "内分泌科": "darkgreen",
    "冠心病": "#6F8DB9",
    "冠爽": "navy",
    "冠爽（BJP）": "crimson",
    "冠爽（SHN）": "crimson",
    "利伐沙班": "rebeccapurple",
    "利塞膦酸钠": "purple",
    "利塞膦酸钠片": "gold",
    "利塞膦酸钠片（YKJ）": "gold",
    "利格列汀": "darkorange",
    "力清之": "darkorange",
    "力清之（KW.）": "darkorange",
    "加巴喷丁": "gold",
    "匹伐他汀": "teal",
    "匹伐他汀钙片": "olivedrab",
    "匹伐他汀钙片（S1Q）": "navy",
    "匹伐他汀钙片（SI6）": "olivedrab",
    "匹伐他汀（JN.）": "dodgerblue",
    "华东区": "navy",
    "华中区": "darkorange",
    "华北区": "darkgreen",
    "华南区": "teal",
    "华法林": "darkorange",
    "华西区": "crimson",
    "卒中": "#2B9B33",
    "单价": "navy",
    "单纯高血压": "#44546A",
    "卡托普利": "darkorange",
    "卡托普利片": "grey",
    "卡格列净": "navy",
    "厄贝沙坦": "#6F8DB9",
    "厄贝沙坦": "navy",
    "厄贝沙坦,氢氯噻嗪": "royalblue",
    "厄贝沙坦氢氯噻嗪": "royalblue",
    "双膦酸盐类": "darkgreen",
    "口服溶液": "deepskyblue",
    "口服片剂": "navy",
    "可定": "crimson",
    "可定（A5Z）": "crimson",
    "可定（AZN）": "crimson",
    "吉加": "orchid",
    "吉加（H9R）": "orchid",
    "吉加（JSH）": "orchid",
    "吲哚布芬": "crimson",
    "吸入性糖皮质激素(ICS)": "navy",
    "咪达普利": "coral",
    "唑来膦酸": "navy",
    "唑来膦酸注射液": "navy",
    "唑来膦酸注射液（KEU）": "saddlebrown",
    "唑来膦酸注射液（SK4）": "saddlebrown",
    "唑来膦酸（SHR）": "pink",
    "唑来膦酸（YAZ）": "darkorange",
    "喹那普利": "saddlebrown",
    "四线城市": "darkgreen",
    "国产阿司匹林": "grey",
    "地舒单抗": "deepskyblue",
    "坎地沙坦": "#FAA53A",
    "坎地沙坦": "olivedrab",
    "埃格列净": "darkorange",
    "培哚普利": "Saddlebrown",
    "培哚普利": "purple",
    "复方妥英麻黄茶碱": "olivedrab",
    "复方胆氨": "darkgreen",
    "复方茶碱麻黄碱": "purple",
    "复泰奥": "deepskyblue",
    "复泰奥（LYG）": "deepskyblue",
    "多索茶碱": "navy",
    "天泉乐宁（FTQ）": "olivedrab",
    "奥卡西平": "darkorange",
    "奥美沙坦": "deepskyblue",
    "奥美沙坦酯": "#2B9B33",
    "奥美沙坦酯片（S6N）": "darkgreen",
    "奥美沙坦（BW.）": "deepskyblue",
    "奥美沙坦（FTQ）": "deepskyblue",
    "奥美沙坦（GY0）": "saddlebrown",
    "奥美沙坦（SI6）": "teal",
    "妥洛特罗": "teal",
    "孟鲁司特": "navy",
    "安博维": "crimson",
    "安博维（SA9）": "crimson",
    "安博维（SG9）": "crimson",
    "安来": "gold",
    "安来（ZJ5）": "gold",
    "密固达": "navy",
    "密固达（NVR）": "navy",
    "密固达（NVU）": "navy",
    "密盖息": "darkorange",
    "密盖息（NVR）": "darkorange",
    "密盖息（NVU）": "darkorange",
    "富利他之（ZHI）": "rebeccapurple",
    "尤佳": "teal",
    "尤佳（TOF）": "darkgreen",
    "尤尼舒（J/G）": "olivedrab",
    "左乙拉西坦": "crimson",
    "左乙拉西坦片（CQU）": "crimson",
    "左乙拉西坦片（ZXJ）": "darkorange",
    "左乙拉西坦（SI6）": "teal",
    "左乙拉西坦（ZJO）": "darkgreen",
    "左旋氨氯地平": "darkorange",
    "布地奈德": "navy",
    "帅信": "darkgreen",
    "帅信/帅泰": "saddlebrown",
    "帅泰": "olivedrab",
    "希佳（C2T）": "darkorange",
    "希佳（NJ2）": "darkorange",
    "希弗全（A1L）": "darkgreen",
    "带量品种": "crimson",
    "平欣": "mediumslateblue",
    "开浦兰（UCB）": "navy",
    "异丙肾上腺素": "grey",
    "心内科": "#44546A",
    "心内科": "teal",
    "心力衰竭": "Saddlebrown",
    "必洛斯": "darkgreen",
    "恩存": "deepskyblue",
    "恩格列净": "crimson",
    "慢性肾病": "#FAA53A",
    "托吡酯": "teal",
    "托妥": "purple",
    "托妥（NJ2）": "purple",
    "托平（ZHT）": "deepskyblue",
    "抗白三烯类药物(LTRA)": "teal",
    "拉莫三嗪": "purple",
    "拜阿司匹灵": "navy",
    "搏力高": "mediumslateblue",
    "搏力高（ZYG）": "mediumslateblue",
    "斯迪诺": "saddlebrown",
    "斯迪诺（LU6）": "teal",
    "斯迪诺（S-Y）": "teal",
    "旗舰社区": "crimson",
    "无以上适应症": "Purple",
    "普仑司特": "crimson",
    "普伐他汀": "olivedrab",
    "普内科": "#2B9B33",
    "普内科": "saddlebrown",
    "普洛静（GTW）": "pink",
    "普瑞巴林": "olivedrab",
    "普罗力": "pink",
    "普罗力（AAI）": "pink",
    "普通社区": "pink",
    "替格瑞洛": "darkorange",
    "替米沙坦": "#ED94B6",
    "替米沙坦": "darkgreen",
    "最好的20%（90分）": "darkgreen",
    "最差的20%（10分）": "crimson",
    "未中标仿制": "dodgerblue",
    "未中标原研": "navy",
    "来适可XL（NVR）": "orchid",
    "来适可XL（NVU）": "orchid",
    "标准盒数（万盒）": "crimson",
    "欣复泰": "teal",
    "欣复泰（XIL）": "teal",
    "比伐芦定": "teal",
    "比伐芦定\n海南双成药业股份有限公司": "darkorange",
    "比伐芦定\n齐鲁制药集团": "deepskyblue",
    "比索洛尔": "navy",
    "氟伐他汀": "darkgreen",
    "氨氯地平": "teal",
    "氨茶碱": "darkorange",
    "氯吡格雷": "teal",
    "氯沙坦": "#BD2843",
    "氯沙坦": "darkorange",
    "氯沙坦氢氯噻嗪": "gold",
    "氯沙坦钾": "darkorange",
    "氯硝西泮": "deepskyblue",
    "沙丁胺醇": "crimson",
    "沙库巴曲缬沙坦钠": "Olive",
    "沙格列汀": "teal",
    "法安明（PHA）": "rebeccapurple",
    "波立维": "crimson",
    "注射剂": "crimson",
    "注射用那屈肝素钙": "deepskyblue",
    "注射用那屈肝素钙（DG+）": "deepskyblue",
    "泰仪": "olivedrab",
    "泰加宁": "teal",
    "泰加宁\n深圳信立泰药业股份有限公司": "teal",
    "泰加宁（SI6）": "teal",
    "泰嘉": "darkgreen",
    "泽朗": "crimson",
    "泽朗\n江苏豪森药业集团有限公司": "crimson",
    "洛伐他汀": "saddlebrown",
    "洛汀新": "olivedrab",
    "洛汀新（NBJ）": "olivedrab",
    "洛汀新（NVU）": "olivedrab",
    "特布他林": "navy",
    "特立帕肽": "pink",
    "环仑特罗": "darkgreen",
    "环索奈德": "darkgreen",
    "珍固": "crimson",
    "珍固（S60）": "crimson",
    "班布特罗": "darkorange",
    "瑞旨": "darkgreen",
    "瑞旨（S6B）": "olivedrab",
    "瑞旨（S7O）": "olivedrab",
    "瑞舒伐他汀": "crimson",
    "瑞舒伐他汀钙片（ZHI）": "orchid",
    "瑞舒伐他汀（C2T）": "dodgerblue",
    "瑞舒伐他汀（LEK）": "olive",
    "瑞舒伐他汀（NJ2）": "dodgerblue",
    "瑞舒伐他汀（NVU）": "olive",
    "百安新": "darkgreen",
    "益盖宁": "teal",
    "益盖宁（ASC）": "pink",
    "短效β2受体激动剂(SABA)": "crimson",
    "短效抗胆碱剂(SAMA)": "olivedrab",
    "硝苯地平": "crimson",
    "硫酸氢氯吡格雷片": "saddlebrown",
    "硫酸镁": "darkgreen",
    "社区医院": "crimson",
    "神内科": "#ED94B6",
    "神内科": "darkorange",
    "福善美": "olivedrab",
    "福善美（MSD）": "olivedrab",
    "福善美（MSG）": "olivedrab",
    "福美加": "darkgreen",
    "福美加（MSD）": "darkgreen",
    "福美加（MSG）": "darkgreen",
    "福莫特罗": "crimson",
    "福辛普利": "teal",
    "科素亚": "darkorange",
    "科素亚（MHU）": "darkorange",
    "科素亚（MSG）": "darkorange",
    "科苏": "darkgreen",
    "穗悦": "olivedrab",
    "立普妥": "navy",
    "立普妥（PFZ）": "navy",
    "立普妥（VI/）": "navy",
    "立迈青（AHK）": "darkorange",
    "等级医院": "navy",
    "米格列醇": "crimson",
    "糖尿病": "#ED94B6",
    "维格列汀": "crimson",
    "缓宁": "gold",
    "缬沙坦": "#44546A",
    "缬沙坦": "crimson",
    "缬沙坦,氨氯地平": "maroon",
    "缬沙坦氨氯地平": "maroon",
    "美卡素": "purple",
    "美卡素（B.I）": "purple",
    "美托洛尔常释剂型": "teal",
    "美托洛尔缓释剂型": "crimson",
    "美洛林": "deepskyblue",
    "美百乐镇（DCG）": "coral",
    "美百乐镇（DSC）": "coral",
    "老干科": "#BD2843",
    "老干科": "navy",
    "肝素": "crimson",
    "肾内科": "#6F8DB9",
    "肾内科": "crimson",
    "舒降之（MHU）": "dodgerblue",
    "苯巴比妥": "pink",
    "茚达特罗": "purple",
    "茶碱": "crimson",
    "茶碱,盐酸甲麻黄碱,暴马子浸膏": "saddlebrown",
    "血脂异常": "#BD2843",
    "西格列汀": "navy",
    "诺欣妥": "crimson",
    "贝尼地平": "darkgreen",
    "贝那普利": "Purple",
    "贝那普利": "coral",
    "贝那普利,氨氯地平": "salmon",
    "贝那普利氨氯地平": "salmon",
    "赖诺普利": "pink",
    "赛倍畅（JJY）": "saddlebrown",
    "赛博利": "gold",
    "赛博利（S1E）": "gold",
    "较好的20%（70分）": "olivedrab",
    "较差的20%（30分）": "pink",
    "辛伐他汀": "darkorange",
    "辛可（GXN）": "olive",
    "达格列净": "teal",
    "达比加群酯": "dodgerblue",
    "达芬盖（SZA）": "dodgerblue",
    "迪之雅": "olive",
    "速避凝（A3N）": "purple",
    "那屈肝素钙注射液（JJY）": "saddlebrown",
    "邦之": "crimson",
    "邦之（JBI）": "saddlebrown",
    "邦之（SFO）": "saddlebrown",
    "金尔力": "purple",
    "金尔力（B-Y）": "purple",
    "销售基恩（万元）": "teal",
    "长效β2受体激动剂(LABA)": "tomato",
    "长效抗胆碱剂(LAMA)": "darkgreen",
    "阿乐": "darkorange",
    "阿乐（SDS）": "darkorange",
    "阿仑膦酸钠": "darkorange",
    "阿仑膦酸钠,维生素D3": "darkgreen",
    "阿仑膦酸钠维生素D3": "darkgreen",
    "阿利沙坦": "teal",
    "阿利沙坦酯": "Deepskyblue",
    "阿卡波糖咀嚼片": "deepskyblue",
    "阿卡波糖片剂": "navy",
    "阿司匹林": "navy",
    "阿哌沙班": "darkgreen",
    "阿托伐他汀": "navy",
    "阿托伐他汀钙分散片（G6B）": "gold",
    "阿托伐他汀（FJ.）": "pink",
    "阿托伐他汀（FXG）": "olive",
    "阿托伐他汀（GI2）": "olive",
    "阿托伐他汀（HNQ）": "deepskyblue",
    "阿托伐他汀（QIL）": "deepskyblue",
    "阿托伐他汀（ZLU）": "deepskyblue",
    "阿格列汀": "darkgreen",
    "阿罗洛尔": "darkorange",
    "降钙素": "crimson",
    "雅施达": "saddlebrown",
    "雅施达（SVU）": "saddlebrown",
    "雅施达（TSV）": "saddlebrown",
    "雷洛昔芬": "gold",
    "雷米普利": "deepskyblue",
    "非带量品种": "teal",
    "非洛地平": "navy",
    "非类固醇类呼吸道消炎药": "saddlebrown",
    "高尿酸": "Deepskyblue",
    "高血压": "#44546A",
    "高血压+冠心病": "#6F8DB9",
    "高血压+卒中": "#2B9B33",
    "高血压+心力衰竭": "Saddlebrown",
    "高血压+慢性肾病": "#FAA53A",
    "高血压+糖尿病": "#ED94B6",
    "高血压+血脂异常": "#BD2843",
    "高血压+高尿酸": "Deepskyblue",
    "鲑降钙素": "crimson",
    "鲑鱼降钙素": "crimson",
    "黄嘌呤类": "darkorange",
    "齐征": "pink",
    "齐征（QLU）": "pink",
}

# COLOR_LIST = [
#     "#44546A",
#     "#6F8DB9",
#     "#BD2843",
#     "#ED94B6",
#     "#FAA53A",
#     "#2B9B33",
#     "Deepskyblue",
#     "Saddlebrown",
#     "Purple",
#     "Olivedrab",
#     "Pink",
# ]

COLOR_LIST = [
    "teal",
    "crimson",
    "navy",
    "tomato",
    "darkorange",
    "darkgreen",
    "olivedrab",
    "purple",
    "deepskyblue",
    "saddlebrown",
    "grey",
    "cornflowerblue",
    "magenta",
    "teal",
    "crimson",
    "navy",
    "tomato",
    "darkorange",
    "darkgreen",
    "olivedrab",
    "purple",
    "deepskyblue",
    "saddlebrown",
    "grey",
    "cornflowerblue",
    "magenta",
]


class UnequalDataGridError(Exception):
    def __init__(self, message):
        super().__init__(message)


def data_to_list(data):
    if isinstance(data, dict):
        return [v for k, v in data.items()]
    elif isinstance(data, pd.DataFrame):
        return [data]
    elif isinstance(data, pd.Series):
        return [data.to_frame()]
    elif isinstance(data, tuple):
        return list(data)
    elif isinstance(data, list):
        return data
    else:
        return data


def check_data_with_axes(data: list, axes: axes):
    if len(data) > len(axes):
        message = f"Got {len(data)} pieces of data, while {len(axes)} axes existed."
        raise UnequalDataGridError(message)


class GridFigure(Figure):
    """
    一个matplotlib图表基本类，主要实现:
    数据预处理，
    grid,
    宽高设置，
    字体大小，
    总标题
    保存
    """

    def __init__(
        self,
        data,  # 原始数
        savepath: str = "./plots/",  # 保存位置
        width: int = 15,  # 宽
        height: int = 6,  # 高
        fontsize: int = 14,  # 字体大小
        gs: GridSpec = None,  # GridSpec
        fmt: list = [",.0f"],  # 每个grid的数字格式
        style: dict = None,  # 风格字典
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.savepath = savepath
        self.width = width
        self.height = height
        self.fontsize = fontsize
        self.gs = gs
        self.fmt = ["{:%s}" % f for f in fmt]
        self.style = style

        # 所有数据处理成列表格式
        self.data = data_to_list(data)

        # 宽高
        self.set_size_inches(self.width, self.height)

        # Grid
        if gs is not None:
            for axes in gs:
                ax = self.add_subplot(axes)
        else:
            ax = self.add_subplot(111)

        # 检查grid大小和数据是否匹配
        check_data_with_axes(self.data, self.axes)

        # 检查grid大小与数字格式是否匹配
        check_data_with_axes(self.fmt, self.axes)

    def set_default_style(self):
        if self.style is None:
            return
        # 总标题
        if "title" in self.style:
            self.suptitle(self.style["title"], fontsize=self.fontsize * 1.5)

        if "ytitle" in self.style:
            self.supylabel(self.style["ytitle"])

        ylim_range = []
        xlim_range = []
        for i, ax in enumerate(self.axes):
            ax.tick_params(axis="x", labelsize=self.fontsize)  # 设置x轴刻度标签字体大小
            ax.tick_params(axis="y", labelsize=self.fontsize)  # 设置x轴刻度标签字体大小

            # y轴标签
            # yticklabels = [
            #     label.get_text().split("（")[0] for label in ax.get_yticklabels()
            # ]  # 去除y轴标签括号内内容
            # ax.set_yticklabels(yticklabels)

            # 添加grid标题
            if "gs_title" in self.style:
                # check_data_with_axes(self.style["gs_title"], self.axes)
                try:
                    ax.set_title(self.style["gs_title"][i], fontsize=self.fontsize)
                except:
                    continue
                # box = ax.get_position()
                # ax.set_position([box.x0, box.y0, box.width, box.height * 0.95])

            # 旋转x轴标签
            if "xlabel_rotation" in self.style:
                ax.tick_params(
                    axis="x", labelrotation=self.style["xlabel_rotation"]
                )

            # 旋转y轴标签
            if "ylabel_rotation" in self.style:
                ax.tick_params(
                    axis="y", labelrotation=self.style["ylabel_rotation"]
                )

                # 去除x轴ticks
            if "remove_xticks" in self.style and self.style["remove_xticks"]:
                ax.get_xaxis().set_ticks([])

                # 去除y轴ticks
            if "remove_yticks" in self.style and self.style["remove_yticks"]:
                ax.get_yaxis().set_ticks([])

            # 添加x轴标签
            if "xlabel" in self.style:
                ax.set_xlabel(self.style["xlabel"], fontsize=self.fontsize)

            # 添加y轴标签
            if "ylabel" in self.style:
                ax.set_ylabel(self.style["ylabel"], fontsize=self.fontsize)

                # 多个子图情况下只显示最下方图片的x轴label
            if "last_xticks_only" in self.style:
                gs = self.axes[0].get_gridspec()
                ncols = gs.ncols

                if self.style["last_xticks_only"] and i < len(self.axes) - ncols:
                    ax.get_xaxis().set_ticks([])

                # 多个子图情况下只显示最左边图片的x轴label
            if "first_yticks_only" in self.style:
                gs = self.axes[0].get_gridspec()
                ncols = gs.ncols

                if self.style["first_yticks_only"] and (i % ncols) != 0:
                    ax.get_yaxis().set_ticks([])

                # 隐藏上/右边框
            if (
                "hide_top_right_spines" in self.style
                and self.style["hide_top_right_spines"]
            ):
                ax.spines["right"].set_visible(False)
                ax.spines["top"].set_visible(False)
                ax.yaxis.set_ticks_position("left")
                ax.xaxis.set_ticks_position("bottom")

            # # x轴显示lim
            # if "xlim" in self.style:
            #     ax.set_xlim(self.style["xlim"][i][0], self.style["xlim"][i][1])

            # y轴显示lim，如果有多个y轴需要注意传参的个数
            if "ylim" in self.style:
                ax.set_ylim(self.style["ylim"][i][0], self.style["ylim"][i][1])
                try:
                    ax2 = ax.get_shared_x_axes().get_siblings(ax)[0]
                except:
                    pass
                if ax2 is not None:
                    ax2.set_ylim(self.style["ylim"][i][0], self.style["ylim"][i][1])
            if "same_ylim" in self.style and self.style["same_ylim"]:
                ylim_min, ylim_max = ax.get_ylim()
                if i == 0:
                    ylim_range = [ylim_min, ylim_max]
                else:
                    if ylim_min > ylim_range[0]:
                        ax.set_ylim(bottom=ylim_range[0])
                    else:
                        ylim_range = [ylim_min, ylim_range[1]]
                    if ylim_max < ylim_range[1]:
                        ax.set_ylim(top=ylim_range[1])
                    else:
                        ylim_range = [ylim_range[0], ylim_max]
            if "same_xlim" in self.style and self.style["same_xlim"]:
                xlim_min, xlim_max = ax.get_xlim()
                if i == 0:
                    xlim_range = [xlim_min, xlim_max]
                else:
                    if xlim_min < xlim_range[0]:
                        xlim_range = [xlim_min, xlim_range[1]]
                    if xlim_max > xlim_range[1]:
                        xlim_range = [xlim_range[0], xlim_max]
            # # 次坐标y轴显示lim
            # if "y2lim" in self.style:
            #     ax2 = ax.get_shared_x_axes().get_siblings(ax)[0]
            #     ax2.set_ylim(self.style["y2lim"][i][0], self.style["y2lim"][i][1])

            # 主网格线
            if "major_grid" in self.style:
                ax.grid(
                    which="major",
                    color=self.style["major_grid"],
                    axis="both",
                    linestyle=":",
                    linewidth=0.3,
                )

            # 次网格线
            if "minor_grid" in self.style:
                plt.minorticks_on()
                ax.grid(
                    which="minor",
                    color=self.style["minor_grid"],
                    axis="both",
                    linestyle=":",
                    linewidth=0.2,
                )
        if "same_xlim" in self.style and self.style["same_xlim"]:
            for ax in self.axes:
                ax.set_xlim(xlim_range[0], xlim_range[1])
        if "same_ylim" in self.style and self.style["same_ylim"]:
            for ax in self.axes:
                ax.set_xlim(ylim_range[0], ylim_range[1])

    def save(self):

        # 设置一些基本格式
        self.set_default_style()

        # 保存
        if os.path.exists(self.savepath) is False:
            os.makedirs(self.savepath)

        path = "%s%s.png" % (
            self.savepath,
            "test"
            if "title" not in self.style
            else self.style["title"].replace("/", "_"),
        )
        self.savefig(
            path,
            format="png",
            bbox_inches="tight",
            transparent=True,
            dpi=600,
        )
        print(path + " has been saved...")

        # Close
        plt.clf()
        plt.cla()
        plt.close()

        return path