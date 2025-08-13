import os
import time
import random
import json
import csv
import pickle
import json_merge_to_csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException


def store_as_json(data,directory,name):
    '''
    # 存储json数据
    :param data: 爬取一个公司的职位，字典
    :param name: 存储的名字，str
    :return:
    '''
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    time=datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    os.makedirs(f"raw_json/{directory[:-4:]}", exist_ok=True)
    with open(f"raw_json/{directory[:-4:]}/{name}.json", "w", encoding="utf-8") as f:
        f.write(json_data)
    print('json存储成功')

def make_driver():
    '''
    user-data-dir的路径改到项目目录下的chrome_user_data文件夹
    设置driver对象，包括分辨率用户数据等
    :return: driver对象，操作浏览器
    '''
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1280,720')
    options.add_argument(r'--user-data-dir=E:\apytorch\python lean\chrome_user_data')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 8.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')

    driver = uc.Chrome(options=options,
                       driver_executable_path=r'E:\apytorch\python lean\chromedriver.exe'
                       )
    driver.set_window_size(1280, 720)
    return driver

def config_salary(salary_str):
    '''
    # 解密工资数字
    :param salary_str:解密前的工资，str
    :return: 解密后的工资，str
    '''
    new_salary_str = ''
    for s in salary_str:
        if s > '\ue020':
            new_salary_str += chr(ord(s) - 57393 + 48)
        else:
            new_salary_str += s
    return new_salary_str

def get_company_name( csv_file,col):
    '''
    # 从csv文件获取公司列表
    :param col: 读取第几列，int
    :param csv_file: csv文件目录,str
    :return:
    '''
    column_data = []
    with open(f'{csv_file}', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > col \
                    and '公司' in row[col] \
                    :
                column_data.append(row[col])
    return column_data

def scroll_to_bottom(driver):
    '''
    滚动页面到底部
    :param driver: make出的driver,chromedriver
    :return:
    '''
    for i in range(5):
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        time.sleep(0.5)

    driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")

def get_one_company(driver,name):
    '''
    获取一个公司的所有职位
    :param driver: make出的driver,chromedriver
    :param name: 公司名字,str
    :return: 待转为json的字典
    '''
    time.sleep(random.uniform(3, 4))
    driver.get("https://www.zhipin.com/web/geek/jobs?"
               "position=100101,100102,100103,100109,100106,100107,100116,100114,100121,101313,100124,100125,100123,100199,100901,100202,100203,100209,100211,100210,100212,100208,100213,100301,100307,100309,100304,100302,100310,100303,100703,100305,100308,100511,100514,100508,100122,100507,100515,100506,100104,100512,100120,101307,101301,101302,101308,130121,101309,101311,101310,100117,100115,101305,100118,101306,101312,100608&"
               f"query={name}")
    print(f'正在爬取{name}')
    # 滚动页面
    scroll_to_bottom(driver)
    # 判断是否登录
    if is_login(driver): pass

    # 判断是否找到公司
    if not is_find_company(driver):
        return {
            'company_name': name,
            'company_job_num': 0,
            'company_tag': '',
            'company_job': ''
        }
    # 等待side栏加载完成
    try:
        side_list = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-list-container"))
        )
    except WebDriverException:
        print(f'{name}的职位信息获取失败')
        return {
            'company_name': name,
            'company_job_num': 0,
            'company_tag': '',
            'company_job':''
        }
    side_jobs = side_list.find_elements(By.CLASS_NAME, "job-info")
    # 总循环数据
    job_total_data = []
    for job in side_jobs:
        driver.execute_script("arguments[0].click();", job)
        time.sleep(random.uniform(0.5, 0.8))
        # 等待右侧box加载
        job_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-detail-box"))
        )
        # print(job_box.text)
        # 获取名字、获取工资、获取标签，如（南京 3-5年 本科）
        job_name = job_box.find_element(By.CLASS_NAME, "job-name")
        job_salary = job_box.find_element(By.CLASS_NAME, "job-salary")
        job_tags = job_box.find_element(By.CLASS_NAME, "tag-list")
        # 尝试查找label,可能为空、获取职位描述、获取地址
        try:
            job_label = driver.find_element(By.CSS_SELECTOR, ".job-label-list").text
        except:
            job_label = ''
        job_desc = job_box.find_element(By.XPATH, "//p[@class='desc']")
        job_address = job_box.find_element(By.XPATH, "//p[@class='job-address-desc']")
        # 本次循环数据
        job_data = {
            'company_name': name,
            'name': job_name.text,
            # 获取解码后的工资
            'salary': config_salary(job_salary.text),
            'job_tags': job_tags.text,
            'job_label': job_label,
            'job_desc': job_desc.text,
            'job_address': job_address.text

        }
        job_total_data.append(job_data)
        #break 测试，只取一个职位

    try:
        company_name = side_list.find_element(By.CLASS_NAME, "company-name")
        company_job_num = side_list.find_element(By.CSS_SELECTOR, ".count-item.count-job")
        company_tag = side_list.find_elements(By.CLASS_NAME, "company-info-tag")
        company_data={
            'company_name': company_name.text,
            'company_job_num': company_job_num.text,
            'company_tag': [tag.text for tag in company_tag],
            'company_job': job_total_data
        }
    except:
        company_data = {
            'company_name': name,
            'company_job_num': '',
            'company_tag': '',
            'company_job': job_total_data
        }


    return company_data

def get_each_company_jobs(driver,name_list,strat_num=0,directory=''):
    '''
    获取所有公司职位
    :param driver:make出的driver,chromedriver
    :param name_list:公司名称，list
    :param strat_num: 从第几个开始
    :return:
    '''
    i=0
    for name in name_list:
        if i<strat_num:print(i);i+=1;continue
        print(f'{i}.',end='');i += 1
        if i%50==0:time.sleep(5);print('--------休息5秒---------')
        total_data = get_one_company(driver,name)
        store_as_json(total_data,directory, name)

def is_login(driver):
    '''
    判断是否登录
    :param driver:make出的driver,chromedriver
    :return:
    '''
    try:
        user_info = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-nav"))
        )
        user_info.find_element(By.PARTIAL_LINK_TEXT, "消息")
        # print('已登录')
        return True
    except:
        input('未登录，点击再次查看状态')
        is_login(driver)

def is_find_company(driver):
    '''
    是否找到公司
    :param driver:make出的driver,chromedriver
    :return:是否成功，bool
    '''
    try:
        no_find = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), '没有找到相关职位')]"))
        )
        return False
    except WebDriverException:
        return True


if __name__ == '__main__':
    dire = '杭州.csv'
    driver = make_driver()
    name_list=get_company_name(dire,col=1 )
    get_each_company_jobs(driver,
                          name_list,
                          strat_num=0,
                          directory=dire)
    json_merge_to_csv.main(dire[:-4:])
    input('完成,输入任意退出')
    driver.quit()

