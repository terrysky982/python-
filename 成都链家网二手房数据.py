#抓取成都链家二手房数据
import csv
import requests
from bs4 import BeautifulSoup
import time
from openpyxl import Workbook
import re


base_page="https://cd.lianjia.com/ershoufang/"

#读取网页
def get_html(url):
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'}
	page_html = requests.get(url,headers=headers).text
	return page_html

#检索出所有区域的代码
def area_url():
	n = 0
	pu_page = []
	soup = BeautifulSoup(get_html(base_page),'lxml')
	#检索出所有区的地址
	area_urls = soup.select('body > div:nth-child(11) > div > div.position > dl:nth-child(2) > dd > div:nth-of-type(1) > div > a')
	area_hrefs = [u['href'] for u in area_urls]

	#检索出所有街道的地址
	for area_url in area_hrefs:
		#载入页面
		area_url= base_page + area_url[12:]
		#读取街道列表
		soup = BeautifulSoup(get_html(area_url),'lxml')

		street_urls1 = soup.select('body > div:nth-child(11) > div > div.position > dl:nth-child(2) > dd > div:nth-child(1) > div:nth-child(2) > a')
		street_hrefs = [s['href'] for s in street_urls1]
		#逐个替换成准确网址并存入pu_page
		for street_href in street_hrefs:
			street_href = base_page + street_href[12:]
			pu_page.append(street_href)
			#计数，防止假死
			n= n + 1
			print('正在运行,找到的街道数据量：' +str(n ))
	#列表去重
	pu_page  = set(pu_page)

	#print(pu_page)
	print('去重后，街道列表元素总量：' +str(len(pu_page))+"。\n")

	return pu_page



#主程序
def main():
	wb= Workbook()
	pu_pages = area_url()
	pu_num = 0
	total_num = 0
	for pu_url in pu_pages:
		#读取当前街道二手房的总数，并计算出页面数量
		soup = BeautifulSoup(get_html(pu_url),'lxml')
		num_url = soup.select('#content > div.leftContent > div.resultDes.clear > h2 > span')
		nums = [n.get_text() for n in num_url]
		num = int(nums[0])
		page_num = num // 30 + 1
		print(pu_url[34:-1]+"区域共有："+str(num)+"套二手房。\n")
		#清空列表
		all_page = []

		#针对每个街道迭代出所有页面
		for n in range(1,page_num+1,1):
			page = pu_url + 'pg'+str(n)+"/"
			all_page.append(page)
		
		print('现在开始爬取'+pu_url[34:-1]+'数据。\n')
		#准备好sheet
		
		sheet = wb.create_sheet('new',index = 0)
		sheet.title = str(pu_url[34:-1])
		sheet.append(['标题','小区名','详情网址','详细信息','楼栋信息','所在区域','发布情况','总价（万元）','单价（元）','建筑面积（m2）','标签信息'])	
		
		#调用get_info函数取得数据

		total_num = total_num + get_info(all_page,sheet)
		pu_num = pu_num + 1
		print(pu_url[34:-1]+"街道二手房数据导出完毕。\n"+pu_num+'个街道的数据已完成，离成功更进一步。\n')
		print('二手房数据总量========>'+ str(total_num))
		#保存数据
		wb.save('./二手房/成都二手房数据'+time.strftime("%Y-%m-%d", time.localtime())+'.xlsx')
		#调试专用！！！！
		#if pu_num == 2:
			#exit()

	print('xlsx文件保存成功！！！\n共抓取到'+str(total_num)+'条数据！！！')


		
	

#读取每页中的数据
def get_info(page_list,sheet):
	
	#获取数据
	i = 0
	info_num = 0
	for page_url in page_list:
		i = i+1
		print("开始爬取：第"+str(i)+"页。")	
		soup = BeautifulSoup(get_html(page_url),'lxml')
		#简介
		all_title = soup.select('div .title > a')
		titles=[t.get_text() for t in all_title]
		
		#print(all_title)
		#print(titles)
		#详情页网址
		info_urls=[t['href'] for t in all_title]
		#print(info_urls)
		#地址
		all_adds = soup.select('div .houseInfo > a')

		adds=[ad.get_text() for ad in all_adds]
		#print(all_adds)
		#print(adds)
		#简要信息
		all_sam_info = soup.find_all('div',class_='houseInfo')
		infos=[info.get_text() for info in all_sam_info]
		#print(all_sam_info)
		#print(infos)
		#楼栋信息
		all_pos_div = soup.select('div .positionInfo')
		lous = [pos.get_text() for pos in all_pos_div]
		#print(lous)
		#区域
		all_pos_area = soup.select('div .positionInfo > a')
		areas = [ar.get_text() for ar in all_pos_area]
		#print(areas)
		#发布信息
		all_follows =soup.find_all('div',class_='followInfo')
		follows =[fo.get_text() for fo in all_follows]
		#print(follows)
		#总价
		all_totalprices = soup.find_all('div',class_='totalPrice')
		totalPrices=[tp.get_text() for tp in all_totalprices]
		#print(all_totalprices)
		#print(totalPrices)
		#单价
		all_unitprices = soup.find_all('div',class_='unitPrice')
		unitPrices=[up.get_text() for up in all_unitprices]
		
		#print(unitPrices)
		#标签信息
		all_tags =soup.find_all('div',class_='tag')
		tags =[ta.get_text() for ta in all_tags]
		#print(tags)

		for title,add,info_url,info,lou,area,foll,totalpr,unitpr,tag in zip(titles,adds,info_urls,infos,lous,areas,follows,totalPrices,unitPrices,tags):
			try:
				totalpr = float(re.findall(r'\d+\.?\d*',totalpr)[0])
				unitpr = float(re.findall(r'\d+\.?\d*',unitpr)[0])
				arnum = totalpr*10000/unitpr
			except:
				totalpr = totalpr
				unitpr = unitpr
				arnum = 0
			sheet.append([str(title),str(add),str(info_url),str(info),str(lou),str(area),str(foll),float(totalpr),float(unitpr),float(arnum),str(tag)])
			info_num = info_num +1
		
		time.sleep(2)
	print('当前街道共' + str(info_num) + '条数据')
	return info_num



main()
print("所有数据导出完毕")
