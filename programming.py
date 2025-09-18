import requests
import csv
import re

def get_url(year, month):
	return f"https://lishi.tianqi.com/foshan/{year}{month:02d}.html"

def parse(page_content):
	# 网页源码为 bytes，需解码
	text = page_content.decode('utf-8', errors='ignore')
	# 正则提取气温数组和日期
	hightemp = re.findall(r'var hightemp = \[(.*?)\];', text)
	lowtemp = re.findall(r'var lowtemp = \[(.*?)\];', text)
	timeaxis = re.findall(r'var timeaxis = \[(.*?)\];', text)
	if not hightemp or not lowtemp or not timeaxis:
		return []
	# 处理为列表
	hightemp = [x.strip().strip('"') for x in hightemp[0].split(',')]
	lowtemp = [x.strip().strip('"') for x in lowtemp[0].split(',')]
	timeaxis = [x.strip() for x in timeaxis[0].split(',')]
	# 日期格式：假设为 "YYYY-MM-DD"，如无年份则补全
	data = []
	for i in range(len(timeaxis)):
		# 日期格式为 "年-月-日"
		day = timeaxis[i]
		# 需从外部传入当前年份和月份，暂用占位
		# 这里返回 (day, hightemp, lowtemp)，主函数负责补全年月
		data.append((day, hightemp[i], lowtemp[i]))
	return data

def fetch_temperature_data(start_year, start_month, end_year, end_month):
    results = []
    year, month = start_year, start_month
    while (year < end_year) or (year == end_year and month <= end_month):
        url = get_url(year, month)
        print(f"正在爬取 {year}年{month}月: {url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            month_data = parse(response.content)
            print(f"解析结果: {month_data}")
            # 补全年月，保存为 YYYY-MM-DD, 最高气温, 最低气温
            for item in month_data:
                day, high, low = item
                date_str = f"{year}-{month:02d}-{day.zfill(2)}"
                results.append([date_str, high, low])
        except Exception as e:
            print(f"跳过 {year}-{month}: {e}")
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return results

def save_to_csv(data, filename):
	with open(filename, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerow(['Date', 'MaxTemp', 'MinTemp'])
		writer.writerows(data)

import matplotlib.pyplot as plt
import matplotlib.animation as animation
def plot_heatmap_animation(csv_file, gif_file):
	import numpy as np
	df = pd.read_csv(csv_file)
	df['Year'] = pd.to_datetime(df['Date']).dt.year
	df['Month'] = pd.to_datetime(df['Date']).dt.month
	# 统计每年每月的最高气温
	pivot = df.pivot_table(index='Year', columns='Month', values='MaxTemp', aggfunc='mean')
	years = pivot.index.tolist()
	months = pivot.columns.tolist()
	data = pivot.values
	fig, ax = plt.subplots(figsize=(10, 6))
	def update(i):
		ax.clear()
		im = ax.imshow(data[:i+1, :], cmap='hot', aspect='auto', vmin=np.nanmin(data), vmax=np.nanmax(data))
		ax.set_xticks(np.arange(len(months)))
		ax.set_xticklabels(months)
		ax.set_yticks(np.arange(i+1))
		ax.set_yticklabels(years[:i+1])
		ax.set_xlabel('Month')
		ax.set_ylabel('Year')
		ax.set_title(f'Foshan Max Temperature Heatmap (Up to {years[i]})')
		fig.colorbar(im, ax=ax, orientation='vertical')
	ani = animation.FuncAnimation(fig, update, frames=len(years), repeat=False)
	ani.save(gif_file, writer='pillow', fps=1)
	plt.close()
	print(f"热力图动画已保存为 {gif_file}")
import pandas as pd

def plot_monthly_boxplot(csv_file, img_file):
	# 读取数据
	df = pd.read_csv(csv_file)
	# 提取月份
	df['Month'] = pd.to_datetime(df['Date']).dt.month
	# 按月份分组，收集所有年份的气温
	month_temp = {m: [] for m in range(1, 13)}
	for _, row in df.iterrows():
		month = row['Month']
		# 最高气温
		month_temp[month].append(float(row['MaxTemp']))
	# 按月份顺序准备箱图数据
	data_for_box = [month_temp[m] for m in range(1, 13)]
	plt.figure(figsize=(12, 6))
	plt.boxplot(data_for_box, labels=[str(m) for m in range(1, 13)])
	plt.xlabel('Month')
	plt.ylabel('Max Temperature (°C)')
	plt.title('Monthly Max Temperature Boxplot (2021-2025)')
	plt.grid(True, axis='y', linestyle='--', alpha=0.5)
	plt.savefig(img_file)
	plt.close()
	print(f"箱型图已保存为 {img_file}")

if __name__ == "__main__":
	start_year, start_month = 2021, 7
	end_year, end_month = 2025, 7
	data = fetch_temperature_data(start_year, start_month, end_year, end_month)
	save_to_csv(data, 'foshan_temperature_2021-2025.csv')
	print("数据已保存到 foshan_temperature_2021-2025.csv")
	# 绘制箱型图
	plot_monthly_boxplot('foshan_temperature_2021-2025.csv', 'monthly_temperature_boxplot.png')
	# 绘制热力图动画
	plot_heatmap_animation('foshan_temperature_2021-2025.csv', 'temperature_heatmap.gif')
