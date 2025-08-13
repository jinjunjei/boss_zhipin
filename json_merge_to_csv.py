import csv
import json
import os
from datetime import datetime


def get_rows(json_data):
    '''
    #得到csv文件一个公司的数据，非表头
    :param json_data:
    :return:一个公司的职位
    '''
    rows = []
    # 如果公司没有职位，则返回一个空数组
    if json_data['company_job'] =='':
        return [[json_data['company_name'],
                json_data['company_job_num'],
                '','','','','','','','']]
    #每个工作执行一次
    for row_job in json_data['company_job']:
        for row_job in json_data['company_job']:
            row = []
            for row_com in json_data.keys():
                if row_com != 'company_job':
                    row.append(json_data[row_com])
            for row_job_value in row_job.values():
                row.append(row_job_value)
            rows.append(row)
    return rows


def get_head():
    '''
    返回固定表头
    :return: 头数组
    '''
    return ['company_name','company_job_num',
            'company_tag','company_name','name',
            'salary','job_tags','job_label',
            'job_desc','job_address']


def get_all_json(directory):
    '''
    :param directory: 遍历目录下的所有文件
    :return: 包含所有公司json的句柄的数组
    '''
    # 保存所有公司json的句柄
    company_json_filepoint = []
    # 遍历目录下的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                # 打开文件并添加到列表
                f = open(file_path, mode='r', encoding='utf-8')
                company_json_filepoint.append(f)
            except Exception as e:
                print(f"无法打开文件 {file_path}: {e}")

    return company_json_filepoint

def merge_json(json_list):
    '''
    # 合并多个公司json
    :param json_list: 文件句柄指针的列表
    :return: 总数组
    '''
    rows = []
    for json_file in json_list:
        json_data = json.load(json_file)
        rows += get_rows(json_data)
    header = get_head()
    data = [header] + rows
    return data


def store_csv(cityname,data):
    '''
    :param cityname: 存储名
    :return:
    '''
    time = datetime.now().strftime("%y-%m-%d %H-%M-%S")
    with open(f'{cityname} job {time}.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 一次性写入所有行
        writer.writerows(data)


def main(cityname):
    json_list = get_all_json(fr'raw_json\{cityname}')
    data = merge_json(json_list)
    store_csv(cityname, data)
    print("csv转换完成")

if __name__ == '__main__':
    cityname = '杭州'
    main(cityname)






