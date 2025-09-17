import requests
import csv
from lxml import html

# 生成目标网站每月历史天气页面的URL
def get_url(year, month):
	return f"https://lishi.tianqi.com/foshan/{year}{month:02d}.html"

# 解析网页内容，提取气温数据
def parse(page_content):
	tree = html.fromstring(page_content)
	tables = tree.xpath('//table')
	if not tables:
		return []
	table = tables[0]
	data = []
	for row in table.xpath('.//tr')[1:]:  # 跳过表头
		tds = row.xpath('./td/text()')
		if len(tds) >= 3:
			date = tds[0].strip()
			temp = tds[1].strip()
			data.append((date, temp))
	return data

# 主函数：批量爬取指定时间段的气温数据
def fetch_temperature_data(start_year, start_month, end_year, end_month):
	results = []
	year, month = start_year, start_month
	while (year < end_year) or (year == end_year and month <= end_month):
		url = get_url(year, month)
		print(f"正在爬取 {year}年{month}月: {url}")
		try:
			response = requests.get(url)
			response.raise_for_status()
			month_data = parse(response.content)
			for date, temp in month_data:
				results.append([date, temp])
		except Exception as e:
			print(f"跳过 {year}-{month}: {e}")
		if month == 12:
			year += 1
			month = 1
		else:
			month += 1
	return results

# 保存数据到 CSV 文件
def save_to_csv(data, filename):
	with open(filename, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerow(['日期', '气温'])
		writer.writerows(data)

if __name__ == "__main__":
	start_year, start_month = 2021, 7
	end_year, end_month = 2025, 7
	data = fetch_temperature_data(start_year, start_month, end_year, end_month)
	save_to_csv(data, 'foshan_temperature_2021-2025.csv')
	print("数据已保存到 foshan_temperature_2021-2025.csv")