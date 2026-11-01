#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEU·绩点计算器：独立运行的单文件版本。"""
import html
import builtins
import types
import json
import os
import re
import sys
from urllib.parse import urlparse
import csv
import io
import math
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
import copy
import queue
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox, simpledialog
from contextvars import ContextVar

__author__ = "X_Y"
APP_TITLE = f"SEU·绩点计算器 @{__author__}"

_backend_sink = ContextVar("backend_log", default=print)

def _backend_print(*args, **kwargs):
    return _backend_sink.get()(*args, **kwargs)








# 用户提供的完整原脚本；通过独立命名空间执行，不进入原命令行菜单。
ORIGINAL_SCRIPT_SHA256 = '330f84845d2abb64bb5eab930bbab136f692a73849895de174a751351144f912'
ORIGINAL_SCRIPT = (
    '#!/usr/bin/env python3\n'
    '# -*- coding: utf-8 -*-\n'
    'import html\n'
    'import json\n'
    'import os\n'
    'import re\n'
    'import sys\n'
    'import getpass\n'
    'import base64\n'
    'import hashlib\n'
    'import secrets\n'
    'import uuid\n'
    'from urllib.parse import urljoin, parse_qs, urlparse, unquote\n'
    '\n'
    '\n'
    'SEU_GRADE_PAGE = (\n'
    '    "https://ehall.seu.edu.cn/jwapp/sys/cjcx/*default/index.do"\n'
    '    "?t_s=1779023371065&EMAP_LANG=zh&THEME=indigo"\n'
    '    "&amp_sec_version_=1"\n'
    '    "&gid_=YUtKNE1nMWZEL1lpdzFhMU9jMXc2aWhjTkZMdlc5YUxDbXA1TlpYaFUxb2RNaWxvQUUvQWc4NDE5RXpuL0x1cHhiNkJTQzc4bEpyTk9hL0lYbWxZNnc9PQ"\n'
    '    "#/cjcx"\n'
    ')\n'
    'SEU_GRADE_API = "https://ehall.seu.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do"\n'
    'SEU_GRADE_API_HTTP = SEU_GRADE_API.replace("https://", "http://", 1)\n'
    'AUTH_BASE = "https://auth.seu.edu.cn/auth"\n'
    'AUTH_DIST = "https://auth.seu.edu.cn/dist/"\n'
    'AUTH_CASBACK = AUTH_BASE + "/casback"\n'
    'SEU_CAS_SERVICE = SEU_GRADE_PAGE.replace("https://", "http://", 1).split("#", 1)[0]\n'
    '\n'
    '\n'
    'def score_to_grade_point(score):\n'
    '    """\n'
    '    东南大学绩点换算标准:\n'
    '    96: 4.8 | 93: 4.5 | 90: 4.0 | 86: 3.8 | 83: 3.5 | 80: 3.0\n'
    '    76: 2.8 | 73: 2.5 | 70: 2.0 | 66: 1.8 | 63: 1.5 | 60: 1.0\n'
    '    两个节点之间按线性计算，例如 92.5 会得到中间绩点。\n'
    '    """\n'
    '    if score < 60:\n'
    '        return 0.0\n'
    '    if score >= 96:\n'
    '        return 4.8\n'
    '\n'
    '    points = [\n'
    '        [60, 1.0],\n'
    '        [63, 1.5],\n'
    '        [66, 1.8],\n'
    '        [70, 2.0],\n'
    '        [73, 2.5],\n'
    '        [76, 2.8],\n'
    '        [80, 3.0],\n'
    '        [83, 3.5],\n'
    '        [86, 3.8],\n'
    '        [90, 4.0],\n'
    '        [93, 4.5],\n'
    '        [96, 4.8],\n'
    '    ]\n'
    '\n'
    '    for i in range(len(points) - 1):\n'
    '        left_score = points[i][0]\n'
    '        left_gpa = points[i][1]\n'
    '        right_score = points[i + 1][0]\n'
    '        right_gpa = points[i + 1][1]\n'
    '\n'
    '        if left_score <= score < right_score:\n'
    '            rate = (score - left_score) / (right_score - left_score)\n'
    '            gpa = left_gpa + rate * (right_gpa - left_gpa)\n'
    '            return round(gpa, 2)\n'
    '\n'
    '    return 0.0\n'
    '\n'
    '\n'
    'def parse_float(value, default=None):\n'
    '    """把字符串、整数、小数等转换成 float。"""\n'
    '    if value is None:\n'
    '        return default\n'
    '    if isinstance(value, (int, float)):\n'
    '        return float(value)\n'
    '\n'
    '    text = str(value).strip()\n'
    '    if text == "":\n'
    '        return default\n'
    '    if text.startswith("."):\n'
    '        text = "0" + text\n'
    '\n'
    '    try:\n'
    '        return float(text)\n'
    '    except ValueError:\n'
    '        return default\n'
    '\n'
    '\n'
    'def grade_name_to_score(value):\n'
    '    """把等级制成绩粗略换算为百分制成绩，便于纳入平均分和绩点计算。"""\n'
    '    if value is None:\n'
    '        return None\n'
    '\n'
    '    text = str(value).strip()\n'
    '    mapping = {\n'
    '        "优": 95.0,\n'
    '        "良": 85.0,\n'
    '        "中": 75.0,\n'
    '        "及格": 65.0,\n'
    '        "合格": 65.0,\n'
    '        "通过": 65.0,\n'
    '        "不及格": 0.0,\n'
    '        "不合格": 0.0,\n'
    '        "未通过": 0.0,\n'
    '    }\n'
    '    return mapping.get(text)\n'
    '\n'
    '\n'
    'def get_score_from_row(row):\n'
    '    """从教务返回包的一条课程记录里取出可计算成绩。"""\n'
    '    possible_keys = ["ZCJ", "XSZCJMC", "ZCJ_DISPLAY", "QMCJ", "QMCJ_DISPLAY"]\n'
    '    for key in possible_keys:\n'
    '        value = row.get(key)\n'
    '        score = parse_float(value)\n'
    '        if score is not None:\n'
    '            return score\n'
    '\n'
    '        score = grade_name_to_score(value)\n'
    '        if score is not None:\n'
    '            return score\n'
    '\n'
    '    return None\n'
    '\n'
    '\n'
    'def is_optional_course(row, course_type):\n'
    '    """判断是否为任选课程。"""\n'
    '    display = str(row.get("KCXZDM_DISPLAY") or course_type or "")\n'
    '    code = str(row.get("KCXZDM") or "")\n'
    '    category = str(row.get("KCLBDM_DISPLAY") or "")\n'
    '    return "任选" in display or code == "02" or "通识选修" in category\n'
    '\n'
    '\n'
    'def find_rows(data):\n'
    '    """\n'
    '    从返回包中查找 rows 列表。\n'
    '    兼容 datas.xscjcx.rows、直接 rows、列表等结构。\n'
    '    """\n'
    '    if isinstance(data, list):\n'
    '        rows = []\n'
    '        for item in data:\n'
    '            if isinstance(item, dict):\n'
    '                rows.append(item)\n'
    '        return rows\n'
    '\n'
    '    if not isinstance(data, dict):\n'
    '        return []\n'
    '\n'
    '    if isinstance(data.get("rows"), list):\n'
    '        rows = []\n'
    '        for item in data["rows"]:\n'
    '            if isinstance(item, dict):\n'
    '                rows.append(item)\n'
    '        return rows\n'
    '\n'
    '    datas = data.get("datas")\n'
    '    if isinstance(datas, dict):\n'
    '        for value in datas.values():\n'
    '            if isinstance(value, dict) and isinstance(value.get("rows"), list):\n'
    '                rows = []\n'
    '                for item in value["rows"]:\n'
    '                    if isinstance(item, dict):\n'
    '                        rows.append(item)\n'
    '                return rows\n'
    '\n'
    '    for value in data.values():\n'
    '        rows = find_rows(value)\n'
    '        if rows:\n'
    '            return rows\n'
    '\n'
    '    return []\n'
    '\n'
    '\n'
    'def find_total_size(data):\n'
    '    """从返回包中查找 totalSize，用于判断是否已经翻页取完。"""\n'
    '    if not isinstance(data, dict):\n'
    '        return None\n'
    '\n'
    '    total_size = parse_float(data.get("totalSize"))\n'
    '    if total_size is not None:\n'
    '        return int(total_size)\n'
    '\n'
    '    datas = data.get("datas")\n'
    '    if isinstance(datas, dict):\n'
    '        for value in datas.values():\n'
    '            if isinstance(value, dict):\n'
    '                total_size = parse_float(value.get("totalSize"))\n'
    '                if total_size is not None:\n'
    '                    return int(total_size)\n'
    '\n'
    '    for value in data.values():\n'
    '        total_size = find_total_size(value)\n'
    '        if total_size is not None:\n'
    '            return total_size\n'
    '\n'
    '    return None\n'
    '\n'
    '\n'
    'def extract_json_from_text(text):\n'
    '    """\n'
    '    从纯 JSON 或“请求头/响应头 + JSON + 其他内容”中提取 JSON。\n'
    '    用户从浏览器抓包复制出来的内容通常不是纯 JSON，所以这里用 raw_decode 自动截取。\n'
    '    """\n'
    '    text = text.strip()\n'
    '    if text == "":\n'
    '        return None\n'
    '\n'
    '    decoder = json.JSONDecoder()\n'
    '\n'
    '    try:\n'
    '        return decoder.decode(text)\n'
    '    except ValueError:\n'
    '        pass\n'
    '\n'
    '    candidate_positions = []\n'
    '    for marker in [\'{"datas"\', \'{"rows"\', \'[{\']:\n'
    '        position = text.find(marker)\n'
    '        if position != -1:\n'
    '            candidate_positions.append(position)\n'
    '\n'
    '    for i, char in enumerate(text):\n'
    '        if char == "{" or char == "[":\n'
    '            candidate_positions.append(i)\n'
    '\n'
    '    used_positions = []\n'
    '    for position in candidate_positions:\n'
    '        if position in used_positions:\n'
    '            continue\n'
    '        used_positions.append(position)\n'
    '\n'
    '        try:\n'
    '            data, end_index = decoder.raw_decode(text[position:])\n'
    '        except ValueError:\n'
    '            continue\n'
    '\n'
    '        if find_rows(data):\n'
    '            return data\n'
    '\n'
    '    return None\n'
    '\n'
    '\n'
    'def make_course(name, score, credit, course_type="", semester="", course_code="", raw=None,\n'
    '                excluded=False, exclude_reason=""):\n'
    '    """用字典存储一门课程。"""\n'
    '    return {\n'
    '        "name": name,\n'
    '        "score": float(score),\n'
    '        "credit": float(credit),\n'
    '        "grade_point": score_to_grade_point(float(score)),\n'
    '        "course_type": course_type,\n'
    '        "semester": semester,\n'
    '        "course_code": course_code,\n'
    '        "raw": raw or {},\n'
    '        "excluded": excluded,\n'
    '        "exclude_reason": exclude_reason,\n'
    '    }\n'
    '\n'
    '\n'
    'def rows_to_courses(rows):\n'
    '    """把教务 rows 转换为课程字典列表。"""\n'
    '    courses = []\n'
    '    skipped = 0\n'
    '\n'
    '    for row in rows:\n'
    '        name = str(row.get("KCM") or row.get("XSKCM") or row.get("TDKCM") or "未命名课程")\n'
    '        score = get_score_from_row(row)\n'
    '        credit = parse_float(row.get("XF"), 0.0)\n'
    '\n'
    '        if score is None or credit is None or credit <= 0:\n'
    '            skipped += 1\n'
    '            continue\n'
    '\n'
    '        course_type = str(row.get("KCXZDM_DISPLAY") or "")\n'
    '        excluded = is_optional_course(row, course_type)\n'
    '        course = make_course(\n'
    '            name=name,\n'
    '            score=score,\n'
    '            credit=credit,\n'
    '            course_type=course_type,\n'
    '            semester=str(row.get("XNXQDM_DISPLAY") or row.get("XNXQDM") or ""),\n'
    '            course_code=str(row.get("KCH") or row.get("XSKCH") or ""),\n'
    '            raw=row,\n'
    '            excluded=excluded,\n'
    '            exclude_reason="任选课程" if excluded else "",\n'
    '        )\n'
    '        courses.append(course)\n'
    '\n'
    '    if skipped > 0:\n'
    '        print("提示：有", skipped, "条记录缺少可计算成绩或学分，已跳过。")\n'
    '\n'
    '    return courses\n'
    '\n'
    '\n'
    'def calculate(courses):\n'
    '    """计算平均成绩、平均绩点、计入总学分。"""\n'
    '    total_credit = 0.0\n'
    '    total_score = 0.0\n'
    '    total_gpa = 0.0\n'
    '\n'
    '    for course in courses:\n'
    '        if course["excluded"]:\n'
    '            continue\n'
    '        total_credit += course["credit"]\n'
    '        total_score += course["score"] * course["credit"]\n'
    '        total_gpa += course["grade_point"] * course["credit"]\n'
    '\n'
    '    if total_credit <= 0:\n'
    '        return 0.0, 0.0, 0.0\n'
    '\n'
    '    average_score = total_score / total_credit\n'
    '    average_gpa = total_gpa / total_credit\n'
    '    return average_score, average_gpa, total_credit\n'
    '\n'
    '\n'
    'def display_width(text):\n'
    '    """计算中英文混排时的简易显示宽度。"""\n'
    '    width = 0\n'
    '    for char in str(text):\n'
    '        if ord(char) > 127:\n'
    '            width += 2\n'
    '        else:\n'
    '            width += 1\n'
    '    return width\n'
    '\n'
    '\n'
    'def format_number(value, digits=2):\n'
    '    text = f"{value:.{digits}f}"\n'
    '    if "." in text:\n'
    '        text = text.rstrip("0").rstrip(".")\n'
    '    return text\n'
    '\n'
    '\n'
    'def format_gpa(value):\n'
    '    return "{:.2f}".format(value)\n'
    '\n'
    '\n'
    'def print_transcript(courses):\n'
    '    """在控制台显示成绩单和计算结果。"""\n'
    '    if not courses:\n'
    '        print("当前没有成绩数据。")\n'
    '        return\n'
    '\n'
    '    headers = ["序号", "学科名称", "成绩", "绩点", "学分", "课程性质", "学期", "是否计入"]\n'
    '    table_rows = []\n'
    '\n'
    '    for index, course in enumerate(courses, start=1):\n'
    '        included_text = "是"\n'
    '        if course["excluded"]:\n'
    '            included_text = "否(" + course["exclude_reason"] + ")"\n'
    '\n'
    '        table_rows.append([\n'
    '            str(index),\n'
    '            course["name"],\n'
    '            format_number(course["score"]),\n'
    '            format_gpa(course["grade_point"]),\n'
    '            format_number(course["credit"]),\n'
    '            course["course_type"] or "-",\n'
    '            course["semester"] or "-",\n'
    '            included_text,\n'
    '        ])\n'
    '\n'
    '    widths = []\n'
    '    for header in headers:\n'
    '        widths.append(display_width(header))\n'
    '\n'
    '    for row in table_rows:\n'
    '        for i in range(len(row)):\n'
    '            widths[i] = max(widths[i], display_width(row[i]))\n'
    '\n'
    '    def pad(text, width):\n'
    '        return str(text) + " " * (width - display_width(text))\n'
    '\n'
    '    print()\n'
    '    print(" | ".join(pad(headers[i], widths[i]) for i in range(len(headers))))\n'
    '    print("-+-".join("-" * w for w in widths))\n'
    '\n'
    '    for row in table_rows:\n'
    '        print(" | ".join(pad(row[i], widths[i]) for i in range(len(row))))\n'
    '\n'
    '    average_score, average_gpa, total_credit = calculate(courses)\n'
    '    included_count = 0\n'
    '    excluded_count = 0\n'
    '    for course in courses:\n'
    '        if course["excluded"]:\n'
    '            excluded_count += 1\n'
    '        else:\n'
    '            included_count += 1\n'
    '\n'
    '    print()\n'
    '    print("计入课程：{} 门；排除课程：{} 门".format(included_count, excluded_count))\n'
    '    print("总学分：{}".format(format_number(total_credit)))\n'
    '    print("总成绩/平均成绩：{:.2f}".format(average_score))\n'
    '    print("绩点：{:.2f}".format(average_gpa))\n'
    '\n'
    '\n'
    'def read_json_from_user():\n'
    '    print("请选择提供返回包的方式：")\n'
    '    print("1. 输入文件路径（可以是纯 JSON，也可以是完整抓包文本）")\n'
    '    print("2. 直接粘贴 JSON/完整抓包文本（输入单独一行 END 结束）")\n'
    '    choice = input("选择：").strip()\n'
    '\n'
    '    try:\n'
    '        if choice == "1":\n'
    '            path = input("JSON 文件路径：").strip().strip(\'"\')\n'
    '            with open(path, "r", encoding="utf-8") as f:\n'
    '                text = f.read()\n'
    '            data = extract_json_from_text(text)\n'
    '            if data is None:\n'
    '                print("没有从文件中识别到有效成绩 JSON。")\n'
    '            return data\n'
    '\n'
    '        if choice == "2":\n'
    '            print("请粘贴 JSON 或完整抓包文本，完成后输入单独一行 END：")\n'
    '            lines = []\n'
    '            while True:\n'
    '                line = input()\n'
    '                if line.strip() == "END":\n'
    '                    break\n'
    '                lines.append(line)\n'
    '\n'
    '            data = extract_json_from_text("\\n".join(lines))\n'
    '            if data is None:\n'
    '                print("没有从粘贴内容中识别到有效成绩 JSON。")\n'
    '            return data\n'
    '\n'
    '        print("选择无效。")\n'
    '    except Exception as error:\n'
    '        print("读取 JSON 失败：", error)\n'
    '\n'
    '    return None\n'
    '\n'
    '\n'
    'def load_from_json_flow():\n'
    '    data = read_json_from_user()\n'
    '    if data is None:\n'
    '        return []\n'
    '\n'
    '    rows = find_rows(data)\n'
    '    if not rows:\n'
    '        print("没有在返回包中找到 rows 成绩列表。")\n'
    '        return []\n'
    '\n'
    '    courses = rows_to_courses(rows)\n'
    '    print("已导入", len(courses), "门可计算课程。")\n'
    '    return courses\n'
    '\n'
    '\n'
    'def input_score(prompt, default=None):\n'
    '    while True:\n'
    '        raw_score = input(prompt).strip()\n'
    '        if raw_score == "" and default is not None:\n'
    '            return default\n'
    '\n'
    '        score = parse_float(raw_score)\n'
    '        if score is None:\n'
    '            score = grade_name_to_score(raw_score)\n'
    '        if score is not None:\n'
    '            return score\n'
    '\n'
    '        print("成绩格式不正确，请重新输入。")\n'
    '\n'
    '\n'
    'def input_credit(prompt, default=None):\n'
    '    while True:\n'
    '        raw_credit = input(prompt).strip()\n'
    '        if raw_credit == "" and default is not None:\n'
    '            return default\n'
    '\n'
    '        credit = parse_float(raw_credit)\n'
    '        if credit is not None and credit > 0:\n'
    '            return credit\n'
    '\n'
    '        print("学分必须是大于 0 的数字。")\n'
    '\n'
    '\n'
    'def input_course_fields(existing=None):\n'
    '    """录入或修改一门课程。existing 不为空时，直接回车保留原值。"""\n'
    '    existing = existing or {}\n'
    '    default_name = existing.get("name", "")\n'
    '\n'
    '    if default_name and "score" not in existing:\n'
    '        name = default_name\n'
    '    else:\n'
    '        while True:\n'
    '            prompt = "学科名称"\n'
    '            if default_name:\n'
    '                prompt += "（回车保留 {}）".format(default_name)\n'
    '            name = input(prompt + "：").strip()\n'
    '            if name:\n'
    '                break\n'
    '            if default_name:\n'
    '                name = default_name\n'
    '                break\n'
    '            print("学科名称不能为空。")\n'
    '\n'
    '    score = input_score(\n'
    '        "成绩（百分制或优秀/良好/良/中/及格/不及格{}）：".format(\n'
    '            "，回车保留 {}".format(format_number(existing["score"])) if "score" in existing else ""\n'
    '        ),\n'
    '        existing.get("score") if "score" in existing else None,\n'
    '    )\n'
    '    credit = input_credit(\n'
    '        "学分{}：".format("（回车保留 {}）".format(format_number(existing["credit"])) if "credit" in existing else ""),\n'
    '        existing.get("credit") if "credit" in existing else None,\n'
    '    )\n'
    '\n'
    '    old_type = existing.get("course_type", "")\n'
    '    type_prompt = "课程性质（含“任选”则不计入"\n'
    '    if old_type:\n'
    '        type_prompt += "，回车保留 {}".format(old_type)\n'
    '    course_type = input(type_prompt + "）：").strip()\n'
    '    if course_type == "" and old_type:\n'
    '        course_type = old_type\n'
    '    if course_type == "":\n'
    '        course_type = "手动录入"\n'
    '\n'
    '    old_semester = existing.get("semester", "")\n'
    '    semester = input("学期{}：".format("（回车保留 {}）".format(old_semester) if old_semester else "（可空）")).strip()\n'
    '    if semester == "":\n'
    '        semester = old_semester\n'
    '\n'
    '    old_code = existing.get("course_code", "")\n'
    '    course_code = input("课程代码{}：".format("（回车保留 {}）".format(old_code) if old_code else "（可空）")).strip()\n'
    '    if course_code == "":\n'
    '        course_code = old_code\n'
    '\n'
    '    excluded = "任选" in course_type\n'
    '    return make_course(\n'
    '        name=name,\n'
    '        score=score,\n'
    '        credit=credit,\n'
    '        course_type=course_type,\n'
    '        semester=semester,\n'
    '        course_code=course_code,\n'
    '        raw=existing.get("raw", {}),\n'
    '        excluded=excluded,\n'
    '        exclude_reason="任选课程" if excluded else "",\n'
    '    )\n'
    '\n'
    '\n'
    'def input_courses_manually():\n'
    '    courses = []\n'
    '    print()\n'
    '    print("手动录入。")\n'
    '    print("在学科名称处输入 0 可以结束录入。")\n'
    '\n'
    '    while True:\n'
    '        name = input("学科名称：").strip()\n'
    '        if name == "" or name == "0":\n'
    '            break\n'
    '\n'
    '        course = input_course_fields({"name": name, "course_type": "手动录入"})\n'
    '        courses.append(course)\n'
    '        print("已加入。")\n'
    '\n'
    '    return courses\n'
    '\n'
    '\n'
    'def filter_courses(courses):\n'
    '    if not courses:\n'
    '        print("当前没有成绩数据。")\n'
    '        return courses\n'
    '\n'
    '    print("筛选字段：1. 学科名称包含  2. 成绩范围  3. 学分范围  4. 是否计入")\n'
    '    field = input("选择：").strip()\n'
    '\n'
    '    if field == "1":\n'
    '        keyword = input("关键词：").strip()\n'
    '        result = []\n'
    '        for course in courses:\n'
    '            if keyword in course["name"]:\n'
    '                result.append(course)\n'
    '        return result\n'
    '\n'
    '    if field == "2" or field == "3":\n'
    '        label = "成绩" if field == "2" else "学分"\n'
    '        min_value = parse_float(input(label + "下限（可空）：").strip(), float("-inf"))\n'
    '        max_value = parse_float(input(label + "上限（可空）：").strip(), float("inf"))\n'
    '        key = "score" if field == "2" else "credit"\n'
    '\n'
    '        result = []\n'
    '        for course in courses:\n'
    '            if min_value <= course[key] <= max_value:\n'
    '                result.append(course)\n'
    '        return result\n'
    '\n'
    '    if field == "4":\n'
    '        only_included = input("只显示计入课程？(Y/n)：").strip().lower() != "n"\n'
    '        result = []\n'
    '        for course in courses:\n'
    '            if only_included and not course["excluded"]:\n'
    '                result.append(course)\n'
    '            if not only_included and course["excluded"]:\n'
    '                result.append(course)\n'
    '        return result\n'
    '\n'
    '    print("选择无效。")\n'
    '    return courses\n'
    '\n'
    '\n'
    'def choose_course_index(courses, prompt="请输入课程序号："):\n'
    '    if not courses:\n'
    '        print("当前没有成绩数据。")\n'
    '        return None\n'
    '\n'
    '    index = parse_float(input(prompt).strip())\n'
    '    if index is None or int(index) != index:\n'
    '        print("序号格式不正确。")\n'
    '        return None\n'
    '\n'
    '    index = int(index)\n'
    '    if index < 1 or index > len(courses):\n'
    '        print("序号超出范围。")\n'
    '        return None\n'
    '    return index - 1\n'
    '\n'
    '\n'
    'def add_course(courses):\n'
    '    course = input_course_fields()\n'
    '    courses.append(course)\n'
    '    print("已新增课程：", course["name"])\n'
    '    return courses\n'
    '\n'
    '\n'
    'def delete_course(courses):\n'
    '    print_transcript(courses)\n'
    '    index = choose_course_index(courses, "请输入要删除的课程序号：")\n'
    '    if index is None:\n'
    '        return courses\n'
    '\n'
    '    course = courses[index]\n'
    '    confirm = input("确认删除“{}”？(y/N)：".format(course["name"])).strip().lower()\n'
    '    if confirm == "y":\n'
    '        del courses[index]\n'
    '        print("已删除。")\n'
    '    else:\n'
    '        print("已取消删除。")\n'
    '    return courses\n'
    '\n'
    '\n'
    'def update_course(courses):\n'
    '    print_transcript(courses)\n'
    '    index = choose_course_index(courses, "请输入要修改的课程序号：")\n'
    '    if index is None:\n'
    '        return courses\n'
    '\n'
    '    old_course = courses[index]\n'
    '    courses[index] = input_course_fields(old_course)\n'
    '    print("已修改课程：", courses[index]["name"])\n'
    '    return courses\n'
    '\n'
    '\n'
    'def save_txt(courses, path):\n'
    '    average_score, average_gpa, total_credit = calculate(courses)\n'
    '    with open(path, "w", encoding="utf-8") as f:\n'
    '        f.write("学科名称\\t成绩\\t绩点\\t学分\\t课程性质\\t学期\\t是否计入\\n")\n'
    '        for course in courses:\n'
    '            f.write(\n'
    '                "\\t".join([\n'
    '                    course["name"],\n'
    '                    format_number(course["score"]),\n'
    '                    format_gpa(course["grade_point"]),\n'
    '                    format_number(course["credit"]),\n'
    '                    course["course_type"],\n'
    '                    course["semester"],\n'
    '                    "否" if course["excluded"] else "是",\n'
    '                ])\n'
    '                + "\\n"\n'
    '            )\n'
    '\n'
    '        f.write("\\n")\n'
    '        f.write("总学分\\t{}\\n".format(format_number(total_credit)))\n'
    '        f.write("总成绩/平均成绩\\t{:.2f}\\n".format(average_score))\n'
    '        f.write("绩点\\t{:.2f}\\n".format(average_gpa))\n'
    '\n'
    '\n'
    'def export_excel(courses, path):\n'
    '    if not path.lower().endswith(".xlsx"):\n'
    '        path += ".xlsx"\n'
    '\n'
    '    headers = ["学科名称", "成绩", "绩点", "学分", "课程性质", "学期", "课程代码", "是否计入", "排除原因"]\n'
    '    data = []\n'
    '    for course in courses:\n'
    '        data.append([\n'
    '            course["name"],\n'
    '            course["score"],\n'
    '            course["grade_point"],\n'
    '            course["credit"],\n'
    '            course["course_type"],\n'
    '            course["semester"],\n'
    '            course["course_code"],\n'
    '            "否" if course["excluded"] else "是",\n'
    '            course["exclude_reason"],\n'
    '        ])\n'
    '\n'
    '    average_score, average_gpa, total_credit = calculate(courses)\n'
    '\n'
    '    try:\n'
    '        from openpyxl import Workbook\n'
    '    except ImportError:\n'
    '        print("导出 Excel 需要安装 openpyxl。请先运行：pip install openpyxl")\n'
    '        return ""\n'
    '\n'
    '    workbook = Workbook()\n'
    '    sheet = workbook.active\n'
    '    sheet.title = "成绩单"\n'
    '    sheet.append(headers)\n'
    '\n'
    '    for row in data:\n'
    '        sheet.append(row)\n'
    '\n'
    '    sheet.append([])\n'
    '    sheet.append(["总学分", total_credit])\n'
    '    sheet.append(["总成绩/平均成绩", round(average_score, 2)])\n'
    '    sheet.append(["绩点", round(average_gpa, 2)])\n'
    '\n'
    '    for column_cells in sheet.columns:\n'
    '        max_len = 0\n'
    '        for cell in column_cells:\n'
    '            max_len = max(max_len, display_width(str(cell.value or "")))\n'
    '        sheet.column_dimensions[column_cells[0].column_letter].width = min(max_len + 2, 40)\n'
    '\n'
    '    workbook.save(path)\n'
    '\n'
    '    return path\n'
    '\n'
    '\n'
    'def find_grade_api_urls_from_text(text, base_url):\n'
    '    """从页面或 JS 源码中提取成绩查询接口地址。"""\n'
    '    urls = []\n'
    '    patterns = [\n'
    '        r"([\\"\'])([^\\"\']*?/jwapp/sys/cjcx/modules/cjcx/xscjcx\\.do[^\\"\']*)\\1",\n'
    '        r"([\\"\'])([^\\"\']*?modules/cjcx/xscjcx\\.do[^\\"\']*)\\1",\n'
    '        r"([\\"\'])([^\\"\']*?xscjcx\\.do[^\\"\']*)\\1",\n'
    '    ]\n'
    '\n'
    '    for pattern in patterns:\n'
    '        matches = re.findall(pattern, text, re.IGNORECASE)\n'
    '        for match in matches:\n'
    '            raw_url = html.unescape(match[1])\n'
    '            if raw_url.startswith("javascript:") or raw_url.startswith("#"):\n'
    '                continue\n'
    '\n'
    '            full_url = urljoin(base_url, raw_url)\n'
    '            if full_url not in urls:\n'
    '                urls.append(full_url)\n'
    '\n'
    '    plain_matches = re.findall(\n'
    '        r"((?:https?://[^\\\\\'\\"\\s]+|/[^\\\\\'\\"\\s]+)?/jwapp/sys/cjcx/modules/cjcx/xscjcx\\.do\\?[^\\\\\'\\"\\s<]+)",\n'
    '        text,\n'
    '        re.IGNORECASE,\n'
    '    )\n'
    '    for raw_url in plain_matches:\n'
    '        full_url = urljoin(base_url, html.unescape(raw_url))\n'
    '        if full_url not in urls:\n'
    '            urls.append(full_url)\n'
    '\n'
    '    return urls\n'
    '\n'
    '\n'
    'def find_script_urls(html_text, base_url):\n'
    '    """提取页面引用的 JS 文件地址。"""\n'
    '    urls = []\n'
    '    script_tags = re.findall(r"<script\\b[^>]*>", html_text, re.IGNORECASE)\n'
    '\n'
    '    for tag in script_tags:\n'
    '        src_match = re.search(r"\\bsrc=[\\"\']([^\\"\']+)[\\"\']", tag, re.IGNORECASE)\n'
    '        if not src_match:\n'
    '            continue\n'
    '        src = html.unescape(src_match.group(1))\n'
    '        full_url = urljoin(base_url, src)\n'
    '        if full_url not in urls:\n'
    '            urls.append(full_url)\n'
    '\n'
    '    return urls\n'
    '\n'
    '\n'
    'def collect_grade_api_urls(session, page_response):\n'
    '    """\n'
    '    收集可用成绩接口。\n'
    '    优先使用成绩页或 JS 里带动态参数的接口，最后才使用固定备用接口。\n'
    '    """\n'
    '    urls = []\n'
    '    base_url = page_response.url\n'
    '\n'
    '    for url in find_grade_api_urls_from_text(page_response.text, base_url):\n'
    '        if url not in urls:\n'
    '            urls.append(url)\n'
    '\n'
    '    for script_url in find_script_urls(page_response.text, base_url):\n'
    '        if "cjcx" not in script_url and "emap" not in script_url and "sys" not in script_url:\n'
    '            continue\n'
    '\n'
    '        try:\n'
    '            script_response = session.get(script_url, timeout=20)\n'
    '            if script_response.status_code >= 400:\n'
    '                continue\n'
    '        except Exception:\n'
    '            continue\n'
    '\n'
    '        for url in find_grade_api_urls_from_text(script_response.text, script_url):\n'
    '            if url not in urls:\n'
    '                urls.append(url)\n'
    '\n'
    '    if SEU_GRADE_API_HTTP not in urls:\n'
    '        urls.append(SEU_GRADE_API_HTTP)\n'
    '    if SEU_GRADE_API not in urls:\n'
    '        urls.append(SEU_GRADE_API)\n'
    '\n'
    '    return urls\n'
    '\n'
    '\n'
    'def is_login_response(response):\n'
    '    """判断响应是否其实是统一认证/VPN 登录页。"""\n'
    '    url = response.url.lower()\n'
    '    text = response.text\n'
    '    lower_text = text.lower()\n'
    '\n'
    '    if "vpn.seu.edu.cn" in url and ("login" in url or "shortcut" in url or "portal" in url):\n'
    '        return True\n'
    '    if "authserver" in url or "/login" in url:\n'
    '        return True\n'
    '    if "username" in lower_text and "password" in lower_text:\n'
    '        return True\n'
    '    if "统一身份认证" in text or "统一认证" in text:\n'
    '        return True\n'
    '    if "登录" in text and ("验证码" in text or "短信" in text or "动态码" in text):\n'
    '        return True\n'
    '    return False\n'
    '\n'
    '\n'
    'def http_grade_page():\n'
    '    return SEU_GRADE_PAGE.replace("https://", "http://", 1)\n'
    '\n'
    '\n'
    'def adapt_ehall_url(url, referer):\n'
    '    """把抓包里的 ehall URL 调整到当前 CAS 落地的协议/域名。"""\n'
    '    parsed_ref = urlparse(referer)\n'
    '    parsed_url = urlparse(url)\n'
    '    if parsed_ref.netloc and parsed_url.netloc == "ehall.seu.edu.cn":\n'
    '        return parsed_url._replace(scheme=parsed_ref.scheme, netloc=parsed_ref.netloc).geturl()\n'
    '    return url\n'
    '\n'
    '\n'
    'def origin_from_url(url):\n'
    '    parsed = urlparse(url)\n'
    '    if parsed.scheme and parsed.netloc:\n'
    '        return "{}://{}".format(parsed.scheme, parsed.netloc)\n'
    '    return ""\n'
    '\n'
    '\n'
    'def read_asn1_length(data, index):\n'
    '    first = data[index]\n'
    '    index += 1\n'
    '    if first < 128:\n'
    '        return first, index\n'
    '\n'
    '    length_bytes = first & 0x7F\n'
    '    length = int.from_bytes(data[index:index + length_bytes], "big")\n'
    '    index += length_bytes\n'
    '    return length, index\n'
    '\n'
    '\n'
    'def read_asn1_tlv(data, index):\n'
    '    tag = data[index]\n'
    '    index += 1\n'
    '    length, index = read_asn1_length(data, index)\n'
    '    value = data[index:index + length]\n'
    '    return tag, value, index + length\n'
    '\n'
    '\n'
    'def parse_rsa_public_key(public_key_text):\n'
    '    """解析认证系统返回的 PEM 公钥，得到 RSA 的 n/e。"""\n'
    '    text = str(public_key_text or "").strip()\n'
    '    text = text.replace("\\\\n", "\\n").replace("\\\\r", "\\r")\n'
    '    if "BEGIN" in text:\n'
    '        key_body = re.sub(r"-----BEGIN [^-]+-----", "", text)\n'
    '        key_body = re.sub(r"-----END [^-]+-----", "", key_body)\n'
    '        key_body = re.sub(r"\\s+", "", key_body)\n'
    '    else:\n'
    '        key_body = re.sub(r"\\s+", "", text)\n'
    '\n'
    '    key_body = key_body.replace("-", "+").replace("_", "/")\n'
    '    if len(key_body) % 4:\n'
    '        key_body += "=" * (4 - len(key_body) % 4)\n'
    '\n'
    '    try:\n'
    '        der = base64.b64decode(key_body, validate=False)\n'
    '    except Exception as error:\n'
    '        raise ValueError("无法解析认证公钥，长度={}，开头={}，错误={}".format(\n'
    '            len(str(public_key_text or "")),\n'
    '            str(public_key_text or "")[:30],\n'
    '            error,\n'
    '        ))\n'
    '\n'
    '    tag, seq, _ = read_asn1_tlv(der, 0)\n'
    '    if tag != 0x30:\n'
    '        raise ValueError("公钥格式不是 ASN.1 SEQUENCE")\n'
    '\n'
    '    tag, first, index = read_asn1_tlv(seq, 0)\n'
    '    if tag == 0x02:\n'
    '        tag2, second, _ = read_asn1_tlv(seq, index)\n'
    '        return int.from_bytes(first, "big"), int.from_bytes(second, "big")\n'
    '\n'
    '    tag, bit_string, _ = read_asn1_tlv(seq, index)\n'
    '    if tag != 0x03 or not bit_string:\n'
    '        raise ValueError("公钥格式中没有 BIT STRING")\n'
    '\n'
    '    rsa_der = bit_string[1:]\n'
    '    tag, rsa_seq, _ = read_asn1_tlv(rsa_der, 0)\n'
    '    if tag != 0x30:\n'
    '        raise ValueError("RSA 公钥格式错误")\n'
    '\n'
    '    tag, modulus, index = read_asn1_tlv(rsa_seq, 0)\n'
    '    tag2, exponent, _ = read_asn1_tlv(rsa_seq, index)\n'
    '    if tag != 0x02 or tag2 != 0x02:\n'
    '        raise ValueError("RSA 公钥缺少 modulus/exponent")\n'
    '\n'
    '    return int.from_bytes(modulus, "big"), int.from_bytes(exponent, "big")\n'
    '\n'
    '\n'
    'def rsa_encrypt_pkcs1_v15(public_key_text, plain_text):\n'
    '    """等价于浏览器 JSEncrypt.encrypt，用 RSA/PKCS#1 v1.5 加密并返回 base64。"""\n'
    '    modulus, exponent = parse_rsa_public_key(public_key_text)\n'
    '    key_size = (modulus.bit_length() + 7) // 8\n'
    '    message = str(plain_text).encode("utf-8")\n'
    '    max_len = key_size - 11\n'
    '    if len(message) > max_len:\n'
    '        raise ValueError("待加密内容过长")\n'
    '\n'
    '    padding_len = key_size - len(message) - 3\n'
    '    padding = bytearray()\n'
    '    while len(padding) < padding_len:\n'
    '        chunk = secrets.token_bytes(padding_len - len(padding))\n'
    '        for byte in chunk:\n'
    '            if byte != 0:\n'
    '                padding.append(byte)\n'
    '                if len(padding) == padding_len:\n'
    '                    break\n'
    '\n'
    '    encoded = b"\\x00\\x02" + bytes(padding) + b"\\x00" + message\n'
    '    encrypted = pow(int.from_bytes(encoded, "big"), exponent, modulus)\n'
    '    return base64.b64encode(encrypted.to_bytes(key_size, "big")).decode("ascii")\n'
    '\n'
    '\n'
    'def auth_json_headers():\n'
    '    return {\n'
    '        "Accept": "application/json",\n'
    '        "Content-Type": "application/json",\n'
    '        "Origin": "https://auth.seu.edu.cn",\n'
    '        "Referer": AUTH_DIST,\n'
    '        "User-Agent": "Mozilla/5.0 GPA-Calculator/1.0",\n'
    '    }\n'
    '\n'
    '\n'
    'def extract_auth_field(data, names):\n'
    '    if isinstance(data, dict):\n'
    '        for name in names:\n'
    '            if name in data:\n'
    '                return data.get(name)\n'
    '        for value in data.values():\n'
    '            found = extract_auth_field(value, names)\n'
    '            if found is not None:\n'
    '                return found\n'
    '    return None\n'
    '\n'
    '\n'
    'def post_auth_json(session, path, payload):\n'
    '    url = AUTH_CASBACK + path\n'
    '    response = session.post(url, json=payload, headers=auth_json_headers(), timeout=20, allow_redirects=True)\n'
    '    response.raise_for_status()\n'
    '    return response.json()\n'
    '\n'
    '\n'
    'def extract_public_key(data):\n'
    '    value = extract_auth_field(data, ["publicKey", "key", "rsaPublicKey", "chiperKey", "cipherKey"])\n'
    '    if value is None:\n'
    '        return ""\n'
    '    text = str(value).strip()\n'
    '    if "BEGIN" in text:\n'
    '        return text\n'
    '    body = re.sub(r"\\s+", "", text)\n'
    '    if body.startswith("MIG") or body.startswith("MFw") or body.startswith("MIIB"):\n'
    '        return body\n'
    '    return text\n'
    '\n'
    '\n'
    'def extract_phone_from_message(message):\n'
    '    match = re.search(r"1\\d{10}", str(message or ""))\n'
    '    if match:\n'
    '        return match.group(0)\n'
    '    return ""\n'
    '\n'
    '\n'
    'def finish_auth_redirect(session, login_data):\n'
    '    redirect_url = ""\n'
    '    if isinstance(login_data, dict):\n'
    '        redirect_url = str(login_data.get("redirectUrl") or login_data.get("redirectURL") or "")\n'
    '\n'
    '    if redirect_url:\n'
    '        target_url = unquote(redirect_url)\n'
    '        if target_url.startswith("http://") or target_url.startswith("https://"):\n'
    '            response = session.get(target_url, timeout=20, allow_redirects=True)\n'
    '        else:\n'
    '            response = session.get(\n'
    '                AUTH_CASBACK + "/loginRedirect?redirectUrl=" + redirect_url,\n'
    '                headers={"Referer": AUTH_DIST, "User-Agent": "Mozilla/5.0 GPA-Calculator/1.0"},\n'
    '                timeout=20,\n'
    '                allow_redirects=True,\n'
    '            )\n'
    '        response.raise_for_status()\n'
    '        return True\n'
    '\n'
    '    verify_data = post_auth_json(session, "/verifyTgt", {"service": SEU_CAS_SERVICE, "loginType": "account"})\n'
    '    redirect_url = str(verify_data.get("redirectUrl") or "")\n'
    '    if redirect_url:\n'
    '        response = session.get(redirect_url, timeout=20, allow_redirects=True)\n'
    '        response.raise_for_status()\n'
    '        return True\n'
    '\n'
    '    response = session.get(http_grade_page(), timeout=20, allow_redirects=True)\n'
    '    response.raise_for_status()\n'
    '    return not is_login_response(response)\n'
    '\n'
    '\n'
    'def login_with_new_auth_api(session, username, password):\n'
    '    """使用 auth.seu.edu.cn/dist 新版 JSON 接口登录，只要求账号、密码和短信验证码。"""\n'
    '    init_response = session.get(AUTH_DIST, headers={"User-Agent": "Mozilla/5.0 GPA-Calculator/1.0"}, timeout=20)\n'
    '    init_response.raise_for_status()\n'
    '\n'
    '    key_data = post_auth_json(session, "/getChiperKey", {})\n'
    '    public_key = extract_public_key(key_data)\n'
    '    if not public_key:\n'
    '        print("自动登录失败：没有拿到加密公钥。")\n'
    '        return False\n'
    '\n'
    '    encrypted_password = rsa_encrypt_pkcs1_v15(public_key, password)\n'
    '    payload = {\n'
    '        "service": SEU_CAS_SERVICE,\n'
    '        "username": username,\n'
    '        "password": encrypted_password,\n'
    '        "captcha": "",\n'
    '        "rememberMe": False,\n'
    '        "loginType": "account",\n'
    '        "wxBinded": False,\n'
    '        "mobilePhoneNum": "",\n'
    '        "fingerPrint": hashlib.md5((username + str(uuid.uuid4())).encode("utf-8")).hexdigest(),\n'
    '    }\n'
    '    login_data = post_auth_json(session, "/casLogin", payload)\n'
    '    code = login_data.get("code") if isinstance(login_data, dict) else None\n'
    '\n'
    '    if code == 502 or str(code) == "502":\n'
    '        try:\n'
    '            send_data = post_auth_json(session, "/sendStage2Code", {"userId": username})\n'
    '            msg = send_data.get("info") or send_data.get("msg") or send_data.get("message")\n'
    '            phone = extract_phone_from_message(msg)\n'
    '            if phone:\n'
    '                print("短信验证码已发送到", phone)\n'
    '            else:\n'
    '                print("短信验证码已发送，请查看手机。")\n'
    '        except Exception as error:\n'
    '            print("自动发送短信验证码失败：", error)\n'
    '\n'
    '        sms_code = input("请输入手机短信验证码：").strip()\n'
    '        if sms_code == "":\n'
    '            print("短信验证码为空，取消自动登录。")\n'
    '            return False\n'
    '\n'
    '        key_data = post_auth_json(session, "/getChiperKey", {})\n'
    '        public_key = extract_public_key(key_data)\n'
    '        if not public_key:\n'
    '            print("自动登录失败：没有拿到二次验证加密公钥。")\n'
    '            return False\n'
    '        encrypted_password = rsa_encrypt_pkcs1_v15(public_key, password)\n'
    '        encrypted_sms_code = rsa_encrypt_pkcs1_v15(public_key, sms_code)\n'
    '        payload["password"] = encrypted_password\n'
    '        payload["mobileVerifyCode"] = encrypted_sms_code\n'
    '        login_data = post_auth_json(session, "/casLogin", payload)\n'
    '        code = login_data.get("code") if isinstance(login_data, dict) else None\n'
    '\n'
    '    if str(code) != "200":\n'
    '        msg = ""\n'
    '        if isinstance(login_data, dict):\n'
    '            msg = str(login_data.get("info") or login_data.get("msg") or login_data.get("message") or login_data)\n'
    '        print("认证登录失败：", msg or login_data)\n'
    '        return False\n'
    '\n'
    '    return finish_auth_redirect(session, login_data)\n'
    '\n'
    '\n'
    'def get_headers_from_packet(packet, referer):\n'
    '    headers = {\n'
    '        "Accept": "application/json, text/javascript, */*; q=0.01",\n'
    '        "X-Requested-With": "XMLHttpRequest",\n'
    '        "Referer": referer,\n'
    '    }\n'
    '\n'
    '    request_headers = {}\n'
    '    if packet:\n'
    '        request_headers.update(packet.get("request", {}).get("headers", {}))\n'
    '        request_headers.update(packet.get("requestExtraHeaders", {}))\n'
    '\n'
    '    keep_headers = ["K2iiimxl", "k2iiimxl", "Origin", "User-Agent"]\n'
    '    for key, value in request_headers.items():\n'
    '        if key in keep_headers:\n'
    '            headers[key] = value\n'
    '\n'
    '    current_origin = origin_from_url(referer)\n'
    '    if current_origin:\n'
    '        headers["Origin"] = current_origin\n'
    '    headers["Referer"] = referer\n'
    '\n'
    '    return headers\n'
    '\n'
    '\n'
    'def get_payload_from_packet(packet, page_number):\n'
    '    payload = {\n'
    '        "pageSize": "100",\n'
    '        "pageNumber": str(page_number),\n'
    '        "*order": "-XNXQDM,-KCH,-KXH",\n'
    '        "querySetting": \'[{"name":"SHOWMAXCJ","caption":"显示最高成绩","linkOpt":"AND","builderList":"cbl_String","builder":"equal","value":0,"value_display":"否"}]\',\n'
    '    }\n'
    '\n'
    '    if packet:\n'
    '        post_data = packet.get("request", {}).get("postData", "")\n'
    '        parsed = parse_qs(post_data, keep_blank_values=True)\n'
    '        for key, values in parsed.items():\n'
    '            if values:\n'
    '                payload[key] = values[0]\n'
    '        payload["pageSize"] = "100"\n'
    '        payload["pageNumber"] = str(page_number)\n'
    '\n'
    '    return payload\n'
    '\n'
    '\n'
    'def fetch_grades_with_saved_packet_templates(session, referer):\n'
    '    """登录成功后，复用 browser_packets.json 里的成绩接口模板请求当前账号成绩。"""\n'
    '    packet_path = "browser_packets.json"\n'
    '    if not os.path.exists(packet_path):\n'
    '        return []\n'
    '\n'
    '    try:\n'
    '        with open(packet_path, "r", encoding="utf-8") as f:\n'
    '            packets = json.load(f)\n'
    '    except Exception as error:\n'
    '        print("读取 browser_packets.json 失败：", error)\n'
    '        return []\n'
    '\n'
    '    if not isinstance(packets, list):\n'
    '        return []\n'
    '\n'
    '    packet_by_url = {}\n'
    '    for packet in packets:\n'
    '        url = packet.get("request", {}).get("url", "")\n'
    '        if "xscjcx.do" in url:\n'
    '            packet_by_url[url] = packet\n'
    '\n'
    '    if not packet_by_url:\n'
    '        return []\n'
    '\n'
    '    grade_urls = list(packet_by_url.keys())\n'
    '    grade_urls.sort(key=lambda url: "pageSize=100" not in packet_by_url[url].get("request", {}).get("postData", ""))\n'
    '\n'
    '    for url in grade_urls:\n'
    '        url = adapt_ehall_url(url, referer)\n'
    '        sample_packet = packet_by_url.get(url)\n'
    '        if not sample_packet:\n'
    '            original_url = None\n'
    '            for candidate in packet_by_url:\n'
    '                if adapt_ehall_url(candidate, referer) == url:\n'
    '                    original_url = candidate\n'
    '                    break\n'
    '            if original_url:\n'
    '                sample_packet = packet_by_url[original_url]\n'
    '            else:\n'
    '                continue\n'
    '\n'
    '        headers = get_headers_from_packet(sample_packet, referer)\n'
    '        if "Cookie" in headers:\n'
    '            del headers["Cookie"]\n'
    '\n'
    '        all_rows = []\n'
    '        total_size = None\n'
    '        for page_number in range(1, 51):\n'
    '            payload = get_payload_from_packet(sample_packet, page_number)\n'
    '            try:\n'
    '                response = session.post(url, data=payload, headers=headers, timeout=20, allow_redirects=True)\n'
    '            except Exception as error:\n'
    '                break\n'
    '\n'
    '            try:\n'
    '                data = response.json()\n'
    '            except ValueError:\n'
    '                break\n'
    '\n'
    '            rows = find_rows(data)\n'
    '            if total_size is None:\n'
    '                total_size = find_total_size(data)\n'
    '\n'
    '            if not rows:\n'
    '                break\n'
    '\n'
    '            all_rows.extend(rows)\n'
    '            if total_size is not None and len(all_rows) >= total_size:\n'
    '                break\n'
    '            if len(rows) < 100:\n'
    '                break\n'
    '\n'
    '        if all_rows:\n'
    '            return rows_to_courses(all_rows)\n'
    '\n'
    '    return []\n'
    '\n'
    '\n'
    'def fetch_grades_from_seu():\n'
    '    """\n'
    '    尝试自动登录并抓取成绩。\n'
    '    由于学校统一身份认证可能出现短信验证码/动态字段/接口变动，失败时建议使用返回包导入。\n'
    '    """\n'
    '    try:\n'
    '        import requests\n'
    '    except ImportError:\n'
    '        print("当前环境未安装 requests，无法自动联网获取。请改用返回包，或先安装 requests。")\n'
    '        return []\n'
    '\n'
    '    username = input("统一身份认证账号：").strip()\n'
    '    password = getpass.getpass("统一身份认证密码（输入时不显示）：")\n'
    '\n'
    '    if username == "" or password == "":\n'
    '        print("账号或密码为空。")\n'
    '        return []\n'
    '\n'
    '    session = requests.Session()\n'
    '    session.headers.update({\n'
    '        "User-Agent": "Mozilla/5.0 GPA-Calculator/1.0",\n'
    '        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",\n'
    '    })\n'
    '\n'
    '    try:\n'
    '        if not login_with_new_auth_api(session, username, password):\n'
    '            return []\n'
    '\n'
    '        page_response = session.get(http_grade_page(), timeout=20, allow_redirects=True)\n'
    '        page_response.raise_for_status()\n'
    '        if is_login_response(page_response):\n'
    '            print("打开成绩应用时仍被要求登录，自动获取失败。")\n'
    '            return []\n'
    '\n'
    '        grade_api_urls = collect_grade_api_urls(session, page_response)\n'
    '\n'
    '        courses = fetch_grades_with_saved_packet_templates(session, page_response.url)\n'
    '        if courses:\n'
    '            print("已获取", len(courses), "门课程。")\n'
    '            return courses\n'
    '\n'
    '        request_payloads = [\n'
    '            {\n'
    '                "pageSize": "100",\n'
    '                "pageNumber": "1",\n'
    '                "*order": "-XNXQDM,-KCH,-KXH",\n'
    '                "querySetting": \'[{"name":"SHOWMAXCJ","caption":"显示最高成绩","linkOpt":"AND","builderList":"cbl_String","builder":"equal","value":0,"value_display":"否"}]\',\n'
    '            },\n'
    '        ]\n'
    '\n'
    '        api_headers = {\n'
    '            "Accept": "application/json, text/javascript, */*; q=0.01",\n'
    '            "X-Requested-With": "XMLHttpRequest",\n'
    '            "Referer": page_response.url,\n'
    '        }\n'
    '\n'
    '        for grade_api_url in grade_api_urls:\n'
    '            for payload_template in request_payloads:\n'
    '                all_rows = []\n'
    '                total_size = None\n'
    '                page_number = 1\n'
    '\n'
    '                while page_number <= 50:\n'
    '                    payload = {}\n'
    '                    for key, value in payload_template.items():\n'
    '                        payload[key] = value\n'
    '                    payload["pageSize"] = "100"\n'
    '                    payload["pageNumber"] = str(page_number)\n'
    '\n'
    '                    api_response = session.post(\n'
    '                        adapt_ehall_url(grade_api_url, page_response.url),\n'
    '                        data=payload,\n'
    '                        timeout=20,\n'
    '                        headers=api_headers,\n'
    '                    )\n'
    '\n'
    '                    if api_response.status_code >= 400:\n'
    '                        break\n'
    '\n'
    '                    try:\n'
    '                        data = api_response.json()\n'
    '                    except ValueError:\n'
    '                        break\n'
    '\n'
    '                    rows = find_rows(data)\n'
    '                    if total_size is None:\n'
    '                        total_size = find_total_size(data)\n'
    '\n'
    '                    if not rows:\n'
    '                        break\n'
    '\n'
    '                    all_rows.extend(rows)\n'
    '\n'
    '                    if total_size is not None and len(all_rows) >= total_size:\n'
    '                        break\n'
    '                    if len(rows) < 100:\n'
    '                        break\n'
    '\n'
    '                    page_number += 1\n'
    '\n'
    '                if all_rows:\n'
    '                    courses = rows_to_courses(all_rows)\n'
    '                    print("已获取", len(courses), "门课程。")\n'
    '                    return courses\n'
    '\n'
    '        print("自动获取成绩失败，请改用返回包 JSON 导入。")\n'
    '    except Exception as error:\n'
    '        print("自动获取失败：", error)\n'
    '\n'
    '    return []\n'
    '\n'
    '\n'
    'def main_menu():\n'
    '    courses = []\n'
    '    view_courses = []\n'
    '\n'
    '    while True:\n'
    '        print()\n'
    '        print("====== 东南大学绩点计算器 ======")\n'
    '        print("1. 输入账号密码和验证码自动获取成绩")\n'
    '        print("2. 用户提供返回包 JSON")\n'
    '        print("3. 手动录入成绩")\n'
    '        print("0. 退出")\n'
    '\n'
    '        choice = input("请选择：").strip()\n'
    '\n'
    '        if choice == "1":\n'
    '            courses = fetch_grades_from_seu()\n'
    '        elif choice == "2":\n'
    '            courses = load_from_json_flow()\n'
    '        elif choice == "3":\n'
    '            courses = input_courses_manually()\n'
    '        elif choice == "0":\n'
    '            print("已退出。")\n'
    '            return\n'
    '        else:\n'
    '            print("选择无效，请重新输入。")\n'
    '            continue\n'
    '\n'
    '        if not courses:\n'
    '            print("没有获取到成绩数据，请重新选择数据来源。")\n'
    '            continue\n'
    '\n'
    '        view_courses = courses[:]\n'
    '        print_transcript(view_courses)\n'
    '        after_calculation_menu(courses, view_courses)\n'
    '\n'
    '\n'
    'def after_calculation_menu(courses, view_courses):\n'
    '    while True:\n'
    '        print()\n'
    '        print("====== 后续操作 ======")\n'
    '        print("1. 新增课程")\n'
    '        print("2. 删除课程")\n'
    '        print("3. 修改课程")\n'
    '        print("4. 按成绩排序")\n'
    '        print("5. 按学分排序")\n'
    '        print("6. 筛选成绩单")\n'
    '        print("7. 恢复完整成绩单")\n'
    '        print("8. 保存为 txt")\n'
    '        print("9. 导出为 Excel")\n'
    '        print("10. 重新选择数据来源")\n'
    '        print("0. 退出")\n'
    '\n'
    '        choice = input("请选择：").strip()\n'
    '\n'
    '        if choice == "1":\n'
    '            add_course(courses)\n'
    '            view_courses = courses[:]\n'
    '            print_transcript(view_courses)\n'
    '        elif choice == "2":\n'
    '            delete_course(courses)\n'
    '            view_courses = courses[:]\n'
    '            print_transcript(view_courses)\n'
    '        elif choice == "3":\n'
    '            update_course(courses)\n'
    '            view_courses = courses[:]\n'
    '            print_transcript(view_courses)\n'
    '        elif choice == "4":\n'
    '            reverse = input("成绩是否降序？(Y/n)：").strip().lower() != "n"\n'
    '            view_courses = sorted(view_courses, key=lambda course: course["score"], reverse=reverse)\n'
    '            print_transcript(view_courses)\n'
    '        elif choice == "5":\n'
    '            reverse = input("学分是否降序？(Y/n)：").strip().lower() != "n"\n'
    '            view_courses = sorted(view_courses, key=lambda course: course["credit"], reverse=reverse)\n'
    '            print_transcript(view_courses)\n'
    '        elif choice == "6":\n'
    '            view_courses = filter_courses(view_courses)\n'
    '            print_transcript(view_courses)\n'
    '        elif choice == "7":\n'
    '            view_courses = courses[:]\n'
    '            print("已恢复完整成绩单。")\n'
    '            print_transcript(view_courses)\n'
    '        elif choice == "8":\n'
    '            path = input("保存路径（默认 成绩单.txt）：").strip()\n'
    '            if path == "":\n'
    '                path = "成绩单.txt"\n'
    '            save_txt(view_courses, path)\n'
    '            print("已保存：", os.path.abspath(path))\n'
    '        elif choice == "9":\n'
    '            path = input("导出路径（默认 成绩单.xlsx）：").strip()\n'
    '            if path == "":\n'
    '                path = "成绩单.xlsx"\n'
    '            actual_path = export_excel(view_courses, path)\n'
    '            if actual_path:\n'
    '                print("已导出：", os.path.abspath(actual_path))\n'
    '        elif choice == "10":\n'
    '            return\n'
    '        elif choice == "0":\n'
    '            print("已退出。")\n'
    '            sys.exit(0)\n'
    '        else:\n'
    '            print("选择无效，请重新输入。")\n'
    '\n'
    '\n'
    'if __name__ == "__main__":\n'
    '    try:\n'
    '        main_menu()\n'
    '    except KeyboardInterrupt:\n'
    '        print("\\n已中断。")\n'
    '        sys.exit(130)\n'
)
_ORIGINAL_CODE = compile(ORIGINAL_SCRIPT, "<内嵌的42225129大作业原稿>", "exec")

def score_to_grade_point(score, scale=4.8):
    """参考网站的东南大学分段方案；小数成绩按下限归档，不做插值。"""
    import math
    if scale not in (4.0, 4.8):
        raise ValueError("只支持 4.0 或 4.8 制")
    score = float(score)
    if not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError("成绩必须是 0 到 100 之间的有限数字")
    for minimum, point in [(96, 4.8), (93, 4.5), (90, 4.0), (86, 3.8),
                           (83, 3.5), (80, 3.0), (76, 2.8), (73, 2.5),
                           (70, 2.0), (66, 1.8), (63, 1.5), (60, 1.0)]:
        if score >= minimum:
            return min(point, scale)
    return 0.0

def parse_float(value, default=None):
    """把字符串、整数、小数等转换成 float。"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if text == "":
        return default
    if text.startswith("."):
        text = "0" + text

    try:
        return float(text)
    except ValueError:
        return default

def grade_name_to_score(value):
    """把等级制成绩粗略换算为百分制成绩，便于纳入平均分和绩点计算。"""
    if value is None:
        return None

    text = str(value).strip()
    mapping = {
        "优秀": 95.0,
        "良好": 85.0,
        "优": 95.0,
        "良": 85.0,
        "中": 75.0,
        "及格": 65.0,
        "合格": 65.0,
        "通过": 65.0,
        "不及格": 0.0,
        "不合格": 0.0,
        "未通过": 0.0,
    }
    return mapping.get(text)

def get_score_from_row(row):
    """从教务返回包的一条课程记录里取出可计算成绩。"""
    possible_keys = ["ZCJ", "XSZCJMC", "ZCJ_DISPLAY", "QMCJ", "QMCJ_DISPLAY"]
    for key in possible_keys:
        value = row.get(key)
        score = parse_float(value)
        if score is not None:
            return score

        score = grade_name_to_score(value)
        if score is not None:
            return score

    return None

def is_optional_course(row, course_type):
    """判断是否为任选课程。"""
    display = str(row.get("KCXZDM_DISPLAY") or course_type or "")
    code = str(row.get("KCXZDM") or "")
    category = str(row.get("KCLBDM_DISPLAY") or "")
    return "任选" in display or code == "02" or "通识选修" in category

def find_rows(data):
    """
    从返回包中查找 rows 列表。
    兼容 datas.xscjcx.rows、直接 rows、列表等结构。
    """
    if isinstance(data, list):
        rows = []
        for item in data:
            if isinstance(item, dict):
                rows.append(item)
        return rows

    if not isinstance(data, dict):
        return []

    if isinstance(data.get("rows"), list):
        rows = []
        for item in data["rows"]:
            if isinstance(item, dict):
                rows.append(item)
        return rows

    datas = data.get("datas")
    if isinstance(datas, dict):
        for value in datas.values():
            if isinstance(value, dict) and isinstance(value.get("rows"), list):
                rows = []
                for item in value["rows"]:
                    if isinstance(item, dict):
                        rows.append(item)
                return rows

    for value in data.values():
        rows = find_rows(value)
        if rows:
            return rows

    return []

def find_total_size(data):
    """从返回包中查找 totalSize，用于判断是否已经翻页取完。"""
    if not isinstance(data, dict):
        return None

    total_size = parse_float(data.get("totalSize"))
    if total_size is not None:
        return int(total_size)

    datas = data.get("datas")
    if isinstance(datas, dict):
        for value in datas.values():
            if isinstance(value, dict):
                total_size = parse_float(value.get("totalSize"))
                if total_size is not None:
                    return int(total_size)

    for value in data.values():
        total_size = find_total_size(value)
        if total_size is not None:
            return total_size

    return None

def extract_json_from_text(text):
    """
    从纯 JSON 或“请求头/响应头 + JSON + 其他内容”中提取 JSON。
    用户从浏览器抓包复制出来的内容通常不是纯 JSON，所以这里用 raw_decode 自动截取。
    """
    text = text.strip()
    if text == "":
        return None

    decoder = json.JSONDecoder()

    try:
        return decoder.decode(text)
    except ValueError:
        pass

    candidate_positions = []
    for marker in ['{"datas"', '{"rows"', '[{']:
        position = text.find(marker)
        if position != -1:
            candidate_positions.append(position)

    for i, char in enumerate(text):
        if char == "{" or char == "[":
            candidate_positions.append(i)

    used_positions = []
    for position in candidate_positions:
        if position in used_positions:
            continue
        used_positions.append(position)

        try:
            data, end_index = decoder.raw_decode(text[position:])
        except ValueError:
            continue

        if find_rows(data):
            return data

    return None

def make_course(name, score, credit, course_type="", semester="", course_code="", raw=None,
                excluded=False, exclude_reason=""):
    """用字典存储一门课程。"""
    return {
        "name": name,
        "score": float(score),
        "credit": float(credit),
        "grade_point": score_to_grade_point(float(score)),
        "course_type": course_type,
        "semester": str(semester or "").strip(),
        "course_code": course_code,
        "raw": raw or {},
        "excluded": excluded,
        "exclude_reason": exclude_reason,
    }

def rows_to_courses(rows):
    """把教务 rows 转换为课程字典列表。"""
    courses = []
    skipped = 0

    for row in rows:
        name = str(row.get("KCM") or row.get("XSKCM") or row.get("TDKCM") or "未命名课程")
        score = get_score_from_row(row)
        credit = parse_float(row.get("XF"), 0.0)

        if score is None or credit is None or credit <= 0:
            skipped += 1
            continue

        course_type = str(row.get("KCXZDM_DISPLAY") or "")
        excluded = is_optional_course(row, course_type)
        course = make_course(
            name=name,
            score=score,
            credit=credit,
            course_type=course_type,
            semester=semester_from_row(row),
            course_code=str(row.get("KCH") or row.get("XSKCH") or ""),
            raw=row,
            excluded=excluded,
            exclude_reason="任选课程" if excluded else "",
        )
        courses.append(course)

    if skipped > 0:
        _backend_print("提示：有", skipped, "条记录缺少可计算成绩或学分，已跳过。")

    return courses

class _OriginalCancelled(BaseException):
    pass


class OriginalScriptRun:
    """原稿全文直接运行；只把终端输入输出连接到 GUI，不改网络函数。"""
    def __init__(self, username, password, sms_callback, status_callback=None, cancel_event=None):
        self.username, self.password = username, password
        self.sms_callback, self.status_callback = sms_callback, status_callback
        self.cancel_event = cancel_event
        self.namespace = None
        self.last_message, self.last_response = "", ""
        self.last_observed_response = None
        self.network_hint = ""
        self.last_report = None

    def cancelled(self):
        return self.cancel_event is not None and self.cancel_event.is_set()

    def report(self, stage, detail):
        if self.status_callback and (stage, detail) != self.last_report:
            self.last_report = (stage, detail)
            self.status_callback(stage, detail)

    def private_text(self, text):
        for value in (self.password, self.username):
            if value:
                text = text.replace(value, "***")
        text = re.sub(r"(?<!\d)1\d{10}(?!\d)", "[手机号]", text)
        return re.sub(r"(?i)((?:password|token|ticket|cookie|mobileVerifyCode)[\"']?\s*[:=]\s*)[^\s,}]+", r"\1[已隐藏]", text)

    def output(self, *args, **kwargs):
        text = self.private_text(kwargs.get("sep", " ").join(map(str, args)))
        if text.strip():
            self.last_message = text
            _backend_print(text)

    def read_input(self, prompt=""):
        if self.cancelled():
            raise _OriginalCancelled()
        if "账号" in prompt:
            return self.username
        if "验证码" in prompt:
            self.report("awaiting_sms", "请输入收到的短信验证码。")
            return self.sms_callback() if self.sms_callback else builtins.input(prompt)
        raise RuntimeError("暂不支持当前输入请求：" + prompt)

    def read_password(self, prompt="", *args, **kwargs):
        if self.cancelled():
            raise _OriginalCancelled()
        return self.password

    def prepare(self):
        namespace = {"__name__":"_embedded_seu_reference", "__file__":__file__}
        local_builtins = vars(builtins).copy()
        original_import = builtins.__import__
        getpass_adapter = types.ModuleType("getpass")
        getpass_adapter.getpass = self.read_password
        def local_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "getpass" and level == 0:
                return getpass_adapter
            return original_import(name, globals, locals, fromlist, level)
        local_builtins.update(input=self.read_input, print=self.output, __import__=local_import)
        namespace["__builtins__"] = local_builtins
        self.namespace = namespace
        exec(_ORIGINAL_CODE, namespace)
        return namespace

    def observe_response(self, response):
        if response is None or response is self.last_observed_response:
            return
        self.last_observed_response = response
        # 只读元信息；不读取 Cookie，不更换会话，也不消费或改写响应。
        parsed = urlparse(str(getattr(response, "url", "")))
        endpoint = parsed._replace(query="", fragment="").geturl()
        status = getattr(response, "status_code", "?")
        headers = getattr(response, "headers", {})
        content_type = headers.get("Content-Type", "未提供类型")
        text = getattr(response, "text", "")
        title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I|re.S)
        self.last_response = "连接信息：{}；HTTP {}；{}".format(endpoint, status, content_type)
        if title:
            self.last_response += "；页面标题：" + re.sub(r"\s+", " ", html.unescape(title.group(1)))[:70]
        self.last_response = self.private_text(self.last_response)
        self.network_hint = ""
        if parsed.hostname == "vpn.seu.edu.cn" and parsed.path.startswith(("/portal/", "/controller/")) and "json" not in content_type.lower():
            self.network_hint = "当前请求进入了 VPN 门户，未返回教务成绩。请检查 VPN / 代理设置是否影响教务访问，调整后重试。"

    def trace(self, frame, event, arg):
        if frame.f_globals is not self.namespace:
            return None
        if self.cancelled():
            raise _OriginalCancelled()
        try:
            name = frame.f_code.co_name
            if event == "call":
                if name == "finish_auth_redirect":
                    self.report("session", "正在连接教务系统…")
                elif name == "collect_grade_api_urls":
                    self.report("fetching", "正在准备成绩查询…")
                elif name == "fetch_grades_with_saved_packet_templates":
                    present = Path("browser_packets.json").is_file()
                    self.report("fetching", "正在加载查询配置…" if present else "正在尝试可用的成绩接口…")
                elif name == "post_auth_json":
                    path = frame.f_locals.get("path", "")
                    stages = {"/getChiperKey":("checking", "正在建立安全认证…"),
                              "/casLogin":("checking", "正在校验账号密码或短信验证码…"),
                              "/sendStage2Code":("sms_required", "正在申请短信验证码…"),
                              "/verifyTgt":("session", "正在连接教务系统…")}
                    if path in stages:
                        self.report(*stages[path])
                if name == "collect_grade_api_urls":
                    frame.f_trace_lines = False
                elif name not in ("fetch_grades_from_seu", "fetch_grades_with_saved_packet_templates"):
                    return None
            elif event == "return" and name == "collect_grade_api_urls":
                self.report("fetching", "查询已准备好，正在读取课程…")
            elif event == "line" and name in ("fetch_grades_from_seu", "fetch_grades_with_saved_packet_templates"):
                response = frame.f_locals.get("api_response")
                if response is None:
                    response = frame.f_locals.get("response")
                if response is None:
                    response = frame.f_locals.get("page_response")
                self.observe_response(response)
        except Exception:
            # 观察失败不影响原稿的任何网络分支。
            pass
        return self.trace

    def run(self):
        previous_trace = sys.gettrace()
        try:
            namespace = self.prepare()
            self.report("checking", "正在验证账号密码并获取教务成绩…")
            sys.settrace(self.trace)
            result = namespace["fetch_grades_from_seu"]()
            if not result and not self.cancelled():
                detail = self.network_hint or self.last_message or "暂未获取到成绩，请稍后重试。"
                if self.last_response:
                    detail += "\n" + self.last_response
                self.report("grades_failed", detail)
            return result
        except _OriginalCancelled:
            return []
        finally:
            sys.settrace(previous_trace)
            self.username = self.password = ""
            self.sms_callback = self.status_callback = None
            self.last_report = None
            self.last_observed_response = None
            if self.namespace is not None:
                self.namespace.clear()
                self.namespace = None


def fetch_grades_from_seu(username, password, sms_callback=None, status_callback=None, cancel_event=None):
    return OriginalScriptRun(username, password, sms_callback, status_callback, cancel_event).run()

ROOT = Path(__file__).resolve().parent

CHINA_TIME = timezone(timedelta(hours=8))

RULES = [(96, 4.8), (93, 4.5), (90, 4.0), (86, 3.8), (83, 3.5),
         (80, 3.0), (76, 2.8), (73, 2.5), (70, 2.0), (66, 1.8),
         (63, 1.5), (60, 1.0), (0, 0.0)]

def semester_from_row(row):
    for key in ("semester", "XNXQDM_DISPLAY", "XNXQMC", "XNXQDM", "XNXQ", "XQMC"):
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    raw = row.get("raw")
    return semester_from_row(raw) if isinstance(raw, dict) and raw is not row else ""


def normalize(row):
    if not isinstance(row, dict):
        raise ValueError("课程记录必须是对象")
    name = str(row.get("name", "")).strip()
    if not name:
        raise ValueError("课程名称不能为空")
    score = parse_float(row.get("score"))
    if score is None:
        score = grade_name_to_score(row.get("score"))
    credit = parse_float(row.get("credit"))
    if score is None or not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError(f"{name}：成绩须在 0–100 之间，也可填写优秀、良好等等级")
    if credit is None or not math.isfinite(credit) or credit <= 0:
        raise ValueError(f"{name}：学分须为大于 0 的有限数字")
    kind = str(row.get("course_type", ""))
    excluded = row.get("excluded", "任选" in kind)
    if isinstance(excluded, str):
        if excluded.lower() not in ("true", "false", "1", "0", "是", "否"):
            raise ValueError(f"{name}：排除标记不正确")
        excluded = excluded.lower() in ("true", "1", "是")
    if not isinstance(excluded, bool):
        raise ValueError(f"{name}：排除标记须为布尔值")
    return make_course(name, score, credit, kind,
                              semester_from_row(row), str(row.get("course_code", "")),
                              excluded=excluded,
                              exclude_reason=str(row.get("exclude_reason", "手动排除")) if excluded else "")

def summary(courses):
    included = [c for c in courses if not c["excluded"]]
    credits = sum(c["credit"] for c in included)
    avg = sum(c["score"] * c["credit"] for c in included) / credits if credits else 0
    result = {"count": len(included), "excluded": len(courses) - len(included),
              "credits": credits, "average": avg,
              "passed": sum(c["score"] >= 60 for c in included)}
    for scale in (4.0, 4.8):
        result[str(scale)] = sum(score_to_grade_point(c["score"], scale) * c["credit"]
                                 for c in included) / credits if credits else 0
        result[f"reference{scale}"] = score_to_grade_point(avg, scale) if credits else 0
    return result

def import_text(text, suffix=".json"):
    if suffix.lower() == ".csv":
        rows = list(csv.DictReader(io.StringIO(text.lstrip("\ufeff"))))
    else:
        data = extract_json_from_text(text.lstrip("\ufeff"))
        if isinstance(data, dict) and "courses" in data:
            rows = data["courses"]
        elif isinstance(data, list):
            rows = data
        else:
            rows = find_rows(data)
        if not isinstance(rows, list):
            raise ValueError("未找到课程列表")
    if not rows:
        raise ValueError("文件中没有课程记录")
    courses, errors = [], []
    for i, row in enumerate(rows, 1):
        try:
            if isinstance(row, dict) and any(k in row for k in ("KCM", "XSKCM", "TDKCM")):
                score = get_score_from_row(row)
                kind = str(row.get("KCXZDM_DISPLAY") or "")
                row = {"name": row.get("KCM") or row.get("XSKCM") or row.get("TDKCM"),
                       "score": score, "credit": row.get("XF"), "course_type": kind,
                       "semester": semester_from_row(row),
                       "course_code": row.get("KCH") or row.get("XSKCH") or "",
                       "excluded": is_optional_course(row, kind), "exclude_reason": "任选课程"}
            courses.append(normalize(row))
        except (ValueError, TypeError) as error:
            errors.append(f"第 {i} 条：{error}")
    return courses, errors

def clean_courses(courses):
    # 白名单重建课程，不把原始响应、账号或额外字段写入磁盘。
    return [{k: v for k, v in normalize(c).items() if k != "raw"} for c in courses]

def atomic_json(path, data):
    path = Path(path)
    text = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".gpa-", suffix=".tmp", delete=False) as f:
            tmp = Path(f.name)
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)

def save_session(path, courses):
    """用户主动导出的 JSON 备份。"""
    atomic_json(path, {"version": 1, "courses": clean_courses(courses)})

class SnapshotLog:
    """手动保存一次生成一个独立 JSON，不自动合并或覆盖历史记录。"""
    def __init__(self, directory=None, now=None):
        self.directory = Path(directory) if directory is not None else ROOT / "log"
        self.now = now or (lambda: datetime.now(CHINA_TIME))

    @staticmethod
    def read(path):
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        if (not isinstance(data, dict) or data.get("version") != 2
                or not isinstance(data.get("courses"), list) or not isinstance(data.get("records"), list)):
            raise ValueError("日志格式不正确")
        data["courses"] = clean_courses(data["courses"])
        return data

    def load_latest(self):
        warnings = []
        if not self.directory.exists():
            return [], None, warnings
        candidates = []
        for path in self.directory.glob("*.json"):
            try:
                datetime.strptime(path.stem[:10], "%Y-%m-%d")
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:_\d{2}-\d{2}-\d{2}-\d{6}(?:_\d{3,})?)?", path.stem):
                    continue
                candidates.append(path)
            except ValueError:
                continue
        for path in sorted(candidates, reverse=True):
            try:
                data = self.read(path)
                return [normalize(c) for c in data["courses"]], path, warnings
            except (OSError, ValueError, TypeError):
                warnings.append(path.name)
        return [], None, warnings

    def save(self, courses, records=()):
        now = self.now().astimezone(CHINA_TIME)
        stem = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
        path = self.directory / f"{stem}.json"
        counter = 1
        while path.exists():
            path = self.directory / f"{stem}_{counter:03d}.json"
            counter += 1
        clean = clean_courses(courses)
        stamp = now.isoformat(timespec="microseconds")
        data = {"version": 2, "date": now.strftime("%Y-%m-%d"), "timezone": "Asia/Shanghai",
                "saved_at": stamp, "updated_at": stamp, "courses": clean,
                "summary": summary(clean), "records": list(records)}
        atomic_json(path, data)
        return path

def export_csv(path, courses):
    fields = ["name", "score", "credit", "course_type", "semester", "course_code", "excluded", "exclude_reason"]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields + ["gpa4.0", "gpa4.8"])
        writer.writeheader()
        for c in courses:
            row = {k: c[k] for k in fields}
            row.update({f"gpa{s}": score_to_grade_point(c["score"], s) for s in (4.0, 4.8)})
            writer.writerow(row)

def export_report(path, courses):
    s = summary(courses)
    lines = ["东南大学成绩报告", "课程\t成绩\t学分\t4.0绩点\t4.8绩点\t学期\t计入"]
    for c in courses:
        lines.append("\t".join([c["name"], f'{c["score"]:g}', f'{c["credit"]:g}',
                                f'{score_to_grade_point(c["score"], 4.0):.2f}',
                                f'{score_to_grade_point(c["score"]):.2f}', c["semester"],
                                "否" if c["excluded"] else "是"]))
    lines += [f'\n计入 {s["count"]} 门 / {s["credits"]:g} 学分；排除 {s["excluded"]} 门',
              f'加权均分：{s["average"]:.2f}']
    for scale in (4.0, 4.8):
        lines.append(f'{scale}制 GPA：{s[str(scale)]:.2f}；均分对应参考绩点：{s[f"reference{scale}"]:.2f}')
    lines.append("GPA = Σ(每门课程分段绩点×学分) / Σ学分；参考绩点 = 将未四舍五入的加权均分按同一分段表换算。")
    Path(path).write_text("\n".join(lines), encoding="utf-8")

sys.dont_write_bytecode = True

BG, WHITE, INK, MUTED = "#f1f3fc", "#ffffff", "#30344f", "#81869f"

BLUE, TEAL, LINE = "#7464d8", "#399a95", "#e8e7f4"

LOG_DIR = ROOT / "log"

def rounded(canvas, x1, y1, x2, y2, radius, **kwargs):
    r = min(radius, (x2-x1)/2, (y2-y1)/2)
    return canvas.create_polygon(x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
                                 x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
                                 x1, y2, x1, y2-r, x1, y1+r, x1, y1,
                                 smooth=True, splinesteps=24, **kwargs)

class RoundPanel(tk.Canvas):
    def __init__(self, parent, color=WHITE, padding=15, **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, width=1, **kwargs)
        self.color, self.padding = color, padding
        self.inner = tk.Frame(self, bg=color)
        self.window = self.create_window(padding, padding, anchor="nw", window=self.inner)
        self.inner.bind("<Configure>", self.fit)
        self.bind("<Configure>", self.layout)

    def fit(self, event=None):
        height = self.inner.winfo_reqheight() + 2*self.padding
        if int(self.cget("height")) != height:
            self.configure(height=height)

    def layout(self, event=None):
        self.delete("surface")
        rounded(self, 1, 1, self.winfo_width()-1, self.winfo_height()-1, 22,
                fill=self.color, outline=LINE, tags="surface")
        self.tag_lower("surface")
        self.itemconfigure(self.window, width=max(1, self.winfo_width()-2*self.padding))

class RoundButton(tk.Canvas):
    def __init__(self, parent, text, command, accent=False):
        try:
            background = parent.cget("background")
        except tk.TclError:
            background = BG
        self.font = tkfont.Font(family="Microsoft YaHei UI", size=10)
        self.text, self.command, self.accent = text, command, accent
        self.enabled, self.hover = True, False
        super().__init__(parent, width=self.font.measure(text)+32,
                         height=self.font.metrics("linespace")+20, background=background,
                         highlightthickness=0, takefocus=1, cursor="hand2")
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", lambda e: self.highlight(True))
        self.bind("<Leave>", lambda e: self.highlight(False))
        self.bind("<ButtonRelease-1>", lambda e: self.invoke() if 0 <= e.x < self.winfo_width() and 0 <= e.y < self.winfo_height() else None)
        self.bind("<Return>", lambda e: self.invoke())
        self.bind("<space>", lambda e: self.invoke())
        self.bind("<FocusIn>", self.draw)
        self.bind("<FocusOut>", self.draw)

    def highlight(self, value):
        self.hover = value
        self.draw()

    def set_enabled(self, value):
        self.enabled = value
        self.configure(cursor="hand2" if value else "arrow")
        self.draw()

    def invoke(self):
        if self.enabled:
            return self.command()

    def draw(self, event=None):
        self.delete("all")
        fill = ("#6654cd" if self.hover else BLUE) if self.accent else ("#eae5fc" if self.hover else "#f1edfc")
        if not self.enabled:
            fill = "#e5e5ee"
        rounded(self, 1, 1, self.winfo_width()-1, self.winfo_height()-1, 13,
                fill=fill, outline=BLUE if str(self.tk.call("focus")) == str(self) else fill)
        self.create_text(self.winfo_width()/2, self.winfo_height()/2, text=self.text, font=self.font,
                         fill=MUTED if not self.enabled else WHITE if self.accent else "#6455a1")

class RoundScrollbar(tk.Canvas):
    """无箭头的胶囊形滚动条，保持 Tk 的 set / view 接口。"""
    def __init__(self, parent, orient="vertical", command=None, background=WHITE):
        self.vertical = orient == "vertical"
        self.command = command
        self.first, self.last = 0., 1.
        self.hover, self.drag_offset = False, None
        scale = max(1, float(parent.tk.call("tk", "scaling")) / (96/72))
        self.thickness = round(13*scale)
        self.minimum = round(28*scale)
        super().__init__(parent, bg=background, highlightthickness=0, takefocus=1,
                         width=self.thickness if self.vertical else 100,
                         height=100 if self.vertical else self.thickness)
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", lambda e: self.highlight(True))
        self.bind("<Leave>", lambda e: self.highlight(False))
        self.bind("<Button-1>", self.press)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<ButtonRelease-1>", self.release)
        self.bind("<MouseWheel>", lambda e: self.scroll(-int(e.delta/120) if abs(e.delta)>=120 else (-1 if e.delta>0 else 1)))
        for key, amount in [("Up", -1), ("Left", -1), ("Down", 1), ("Right", 1)]:
            self.bind(f"<{key}>", lambda e, n=amount: self.scroll(n))
        self.bind("<Prior>", lambda e: self.scroll(-1, "pages"))
        self.bind("<Next>", lambda e: self.scroll(1, "pages"))
        self.bind("<Home>", lambda e: self.command and self.command("moveto", 0))
        self.bind("<End>", lambda e: self.command and self.command("moveto", 1))

    def set(self, first, last):
        self.first = max(0., min(1., float(first)))
        self.last = max(self.first, min(1., float(last)))
        self.draw()

    def metrics(self):
        length = self.winfo_height() if self.vertical else self.winfo_width()
        track = max(1, length-6)
        span = self.last-self.first
        thumb = min(track, max(self.minimum, track*span))
        start = 3 + (track-thumb)*self.first/(1-span) if span < 1 else 3
        return start, thumb, track

    def highlight(self, value):
        self.hover = value
        self.draw()

    def draw(self, event=None):
        self.delete("all")
        if self.last-self.first >= .999999:
            return
        start, thumb, track = self.metrics()
        cross = self.winfo_width() if self.vertical else self.winfo_height()
        color = BLUE if self.drag_offset is not None else "#b3a6e0" if self.hover else "#d2c9ed"
        if self.vertical:
            rounded(self, 3, 3, cross-3, track+3, cross/2, fill="#f3f0fa", outline="")
            rounded(self, 3, start, cross-3, start+thumb, cross/2, fill=color, outline="")
        else:
            rounded(self, 3, 3, track+3, cross-3, cross/2, fill="#f3f0fa", outline="")
            rounded(self, start, 3, start+thumb, cross-3, cross/2, fill=color, outline="")

    def press(self, event):
        self.focus_set()
        position = event.y if self.vertical else event.x
        start, thumb, _ = self.metrics()
        if start <= position <= start+thumb and self.last-self.first < 1:
            self.drag_offset = position-start
        elif self.command:
            self.command("scroll", -1 if position < start else 1, "pages")
        self.draw()

    def drag(self, event):
        if self.drag_offset is None or not self.command:
            return
        position = event.y if self.vertical else event.x
        _, thumb, track = self.metrics()
        if track > thumb:
            fraction = (position-self.drag_offset-3)/(track-thumb)*(1-self.last+self.first)
            self.command("moveto", max(0., min(1., fraction)))

    def release(self, event=None):
        self.drag_offset = None
        self.draw()

    def scroll(self, amount, unit="units"):
        if self.command:
            self.command("scroll", amount, unit)
        return "break"

class RoundEntry(tk.Canvas):
    def __init__(self, parent, textvariable=None, width=20, show=""):
        self.font = tkfont.Font(family="Microsoft YaHei UI", size=10)
        super().__init__(parent, bg=BG, highlightthickness=0,
                         width=self.font.measure("0")*width+28, height=self.font.metrics("linespace")+20)
        self.entry = tk.Entry(self, textvariable=textvariable, show=show, font=self.font, bd=0,
                              highlightthickness=0, bg=WHITE, fg=INK, insertbackground=BLUE,
                              disabledbackground="#f6f4fb", disabledforeground=MUTED,
                              selectbackground="#e5dcfc", selectforeground=INK)
        self.window = self.create_window(14, 10, anchor="nw", window=self.entry)
        self.bind("<Configure>", self.draw)
        self.entry.bind("<FocusIn>", self.draw)
        self.entry.bind("<FocusOut>", self.draw)
        self.bind("<Button-1>", lambda e: self.entry.focus_set())

    def draw(self, event=None):
        super().delete("surface")
        rounded(self, 1, 1, self.winfo_width()-1, self.winfo_height()-1, 16,
                fill="#f6f4fb" if self.entry.cget("state")=="disabled" else WHITE,
                outline="#b8a9e8" if str(self.tk.call("focus"))==str(self.entry) else LINE, tags="surface")
        self.tag_lower("surface")
        self.itemconfigure(self.window, width=max(1, self.winfo_width()-28))

    def configure(self, cnf=None, **kwargs):
        if "state" in kwargs and hasattr(self, "entry"):
            self.entry.configure(state=kwargs.pop("state"))
            self.draw()
        if cnf is not None or kwargs:
            return super().configure(cnf, **kwargs)

    def get(self):
        return self.entry.get()

    def insert(self, index, text):
        return self.entry.insert(index, text)

    def delete(self, first, last=None):
        return self.entry.delete(first, last)

    def focus_set(self):
        return self.entry.focus_set()

class RoundSelect(tk.Canvas):
    """原生下拉选择负责键盘和焦点，Canvas 仅绘制圆角外框。"""
    def __init__(self, parent, textvariable, values=(), width=20, state="readonly"):
        self.variable = textvariable
        font = tkfont.Font(family="Microsoft YaHei UI", size=10)
        self.font = font
        super().__init__(parent, bg=BG, highlightthickness=0,
                         width=font.measure("0")*width+40, height=font.metrics("linespace")+20)
        self.combo = ttk.Combobox(self, textvariable=textvariable, values=tuple(values),
                                  state=state, font=font, style="Round.TCombobox")
        self.window = self.create_window(13, 0, anchor="w", window=self.combo)
        self.bind("<Configure>", self.draw)
        self.bind("<Button-1>", self.open)
        self.combo.bind("<FocusIn>", self.draw)
        self.combo.bind("<FocusOut>", self.draw)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.event_generate("<<ComboboxSelected>>"))
        self.trace = self.variable.trace_add("write", lambda *args: self.draw())
        self.bind("<Destroy>", self.cleanup)
        popup = self.tk.call("ttk::combobox::PopdownWindow", str(self.combo))
        self.tk.call(str(popup)+".f.l", "configure", "-background", WHITE, "-foreground", INK,
                     "-selectbackground", "#eee8fc", "-selectforeground", BLUE,
                     "-font", font, "-borderwidth", 0, "-highlightthickness", 0)

    def __getitem__(self, key):
        return tuple(self.combo["values"]) if key == "values" else super().__getitem__(key)

    def __setitem__(self, key, value):
        if key == "values":
            self.combo.configure(values=tuple(value))
        else:
            super().__setitem__(key, value)

    def draw(self, event=None):
        self.delete("surface")
        w, h = self.winfo_width(), self.winfo_height()
        rounded(self, 1, 1, w-1, h-1, 16, fill=WHITE,
                outline="#b8a9e8" if str(self.tk.call("focus"))==str(self.combo) else LINE, tags="surface")
        self.tag_lower("surface")
        self.coords(self.window, 13, h/2)
        self.itemconfigure(self.window, width=max(1, w-26))

    def open(self, event=None):
        self.combo.focus_set()
        self.combo.event_generate("<Button-1>", x=5, y=5)
        return "break"

    def dismiss(self):
        self.tk.call("ttk::combobox::Unpost", str(self.combo))

    def cleanup(self, event):
        if event.widget == self:
            self.variable.trace_remove("write", self.trace)

class RoundProgress(tk.Canvas):
    def __init__(self, parent):
        scale = max(1, float(parent.tk.call("tk", "scaling")) / (96/72))
        super().__init__(parent, bg=BG, height=round(8*scale), width=1, highlightthickness=0)
        self.timer, self.phase = None, 0
        self.bind("<Configure>", self.draw)
        self.bind("<Destroy>", lambda e: self.stop())

    def draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        rounded(self, 0, 0, w, h, h, fill="#e7e1f6", outline="")
        if self.timer is not None:
            start = (1-abs(self.phase % 2-1)) * w*.65
            rounded(self, start, 0, start+w*.35, h, h, fill="#ad9be8", outline="")

    def tick(self):
        self.phase += .035
        self.timer = self.after(30, self.tick)
        self.draw()

    def start(self, interval=None):
        if self.timer is None:
            self.tick()

    def stop(self):
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None
        if self.winfo_exists():
            self.draw()

class RoundTabs(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.header = tk.Frame(self, bg=BG)
        self.header.pack(fill="x", pady=(0, 8))
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True)
        self.pages, self.buttons, self.current = [], [], None

    def add(self, page, text):
        index = len(self.pages)
        self.pages.append(page)
        button = RoundButton(self.header, text.strip(), lambda: self.select(index))
        button.pack(side="left", padx=(0, 8))
        self.buttons.append(button)
        if self.current is None:
            self.select(0)

    def select(self, index=None):
        if index is None:
            return self.pages[self.current] if self.current is not None else None
        index = int(index)
        if self.current is not None:
            self.pages[self.current].pack_forget()
        self.current = index
        self.pages[index].pack(in_=self.body, fill="both", expand=True)
        for i, button in enumerate(self.buttons):
            button.accent = i == index
            button.draw()

class App(tk.Tk):
    def __init__(self, log_dir=LOG_DIR):
        super().__init__()
        self.ui_scale = max(1, float(self.tk.call("tk", "scaling")) / (96 / 72))
        self.title(APP_TITLE)
        self.geometry(f"{min(round(1280 * self.ui_scale), self.winfo_screenwidth() - 60)}x{min(round(850 * self.ui_scale), self.winfo_screenheight() - 90)}")
        self.minsize(min(round(1050 * self.ui_scale), self.winfo_screenwidth() - 60),
                     min(round(720 * self.ui_scale), self.winfo_screenheight() - 90))
        self.configure(bg=BG)
        self.storage = SnapshotLog(log_dir)
        self.pending_records = []
        self.dirty = False
        self.courses, self.history, self.visible = [], [], []
        self.events = queue.Queue()
        self.closed = threading.Event()
        self.cancel_fetch = threading.Event()
        self.sms_event, self.sms_value = threading.Event(), ""
        self.busy = False
        self.login_window = None
        self.sort_key, self.sort_reverse = "", False
        self.search = tk.StringVar()
        self.semester = tk.StringVar(value="全部学期")
        self.scope = tk.StringVar(value="全部课程")
        self.status = tk.StringVar(value="就绪 · 点击“保存记录”后写入本机")
        self.setup_style()
        self.build()
        try:
            self.courses, restored, warnings = self.storage.load_latest()
            if restored:
                self.status.set("已恢复 " + restored.name + " 中的最新成绩")
            if warnings:
                messagebox.showwarning("部分日志无法读取", "已跳过：" + "、".join(warnings) +
                                       "\n原文件保留。可导出备份后删除损坏日志或整个 log 文件夹。")
        except OSError:
            self.status.set("日志目录暂不可读取，可继续录入或导入成绩")
        self.refresh()
        self.poll_id = self.after(120, self.poll)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Control-n>", lambda e: self.edit())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-s>", lambda e: self.save_record())

    def setup_style(self):
        self.option_add("*Font", ("Microsoft YaHei UI", 10))
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("TFrame", background=BG)
        st.configure("TLabel", background=BG, foreground=INK)
        st.configure("TButton", font=("Microsoft YaHei UI", 10), padding=(12, 8),
                     background=WHITE, foreground=INK, borderwidth=0)
        st.map("TButton", background=[("active", "#e8efff")])
        st.configure("Accent.TButton", background=BLUE, foreground=WHITE)
        st.map("Accent.TButton", background=[("active", "#2855c6")])
        st.configure("TEntry", padding=7, fieldbackground=WHITE, bordercolor=LINE,
                     lightcolor=WHITE, darkcolor=WHITE, insertcolor=INK)
        st.map("TEntry", bordercolor=[("focus", "#b8a9e8")])
        st.configure("TCombobox", padding=6, fieldbackground=WHITE)
        st.layout("Round.TCombobox", [("Combobox.padding", {"sticky": "nswe", "children": [
            ("Combobox.downarrow", {"side": "right", "sticky": "ns"}),
            ("Combobox.textarea", {"sticky": "nswe"})]})])
        st.configure("Round.TCombobox", padding=0, background=WHITE, fieldbackground=WHITE,
                     foreground=INK, arrowcolor="#a495d1", arrowsize=12, borderwidth=0)
        st.map("Round.TCombobox", fieldbackground=[("readonly", WHITE)],
               background=[("readonly", WHITE)], selectbackground=[("readonly", WHITE)],
               selectforeground=[("readonly", INK)])
        st.layout("Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
            ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
        st.configure("Vertical.TScrollbar", background="#d2c9ed", troughcolor="#f3f0fa",
                     bordercolor=WHITE, lightcolor="#d2c9ed", darkcolor="#d2c9ed", borderwidth=0,
                     gripcount=0, width=10)
        st.configure("Treeview", font=("Microsoft YaHei UI", 10), rowheight=round(36 * self.ui_scale),
                     background=WHITE, fieldbackground=WHITE, foreground=INK, borderwidth=0)
        st.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        st.configure("Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"),
                     background="#f0edfa", foreground=MUTED, padding=10, relief="flat", borderwidth=0)
        st.map("Treeview", background=[("selected", "#dfe9ff")], foreground=[("selected", INK)])
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", background="#eae5f8", foreground=MUTED, padding=(18, 8))
        st.map("TNotebook.Tab", background=[("selected", WHITE)], foreground=[("selected", BLUE)])

    def label(self, parent, text, size=10, color=INK, bg=BG, bold=False, **kw):
        return tk.Label(parent, text=text, bg=bg, fg=color,
                        font=("Microsoft YaHei UI", size, "bold" if bold else "normal"), **kw)

    def button(self, parent, text, command, accent=False):
        return RoundButton(parent, text, command, accent)

    def build(self):
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=round(38*self.ui_scale), pady=20)
        head = tk.Frame(main, bg=BG)
        head.pack(fill="x")
        self.label(head, APP_TITLE, 26, BLUE, bold=True).pack(anchor="w", pady=(0, 4))
        self.label(head, "东南大学 · 4.0 / 4.8 双制对照 · 分段换算，无插值", 10, MUTED).pack(anchor="w")

        tools = RoundPanel(main, padding=12)
        tools.pack(fill="x", pady=(16, 14))
        self.tools_frame = tk.Frame(tools.inner, bg=WHITE)
        self.tools_frame.pack(anchor="center")
        self.label(self.tools_frame, "数据管理", 10, MUTED, WHITE).pack(side="left", padx=(0, 12))
        self.sync_button = self.button(self.tools_frame, "登录并获取成绩", self.login, True)
        self.sync_button.pack(side="left", padx=4)
        for title, cmd in [("保存记录", self.save_record), ("导入文件", self.import_file), ("粘贴返回包", self.paste),
                           ("导出与备份", self.export), ("撤销更改", self.undo), ("计算规则", self.rules)]:
            self.button(self.tools_frame, title, cmd).pack(side="left", padx=4)

        cards = tk.Frame(main, bg=BG)
        cards.pack(fill="x")
        self.card_values = {}
        for i, (key, title, subtitle, color) in enumerate([
            ("4.0", "4.0 制 GPA", "逐门换算 · 学分加权", BLUE),
            ("4.8", "4.8 制 GPA", "逐门换算 · 学分加权", TEAL),
            ("average", "加权均分", "按计入课程的学分加权", INK)]):
            cards.columnconfigure(i, weight=1)
            panel = RoundPanel(cards, padding=10)
            panel.grid(row=0, column=i, sticky="nsew", padx=(0, 12 if i < 2 else 0))
            card = panel.inner
            self.label(card, title, 11, MUTED, WHITE).pack(anchor="w", padx=18, pady=(14, 0))
            var = tk.StringVar(value="—")
            self.card_values[key] = var
            tk.Label(card, textvariable=var, bg=WHITE, fg=color, font=("Segoe UI", 32, "bold")).pack(anchor="w", padx=18)
            self.label(card, subtitle, 9, MUTED, WHITE).pack(anchor="w", padx=18, pady=(0, 12))
        self.reference = tk.StringVar()
        reference_panel = RoundPanel(main, color="#ede9fc", padding=10)
        reference_panel.pack(fill="x", pady=(12, 7))
        reference_label = tk.Label(reference_panel.inner, textvariable=self.reference, bg="#ede9fc", fg="#6955ad", anchor="w", padx=4, pady=0,
                                   justify="left", font=("Microsoft YaHei UI", 10))
        reference_label.pack(fill="x")
        self.stats = tk.StringVar()
        stats_label = tk.Label(main, textvariable=self.stats, bg=BG, fg=MUTED, anchor="w", justify="left")
        stats_label.pack(fill="x", pady=(0, 15))
        main.bind("<Configure>", lambda e: (reference_label.configure(wraplength=max(300, e.width - 30)),
                                            stats_label.configure(wraplength=max(300, e.width - 10))))

        tabs = RoundTabs(main)
        tabs.pack(fill="both", expand=True)
        sheet, analysis = ttk.Frame(tabs, padding=12), ttk.Frame(tabs, padding=14)
        tabs.add(sheet, text="  课程明细  ")
        tabs.add(analysis, text="  分布与学期分析  ")
        toolbar = ttk.Frame(sheet)
        toolbar.pack(fill="x", pady=(0, 10))
        fields = []
        for title in ("搜索课程", "学期筛选", "计入范围"):
            field = ttk.Frame(toolbar)
            field.pack(side="left", padx=(0, 10))
            self.label(field, title, 9, MUTED).pack(anchor="w", pady=(0, 4))
            fields.append(field)
        self.search_entry = RoundEntry(fields[0], textvariable=self.search, width=21)
        self.search_entry.pack()
        self.term_box = RoundSelect(fields[1], textvariable=self.semester, width=20)
        self.term_box.pack()
        self.scope_box = RoundSelect(fields[2], textvariable=self.scope, width=13,
                     values=["全部课程", "仅计入", "仅排除", "未通过"])
        self.scope_box.pack()
        self.button(toolbar, "重置筛选", self.reset_filters).pack(side="right")
        self.filter_hint = tk.StringVar()
        tk.Label(sheet, textvariable=self.filter_hint, bg=BG, fg=MUTED, anchor="w",
                 font=("Microsoft YaHei UI", 9)).pack(fill="x", pady=(0, 8))
        box = ttk.Frame(sheet)
        box.pack(fill="both", expand=True)
        keys = ("name", "score", "credit", "gpa4", "gpa48", "course_type", "semester", "included")
        self.tree = ttk.Treeview(box, columns=keys, show="headings", selectmode="extended", height=5)
        for key, title, width in zip(keys, ["课程名称", "成绩", "学分", "4.0 绩点", "4.8 绩点", "课程性质", "学期", "计入"],
                                     [200, 65, 60, 78, 78, 90, 150, 60]):
            self.tree.heading(key, text=title, command=lambda k=key: self.sort(k))
            self.tree.column(key, width=width, minwidth=55, anchor="w" if key == "name" else "center")
        self.y_scroll = RoundScrollbar(box, orient="vertical", command=self.tree.yview)
        self.x_scroll = RoundScrollbar(box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.y_scroll.set, xscrollcommand=self.x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.y_scroll.grid(row=0, column=1, sticky="ns", padx=(3, 0))
        self.x_scroll.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)
        self.tree.tag_configure("excluded", foreground="#96a1b2")
        self.tree.tag_configure("failed", foreground="#c14848")
        self.tree.tag_configure("alt", background="#f8faff")
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        actions = ttk.Frame(sheet)
        actions.pack(side="bottom", fill="x", pady=(10, 0), before=box)
        self.button(actions, "＋ 添加课程", self.edit, True).pack(side="left", padx=(0, 6))
        for title, cmd in [("编辑", self.edit_selected), ("计入 / 排除", self.toggle), ("删除选中", self.delete),
                           ("清空全部", self.clear)]:
            self.button(actions, title, cmd).pack(side="left", padx=(0, 6))
        self.button(actions, "加载示例", self.demo).pack(side="right")

        self.chart = tk.Canvas(analysis, bg=WHITE, highlightthickness=0, height=round(210 * self.ui_scale))
        self.chart.pack(fill="x")
        self.chart.bind("<Configure>", lambda e: self.draw_chart())
        analysis.bind("<Configure>", lambda e: self.chart.configure(
            height=round(min(210*self.ui_scale, max(90*self.ui_scale, e.height-230*self.ui_scale)))))
        self.label(analysis, "学期对照 · 仅统计计入课程", 11, bold=True).pack(anchor="w", pady=(12, 8))
        self.term_tree = ttk.Treeview(analysis, columns=("term", "count", "credits", "avg", "4", "48"), show="headings", height=2)
        for key, title in zip(self.term_tree["columns"], ["学期", "课程数", "学分", "加权均分", "4.0 GPA", "4.8 GPA"]):
            self.term_tree.heading(key, text=title)
            self.term_tree.column(key, width=90, anchor="center")
        term_box = ttk.Frame(analysis)
        term_box.pack(fill="both", expand=True)
        # Treeview 的 master 不变，使用 in_ 在表格容器内排版。
        self.term_tree.pack(in_=term_box, side="left", fill="both", expand=True)
        term_scroll = RoundScrollbar(term_box, command=self.term_tree.yview)
        term_scroll.pack(side="right", fill="y")
        self.term_tree.configure(yscrollcommand=term_scroll.set)
        predict_label = self.label(analysis, "均分目标预测：在当前筛选范围的基础上，计算未来课程所需均分。", 9, MUTED)
        predict_label.pack(side="bottom", anchor="w", pady=(10, 5), before=term_box)
        self.button(analysis, "计算目标均分", self.predict).pack(side="bottom", anchor="w", before=predict_label)
        footer = tk.Frame(main, bg=BG)
        footer.pack(side="bottom", fill="x", pady=(10, 0), before=tabs)
        self.author_label = tk.Label(footer, text="@" + __author__, bg=BG, fg=MUTED,
                                     font=("Microsoft YaHei UI", 9))
        self.author_label.pack(side="right", padx=(12, 0))
        tk.Label(footer, textvariable=self.status, bg=BG, fg=MUTED, anchor="w",
                 font=("Microsoft YaHei UI", 9)).pack(side="left", fill="x", expand=True)
        for var in (self.search, self.semester, self.scope):
            var.trace_add("write", lambda *args: self.refresh())

    def reset_filters(self):
        self.search.set("")
        self.semester.set("全部学期")
        self.scope.set("全部课程")

    def filtered(self):
        keywords = self.search.get().strip().casefold().split()
        rows = [(i, c) for i, c in enumerate(self.courses)
                if all(key in " ".join([c["name"], c["course_code"], c["course_type"], c["semester"]]).casefold() for key in keywords)
                and (self.semester.get() == "全部学期" or (c["semester"] or "未填写学期") == self.semester.get())
                and (self.scope.get() != "仅计入" or not c["excluded"])
                and (self.scope.get() != "仅排除" or c["excluded"])
                and (self.scope.get() != "未通过" or c["score"] < 60)]
        if self.sort_key:
            def value(pair):
                c = pair[1]
                if self.sort_key in ("gpa4", "gpa48"):
                    return score_to_grade_point(c["score"], 4.0 if self.sort_key == "gpa4" else 4.8)
                if self.sort_key == "included":
                    return not c["excluded"]
                return c[self.sort_key]
            rows.sort(key=value, reverse=self.sort_reverse)
        return rows

    def refresh(self):
        terms = sorted({c["semester"] or "未填写学期" for c in self.courses})
        self.term_box["values"] = ["全部学期"] + terms
        if self.semester.get() not in self.term_box["values"]:
            self.semester.set("全部学期")
        rows = self.filtered()
        self.visible = [c for _, c in rows]
        self.filter_hint.set("暂无课程：请先登录获取、导入或添加课程，学期选项会自动生成。" if not self.courses else
                             "没有匹配课程，请调整搜索条件或点击“重置筛选”。" if not rows else
                             "可搜索课程名称、代码、性质或学期；多个关键词用空格分开；双击课程编辑。")
        self.tree.delete(*self.tree.get_children())
        for n, (i, c) in enumerate(rows):
            self.tree.insert("", "end", iid=str(i), values=(c["name"], f'{c["score"]:g}', f'{c["credit"]:g}',
                             f'{score_to_grade_point(c["score"], 4.0):.2f}',
                             f'{score_to_grade_point(c["score"]):.2f}', c["course_type"] or "—",
                             c["semester"] or "—", "否" if c["excluded"] else "是"),
                             tags=("excluded" if c["excluded"] else "failed" if c["score"] < 60 else "normal",
                                   "alt" if n % 2 else "normal"))
        s = summary(self.visible)
        for key, var in self.card_values.items():
            var.set(f'{s[key]:.2f}' if s["credits"] else "—")
        self.reference.set((f'均分对应参考绩点  →  4.0 制 {s["reference4.0"]:.2f}    /    4.8 制 {s["reference4.8"]:.2f}'
                            if s["credits"] else "均分对应参考绩点  →  暂无计入课程") + "    ·    直接对均分分段换算，仅供比较")
        rate = f'{s["passed"] / s["count"]:.0%}' if s["count"] else "—"
        self.stats.set(f'当前显示 {len(rows)} / {len(self.courses)} 门    ·    计入 {s["count"]} 门    ·    排除 {s["excluded"]} 门'
                       f'    ·    计入学分 {s["credits"]:g}    ·    通过 {s["passed"]} 门 / {rate}')
        self.term_tree.delete(*self.term_tree.get_children())
        for term in sorted({c["semester"] or "未填写学期" for c in self.visible}):
            ss = summary([c for c in self.visible if (c["semester"] or "未填写学期") == term])
            self.term_tree.insert("", "end", values=(term, ss["count"], f'{ss["credits"]:g}',
                                  f'{ss["average"]:.2f}' if ss["credits"] else "—",
                                  f'{ss["4.0"]:.2f}' if ss["credits"] else "—", f'{ss["4.8"]:.2f}' if ss["credits"] else "—"))
        self.draw_chart()

    def draw_chart(self):
        if not hasattr(self, "chart"):
            return
        c = self.chart
        c.delete("all")
        width = max(c.winfo_width(), 500)
        c.create_text(20, 22, text="成绩分布 · 计入课程", fill=INK, anchor="w", font=("Microsoft YaHei UI", 11, "bold"))
        bins = [(0, 60, "<60"), (60, 70, "60–69"), (70, 80, "70–79"), (80, 90, "80–89"), (90, 96, "90–95"), (96, 101, "96–100")]
        counts = [sum(not x["excluded"] and lo <= x["score"] < hi for x in self.visible) for lo, hi, _ in bins]
        maximum = max(counts + [1])
        slot = (width - 60) / 6
        c.create_line(24, 170, width - 24, 170, fill=LINE)
        for i, ((_, _, label), count) in enumerate(zip(bins, counts)):
            x = 30 + i * slot
            height = 100 * count / maximum
            c.create_rectangle(x + slot * .2, 170 - height, x + slot * .8, 170, fill="#df7777" if i == 0 else BLUE if i < 4 else TEAL, outline="")
            c.create_text(x + slot / 2, 155 - height, text=str(count), fill=INK)
            c.create_text(x + slot / 2, 190, text=label, fill=MUTED)
        if not any(counts):
            c.create_text(width / 2, 90, text="添加或导入成绩后，在这里查看分布", fill=MUTED)
        c.scale("all", 0, 0, 1, max(.5, min(self.ui_scale, c.winfo_height()/210)))

    def sort(self, key):
        self.sort_reverse = not self.sort_reverse if self.sort_key == key else False
        self.sort_key = key
        self.refresh()

    def commit(self, courses, note):
        self.history.append(copy.deepcopy(self.courses))
        self.history = self.history[-20:]
        self.courses = courses
        self.persist(note)
        self.refresh()

    def persist(self, note):
        self.dirty = True
        self.log_event(note)
        self.status.set(note + " · 尚未保存，请点击“保存记录”或按 Ctrl+S")

    def save_record(self):
        try:
            path = self.storage.save(self.courses, self.pending_records)
            self.pending_records = []
            self.dirty = False
            self.status.set("已保存至 log/" + path.name)
        except (OSError, ValueError, TypeError) as error:
            self.status.set("保存失败，可重试或导出备份")
            messagebox.showerror("保存失败", "日志未能写入，当前成绩仍保留在窗口中。\n" + str(error))

    def log_event(self, action):
        self.pending_records.append({"time": self.storage.now().isoformat(timespec="seconds"), "action": action})

    def selected(self):
        return [int(i) for i in self.tree.selection()]

    def edit_selected(self):
        ids = self.selected()
        if len(ids) != 1:
            messagebox.showinfo("编辑课程", "请选择一门课程。")
            return
        self.edit(ids[0])

    def edit(self, index=None):
        old = self.courses[index] if index is not None else {}
        win = tk.Toplevel(self)
        win.title("编辑课程" if old else "添加课程")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        form = ttk.Frame(win, padding=24)
        form.pack(fill="both", expand=True)
        variables = {}
        fields = [("name", "课程名称 *"), ("score", "成绩 *（支持等级制）"), ("credit", "学分 *"),
                  ("course_type", "课程性质"), ("semester", "学期"), ("course_code", "课程代码")]
        for i, (key, title) in enumerate(fields):
            ttk.Label(form, text=title).grid(row=i, column=0, sticky="w", padx=(0, 15), pady=6)
            var = tk.StringVar(value=str(old.get(key, "")))
            variables[key] = var
            entry = RoundEntry(form, textvariable=var, width=29)
            entry.grid(row=i, column=1, pady=6)
            if i == 0:
                entry.focus_set()
        excluded = tk.BooleanVar(value=old.get("excluded", False))
        ttk.Checkbutton(form, text="排除本课程（不计入均分与 GPA）", variable=excluded).grid(row=6, column=0, columnspan=2, sticky="w", pady=10)
        ttk.Label(form, text="新课程性质含“任选”时默认排除，可在主表切换。", foreground=MUTED).grid(row=7, column=0, columnspan=2, sticky="w")
        def save():
            row = {key: var.get() for key, var in variables.items()}
            row["excluded"] = excluded.get() or (index is None and "任选" in row["course_type"])
            row["exclude_reason"] = "手动排除" if excluded.get() else "任选课程"
            try:
                course = normalize(row)
            except ValueError as error:
                messagebox.showerror("请检查输入", str(error), parent=win)
                return
            courses = self.courses[:]
            if index is None:
                courses.append(course)
            else:
                courses[index] = course
            self.commit(courses, "课程已保存")
            win.destroy()
        self.button(form, "保存课程", save, True).grid(row=8, column=1, sticky="e", pady=(18, 0))
        win.bind("<Return>", lambda e: save())
        win.bind("<Escape>", lambda e: win.destroy())

    def toggle(self):
        ids = self.selected()
        if not ids:
            return
        courses = copy.deepcopy(self.courses)
        for i in ids:
            courses[i]["excluded"] = not courses[i]["excluded"]
            courses[i]["exclude_reason"] = "手动排除" if courses[i]["excluded"] else ""
        self.commit(courses, "已更新课程计入状态")

    def delete(self):
        ids = self.selected()
        if ids and messagebox.askyesno("删除课程", f"删除选中的 {len(ids)} 门课程？可使用撤销恢复。"):
            self.commit([c for i, c in enumerate(self.courses) if i not in ids], "已删除课程")

    def clear(self):
        if self.courses and messagebox.askyesno("清空成绩", "清空全部课程？可使用撤销恢复。"):
            self.commit([], "已清空")

    def undo(self):
        if self.history:
            self.courses = self.history.pop()
            self.persist("已撤销")
            self.refresh()
        else:
            self.status.set("暂无可撤销的更改")

    def merge(self, incoming, errors=None):
        if not incoming:
            messagebox.showwarning("没有可导入课程", "\n".join((errors or ["未获取到课程"] )[:8]))
            return
        def identity(c):
            return tuple(c[k] for k in ("name", "course_code", "semester", "score", "credit"))
        known = {identity(c) for c in self.courses}
        added = []
        for course in incoming:
            if identity(course) not in known:
                added.append(course)
                known.add(identity(course))
        self.commit(self.courses + added, f"导入 {len(added)} 门，跳过重复 {len(incoming) - len(added)} 门")
        if errors:
            messagebox.showwarning("部分记录已跳过", f"有效 {len(incoming)} 条，无效 {len(errors)} 条。\n" + "\n".join(errors[:8]))

    def import_file(self):
        path = filedialog.askopenfilename(title="导入成绩或教务返回包", filetypes=[("成绩文件", "*.json *.txt *.csv"), ("全部文件", "*.*")])
        if path:
            try:
                text = Path(path).read_text(encoding="utf-8-sig")
                courses, errors = import_text(text, Path(path).suffix)
                self.merge(courses, errors)
            except (OSError, ValueError, UnicodeError) as error:
                self.log_event("导入文件失败")
                messagebox.showerror("导入失败", str(error))

    def paste(self):
        win = tk.Toplevel(self)
        win.title("粘贴教务成绩 JSON / 完整返回包")
        win.geometry("700x450")
        win.transient(self)
        text = tk.Text(win, wrap="word", font=("Consolas", 11))
        text.pack(fill="both", expand=True, padx=15, pady=15)
        def load():
            try:
                courses, errors = import_text(text.get("1.0", "end"))
                self.merge(courses, errors)
                if courses:
                    win.destroy()
            except ValueError as error:
                self.log_event("粘贴数据解析失败")
                messagebox.showerror("解析失败", str(error), parent=win)
        self.button(win, "解析并导入", load, True).pack(pady=(0, 15))

    def export(self):
        if not self.courses:
            messagebox.showinfo("导出", "请先添加课程。")
            return
        win = tk.Toplevel(self)
        win.title("导出成绩")
        win.configure(bg=BG)
        win.transient(self)
        frame = ttk.Frame(win, padding=24)
        frame.pack()
        scope = tk.StringVar(value="全部课程")
        ttk.Label(frame, text="选择导出范围").pack(anchor="w")
        RoundSelect(frame, textvariable=scope, values=["全部课程", "当前筛选"]).pack(fill="x", pady=10)
        def save(kind):
            courses = self.courses if scope.get() == "全部课程" else self.visible
            path = filedialog.asksaveasfilename(parent=win, initialfile="成绩单" + kind, defaultextension=kind,
                                              filetypes=[(kind[1:].upper(), "*" + kind)])
            if not path:
                return
            try:
                if kind == ".json":
                    save_session(path, courses)
                elif kind == ".csv":
                    export_csv(path, courses)
                elif kind == ".txt":
                    export_report(path, courses)
                self.status.set("已导出：" + path)
                self.log_event("导出 " + kind.lstrip(".").upper())
                win.destroy()
            except (OSError, ValueError) as error:
                self.log_event("导出文件失败")
                messagebox.showerror("导出失败", str(error), parent=win)
        for name, kind in [("JSON 备份（可重新导入）", ".json"), ("CSV 表格（Excel 可打开）", ".csv"), ("TXT 报告（含双制统计）", ".txt")]:
            self.button(frame, name, lambda k=kind: save(k)).pack(fill="x", pady=5)

    def login(self):
        if self.login_window is not None and self.login_window.winfo_exists():
            self.login_window.deiconify()
            self.login_window.lift()
            return
        if self.busy:
            messagebox.showinfo("正在同步", "当前同步仍在进行，请稍候。")
            return
        win = tk.Toplevel(self)
        self.login_window = win
        win.title("登录并获取成绩")
        win.transient(self)
        win.configure(bg=BG)
        frame = ttk.Frame(win, padding=24)
        frame.pack()
        ttk.Label(frame, text="登录东南大学教务", font=("Microsoft YaHei UI", 15, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(frame, text="输入统一认证账号和密码，按需完成短信验证。", foreground=MUTED).pack(anchor="w", pady=(0, 18))
        username, password = tk.StringVar(), tk.StringVar()
        self.login_entries = []
        for title, var, mask in [("统一认证账号", username, ""), ("密码", password, "●")]:
            ttk.Label(frame, text=title).pack(anchor="w")
            entry = RoundEntry(frame, textvariable=var, show=mask, width=40)
            entry.pack(fill="x", pady=(5, 12))
            self.login_entries.append(entry)
        self.login_entries[0].focus_set()
        self.login_steps = tk.StringVar(value="① 验证账号密码    →    ② 短信验证（按需）    →    ③ 获取成绩")
        ttk.Label(frame, textvariable=self.login_steps, foreground=BLUE).pack(anchor="w", pady=(8, 8))
        self.login_detail = tk.StringVar(value="请输入账号和密码。认证信息仅用于本次登录，不保存。")
        ttk.Label(frame, textvariable=self.login_detail, wraplength=round(410*self.ui_scale),
                  foreground=MUTED, justify="left").pack(anchor="w", fill="x", pady=(0, 8))
        self.login_progress = RoundProgress(frame)
        self.login_progress.pack(fill="x", pady=(0, 8))
        def start():
            if self.busy:
                return
            user, secret = username.get().strip(), password.get()
            if not user or not secret:
                messagebox.showerror("信息不完整", "请输入账号和密码。", parent=win)
                return
            password.set("")
            self.busy = True
            self.cancel_fetch.clear()
            self.sync_button.set_enabled(False)
            self.login_submit.set_enabled(False)
            self.login_cancel.set_enabled(True)
            for entry in self.login_entries:
                entry.configure(state="disabled")
            self.login_progress.start(12)
            self.login_detail.set("正在验证账号密码，请稍候…")
            self.status.set("正在验证账号密码…")
            def sms():
                self.sms_value = ""
                self.sms_event.clear()
                self.events.put(("sms", None))
                while not self.sms_event.wait(.25):
                    if self.closed.is_set() or self.cancel_fetch.is_set():
                        return ""
                return self.sms_value
            def worker():
                # 日志回调仅在当前工作线程生效，不替换全局函数。
                log_token = _backend_sink.set(lambda *args, **kw: self.events.put(("log", " ".join(map(str, args)))))
                try:
                    status = lambda stage, message: self.events.put(("auth", (stage, message)))
                    courses = fetch_grades_from_seu(user, secret, sms, status, self.cancel_fetch)
                    if self.cancel_fetch.is_set():
                        self.events.put(("cancelled", None))
                        return
                    valid, errors = [], []
                    for c in courses:
                        try:
                            valid.append(normalize(c))
                        except ValueError as error:
                            errors.append(str(error))
                    self.events.put(("done", (valid, errors)))
                except Exception as error:
                    self.events.put(("error", str(error)))
                finally:
                    _backend_sink.reset(log_token)
            # 关闭窗口时允许原脚本结束当前请求，不强制中断其会话。
            threading.Thread(target=worker, daemon=False).start()
        self.login_submit = self.button(frame, "验证账号密码并登录", start, True)
        self.login_submit.pack(fill="x", pady=(12, 0))
        self.login_cancel = self.button(frame, "取消获取", self.cancel_fetch.set)
        self.login_cancel.pack(fill="x", pady=(8, 0))
        self.login_cancel.set_enabled(False)
        win.bind("<Return>", lambda e: start())
        def dismiss():
            if self.busy:
                win.withdraw()
            else:
                win.destroy()
                self.login_window = None
        win.protocol("WM_DELETE_WINDOW", dismiss)

    def finish_login(self, success, detail=""):
        self.busy = False
        self.sms_value = ""
        self.sync_button.set_enabled(True)
        if self.login_window is not None and self.login_window.winfo_exists():
            self.login_progress.stop()
            self.login_cancel.set_enabled(False)
            if success:
                self.login_window.destroy()
                self.login_window = None
            else:
                self.login_window.deiconify()
                self.login_submit.set_enabled(True)
                self.login_detail.set(detail)
                for entry in self.login_entries:
                    entry.configure(state="normal")
                self.login_entries[1].focus_set()

    def poll(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "sms":
                    parent = self.login_window if self.login_window is not None and self.login_window.winfo_exists() else self
                    parent.deiconify()
                    self.sms_value = simpledialog.askstring("短信验证", "学校要求短信二次验证。\n请输入你收到的短信验证码：", parent=parent) or ""
                    self.sms_event.set()
                elif kind == "auth":
                    stage, detail = payload
                    # 只保存固定阶段名，接口原文可能包含账号、手机号或令牌。
                    allowed = {"checking", "rejected", "sms_required", "sms_failed", "awaiting_sms",
                               "verifying_sms", "sms_rejected", "authenticated", "fetching", "session", "session_failed", "grades_failed"}
                    self.log_event("认证阶段：" + (stage if stage in allowed else "unknown"))
                    self.status.set(detail)
                    if self.login_window is not None and self.login_window.winfo_exists():
                        self.login_detail.set(detail)
                        step = ("① 正在检查账号密码" if stage == "checking" else
                                "① 账号密码认证未通过" if stage == "rejected" else
                                "① 已完成首次认证  →  ② 短信验证未通过" if stage == "sms_rejected" else
                                "① 认证已完成  →  ③ 教务会话建立失败" if stage == "session_failed" else
                                "③ 成绩获取失败（请查看下方具体原因）" if stage == "grades_failed" else
                                "② 正在连接教务系统" if stage == "session" else
                                "③ 正在查询成绩" if stage == "fetching" else
                                "① 已收到二次验证要求  →  ② 短信验证" if stage in ("sms_required", "awaiting_sms", "verifying_sms", "sms_failed") else
                                "① 认证通过  →  ② 已完成或无需验证  →  ③ 获取成绩")
                        self.login_steps.set(step)
                elif kind == "log":
                    self.status.set(payload)
                    if self.login_window is not None and self.login_window.winfo_exists():
                        self.login_detail.set(payload)
                elif kind == "done":
                    if payload[0]:
                        self.finish_login(True)
                        self.merge(*payload)
                        self.reset_filters()
                    else:
                        self.log_event("成绩同步失败或未返回成绩")
                        self.finish_login(False, self.status.get() + "\n请检查后重试，也可导入教务返回包。")
                elif kind == "error":
                    self.log_event("成绩同步异常")
                    self.status.set("同步失败，可改用返回包导入")
                    self.finish_login(False, "同步失败：" + payload)
                elif kind == "cancelled":
                    self.status.set("已取消获取成绩")
                    self.finish_login(False, "已取消。可重新输入密码后重试。")
        except queue.Empty:
            pass
        if not self.closed.is_set():
            self.poll_id = self.after(120, self.poll)

    def rules(self):
        win = tk.Toplevel(self)
        win.title("分段规则与计算口径")
        win.geometry("650x690")
        text = tk.Text(win, padx=24, pady=20, wrap="word", font=("Microsoft YaHei UI", 11), bg=WHITE, relief="flat")
        text.pack(fill="both", expand=True)
        lines = ["东南大学 · 双制分段换算\n", "成绩区间                 4.0 制       4.8 制"]
        upper = 100
        for lower, point in RULES:
            label = f"{lower} ≤ 成绩 ≤ 100" if lower == 96 else f"{lower} ≤ 成绩 < {upper}"
            lines.append(f"{label:<24} {min(point, 4.0):.1f}             {point:.1f}")
            upper = lower
        lines += ["\n4.0 制仅将 90 分及以上统一封顶为 4.0，其余分段与 4.8 制一致。",
                  "小数成绩按分段下限归档。例如 92.5 分：两制均为 4.0，不插值。",
                  "\n课程 GPA = Σ(每门课程的分段绩点 × 学分) ÷ Σ学分。",
                  "均分参考绩点 = 先求学分加权均分，再查同一分段表。它用于比较卡绩影响，不作为课程 GPA。",
                  "计算使用未四舍五入的均分，仅显示时保留两位小数；因此显示 93.00 的均分可能实际略低于 93。",
                  "\n任选课程默认排除，可手动切换。未通过课程默认计入，绩点为 0。通过率按计入课程门数计算。",
                  "等级制沿用原程序的近似折算：优秀/优 95，良好/良 85，中 75，及格/合格/通过 65，不通过 0。",
                  "重修不会自动取最高分，请根据需要手动排除某条记录。",
                  "\n参考：https://seucseweb.github.io/GPA-Calculator/\n该规则用于个人估算，最终成绩以教务认定为准。"]
        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")

    def predict(self):
        s = summary(self.visible)
        target = simpledialog.askfloat("均分目标", "希望达到的加权均分（0–100）：", minvalue=0, maxvalue=100, parent=self)
        if target is None:
            return
        credits = simpledialog.askfloat("未来学分", "计划新增多少学分？", minvalue=.01, parent=self)
        if credits is None:
            return
        needed = (target * (s["credits"] + credits) - s["average"] * s["credits"]) / credits
        msg = f"当前范围计入 {s['credits']:g} 学分，均分 {s['average']:.2f}。\n新增 {credits:g} 学分需达到均分 {needed:.2f}。"
        if needed > 100:
            msg += "\n按当前计划无法达到目标，可增加未来学分或调整目标。"
        elif needed < 0:
            msg += "\n即使未来均分为 0，也已满足这个目标。"
        messagebox.showinfo("目标预测", msg, parent=self)

    def demo(self):
        data = [("高等数学 A", 92.5, 5, "必修", "2025–2026 第一学期"),
                ("大学物理", 87, 4, "必修", "2025–2026 第一学期"),
                ("程序设计基础", 97, 3, "必修", "2025–2026 第二学期"),
                ("线性代数", 94, 3, "必修", "2025–2026 第二学期"),
                ("通识艺术", 95, 2, "任选", "2025–2026 第二学期")]
        self.merge([normalize(dict(name=n, score=s, credit=c, course_type=t, semester=term)) for n, s, c, t, term in data])

    def close(self):
        if self.dirty and not messagebox.askokcancel("尚未保存", "当前成绩有未保存的更改。\n点击确定将直接关闭；如需保存，请取消后点击“保存记录”。"):
            return
        self.closed.set()
        self.cancel_fetch.set()
        self.sms_event.set()
        self.after_cancel(self.poll_id)
        self.destroy()

if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    try:
        App().mainloop()
    except Exception:
        import traceback
        detail = traceback.format_exc()
        try:
            messagebox.showerror("绩点计算器启动失败", "程序未能启动，错误信息如下：\n\n" + detail)
        except Exception:
            if sys.stderr is not None:
                sys.stderr.write(detail)
