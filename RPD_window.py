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
        self.form_serv = Entry(width=20)
        self.form_login = Entry(width=20)
        self.form_pass = Entry(width=20)
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
        self.group_check_value = BooleanVar(False)
        # Расположение и конфигурация
        self.setup()    
        
    def setup(self):
        self.tkroot.title('RPD')
        
        self.debug_lbl.grid(row=0, column=0, columnspan=5)
        self.debug("РПД Обработчик")
        
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
        
        group_check = Checkbutton(
            text='Группировать', 
            variable=self.group_check_value, 
            onvalue=True, 
            offvalue=False)
        group_check.grid(row=4, column=3)
        
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
    
    def debug(self, text):
        # Показать в окне заданный текст
        self.debug_lbl.config(text = text)
        self.tkroot.update()
    
    def get_folder(self):
        # Форма выбора папки
        selected_folder = filedialog.askdirectory()
        self.lbl_dwnld_name.config(text = selected_folder)
        
    def ftp_download(self):
        #Получить переменные
        ftp_server = self.form_serv.get()
        ftp_login = self.form_login.get()
        ftp_pass = self.form_pass.get()
        ftp_folder = self.lbl_dwnld_name["text"]
        
        # Значения по умолчанию
        if ftp_server == "":
            self.form_serv.insert(0, '127.0.0.1')
            ftp_server = self.form_serv.get()
        if ftp_login == "":
            self.form_login.insert(0, 'username')
            ftp_login = self.form_login.get()
        if ftp_folder == "":
            self.lbl_dwnld_name.config(text = os.getcwd()+"\\"+'RPD_Chunk')
            ftp_folder = self.lbl_dwnld_name["text"]
        
        # Загрузка с сервера
        self.debug("Загрузка...")
        if ftp_server != "" and ftp_login != "" and ftp_folder != "":
            download_confirm = RPD_ftp.loadftp(ftp_server, ftp_login, ftp_pass, ftp_folder)
            if not download_confirm:
                self.debug("Нет FTP Соединения.")
            else:
                self.debug("Загружен в "+ftp_folder)
        else:
            self.debug("Не все параметры.")
    
    def dictionary_gen(self):
        # Значения по умолчанию
        path = self.lbl_dwnld_name["text"]
        if path == "":
            self.lbl_dwnld_name.config(text = os.getcwd()+"\\"+'RPD_Chunk')
            path = self.lbl_dwnld_name["text"]
            
        dic_path = self.lbl_dict_name["text"]
        if dic_path == "":
            self.lbl_dict_name.config(text = 'dict.csv')
            dic_path = self.lbl_dict_name["text"]
        
        # Главная процедура
        global_bag_table = {"dictionary": {}}
        self.debug("Обработка...")
        for doc_name in os.listdir(path):
            doc = RPD_docprocessor.docload(path, doc_name)
            if doc:
                doc_param = RPD_docprocessor.group_doc_name(doc_name)
                self.debug(">> " + doc_param["year"] +" "+ doc_param["dept"] +" "+ doc_param["code"] +" "+ doc_param["subject"])
                
                topics_list = RPD_docprocessor.parse_doc_topics(doc)
                topics_list = RPD_docprocessor.clean_topics(topics_list)
                topics_tokens_list = RPD_neuroling.tokenize_topics(topics_list)
                topics_tokens_list = RPD_neuroling.lemma_token(topics_tokens_list)
                topics_wordbags = RPD_neuroling.word_bag(topics_tokens_list)
                global_bag_table = RPD_neuroling.dictionary_generator(global_bag_table, topics_wordbags, doc_param)
        self.debug("Генерация словаря завершена.")
        dictionary_dataframe = RPD_neuroling.convert_dict_dataframe(global_bag_table)
        RPD_neuroling.csv_export(dictionary_dataframe, dic_path)
        self.debug("Словарь экспортирован.")
        
    def analyze(self):
        # Значения по умолчанию
        dic_path = self.lbl_dict_name["text"]
        if dic_path == "":
            self.lbl_dict_name.config(text = 'dict.csv')
            dic_path = self.lbl_dict_name["text"]
            
        filter = self.filter_value.get()
        if filter == "":
            filter = " "
            
        self.debug("Импорт...")
        table = RPD_neuroling.import_table(dic_path)
        self.debug("Анализ...")
        table = RPD_neuroling.compress_table(table)
        if self.group_check_value.get():
            table = RPD_neuroling.group_table(table)
        # RPD_neuroling.showtable(table)
        RPD_neuroling.table_heatmap(table, filter)
        self.debug("Готово.")
        
    def run(self):
        # Запуск процедуры обработки окна
        mainloop()  