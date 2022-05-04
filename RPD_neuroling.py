import os, re, csv
import pandas as pd
from pandasgui import show as pdshow
#from IPython.display import display as pdisplay
import pymorphy3
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

# Токенизация по словам
def tokenize_topics(topic_list):
    topics_tokens_list = []
    for topic in topic_list:
        # Убрать слово в скобках
        topic = topic.replace(" (Лек)", "")
        # Убрать пунктуацию
        # надо включать английские слова
        # regex = re.compile(r'[А-ЯЁа-яё]+')
        # С английскими словами таблица выходит пустой
        regex = re.compile(r'\w+', re.UNICODE)
        # Разбить на слова
        topic_tokens = regex.findall(topic.strip().lower())
        topics_tokens_list.append(topic_tokens)
    return topics_tokens_list

# Лемматизация
def lemma_token(topic_tokens_list):
    morphanalyzer = pymorphy3.MorphAnalyzer()
    # определить язык слова
    lemmas_list = []
    # Для каждой темы для кажого токена
    for topic_tokens in topic_tokens_list: 
        # Получить изначальную форму слова
        topic_tokens = [morphanalyzer.parse(token)[0].normal_form for token in topic_tokens]
        # Двухслойный список
        lemmas_list.append(topic_tokens)
    return lemmas_list

# Мешок слов
def word_bag(topic_tokens_list):
    topics_bags = []
    for topic_tokens in topic_tokens_list:
        topic_bag = {}
        for topic_token in topic_tokens:
            # Посчитать количество в лекции
            if topic_token in topic_bag.keys():
                topic_bag[topic_token] += 1 
            else:
                topic_bag[topic_token] = 1
        topics_bags.append(topic_bag)
    return topics_bags

# Создание словаря
def dictionary_generator(global_bag_table, topics_wordbags, doc_param, method):
    for topic_id in range(len(topics_wordbags)):
        for token, val in topics_wordbags[topic_id].items():
            # Проссуммировать для общего
            if token in global_bag_table["dictionary"].keys():
                global_bag_table["dictionary"][token] += val
            else:
                global_bag_table["dictionary"][token] = val
        # Создать метки по лекциям
        topic_name = doc_param["code"]+"_"+doc_param["dept"]+"_"+doc_param["subject"]+"_ЛК_"+str(topic_id)
        global_bag_table[topic_name] = topics_wordbags[topic_id]
    
    return global_bag_table

def tfidf_generator(table):
    tf = table.copy()
    for doc, wordbag in table.items():
        for word, wordcount in wordbag.items():
            tf[doc][word] = wordcount / len(wordbag)
    showtable(table)
    idf = len(table)-1
    print(idf)
    input("PAUSE")

# elif mode == 'pmi':
      # sum_of_sizes_of_docs = np.array(result.sum())
      # sizes_of_every_doc = np.array(result.sum(1))
      # count_word_in_docs = np.array(result.sum(0))
      # result = result.multiply((sum_of_sizes_of_docs**2)/((sizes_of_every_doc**2) * count_word_in_docs))
      # result.data = np.log(result.data)

# Редактор фреймов
def showtable(table):
    pdshow(table)
    #pdisplay(table)
    #table.style
    pass

# Dictionary 2 Pandas
def convert_dict_dataframe(table):
    table = pd.DataFrame.from_dict(table, orient='columns').fillna(0).astype(int)
    # Сортировка по токенам
    table = table.sort_index(axis=1)
    # Сортировка по темам
    table = table.sort_index(axis=0)
    return table

# Экспорт
def csv_export(table, dic_path):
    table.to_csv(dic_path)

# Импорт
def import_table(dic_path):
    table = pd.read_csv(dic_path, index_col=[0])
    
    #Перемещение общего ряда вперед
    table.insert(0, 'dictionary', table.pop('dictionary'))
    table = table.sort_values(by=['dictionary'], ascending=False)
    return table

# Фильтры
def compress_table(table):
    #Убрать стоп-слова (союзы и падежи)
    st_words = stopwords.words('russian')
    table = table.drop(st_words, axis=0, errors="ignore")
    
    #Убрать N% слов из начала и слова реже чем N с конца
    cutoff_perc = 3
    cut = len(table.index) // int(100/cutoff_perc)
    table = table.iloc[cut: , :]
    table = table[table['dictionary'] >= table['dictionary'][-cut]]
    return table
    
# Просуммировать и сжать лекции одного документа
def group_table(table):
    groups = [col.split("_ЛК")[0] for col in table.head()]
    table.columns = table.columns[:0].tolist() + groups
    table = table.groupby(table.columns, axis=1).sum()
    
    groups = [col.rsplit("_")[-1] for col in table.head()]
    table.columns = table.columns[:0].tolist() + groups
    table = table.groupby(table.columns, axis=1).max()
    
    return table

# График матрицы коррелиации
def table_heatmap(table, filt_exp):
    if filt_exp != "":
        table = table.filter(like=filt_exp, axis=1)
    #print(table)
    table = table.corr(method ='pearson').fillna(0)
    table = table[table < 0.9]
    table = table.iloc[1: , 1:]
    
    fig = plt.figure("Correlation Matrix", figsize=(20, 10))
    plt.matshow(table, fignum=fig.number)
    values = range(table.select_dtypes(['number']).shape[1])
    labels = table.select_dtypes(['number']).columns
    plt.yticks(values, labels, fontsize=8)
    plt.xticks(values, labels, fontsize=8, rotation=90, ha="left", rotation_mode="anchor", wrap=False)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=16)
    plt.show(block=False)
    