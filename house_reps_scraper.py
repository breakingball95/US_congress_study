#!/usr/bin/env python3
"""
美国众议院议员网站爬虫

功能：爬取美国众议院网站上所有议员的个人官网链接，并保存为Excel文件

使用方法：
1. 确保已安装Python 3
2. 安装依赖：pip install requests beautifulsoup4 pandas openpyxl
3. 运行脚本：python house_reps_scraper.py

输出：生成 house_representatives_websites.xlsx 文件，包含议员姓名、个人网站链接、选区、所属地区分类、政党和委员会信息
"""

# 首先创建一个日志文件，确认脚本开始执行
with open('scraper_log.txt', 'w', encoding='utf-8') as log_file:
    log_file.write('脚本开始执行...\n')

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
import os
import sys
import re

# 写入日志
with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
    log_file.write('模块导入成功\n')

# 定义地区分类
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma",
    "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
    "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

US_TERRITORIES = [
    "American Samoa", "Guam", "Northern Mariana Islands", "Puerto Rico", "Virgin Islands"
]

FEDERAL_DISTRICT = ["District of Columbia"]

def get_region_category(state_name):
    """根据州名返回地区分类"""
    if state_name in US_STATES:
        return "State"
    elif state_name in US_TERRITORIES:
        return "U.S. Territories"
    elif state_name in FEDERAL_DISTRICT:
        return "The Federal District"
    else:
        return "Unknown"

def parse_district(district_text):
    """
    解析district文本，提取州名和选区
    例如："North Carolina 12th" -> ("North Carolina", "12th")
          "Alabama 4th" -> ("Alabama", "4th")
          "Puerto Rico" -> ("Puerto Rico", "At-large")
    """
    if not district_text:
        return "", ""
    
    district_text = district_text.strip()
    
    # 匹配模式：州名 + 选区数字 + 序数词后缀
    # 例如："North Carolina 12th", "Alabama 4th"
    match = re.match(r'^(.+?)\s+(\d+)(?:st|nd|rd|th)$', district_text)
    if match:
        state = match.group(1).strip()
        district_num = match.group(2)
        # 确定序数词后缀
        if district_num.endswith('1') and not district_num.endswith('11'):
            suffix = 'st'
        elif district_num.endswith('2') and not district_num.endswith('12'):
            suffix = 'nd'
        elif district_num.endswith('3') and not district_num.endswith('13'):
            suffix = 'rd'
        else:
            suffix = 'th'
        district = f"{district_num}{suffix}"
        return state, district
    
    # 如果没有匹配到数字选区，可能是 At-large 选区（如 Puerto Rico）
    return district_text, "At-large"

def get_representatives():
    """获取众议院议员信息"""
    # 写入日志
    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write('开始获取众议员信息...\n')
    
    # 众议院网站URL
    url = "https://www.house.gov/representatives"
    
    # 发送请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'正在请求URL: {url}\n')
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # 检查请求是否成功
        
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'请求成功，状态码: {response.status_code}\n')
    except Exception as e:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'请求失败: {e}\n')
        return []
    
    # 解析HTML
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write('HTML解析成功\n')
    except Exception as e:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'HTML解析失败: {e}\n')
        return []
    
    # 查找众议员信息
    representatives = []
    
    # 首先尝试从 "By Last Name" 视图提取数据
    try:
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write('尝试从 By Last Name 视图提取数据...\n')
        
        # 查找所有表格
        tables = soup.find_all('table')
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'找到 {len(tables)} 个表格\n')
        
        for table in tables:
            # 查找表头，确认是否是议员表格
            header = table.find('thead')
            if header:
                header_text = header.get_text(strip=True)
                # 检查是否包含关键列名
                if 'Name' in header_text and 'District' in header_text:
                    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                        log_file.write('找到议员信息表格\n')
                    
                    # 提取数据行
                    rows = table.find_all('tr')
                    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                        log_file.write(f'表格中有 {len(rows)} 行数据\n')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 6:  # 确保有足够的单元格
                            # 提取数据
                            name_cell = cells[0]
                            district_cell = cells[1]
                            party = cells[2].get_text(strip=True)
                            office = cells[3].get_text(strip=True)
                            phone = cells[4].get_text(strip=True)
                            committee = cells[5].get_text(strip=True)
                            
                            # 提取姓名和网站链接
                            name_link = name_cell.find('a', href=True)
                            if name_link:
                                name = name_link.get_text(strip=True).replace('(link is external)', '').strip()
                                website = name_link.get('href')
                                
                                # 解析 district 文本
                                district_text = district_cell.get_text(strip=True)
                                state, district = parse_district(district_text)
                                
                                # 确定地区分类
                                region_category = get_region_category(state)
                                
                                if name and website:
                                    representatives.append({
                                        "name": name,
                                        "website": website,
                                        "district": district,
                                        "state": state,
                                        "region_category": region_category,
                                        "party": party,
                                        "committee": committee
                                    })
                                    # 写入日志
                                    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                                        log_file.write(f'添加众议员: {name} ({state}, {district}, {region_category})\n')
        
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'从 By Last Name 视图找到 {len(representatives)} 位众议员\n')
    except Exception as e:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'从 By Last Name 视图提取数据失败: {e}\n')
            import traceback
            log_file.write(traceback.format_exc())
    
    # 如果从 By Last Name 视图没有找到数据，尝试从 "By State and District" 视图提取
    if not representatives:
        try:
            with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write('尝试从 By State and District 视图提取数据...\n')
            
            # 合并所有有效的地区名称
            all_regions = US_STATES + US_TERRITORIES + FEDERAL_DISTRICT
            
            current_state = ""
            
            # 遍历所有元素，寻找州名和众议员数据
            for element in soup.find_all(['h2', 'h3', 'tr']):
                # 检查是否是州名
                if element.name in ['h2', 'h3']:
                    text = element.get_text(strip=True)
                    # 检查是否是有效的地区名称
                    if text in all_regions:
                        current_state = text
                        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                            log_file.write(f'识别到地区: {current_state}\n')
                
                # 检查是否是众议员行
                elif element.name == 'tr' and current_state:
                    # 查找所有单元格
                    cells = element.find_all('td')
                    if len(cells) >= 6:  # 确保有足够的单元格
                        # 提取数据
                        district = cells[0].get_text(strip=True)
                        name_cell = cells[1]
                        party = cells[2].get_text(strip=True)
                        office = cells[3].get_text(strip=True)
                        phone = cells[4].get_text(strip=True)
                        committee = cells[5].get_text(strip=True)
                        
                        # 提取姓名和网站链接
                        name_link = name_cell.find('a', href=True)
                        if name_link:
                            name = name_link.get_text(strip=True).replace('(link is external)', '').strip()
                            website = name_link.get('href')
                            
                            if name and website:
                                # 确定地区分类
                                region_category = get_region_category(current_state)
                                
                                representatives.append({
                                    "name": name,
                                    "website": website,
                                    "district": district,
                                    "state": current_state,
                                    "region_category": region_category,
                                    "party": party,
                                    "committee": committee
                                })
                                # 写入日志
                                with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                                    log_file.write(f'添加众议员: {name} ({current_state}, {district}, {region_category})\n')
            
            # 写入日志
            with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f'从 By State and District 视图找到 {len(representatives)} 位众议员\n')
        except Exception as e:
            # 写入日志
            with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f'从 By State and District 视图提取数据失败: {e}\n')
                import traceback
                log_file.write(traceback.format_exc())
    
    # 去重，避免重复条目
    seen = set()
    unique_representatives = []
    for rep in representatives:
        if rep["website"] not in seen:
            seen.add(rep["website"])
            unique_representatives.append(rep)
    
    # 写入日志
    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f'去重后找到 {len(unique_representatives)} 个唯一链接\n')
    
    return unique_representatives

def save_to_excel(representatives):
    """保存议员信息到Excel文件"""
    # 写入日志
    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write('开始保存到Excel...\n')
    
    if not representatives:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write('未找到众议员网站链接\n')
        return False
    
    # 写入日志
    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f'找到 {len(representatives)} 位众议员的网站链接\n')
    
    # 保存为CSV格式（更可靠）
    csv_file = os.path.join(os.getcwd(), "house_representatives_websites.csv")
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "website", "district", "state", "region_category", "party", "committee"])
            for rep in representatives:
                writer.writerow([
                    rep["name"], 
                    rep["website"], 
                    rep.get("district", ""),
                    rep.get("state", ""), 
                    rep.get("region_category", ""),
                    rep.get("party", ""), 
                    rep.get("committee", "")
                ])
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'已保存为CSV格式: {csv_file}\n')
        # 打印到控制台
        print(f'已保存为CSV格式: {csv_file}')
    except Exception as e:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'保存CSV失败: {e}\n')
        # 打印到控制台
        print(f'保存CSV失败: {e}')
    
    # 尝试保存为Excel格式
    try:
        df = pd.DataFrame(representatives)
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write('DataFrame创建成功\n')
        
        excel_file = os.path.join(os.getcwd(), "house_representatives_websites.xlsx")
        df.to_excel(excel_file, index=False)
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'已保存为Excel格式: {excel_file}\n')
        # 打印到控制台
        print(f'已保存为Excel格式: {excel_file}')
        return True
    except Exception as e:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'保存Excel失败: {e}\n')
        # 打印到控制台
        print(f'保存Excel失败: {e}')
        # 即使Excel保存失败，只要CSV保存成功，就返回True
        return True

def main():
    """主函数"""
    # 写入日志
    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write('开始执行主函数\n')
    
    try:
        # 获取议员信息
        representatives = get_representatives()
        
        # 保存到Excel
        success = save_to_excel(representatives)
        
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            if success:
                log_file.write('爬取完成！\n')
            else:
                log_file.write('爬取失败！\n')
    except Exception as e:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'发生错误: {e}\n')
            import traceback
            log_file.write(traceback.format_exc())

if __name__ == "__main__":
    main()
    # 写入日志
    with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write('脚本执行完毕\n')
