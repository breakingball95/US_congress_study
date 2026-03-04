#!/usr/bin/env python3
"""
美国众议院议员社交媒体爬虫

功能：爬取美国众议院议员的X（Twitter）和Facebook个人主页链接，并保存为Excel和CSV文件

使用方法：
1. 确保已安装Python 3
2. 安装依赖：pip install requests beautifulsoup4 pandas openpyxl
3. 运行脚本：python scrape_social_media.py

输出：生成 house_representatives_social_media.xlsx 和 house_representatives_social_media.csv 文件
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
import os
import random
from urllib.parse import urljoin, urlparse

# 反反爬虫设置
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
]

# 读取之前爬取的众议员数据
def load_representatives():
    """从Excel或CSV文件加载众议员数据"""
    data_file = "house_representatives_websites.xlsx"
    if not os.path.exists(data_file):
        data_file = "house_representatives_websites.csv"
    
    if not os.path.exists(data_file):
        print("错误: 未找到众议员数据文件，请先运行 house_reps_scraper.py")
        return []
    
    try:
        if data_file.endswith(".xlsx"):
            df = pd.read_excel(data_file)
        else:
            df = pd.read_csv(data_file)
        
        representatives = []
        for index, row in df.iterrows():
            representatives.append({
                "name": row.get("name", ""),
                "website": row.get("website", ""),
                "state": row.get("state", ""),
                "party": row.get("party", ""),
                "committee": row.get("committee", "")
            })
        return representatives
    except Exception as e:
        print(f"读取数据文件失败: {e}")
        return []

# 获取社交媒体链接
def get_social_media_links(url):
    """从议员个人网站获取X和Facebook链接"""
    social_links = {
        "x": "",
        "facebook": ""
    }
    
    if not url:
        return social_links
    
    # 随机选择User-Agent
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # 随机延迟，模拟真人行为
        time.sleep(random.uniform(2, 5))
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 查找所有链接
        links = soup.find_all("a", href=True)
        
        for link in links:
            href = link.get("href")
            text = link.get_text(strip=True).lower()
            
            # 检查X/Twitter链接
            if any(keyword in href.lower() for keyword in ["twitter.com", "x.com"]):
                social_links["x"] = href
            
            # 检查Facebook链接
            if "facebook.com" in href.lower():
                social_links["facebook"] = href
        
        # 如果没有找到，尝试查找图标链接
        if not social_links["x"] or not social_links["facebook"]:
            icons = soup.find_all(["i", "span", "div"], class_=True)
            for icon in icons:
                classes = icon.get("class", [])
                classes_str = " ".join(classes).lower()
                
                if any(keyword in classes_str for keyword in ["twitter", "x-icon"]):
                    parent = icon.find_parent("a", href=True)
                    if parent and any(keyword in parent.get("href", "").lower() for keyword in ["twitter.com", "x.com"]):
                        social_links["x"] = parent.get("href")
                
                if "facebook" in classes_str:
                    parent = icon.find_parent("a", href=True)
                    if parent and "facebook.com" in parent.get("href", "").lower():
                        social_links["facebook"] = parent.get("href")
        
    except Exception as e:
        print(f"获取 {url} 的社交媒体链接失败: {e}")
    
    # 随机延迟，避免请求过快
    time.sleep(random.uniform(1, 3))
    
    return social_links

# 保存数据到文件
def save_data(representatives):
    """保存数据到Excel和CSV文件"""
    # 保存为CSV
    csv_file = "house_representatives_social_media.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "website", "state", "party", "committee", "x", "facebook"])
            for rep in representatives:
                writer.writerow([
                    rep["name"], 
                    rep["website"], 
                    rep.get("state", ""), 
                    rep.get("party", ""), 
                    rep.get("committee", ""), 
                    rep.get("x", ""), 
                    rep.get("facebook", "")
                ])
        print(f"已保存为CSV格式: {csv_file}")
    except Exception as e:
        print(f"保存CSV失败: {e}")
    
    # 保存为Excel
    excel_file = "house_representatives_social_media.xlsx"
    try:
        df = pd.DataFrame(representatives)
        df.to_excel(excel_file, index=False)
        print(f"已保存为Excel格式: {excel_file}")
    except Exception as e:
        print(f"保存Excel失败: {e}")

def main():
    """主函数"""
    print("美国众议院议员社交媒体爬虫")
    print("=" * 60)
    
    # 加载众议员数据
    print("正在加载众议员数据...")
    representatives = load_representatives()
    
    if not representatives:
        print("没有众议员数据，无法继续")
        return
    
    print(f"找到 {len(representatives)} 位众议员")
    
    # 为每位众议员获取社交媒体链接
    print("正在获取社交媒体链接...")
    print("这可能需要一段时间，请耐心等待...")
    
    for i, rep in enumerate(representatives):
        name = rep.get("name", "")
        website = rep.get("website", "")
        
        print(f"[{i+1}/{len(representatives)}] 正在处理: {name}")
        
        # 获取社交媒体链接
        social_links = get_social_media_links(website)
        rep.update(social_links)
        
        # 打印结果
        if social_links["x"] or social_links["facebook"]:
            print(f"  X: {social_links['x']}")
            print(f"  Facebook: {social_links['facebook']}")
        else:
            print("  未找到社交媒体链接")
    
    # 保存数据
    print("\n正在保存数据...")
    save_data(representatives)
    
    print("=" * 60)
    print("爬虫执行完成！")
    print("请查看生成的 house_representatives_social_media.xlsx 和 house_representatives_social_media.csv 文件")

if __name__ == "__main__":
    main()
