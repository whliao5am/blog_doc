import os
import re


name_list = []
# 搜索一个文件夹里的所有文件（包括其子文件夹内的）
# 并将与设定后缀相符的文件的路径放入一个列表中返回
def findmd(path):
    for p in os.listdir(path):
        npath = os.path.join(path, p)
        print(npath)
        if p[-3:] == suffix_name:
            name_list.append(npath)
        elif os.path.isdir(npath):
            findmd(npath)
    return name_list

  
# 对单个文件进行内容替换
def modifymd(path):
    with open(path, 'r') as f:
        result = re.sub(pattern, repl, f.read())

    with open(path, 'w') as f:
        f.write(result)
        print(1)

if __name__ == '__main__':
    suffix_name = '.md'  # 需要修改的文件后缀
    pattern = r'/.+/gifs'  # 需要被替换的字符串的正则表达式
    repl = 'gifs'  # 被替换后的字符串
    path = '1_text_formats'  # 需要进行替换的文件夹的路径（绝对或者相对）
    
    name_list = findmd(path)
    print(name_list)
    for n in name_list:
        modifymd(n)