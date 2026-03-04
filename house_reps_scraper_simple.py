#!/usr/bin/env python3
"""
美国众议院议员网站爬虫

功能：爬取美国众议院网站上所有议员的个人官网链接，并保存为Excel文件

使用方法：
1. 确保已安装Python 3
2. 安装依赖：pip install requests beautifulsoup4 pandas openpyxl
3. 运行脚本：python house_reps_scraper_simple.py

输出：生成 house_representatives_websites.xlsx 文件，包含议员姓名、个人网站链接、所属政党和委员会分配信息
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

# 写入日志
with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
    log_file.write('模块导入成功\n')

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
    
    # 查找众议员数据
    try:
        # 查找所有表格
        tables = soup.find_all('table')
        
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'找到 {len(tables)} 个表格\n')
        
        # 遍历每个表格
        for table in tables:
            # 查找表格中的所有行
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
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
                            representatives.append({
                                "name": name,
                                "website": website,
                                "party": party,
                                "committee": committee
                            })
                            # 写入日志
                            with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
                                log_file.write(f'添加众议员: {name}\n')
        
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'找到 {len(representatives)} 位众议员的详细信息\n')
    except Exception as e:
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'解析众议员数据失败: {e}\n')
            import traceback
            log_file.write(traceback.format_exc())
    
    # 如果没有找到详细信息，使用旧的链接提取策略
    if not representatives:
        # 先查找所有可能的链接
        links = soup.find_all("a", href=True)
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'找到 {len(links)} 个链接\n')
        
        # 尝试不同的链接提取策略
        # 策略1: 查找带有 "link is external" 标记的链接
        external_links = 0
        for link in links:
            href = link.get("href")
            text = link.get_text(strip=True)
            
            if href and "link is external" in text:
                external_links += 1
                # 提取议员姓名（去除 " (link is external)" 部分）
                name = text.replace(" (link is external)", "").strip()
                if name and href:
                    representatives.append({
                        "name": name,
                        "website": href,
                        "party": "",
                        "committee": ""
                    })
        
        # 写入日志
        with open('scraper_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'策略1找到 {external_links} 个外部链接\n')
    
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
            writer.writerow(["name", "website", "party", "committee"])
            for rep in representatives:
                writer.writerow([
                    rep["name"], 
                    rep["website"], 
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
