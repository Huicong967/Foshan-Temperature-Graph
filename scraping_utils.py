# scraping_utils.py

def get_url(year, month):
    # 请根据目标网站实际URL格式修改
    return f"https://example.com/foshan-temperature/{year}/{month:02d}"

from lxml import html

def parse(page_content):
    tree = html.fromstring(page_content)
    # 请根据实际网页结构修改xpath
    data = []
    for row in tree.xpath('//table[@id="temperature-table"]/tbody/tr'):
        date = row.xpath('./td[1]/text()')[0]
        temp = row.xpath('./td[2]/text()')[0]
        data.append((date, temp))
    return data
