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
        self.debug_lbl = Label(width=70, justify="left")
        self.form_serv = Entry()
        self.form_login = Entry()
        self.form_pass = Entry()
        self.lbl_dwnld_name = Label(wraplength=120, justify="left")
        # Расположение и конфигурация
        self.setup()    
        
    def setup(self):
        self.tkroot.title('RPD')
        
        self.debug_lbl.grid(row=0, column=0, columnspan=3)
        self.debug("РПД Обработчик")
        
        lbl_serv = Label(text="Сервер")
        lbl_serv.grid(row=1, column=0)
        self.form_serv.grid(row=1, column=1)
        
        lbl_login = Label(text="Логин")
        lbl_login.grid(row=2, column=0)
        self.form_login.grid(row=2, column=1)
        
        lbl_pass = Label(text="Пароль")
        lbl_pass.grid(row=3, column=0)
        self.form_pass.grid(row=3, column=1)
        
        btn_dwnld_slct = Button(text="Выбрать папку", command=self.get_folder)
        btn_dwnld_slct.grid(row=4, column=0)
        self.lbl_dwnld_name.grid(row=4, column=1)
        
        btn_dwnld = Button(text="Скачать РПД в папку", command=self.ftp_download)
        btn_dwnld.grid(row=1, column=2)
        btn_dwnld = Button(text="Сгенерировать словарь", command=self.process_neuro)
        btn_dwnld.grid(row=2, column=2)
        
        btn_anz = Button(text="Анализировать словарь", command=self.analyze)
        btn_anz.grid(row=3, column=2)
    
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
    
    def process_neuro(self):
        # Значение папки по умолчанию
        path = self.lbl_dwnld_name["text"]
        if path == "":
            self.lbl_dwnld_name.config(text = os.getcwd()+"\\"+'RPD_Chunk')
            path = self.lbl_dwnld_name["text"]
        
        # Главная процедура
        global_bag_table = {"dictionary": {}}
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
        RPD_neuroling.csv_export(dictionary_dataframe)
        self.debug("Словарь экспортирован.")
        
    def analyze(self):
        self.debug("Импорт...")
        table = RPD_neuroling.import_table()
        self.debug("Анализ...")
        
        # table = RPD_neuroling.group_table(table)
        RPD_neuroling.table_heatmap(table)
        # RPD_neuroling.showtable(table)
        self.debug("Готово.")
        
    def run(self):
        # Запуск процедуры обработки окна
        mainloop()  