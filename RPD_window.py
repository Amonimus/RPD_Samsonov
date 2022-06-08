from tkinter import *
from tkinter import filedialog
import os
import RPD_ftp
import RPD_docprocessor
import RPD_neuroling

class wnd:
    def __init__(self):
        # Создание окна
        self.tkroot = Tk()
        
        # Элементы, которые работают как переменные
        self.debug_lbl = Label(justify="left")
        self.form_serv = Entry(width=10)
        self.form_login = Entry(width=10)
        self.form_pass = Entry(width=10)
        self.filter_value = Entry(width=20)
        self.lbl_dwnld_name = Label(
            wraplength=120,
            width=20,
            justify="left",
            borderwidth=1,
            relief="solid")
        self.lbl_dict_name = Label(
            wraplength=120,
            width=20,
            justify="left",
            borderwidth=1,
            relief="solid")
        self.group_check_value = BooleanVar(self.tkroot, True)
        self.dict_method = StringVar()
        
        self.setup()    
        
    def setup(self):
        # Расположение и конфигурация
        self.tkroot.title('RPD')
        
        self.debug_lbl.grid(row=0, column=0, columnspan=5)
        
        lbl_serv = Label(text="Сервер", width=8)
        lbl_serv.grid(row=1, column=0)
        self.form_serv.grid(row=1, column=1)
        
        lbl_login = Label(text="Логин", width=8)
        lbl_login.grid(row=2, column=0)
        self.form_login.grid(row=2, column=1)
        
        lbl_pass = Label(text="Пароль", width=8)
        lbl_pass.grid(row=3, column=0)
        self.form_pass.grid(row=3, column=1)
        
        btn_dwnld_slct = Button(
            text="Выбрать папку РПД", 
            width=20,
            command=self.get_folder)
        btn_dwnld_slct.grid(row=1, column=2)
        self.lbl_dwnld_name.grid(row=1, column=3)
        
        btn_dict_slct = Button(
            text="Выбрать файл словаря",
            width=20,
            command=self.get_folder)
        btn_dict_slct.grid(row=2, column=2)
        self.lbl_dict_name.grid(row=2, column=3)
        
        lbl_filter = Label(text="Фильтр датасета", width=20)
        lbl_filter.grid(row=3, column=2)
        self.filter_value.grid(row=3, column=3)
        
        group_check_mark = Checkbutton(
            text='Группировать', 
            variable=self.group_check_value, 
            onvalue=True, 
            offvalue=False)
        group_check_mark.grid(row=4, column=3)
        
        btn_dwnld = Button(
            text="Скачать РПД в папку", 
            width=20, 
            command=self.ftp_download)
        btn_dwnld.grid(row=1, column=4)
        
        btn_dwnld = Button(
            text="Сгенерировать словарь", 
            width=20, 
            command=self.dictionary_gen)
        btn_dwnld.grid(row=2, column=4)
        
        btn_anz = Button(
            text="Анализировать словарь", 
            width=20, 
            command=self.analyze)
        btn_anz.grid(row=3, column=4)
        
        lbl_serv = Label(text="Метод словаря", width=12)
        lbl_serv.grid(row=4, column=1)
        var_list = ["BOW", "TF-IDF", "PMI"]
        dict_method_dropdown = OptionMenu(self.tkroot, self.dict_method, *var_list)
        self.dict_method.set(var_list[0])
        dict_method_dropdown.grid(row=4, column=2)
        
        self.debug("РПД Обработчик")
    
    def debug(self, dbg_str):
        # Показать в окне заданный текст
        self.debug_lbl.config(text = dbg_str)
        self.tkroot.update()
    
    def get_folder(self):
        # Форма выбора папки
        selected_folder = filedialog.askdirectory()
        self.lbl_dwnld_name.config(text = selected_folder)
    
    def check_default(self):
        # Значения по умолчанию
        if self.form_serv.get() == "":
            self.form_serv.insert(0, '127.0.0.1')
        if self.form_login.get() == "":
            self.form_login.insert(0, 'username')
        if self.form_pass.get() == "":
            self.form_pass.insert(0, '')
        if self.lbl_dwnld_name["text"] == "":
            self.lbl_dwnld_name.config(text = os.getcwd()+'\\'+"RPD_Chunk")
        if self.lbl_dict_name["text"] == "":
            self.lbl_dict_name.config(text = 'dict.csv')
        if self.filter_value.get() == "":
            self.filter_value.insert(0, "")

    def ftp_download(self):
        # Получить переменные
        self.check_default()
        ftp_server = self.form_serv.get()
        ftp_login = self.form_login.get()
        ftp_pass = self.form_pass.get()
        ftp_folder = self.lbl_dwnld_name['text']
                
        # Загрузка с сервера
        self.debug("Загрузка...")
        download_confirm = RPD_ftp.loadftp(ftp_server, ftp_login, ftp_pass, ftp_folder)
        if not download_confirm:
            self.debug("Нет FTP Соединения.")
        else:
            self.debug("Загружен в "+ftp_folder)
    
    def dictionary_gen(self):
        # Получить переменные
        self.check_default()
        work_path = self.lbl_dwnld_name['text']            
        dic_path = self.lbl_dict_name['text']
        dic_method = self.dict_method.get()
        
        # Генерация словаря
        self.debug("Обработка...")
        rpd_bigdata = {} # speciality - department - discipline - lecture - topic
        
        # global_dictionary = {"dictionary": {}}
        for doc_name in os.listdir(work_path):
            doc_param = RPD_docprocessor.group_doc_name(doc_name)
            self.debug(">> " + doc_param["year"] +" "+ doc_param["dept"] +" "+ doc_param["code"] +" "+ doc_param["subject"])
            doc = RPD_docprocessor.docload(work_path, doc_name)
            if doc:
                rpd_bigdata = RPD_docprocessor.parse_doc_topics(doc, rpd_bigdata)
        print(rpd_bigdata)
        input("PAUSE")
                
                # topics_list = RPD_docprocessor.parse_doc_topics(doc)
                # topics_list = RPD_docprocessor.clean_topics(topics_list)
                # topics_tokens_list = RPD_neuroling.tokenize_topics(topics_list)
                # topics_tokens_list = RPD_neuroling.lemma_token(topics_tokens_list)
                # topics_wordbags = RPD_neuroling.word_bag(topics_tokens_list)
                # global_dictionary = RPD_neuroling.dictionary_generator(global_dictionary, topics_wordbags, doc_param, dic_method)
        self.debug("Генерация словаря завершена.")
        # dictionary_dataframe = RPD_neuroling.convert_dict_dataframe(global_dictionary)
        
        # Экспорт
        # RPD_neuroling.csv_export(dictionary_dataframe, dic_path)
        self.debug("Словарь экспортирован.")
        
    def analyze(self):
        # Получить переменные
        self.check_default()
        dic_path = self.lbl_dict_name["text"]
        filter = self.filter_value.get()
        
        # Работа со словарём
        self.debug("Импорт...")
        table = RPD_neuroling.import_table(dic_path)
        
        #RPD_neuroling.tfidf_generator(table)
        
        self.debug("Анализ...")
        table = RPD_neuroling.compress_table(table)
        if self.group_check_value.get():
            table = RPD_neuroling.group_table(table)
        self.debug("Вывод...")
        #RPD_neuroling.showtable(table)
        RPD_neuroling.table_heatmap(table, filter)
        self.debug("Готово.")
        
    def run(self):
        # Запуск процедуры обработки окна
        mainloop()  