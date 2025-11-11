"""
迁移脚本：转换颜色字典，将命名颜色转换为 HEX 值

功能：
1. 读取 data/color_dict.json
2. 对于 color 字段不是 HEX 值的颜色：
   - 将原值复制到 named_color 字段
   - 将 color 字段转换为对应的 HEX 值
3. 备份原文件并保存新文件
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Matplotlib 命名颜色到 HEX 的映射
MATPLOTLIB_COLORS = {
    # 基础颜色
    "blue": "#0000FF",
    "green": "#008000",
    "red": "#FF0000",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "yellow": "#FFFF00",
    "black": "#000000",
    "white": "#FFFFFF",
    # Tableau 调色板
    "tab:blue": "#1f77b4",
    "tab:orange": "#ff7f0e",
    "tab:green": "#2ca02c",
    "tab:red": "#d62728",
    "tab:purple": "#9467bd",
    "tab:brown": "#8c564b",
    "tab:pink": "#e377c2",
    "tab:gray": "#7f7f7f",
    "tab:olive": "#bcbd22",
    "tab:cyan": "#17becf",
    # CSS 颜色
    "aliceblue": "#F0F8FF",
    "antiquewhite": "#FAEBD7",
    "aqua": "#00FFFF",
    "aquamarine": "#7FFFD4",
    "azure": "#F0FFFF",
    "beige": "#F5F5DC",
    "bisque": "#FFE4C4",
    "blanchedalmond": "#FFEBCD",
    "blueviolet": "#8A2BE2",
    "brown": "#A52A2A",
    "burlywood": "#DEB887",
    "cadetblue": "#5F9EA0",
    "chartreuse": "#7FFF00",
    "chocolate": "#D2691E",
    "coral": "#FF7F50",
    "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC",
    "crimson": "#DC143C",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9",
    "darkgreen": "#006400",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00",
    "darkorchid": "#9932CC",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deepskyblue": "#00BFFF",
    "dimgray": "#696969",
    "dodgerblue": "#1E90FF",
    "firebrick": "#B22222",
    "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22",
    "fuchsia": "#FF00FF",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "gold": "#FFD700",
    "goldenrod": "#DAA520",
    "gray": "#808080",
    "grey": "#808080",
    "greenyellow": "#ADFF2F",
    "honeydew": "#F0FFF0",
    "hotpink": "#FF69B4",
    "indianred": "#CD5C5C",
    "indigo": "#4B0082",
    "ivory": "#FFFFF0",
    "khaki": "#F0E68C",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lightblue": "#ADD8E6",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0",
    "lime": "#00FF00",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "maroon": "#800000",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "navy": "#000080",
    "oldlace": "#FDF5E6",
    "olive": "#808000",
    "olivedrab": "#6B8E23",
    "orange": "#FFA500",
    "orangered": "#FF4500",
    "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "pink": "#FFC0CB",
    "plum": "#DDA0DD",
    "powderblue": "#B0E0E6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seashell": "#FFF5EE",
    "sienna": "#A0522D",
    "silver": "#C0C0C0",
    "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD",
    "slategray": "#708090",
    "snow": "#FFFAFA",
    "springgreen": "#00FF7F",
    "steelblue": "#4682B4",
    "tan": "#D2B48C",
    "teal": "#008080",
    "thistle": "#D8BFD8",
    "tomato": "#FF6347",
    "turquoise": "#40E0D0",
    "violet": "#EE82EE",
    "wheat": "#F5DEB3",
    "whitesmoke": "#F5F5F5",
    "yellowgreen": "#9ACD32",
    # 额外的别名
    "c": "#00FFFF",  # cyan
    "Purple": "#800080",
    "Violet": "#EE82EE",
    "Olive": "#808000",
    "Saddlebrown": "#8B4513",
}


def is_hex_color(color: str) -> bool:
    """检查是否为有效的 HEX 颜色"""
    return bool(re.match(r"^#[0-9A-Fa-f]{6}$", color))


def convert_named_to_hex(color: str) -> tuple[str, str | None]:
    """
    转换命名颜色为 HEX

    返回: (hex_color, named_color)
    """
    color_lower = color.strip().lower()

    # 如果已经是 HEX，直接返回
    if is_hex_color(color):
        return (color.upper(), None)

    # 查找命名颜色
    hex_color = MATPLOTLIB_COLORS.get(color_lower)
    if hex_color:
        return (hex_color.upper(), color)

    # 未知颜色，保持原样并警告
    print(f"警告: 未知颜色 '{color}'，保持原样")
    return (color, None)


def migrate_color_dict(json_path: Path):
    """迁移颜色字典"""
    # 读取原文件
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 备份原文件
    backup_path = (
        json_path.parent
        / f"{json_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已备份原文件到: {backup_path}")

    # 转换数据
    migrated_count = 0
    for name, color_obj in data.items():
        if isinstance(color_obj, dict):
            original_color = color_obj.get("color", "")
            hex_color, named_color = convert_named_to_hex(original_color)

            # 更新颜色值
            if hex_color != original_color:
                color_obj["color"] = hex_color
                if named_color:
                    color_obj["named_color"] = named_color
                migrated_count += 1
                print(
                    f"转换: {name} - {original_color} -> {hex_color} (named: {named_color})"
                )

    # 保存新文件
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n迁移完成！")
    print(f"- 总颜色数: {len(data)}")
    print(f"- 转换数量: {migrated_count}")
    print(f"- 保存到: {json_path}")


if __name__ == "__main__":
    # 项目根目录
    project_root = Path(__file__).parent.parent
    color_dict_path = project_root / "data" / "color_dict.json"

    if not color_dict_path.exists():
        print(f"错误: 找不到文件 {color_dict_path}")
        exit(1)

    print(f"开始迁移颜色字典: {color_dict_path}\n")
    migrate_color_dict(color_dict_path)
