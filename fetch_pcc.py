# -*- coding: utf-8 -*-
pcc_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/'
baidu_url = 'http://www.baidu.com'

import urllib2
import pdb
import json
import time
from functools import wraps

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry

@retry(urllib2.URLError, tries=4, delay=3, backoff=2)
def urlopen_with_retry(url_request):
    return urllib2.urlopen(url_request)

def main():
	pcc_data = {}

	req = urllib2.Request(pcc_url)
	req.add_header('Cache-Control', 'no-cache')
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
	time.sleep(1)
	resp = urlopen_with_retry(req)
	contents = resp.read()
	refined_province = contents[contents.find('provincetr'):]
	while True:
		href_pos = refined_province.find('href=')
		if href_pos == -1:
			break
		html_pos = refined_province.find('html', href_pos)
		if html_pos == -1:
			break
		province_no = int(refined_province[href_pos + 6:html_pos - 1])
		print province_no
		br_pos = refined_province.find('br', href_pos)
		if br_pos == -1:
		    break
		greater_pos = refined_province.find('>', href_pos)
		if greater_pos == -1:
		    break
		province_name = refined_province[href_pos + 15:br_pos - 1].decode('gbk').encode('utf8')
		print province_name

		pcc_data[province_no] = {'name': province_name, 'cities': {}}

		# City
		city_req = urllib2.Request(pcc_url + str(province_no) + '.html')
		city_req.add_header('Cache-Control', 'no-cache')
		city_req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
		time.sleep(1)
		city_resp = urlopen_with_retry(city_req)
		city_contents = city_resp.read()
		refined_city = city_contents[city_contents.find('cityhead'):]
		while True:
			city_pos = refined_city.find('citytr')
			if city_pos == -1:
				break
			html_pos = refined_city.find('html', city_pos)
			if html_pos == -1:
				break
			slash_a_pos = refined_city.find('/a', html_pos + 1)
			if slash_a_pos == -1:
				break
			city_no = int(refined_city[html_pos + 6:slash_a_pos - 1])
			print '	', city_no
			html_pos = refined_city.find('html', html_pos + 1)
			if html_pos == -1:
				break
			slash_a_pos = refined_city.find('/a', html_pos + 1)
			if slash_a_pos == -1:
				break
			city_name = refined_city[html_pos + 6:slash_a_pos - 1].decode('gbk').encode('utf8')
			print '	', city_name

			pcc_data[province_no]['cities'][city_no / 100000] = {'name': city_name, 'counties': {}}

			# County
			county_req = urllib2.Request(pcc_url + str(province_no) + '/' + str(city_no / 100000000) + '.html')
			county_req.add_header('Cache-Control', 'no-cache')
			county_req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
			time.sleep(1)
			county_resp = urlopen_with_retry(county_req)
			county_contents = county_resp.read()
			refined_county = county_contents[county_contents.find('countyhead'):]
			while True:
				county_pos = refined_county.find('countytr')
				if county_pos == -1:
					break
				html_pos = refined_county.find('html', county_pos)
				if html_pos == -1:
					break
				slash_a_pos = refined_county.find('/a', html_pos + 1)
				if slash_a_pos == -1:
					break
				county_no = int(refined_county[html_pos + 6:slash_a_pos - 1])

				html_pos = refined_county.find('html', html_pos + 1)
				if html_pos == -1:
					break
				slash_a_pos = refined_county.find('/a', html_pos + 1)
				if slash_a_pos == -1:
					break
				county_name = refined_county[html_pos + 6:slash_a_pos - 1].decode('gbk').encode('utf8')
				print '		', county_name
				refined_county = refined_county[slash_a_pos:]

				pcc_data[province_no]['cities'][city_no / 100000]['counties'][county_no  / 10000] = county_name

			refined_city = refined_city[slash_a_pos:]

		refined_province = refined_province[br_pos:]

	pcc_data_json_str = json.dumps(pcc_data, ensure_ascii=False)
	js_file = open('pcc.js', 'w')
	js_file.write(pcc_data_json_str)
	js_file.close()

if __name__ == "__main__":
	main()
