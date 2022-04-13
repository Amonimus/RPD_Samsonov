import re
from docx import Document

# Импорт файла
def docload(path, file):
    # Если расширение файла не .docx, пропустить
    if re.compile('.*.docx$').match(file) != None:
        return Document(path+"\\"+file)
    else:
        return False

# Изъятие текста из документа    
def parse_doc_topics(doc):
    f_in_word_area = False
    topics_list = []
    for table in doc.tables:
        for cell in table.column_cells(2):
            # Предположить что темы всегда находятся во второй колонке и мы знаем заначения ячеек в строках до и после интересующей области
            if f_in_word_area:
                topics_list.append(cell.text)
            if "Наименование разделов и тем" in cell.text:
                f_in_word_area = True
            if "ОЦЕНОЧНЫЕ МАТЕРИАЛЫ" in cell.text:
                f_in_word_area = False
    return topics_list

# Удалить элемент из текстового массива
def remove_filter_item(text_list, remove_match):
    regex = re.compile(r''+remove_match)
    text_list = [i for i in text_list if not regex.match(i)]
    return text_list

# Пред-обработка списка тем
def clean_topics(topics_list):
    # Убрать пустые ячейки
    topics_list = remove_filter_item(topics_list, '^\s*$')
    # Убрать ячейки с нумерацей разделов
    topics_list = remove_filter_item(topics_list, '\s\d\.\s.*$') 
    # Убрать ячеки с практическими занятиям
    topics_list = remove_filter_item(topics_list, '.*(Пр).*')
    return topics_list
    
# Представить имя файла как объект
def group_doc_name(doc_name):
    doc_param = {}
    doc_param["year"] = re.search('\d+-\d+', doc_name).group(0)
    doc_param["code"] = re.search('_\d\d_\d\d_\d\d', doc_name).group(0)[1:]
    doc_param["dept"] = re.search('[А-Я]+_[А-Я]+', doc_name).group(0)
    doc_param["subject"] = doc_name.split("_plx_")[1].split(".doc")[0]
    return doc_param
