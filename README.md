# 美国众议院议员网站爬虫使用指南

## 问题分析

当前环境中缺少必要的Python依赖包，导致爬虫脚本无法正常运行。为了解决这个问题，我们需要在本地环境中正确安装依赖并运行脚本。

## 解决方案

### 方法1：在本地环境中运行（推荐）

1. **安装Python 3**
   - 访问 [Python官网](https://www.python.org/downloads/)
   - 下载并安装适合您操作系统的Python 3版本（推荐3.8或更高版本）
   - 确保在安装过程中勾选"Add Python to PATH"选项

2. **安装依赖包**
   - 打开命令提示符（CMD）或终端
   - 运行以下命令：
     ```
     python -m pip install requests beautifulsoup4 pandas openpyxl
     ```

3. **运行爬虫脚本**
   - 导航到脚本所在目录：
     ```
     cd d:\coding\US_congress_study
     ```
   - 运行脚本：
     ```
     python house_reps_scraper.py
     ```

### 方法2：使用在线Python环境

如果您不想在本地安装Python，可以使用以下在线Python环境：

- [Google Colab](https://colab.research.google.com/)
- [Replit](https://replit.com/)
- [PythonAnywhere](https://www.pythonanywhere.com/)

## 脚本功能

- 爬取美国众议院网站上所有议员的个人官网链接
- 提取每位议员的所属州、所属政党和委员会分配信息
- 生成Excel和CSV文件，包含所有收集到的信息
- 包含详细的日志记录，便于调试和错误排查

## 预期输出

运行脚本后，会生成以下文件：

1. **house_representatives_websites.xlsx** - Excel格式的众议员信息
2. **house_representatives_websites.csv** - CSV格式的众议员信息
3. **scraper_log.txt** - 脚本执行的日志文件

## 常见问题

### 问题1：依赖包安装失败
**解决方案**：
- 确保网络连接正常
- 尝试使用 `python -m pip install --user requests beautifulsoup4 pandas openpyxl` 以用户权限安装
- 检查Python版本是否兼容（推荐3.8或更高版本）

### 问题2：脚本运行后没有生成文件
**解决方案**：
- 检查 `scraper_log.txt` 文件，查看是否有错误信息
- 确保您有足够的权限在当前目录创建文件
- 检查网络连接是否正常

### 问题3：州信息不正确
**解决方案**：
- 脚本已经更新，使用了美国州名列表来验证州名
- 确保您使用的是最新版本的 `house_reps_scraper.py` 文件

## 技术支持

如果您在使用过程中遇到任何问题，请查看 `scraper_log.txt` 文件获取详细的错误信息，或参考本指南中的解决方案。
