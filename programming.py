# ================== 热力图动画 ==================
def plot_heatmap_animation(csv_file, gif_file):
	df = pd.read_csv(csv_file)
	df['Year'] = pd.to_datetime(df['Date']).dt.year
	df['Month'] = pd.to_datetime(df['Date']).dt.month
	# 统计每年每月的均值气温
	df['MeanTemp'] = (df['MaxTemp'].astype(float) + df['MinTemp'].astype(float)) / 2
	pivot = df.pivot_table(index='Year', columns='Month', values='MeanTemp', aggfunc='mean')
	years = pivot.index.tolist()
	months = pivot.columns.tolist()
	data = pivot.values
	cmap = plt.get_cmap('hot').copy()
	cmap.set_bad(color='gray')
	fig, ax = plt.subplots(figsize=(10, 6))
	def update(i):
		ax.clear()
		show_data = np.ma.masked_invalid(data[:i+1, :])
		im = ax.imshow(show_data, cmap=cmap, aspect='auto', vmin=np.nanmin(data), vmax=np.nanmax(data))
		ax.set_xticks(np.arange(len(months)))
		ax.set_xticklabels(months)
		ax.set_yticks(np.arange(i+1))
		ax.set_yticklabels(years[:i+1])
		ax.set_xlabel('Month')
		ax.set_ylabel('Year')
		ax.set_title(f'Foshan Mean Temperature Heatmap (Up to {years[i]})')
		fig.colorbar(im, ax=ax, orientation='vertical')
	ani = animation.FuncAnimation(fig, update, frames=len(years), repeat=False)
	ani.save(gif_file, writer='pillow', fps=1)
	plt.close()
	print(f"热力图动画已保存为 {gif_file}")

# ================== 箱型图 ==================
def plot_monthly_boxplot(csv_file, img_file):
	df = pd.read_csv(csv_file)
	df['Month'] = pd.to_datetime(df['Date']).dt.month
	month_temp = {m: [] for m in range(1, 13)}
	for _, row in df.iterrows():
		month = row['Month']
		month_temp[month].append(float(row['MaxTemp']))
	data_for_box = [month_temp[m] for m in range(1, 13)]
	plt.figure(figsize=(12, 6))
	plt.boxplot(data_for_box, labels=[str(m) for m in range(1, 13)])
	plt.xlabel('Month')
	plt.ylabel('Max Temperature (°C)')
	plt.title('Monthly Max Temperature Boxplot (2021-2025)')
	plt.savefig(img_file)
	plt.close()
	print(f"箱型图已保存为 {img_file}")
import requests
import csv
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from datetime import datetime

# ================== 数据采集与保存 ==================
def get_url(year, month):
	"""生成气温数据网页的URL"""
	return f"https://lishi.tianqi.com/foshan/{year}{month:02d}.html"

def parse(page_content):
	"""解析网页源码，提取气温和日期数据"""
	try:
		text = page_content.decode('utf-8', errors='ignore')
		hightemp = re.findall(r'var hightemp = \[(.*?)\];', text)
		lowtemp = re.findall(r'var lowtemp = \[(.*?)\];', text)
		timeaxis = re.findall(r'var timeaxis = \[(.*?)\];', text)
		if not hightemp or not lowtemp or not timeaxis:
			return []
		hightemp = [x.strip().strip('"') for x in hightemp[0].split(',')]
		lowtemp = [x.strip().strip('"') for x in lowtemp[0].split(',')]
		timeaxis = [x.strip() for x in timeaxis[0].split(',')]
		data = []
		for i in range(len(timeaxis)):
			data.append((timeaxis[i], hightemp[i], lowtemp[i]))
		return data
	except Exception as e:
		print(f"解析异常: {e}")
		return []

def fetch_temperature_data(start_year, start_month, end_year, end_month):
	"""爬取指定区间的气温数据，返回[[date, max, min], ...]"""
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
	"""保存气温数据到 CSV 文件"""
	with open(filename, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerow(['Date', 'MaxTemp', 'MinTemp'])
		writer.writerows(data)

# ================== 可视化与动画 ==================
def plot_line_animation(csv_file, gif_file):
	"""
	生成每年每月最高气温的动态折线图动画，并保存为 GIF。
	输入: csv_file（气温数据），gif_file（输出动画文件名）
	"""
	df = pd.read_csv(csv_file)
	df['Year'] = pd.to_datetime(df['Date']).dt.year
	df['Month'] = pd.to_datetime(df['Date']).dt.month
	# 按年份分组，每年每月的最高气温
	pivot = df.pivot_table(index='Year', columns='Month', values='MaxTemp', aggfunc='mean')
	years = pivot.index.tolist()
	months = pivot.columns.tolist()
	fig, ax = plt.subplots(figsize=(10, 6))
	def update(i):
		ax.clear()
		for j in range(i+1):
			ax.plot(months, pivot.iloc[j], marker='o', label=str(years[j]))
		ax.set_xticks(months)
		ax.set_xticklabels(months)
		ax.set_xlabel('Month')
		ax.set_ylabel('Max Temperature (°C)')
		ax.set_title('Monthly Max Temperature Line Animation (2021-2025)')
		ax.legend()
		ax.grid(True, linestyle='--', alpha=0.5)
	ani = animation.FuncAnimation(fig, update, frames=len(years), repeat=False)
	ani.save(gif_file, writer='pillow', fps=1)
	plt.close()
	print(f"折线图动画已保存为 {gif_file}")

# ================== 主流程入口 ==================
if __name__ == "__main__":
	# 设置采集区间（仅采集2021年7月至2025年7月）
	start_year, start_month = 2021, 7
	end_year, end_month = 2025, 7
	# 采集数据
	data = fetch_temperature_data(start_year, start_month, end_year, end_month)
	# 保存为csv
	csv_file = "foshan_temperature_2021-2025.csv"
	save_to_csv(data, csv_file)
	print(f"数据已保存到 {csv_file}")
	# 生成折线图动画
	plot_line_animation(csv_file, "temperature_line_animation.gif")
	# 生成热力图动画
	plot_heatmap_animation(csv_file, "temperature_heatmap.gif")
	# 生成箱型图
	plot_monthly_boxplot(csv_file, "monthly_temperature_boxplot.png")

def get_url(year, month):
	return f"https://lishi.tianqi.com/foshan/{year}{month:02d}.html"

def parse(page_content):
	# 网页源码为 bytes，需解码
	# 绘制折线图动画
	plot_line_animation('foshan_temperature_2021-2025.csv', 'temperature_line_animation.gif')
