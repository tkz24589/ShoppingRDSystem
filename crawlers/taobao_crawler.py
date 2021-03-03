import requests as rq
import cv2 as cv
import re
import xlwt


def writeToExcel(ilt, name):
    if name != '':
        count = 0
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('temp')
        worksheet.write(count, 0, '序号')
        worksheet.write(count, 1, '购买')
        worksheet.write(count, 2, '价格')
        worksheet.write(count, 3, '描述')
        worksheet.write(count, 4, '图片地址')
        for g in ilt:
            count = count + 1
            worksheet.write(count, 0, count)
            worksheet.write(count, 1, g[0])
            worksheet.write(count, 2, g[1])
            worksheet.write(count, 3, g[2])
            worksheet.write(count, 4, g[3])
        workbook.save(name + '.xls')
        print('已保存为' + name + '.xls')
    else:
        printGoodsList(ilt)


def printGoodsList(ilt):
    tplt = "{:4}\t{:8}\t{:16}\t{:32}"
    print(tplt.format("序号", "购买", "价格", "商品名称", "图片地址"))
    count = 0
    for g in ilt:
        count = count + 1
        print(tplt.format(count, g[0], g[1], g[2], g[3]))


def main():
    

