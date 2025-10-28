import random
from tkinter import *
from tkinter import ttk, messagebox, filedialog, scrolledtext
import webbrowser
import os
import json
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import csv
import sqlite3

class PeopleGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("pgen5")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)

        # Иконка приложения
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass

        # Темы оформления
        self.themes = {
            "Светлая": {"bg": "#f0f0f0", "fg": "#000000", "highlight": "#4CAF50"},
            "Темная": {"bg": "#2d2d2d", "fg": "#ffffff", "highlight": "#45a049"},
            "Синяя": {"bg": "#e6f3ff", "fg": "#003366", "highlight": "#0066cc"}
        }
        self.current_theme = "Светлая"

        # Загрузка данных из JSON (если есть)
        self.data_sources = {
            "malenames": "data/malenames.json",
            "femalenames": "data/femalenames.json",
            "surnames": "data/surnames.json",
            "cities": "data/cities.json",
            "streets": "data/streets.json",
            "words": "data/words.json"
        }

        self.load_data()
        self.create_widgets()
        self.output_folder = os.getcwd()
        self.apply_theme()

        # Статистика
        self.generated_count = 0
        self.last_generation_time = None

        # База данных для истории генераций
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect('generator_history.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS generations
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              timestamp TEXT,
                              count INTEGER,
                              parameters TEXT)''')
        self.conn.commit()

    def save_generation_stats(self, count, params):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO generations (timestamp, count, parameters) VALUES (?, ?, ?)",
                           (timestamp, count, json.dumps(params)))
        self.conn.commit()

    def load_data(self):
        # Основные данные
        self.malenames = self.load_json_data("malenames", [
            'Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей',
            'Алексей', 'Артём', 'Илья', 'Кирилл', 'Михаил'
        ])

        self.femalenames = self.load_json_data("femalenames", [
            'Анастасия', 'Анна', 'Мария', 'Елена', 'Дарья',
            'Алина', 'Ирина', 'Ольга', 'Татьяна', 'Юлия'
        ])

        self.surnames = self.load_json_data("surnames", [
            'Иванов', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев',
            'Петров', 'Соколов', 'Михайлов', 'Новиков', 'Фёдоров'
        ])

        self.cities = self.load_json_data("cities", [
            'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
            'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону'
        ])

        self.streets = self.load_json_data("streets", [
            'Ленина', 'Гагарина', 'Советская', 'Мира', 'Кирова',
            'Пушкина', 'Лермонтова', 'Горького', 'Чехова', 'Толстого'
        ])

        self.words = self.load_json_data("words", [
            'Безударный', 'Выползень', 'Запад', 'Инсценировать', 'Неукротимый',
            'Отроиться', 'Сменить', 'Ударник', 'Цикорий', 'Шиповник'
        ])

        # Дополнительные данные
        self.male_patronymics = [
            'Александрович', 'Алексеевич', 'Анатольевич', 'Андреевич', 'Антонович',
            'Аркадьевич', 'Артемович', 'Борисович', 'Вадимович', 'Валентинович'
        ]

        self.female_patronymics = [
            'Александровна', 'Алексеевна', 'Анатольевна', 'Андреевна', 'Антоновна',
            'Аркадьевна', 'Артемовна', 'Борисовна', 'Вадимовна', 'Валентиновна'
        ]

        self.services = [
            "Яндекс.Такси", "СберБанк", "Тинькофф", "ВТБ", "Газпромбанк", "Альфа-Банк",
            "МТС", "Билайн", "Мегафон", "Tele2", "Яндекс.Еда", "Delivery Club",
            "СберМаркет", "Ozon", "Wildberries", "Авито", "ДомКлик", "ЦИАН", "Росгосстрах",
            "Ингосстрах", "АльфаСтрахование", "РЖД", "Аэрофлот", "S7 Airlines", "Почта России",
            "Лукойл", "Роснефть", "Газпром", "Новатэк", "Сургутнефтегаз",
            "Русал", "Норникель", "Северсталь", "Магнит", "X5 Group",
            "Лента", "М.Видео", "Эльдорадо", "DNS", "Ситилинк",
            "Касперский", "1С", "Лаборатория Касперского", "Яндекс", "Mail.ru Group",
            "Рамблер", "ВКонтакте", "Одноклассники", "СберТех", "Тинькофф Технологии",
            "Черкизово", "РусАгро", "Мираторг", "Балтика", "Сабмиллер Раша",
            "ВкусВилл", "Утконос", "Дикси", "Ашан", "Перекрёсток",
            "Пятёрочка", "Бристоль", "Теремок", "Му-Му", "Вилка-Ложка",
            "Додо Пицца", "Крошка Картошка", "Бургер Кинг", "KFC", "Макдоналдс",
            "Шоколадница", "Кофе Хауз", "Старбакс", "Сибирская корона", "Жигулёвское",
            "Пельменная №1", "Шаурма у Ашота", "Такси 'Бывалый'", "Банк 'На диване'",
            "Доставка 'Сами привезём'", "Страховка 'Авось'", "Авиалинии 'Кукурузник'",
            "РЖД 'Туда-Сюда'", "Интернет 'Через пень колоду'", "Маркетплейс 'С барахолки'",
            "КосмоБанк", "КиберТакси", "НефтьОнлайн", "Дроникурьер", "ВиртЕда",
            "КвантСтрах", "БлокчейнБургер", "ИИМаркет", "НейроБанк", "КриптоАвиа"
        ]

        self.crime_types = [
            "Кража", "Мошенничество", "Грабеж", "Разбой", "Угон",
            "Наркотики", "Хулиганство", "Нанесение телесных повреждений",
            "Неуплата алиментов", "Клевета", "Вымогательство", "Подделка документов",
            "Незаконное предпринимательство", "Уклонение от налогов", "Дача взятки",
            "Получение взятки", "Присвоение средств", "Растрата", "Рецидив",
            "Незаконное лишение свободы", "Похищение человека", "Торговля людьми",
            "Незаконное проникновение", "Вандализм", "Порча имущества",
            "Незаконная охота", "Браконьерство", "Экоцид", "Загрязнение вод",
            "Незаконная вырубка", "Нарушение ПДД", "Управление в нетрезвом виде",
            "Незаконный оборот оружия", "Терроризм", "Экстремизм",
            "Госизмена", "Шпионаж", "Неуважение к суду", "Лжесвидетельство",
            "Подкуп свидетеля", "Фальсификация доказательств", "Незаконное усыновление",
            "Нарушение авторских прав", "Пиратство", "Незаконное копирование",
            "Компьютерные преступления", "Хакерство", "Фишинг", "Кардинг",
            "Незаконный митинг", "Массовые беспорядки", "Неповиновение властям",
            "Самоуправство", "Незаконное задержание", "Превышение полномочий",
            "Фальшивомонетничество", "Незаконный оборот драгметаллов",
            "Контрабанда", "Незаконный экспорт", "Незаконный импорт",
            "Незаконная банковская деятельность", "Отмывание денег",
            "Незаконная игорная деятельность", "Сутенёрство", "Сводничество",
            "Незаконный оборот алкоголя", "Незаконный оборот табака",
            "Нарушение миграционного законодательства", "Незаконное трудоустройство",
            "Незаконное предпринимательство", "Незаконная медицинская деятельность",
            "Незаконная фармацевтическая деятельность", "Продажа некачественных товаров",
            "Обман потребителей", "Незаконная реклама", "Незаконный сбор данных",
            "Нарушение тайны переписки", "Незаконное распространение информации",
            "Кибербуллинг", "Киберсталкинг", "Незаконный контент"
        ]

        self.loan_companies = [
            "МигКредит", "Домашние деньги", "Турбозайм", "Займер", "Деньги сразу",
            "Быстроденьги", "Е-Капуста", "СМСфинанс", "Честное слово", "Робот Займер",
            "ЦентрИнвест", "Русский стандарт", "ОТП Банк", "Ренессанс Кредит",
            "Хоум Кредит", "Восточный Экспресс Банк", "Совкомбанк", "Тинькофф Банк",
            "Деньги за час", "Займ онлайн", "КредитПлюс", "Финансовая помощь",
            "Срочноденьги", "Веб-займ", "Кредитная линия", "Деньги в долг",
            "Быстрокредит", "Экспресс займ", "Финансист", "Кредитный робот",
            "Деньги на карту", "МоментКредит", "Скорая финансовая помощь",
            "Кредит за 5 минут", "Деньги без отказов", "Займ без проверок",
            "Круглосуточный займ", "Финансовая палочка-выручалочка",
            "Кредит под 0%", "Деньги до зарплаты", "Срочный кредит онлайн",
            "Микрофинанс онлайн", "Займ без процентов", "Кредитный экспресс",
            "Деньги без заморочек", "Быстро и деньги", "Кредит за секунду",
            "Финансовый спасатель", "Займ-антикризис", "Деньги 24/7",
            "Кредитный помощник", "Микрозайм онлайн", "Деньги на всё",
            "Займ без отказа", "Кредит за минуту", "Финансовый друг",
            "Деньги здесь и сейчас", "Срочный займ онлайн", "Кредитный ангел",
            "Займ без справок", "Деньги без вопросов", "Кредит моментально",
            "Финансовая подушка", "Займ круглосуточно", "Деньги легко",
            "Кредитный бум", "Микрофинанс за минуту", "Займ без заморочек",
            "Деньги на любые цели", "Кредит без хлопот", "Финансовый экспресс",
            "Займ с плохой кредитной историей", "Деньги без поручителей",
            "Кредит без залога", "Микрозайм срочно", "Займ без визита в офис",
            "Деньги без комиссии", "Кредитный рай", "Финансовый светофор",
            "Займ без скрытых платежей", "Деньги без нервов", "Кредитный ветер",
            "Микрофинанс 24 часа", "Займ без бумажной волокиты", "Деньги без границ"
        ]

        self.border_crossings = [
            "Шереметьево", "Домодедово", "Пулково", "Кольцово", "Толмачево",
            "Храброво", "Уфа", "Казань", "Сочи", "Минеральные Воды",
            "Адлер", "Белорусский вокзал", "Киевский вокзал", "Финляндский вокзал",
            "Аэропорт Внуково", "МАПП Торфяновка", "МАПП Брусничное", "МАПП Светогорск",
            "Аэропорт Жуковский", "Аэропорт Ростов-на-Дону", "Аэропорт Самара",
            "Аэропорт Красноярск", "Аэропорт Владивосток", "Аэропорт Хабаровск",
            "Аэропорт Новосибирск", "Аэропорт Екатеринбург", "Аэропорт Калининград",
            "МАПП Ивангород", "МАПП Бурачки", "МАПП Убылинка", "МАПП Гребнево",
            "МАПП Скандинавия", "МАПП Балтийск", "МАПП Багратионовск", "МАПП Гусев",
            "Морской порт Санкт-Петербург", "Морской порт Калининград",
            "Морской порт Новороссийск", "Морской порт Владивосток",
            "Железнодорожный пункт Бусловская", "Железнодорожный пункт Светлогорск",
            "Железнодорожный пункт Себеж", "Железнодорожный пункт Суземка",
            "Пункт пропуска Вяртсиля", "Пункт пропуска Люття", "Пункт пропуска Ниирала",
            "Пункт пропуска Иматра", "Пункт пропуска Ваалимаа", "Пункт пропуска Нуйямаа",
            "Пункт пропуска Рая-Йоосеппи", "Пункт пропуска Салла", "Пункт пропуска Келлоселькя",
            "Пункт пропуска Лотта", "Пункт пропуска Борисоглебск", "Пункт пропуска Урлах",
            "Пункт пропуска Шумилкино", "Пункт пропуска Гродеково", "Пункт пропуска Полтавка",
            "Пункт пропуска Пограничный", "Пункт пропуска Махалино", "Пункт пропуска Хасан",
            "Пункт пропуска Забайкальск", "Пункт пропуска Кяхта", "Пункт пропуска Алтан-Булак",
            "Пункт пропуска Монды", "Пункт пропуска Ташанта", "Пункт пропуска Ханхи",
            "Пункт пропуска Верхний Ларс", "Пункт пропуска Нижний Зарамаг",
            "Пункт пропуска Весело-Вознесенск", "Пункт пропуска Джула", "Пункт пропуска Адлер",
            "Пункт пропуска Веселовка", "Пункт пропуска Новошахтинск", "Пункт пропуска Куйбышево",
            "Пункт пропуска Матвеев Курган", "Пункт пропуска Гуково", "Пункт пропуска Донецк",
            "Пункт пропуска Новые Юрковичи", "Пункт пропуска Тереховка", "Пункт пропуска Сеньковка",
            "Пункт пропуска Бачевск", "Пункт пропуска Красная Таловка", "Пункт пропуска Гордеевка",
            "Пункт пропуска Сураж", "Пункт пропуска Клинцы", "Пункт пропуска Злынка",
            "Пункт пропуска Славгород", "Пункт пропуска Тарутино", "Пункт пропуска Болград",
            "Пункт пропуска Рени", "Пункт пропуска Измаил", "Пункт пропуска Орловка",
            "Пункт пропуска Подгорное", "Пункт пропуска Павловка", "Пункт пропуска Меловое",
            "Пункт пропуска Троицкое", "Пункт пропуска Старобельск", "Пункт пропуска Новоазовск",
            "Пункт пропуска Успенка", "Пункт пропуска Марковка", "Пункт пропуска Меловое",
            "Пункт пропуска Чертково", "Пункт пропуска Миллерово", "Пункт пропуска Каменск-Шахтинский",
            "Пункт пропуска Морозовск", "Пункт пропуска Цимлянск", "Пункт пропуска Волгодонск",
            "Пункт пропуска Дубовка", "Пункт пропуска Романовская", "Пункт пропуска Морозовская",
            "Пункт пропуска Целина", "Пункт пропуска Зимовники", "Пункт пропуска Ремонтное",
            "Пункт пропуска Заветное", "Пункт пропуска Дубовское", "Пункт пропуска Орловский",
            "Пункт пропуска Пролетарск", "Пункт пропуска Сальск", "Пункт пропуска Песчанокопское",
            "Пункт пропуска Целинный", "Пункт пропуска Егорлыкская", "Пункт пропуска Кагальницкая",
            "Пункт пропуска Кущевская", "Пункт пропуска Ленинградская", "Пункт пропуска Каневская",
            "Пункт пропуска Староминская", "Пункт пропуска Щербиновская", "Пункт пропуска Павловская",
            "Пункт пропуска Крыловская", "Пункт пропуска Кущевская", "Пункт пропуска Старощербиновская",
            "Пункт пропуска Выселки", "Пункт пропуска Кореновск", "Пункт пропуска Динская",
            "Пункт пропуска Усть-Лабинск", "Пункт пропуска Тбилисская", "Пункт пропуска Кавказская",
            "Пункт пропуска Гулькевичи", "Пункт пропуска Новокубанск", "Пункт пропуска Армавир",
            "Пункт пропуска Курганинск", "Пункт пропуска Лабинск", "Пункт пропуска Мостовской",
            "Пункт пропуска Отрадная", "Пункт пропуска Успенское", "Пункт пропуска Новопокровская",
            "Пункт пропуска Белоглинская", "Пункт пропуска Тихорецк", "Пункт пропуска Выселковская",
            "Пункт пропуска Брюховецкая", "Пункт пропуска Тимашевск", "Пункт пропуска Приморско-Ахтарск",
            "Пункт пропуска Калининская", "Пункт пропуска Старовеличковская", "Пункт пропуска Каневская",
            "Пункт пропуска Ленинградская", "Пункт пропуска Кущевская", "Пункт пропуска Щербиновская",
            "Пункт пропуска Ейск", "Пункт пропуска Приморско-Ахтарск", "Пункт пропуска Темрюк",
            "Пункт пропуска Анапа", "Пункт пропуска Новороссийск", "Пункт пропуска Геленджик",
            "Пункт пропуска Туапсе", "Пункт пропуска Сочи", "Пункт пропуска Адлер",
            "Пункт пропуска Лазаревское", "Пункт пропуска Хоста", "Пункт пропуска Кудепста",
            "Пункт пропуска Веселое", "Пункт пропуска Лоо", "Пункт пропуска Дагомыс",
            "Пункт пропуска Мацеста", "Пункт пропуска Хоста", "Пункт пропуска Адлер",
            "Пункт пропуска Красная Поляна", "Пункт пропуска Эсто-Садок", "Пункт пропуска Роза Хутор"
        ]

    def load_json_data(self, key, default_data):
        path = self.data_sources.get(key)
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_data
        return default_data

    def create_widgets(self):
        # Главный контейнер
        main_frame = Frame(self.root)
        main_frame.pack(pady=10, padx=10, fill=BOTH, expand=True)

        # Верхняя панель инструментов
        toolbar = Frame(main_frame)
        toolbar.pack(fill=X, pady=5)

        Button(toolbar, text="Экспорт данных", command=self.show_export_dialog, bg="#4CAF50", fg="white").pack(side=LEFT, padx=5)
        Button(toolbar, text="История", command=self.show_history, bg="#2196F3", fg="white").pack(side=LEFT, padx=5)
        Button(toolbar, text="Настройки", command=self.show_settings, bg="#607D8B", fg="white").pack(side=LEFT, padx=5)

        # Панель темы
        theme_frame = Frame(toolbar)
        theme_frame.pack(side=RIGHT, padx=5)
        Label(theme_frame, text="Тема:").pack(side=LEFT)
        self.theme_var = StringVar(value=self.current_theme)
        OptionMenu(theme_frame, self.theme_var, *self.themes.keys(), command=self.change_theme).pack(side=LEFT)

        # Основное содержимое
        content_frame = Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True)

        # Левая панель - параметры генерации
        params_frame = LabelFrame(content_frame, text="Параметры генерации")
        params_frame.pack(side=LEFT, fill=Y, padx=5)

        # Параметры количества
        quantity_frame = Frame(params_frame)
        quantity_frame.pack(pady=5, fill=X)
        Label(quantity_frame, text="Количество записей:").pack(side=LEFT)
        self.quantity_entry = Entry(quantity_frame)
        self.quantity_entry.pack(side=LEFT, padx=5)
        self.quantity_entry.insert(0, "100")

        # Параметры пола
        sex_frame = Frame(params_frame)
        sex_frame.pack(pady=5, fill=X)
        Label(sex_frame, text="Распределение пола:").pack()
        self.sex_var = StringVar(value="random")
        Radiobutton(sex_frame, text="Случайно", variable=self.sex_var, value="random").pack(anchor=W)
        Radiobutton(sex_frame, text="Больше мужчин", variable=self.sex_var, value="male").pack(anchor=W)
        Radiobutton(sex_frame, text="Больше женщин", variable=self.sex_var, value="female").pack(anchor=W)

        # Вероятности
        Label(params_frame, text="Вероятности добавления:").pack(pady=(10,5))

        self.create_probability_slider(params_frame, "Места работы:", "job_prob", 80)
        self.create_probability_slider(params_frame, "Зарплаты:", "salary_prob", 50)
        self.create_probability_slider(params_frame, "Соцсетей:", "social_prob", 50)
        self.create_probability_slider(params_frame, "Семей:", "family_prob", 30)
        self.create_probability_slider(params_frame, "Отчеств:", "patronymic_prob", 70)
        self.create_probability_slider(params_frame, "Клиентов сервисов:", "service_prob", 40)
        self.create_probability_slider(params_frame, "Пересечений границы:", "border_prob", 20)
        self.create_probability_slider(params_frame, "Микрозаймов:", "loan_prob", 25)
        self.create_probability_slider(params_frame, "Уголовных дел:", "crime_prob", 15)

        # Правая панель - управление выводом
        output_frame = LabelFrame(content_frame, text="Вывод данных")
        output_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)

        # Формат вывода
        format_frame = Frame(output_frame)
        format_frame.pack(pady=5, fill=X)
        Label(format_frame, text="Формат вывода:").pack(anchor=W)

        self.output_var = IntVar(value=1)
        output_options = [
            ("Один файл (TXT)", 1),
            ("Один файл (HTML)", 2),
            ("Один файл (JSON)", 5),
            ("Один файл (CSV)", 6),
            ("Отдельные файлы (TXT)", 3),
            ("Отдельные файлы (HTML)", 4),
            ("Отдельные файлы (JSON)", 7)
        ]

        for text, value in output_options:
            Radiobutton(format_frame, text=text, variable=self.output_var, value=value).pack(anchor=W)

        # Дополнительные параметры вывода
        Label(output_frame, text="Дополнительные параметры:").pack(pady=(10,5), anchor=W)

        self.include_photo_var = IntVar(value=0)
        Checkbutton(output_frame, text="Включить фото (для HTML)", variable=self.include_photo_var).pack(anchor=W)

        self.group_family_var = IntVar(value=1)
        Checkbutton(output_frame, text="Группировать семьи", variable=self.group_family_var).pack(anchor=W)

        # Выбор папки
        folder_frame = Frame(output_frame)
        folder_frame.pack(pady=10, fill=X)
        Button(folder_frame, text="Выбрать папку", command=self.select_folder).pack(side=LEFT)
        self.folder_label = Label(folder_frame, text=f"Папка: {os.getcwd()}", wraplength=300)
        self.folder_label.pack(side=LEFT, padx=5)

        # Кнопка генерации
        Button(output_frame, text="Сгенерировать данные", command=self.generate_data,
              bg="#4CAF50", fg="white", font=('Arial', 10, 'bold')).pack(pady=20)

        # Предпросмотр
        self.preview_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=WORD)
        self.preview_text.pack(fill=BOTH, expand=True)
        self.preview_text.insert(END, "Здесь будет отображаться предпросмотр данных...")

        # Статус бар
        self.status = Label(self.root, text="Готов к работе", bd=1, relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

    def create_probability_slider(self, frame, label_text, attr_name, default_value):
        slider_frame = Frame(frame)
        slider_frame.pack(fill=X, pady=2)
        Label(slider_frame, text=label_text, width=20, anchor=W).pack(side=LEFT)
        setattr(self, attr_name, Scale(slider_frame, from_=0, to=100, orient=HORIZONTAL, length=150))
        getattr(self, attr_name).set(default_value)
        getattr(self, attr_name).pack(side=LEFT, padx=5)
        Label(slider_frame, text="%", width=3).pack(side=LEFT)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.folder_label.config(text=f"Папка: {folder}")

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.config(bg=theme["bg"])

        for widget in self.root.winfo_children():
            self.apply_theme_to_widget(widget, theme)

    def apply_theme_to_widget(self, widget, theme):
        if isinstance(widget, (Frame, LabelFrame, Toplevel)):
            widget.config(bg=theme["bg"])

        if isinstance(widget, (Label, Button, Checkbutton, Radiobutton, Entry, Scale)):
            widget.config(bg=theme["bg"], fg=theme["fg"])

        if isinstance(widget, Button):
            if widget.cget("bg") in ["#4CAF50", "#2196F3", "#607D8B"]:
                widget.config(bg=theme["highlight"])

        for child in widget.winfo_children():
            self.apply_theme_to_widget(child, theme)

    def show_export_dialog(self):
        export_dialog = Toplevel(self.root)
        export_dialog.title("Экспорт данных")
        export_dialog.geometry("400x300")

        Label(export_dialog, text="Выберите данные для экспорта:").pack(pady=10)

        self.export_var = IntVar(value=1)
        export_options = [
            ("Имена (мужские)", 1),
            ("Имена (женские)", 2),
            ("Фамилии", 3),
            ("Города", 4),
            ("Улицы", 5),
            ("Названия компаний", 6),
            ("Все данные", 7)
        ]

        for text, value in export_options:
            Radiobutton(export_dialog, text=text, variable=self.export_var, value=value).pack(anchor=W)

        Label(export_dialog, text="Формат экспорта:").pack(pady=10)

        self.export_format_var = StringVar(value="json")
        Radiobutton(export_dialog, text="JSON", variable=self.export_format_var, value="json").pack(anchor=W)
        Radiobutton(export_dialog, text="TXT", variable=self.export_format_var, value="txt").pack(anchor=W)
        Radiobutton(export_dialog, text="CSV", variable=self.export_format_var, value="csv").pack(anchor=W)

        Button(export_dialog, text="Экспортировать", command=lambda: self.export_data(export_dialog)).pack(pady=20)

    def export_data(self, dialog):
        data_type = self.export_var.get()
        export_format = self.export_format_var.get()

        data = None
        filename = ""

        if data_type == 1:
            data = self.malenames
            filename = "malenames"
        elif data_type == 2:
            data = self.femalenames
            filename = "femalenames"
        elif data_type == 3:
            data = self.surnames
            filename = "surnames"
        elif data_type == 4:
            data = self.cities
            filename = "cities"
        elif data_type == 5:
            data = self.streets
            filename = "streets"
        elif data_type == 6:
            data = self.words
            filename = "company_names"
        elif data_type == 7:
            data = {
                "malenames": self.malenames,
                "femalenames": self.femalenames,
                "surnames": self.surnames,
                "cities": self.cities,
                "streets": self.streets,
                "words": self.words
            }
            filename = "all_data"

        if not data:
            messagebox.showerror("Ошибка", "Нет данных для экспорта")
            return

        filepath = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=f".{export_format}",
            filetypes=[(f"{export_format.upper()} files", f"*.{export_format}")]
        )

        if not filepath:
            return

        try:
            if export_format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif export_format == "txt":
                with open(filepath, 'w', encoding='utf-8') as f:
                    if isinstance(data, dict):
                        for key, values in data.items():
                            f.write(f"=== {key.upper()} ===\n")
                            for item in values:
                                f.write(f"{item}\n")
                            f.write("\n")
                    else:
                        for item in data:
                            f.write(f"{item}\n")
            elif export_format == "csv":
                with open(filepath, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    if isinstance(data, dict):
                        for key, values in data.items():
                            writer.writerow([key.upper()])
                            for item in values:
                                writer.writerow([item])
                            writer.writerow([])
                    else:
                        for item in data:
                            writer.writerow([item])

            messagebox.showinfo("Успех", f"Данные успешно экспортированы в {filepath}")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def show_history(self):
        history_window = Toplevel(self.root)
        history_window.title("История генераций")
        history_window.geometry("800x500")

        columns = ("ID", "Дата и время", "Количество", "Параметры")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column("Параметры", width=300)

        scrollbar = ttk.Scrollbar(history_window, orient=VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True)

        try:
            self.cursor.execute("SELECT * FROM generations ORDER BY timestamp DESC LIMIT 100")
            for row in self.cursor.fetchall():
                params = json.loads(row[3])
                params_str = ", ".join(f"{k}:{v}" for k, v in params.items())
                tree.insert("", END, values=(row[0], row[1], row[2], params_str))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")

    def show_settings(self):
        settings_window = Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("500x400")

        # Настройки генерации имен
        name_frame = LabelFrame(settings_window, text="Настройки имен")
        name_frame.pack(pady=10, padx=10, fill=X)

        Label(name_frame, text="Формат фамилий для женщин:").pack(anchor=W)
        self.surname_format_var = StringVar(value="a")
        Radiobutton(name_frame, text="Иванова", variable=self.surname_format_var, value="a").pack(anchor=W)
        Radiobutton(name_frame, text="Иванов", variable=self.surname_format_var, value="none").pack(anchor=W)

        # Настройки адресов
        address_frame = LabelFrame(settings_window, text="Настройки адресов")
        address_frame.pack(pady=10, padx=10, fill=X)

        Label(address_frame, text="Диапазон номеров домов:").pack(anchor=W)
        self.house_range_frame = Frame(address_frame)
        self.house_range_frame.pack(fill=X)
        self.house_min = Entry(self.house_range_frame, width=5)
        self.house_min.pack(side=LEFT, padx=5)
        self.house_min.insert(0, "1")
        Label(self.house_range_frame, text="-").pack(side=LEFT)
        self.house_max = Entry(self.house_range_frame, width=5)
        self.house_max.pack(side=LEFT, padx=5)
        self.house_max.insert(0, "126")

        Label(address_frame, text="Диапазон номеров квартир:").pack(anchor=W, pady=(5,0))
        self.apt_range_frame = Frame(address_frame)
        self.apt_range_frame.pack(fill=X)
        self.apt_min = Entry(self.apt_range_frame, width=5)
        self.apt_min.pack(side=LEFT, padx=5)
        self.apt_min.insert(0, "1")
        Label(self.apt_range_frame, text="-").pack(side=LEFT)
        self.apt_max = Entry(self.apt_range_frame, width=5)
        self.apt_max.pack(side=LEFT, padx=5)
        self.apt_max.insert(0, "400")

        # Кнопки
        button_frame = Frame(settings_window)
        button_frame.pack(pady=10)
        Button(button_frame, text="Сохранить", command=settings_window.destroy, bg="#4CAF50", fg="white").pack(side=LEFT, padx=5)
        Button(button_frame, text="Отмена", command=settings_window.destroy, bg="#f44336", fg="white").pack(side=LEFT, padx=5)

    def generate_person(self, family_id=None):
        # Определение пола
        sex_choice = self.sex_var.get()
        if sex_choice == "random":
            sex = random.randint(0, 1)
        elif sex_choice == "male":
            sex = 0 if random.random() < 0.7 else 1  # 70% мужчин
        else:
            sex = 1 if random.random() < 0.7 else 0  # 70% женщин

        # Генерация имени и фамилии
        if sex == 0:
            name = random.choice(self.malenames)
            surname = random.choice(self.surnames)
            patronymic = random.choice(self.male_patronymics)
        else:
            name = random.choice(self.femalenames)
            surname_format = self.surname_format_var.get() if hasattr(self, 'surname_format_var') else "a"
            surname = random.choice(self.surnames) + ('а' if surname_format == "a" else '')
            patronymic = random.choice(self.female_patronymics)

        if family_id:
            surname += f" (Семья {family_id})"

        # Генерация адреса
        try:
            house_min = int(self.house_min.get()) if hasattr(self, 'house_min') else 1
            house_max = int(self.house_max.get()) if hasattr(self, 'house_max') else 126
            apt_min = int(self.apt_min.get()) if hasattr(self, 'apt_min') else 1
            apt_max = int(self.apt_max.get()) if hasattr(self, 'apt_max') else 400
        except:
            house_min, house_max, apt_min, apt_max = 1, 126, 1, 400

        person = {
            "name": name,
            "surname": surname,
            "patronymic": patronymic if random.randint(1, 100) <= self.patronymic_prob.get() else "",
            "city": random.choice(self.cities),
            "street": random.choice(self.streets),
            "home_num": random.randint(house_min, house_max),
            "apart_num": random.randint(apt_min, apt_max),
            "phone": f'+79{random.randint(10_000_00_00, 99_999_99_99)}',
            "birth": f"{random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(1940, 2005)}",
            "passport": f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}",
            "sex": "male" if sex == 0 else "female"
        }

        # Место работы с вероятностью
        if random.randint(1, 100) <= self.job_prob.get():
            person["job"] = f'ООО <<{random.choice(self.words)}>>'
            person["job_position"] = random.choice(["Менеджер", "Директор", "Бухгалтер", "Программист", "Аналитик", "Инженер"])

        # Зарплата с вероятностью
        if random.randint(1, 100) <= self.salary_prob.get():
            person["salary"] = random.randint(10000, 250000)

        # Соцсети с вероятностью
        if random.randint(1, 100) <= self.social_prob.get():
            social_networks = []
            if random.random() < 0.5:
                social_networks.append(('vk', f'https://vk.com/id{random.randint(397251, 17837567)}'))
            if random.random() < 0.5:
                social_networks.append(('ok', f'https://ok.ru/profile/{random.randint(58357, 765987123123)}'))
            if social_networks:
                person["social_networks"] = dict(social_networks)

        # Клиент сервиса с вероятностью
        if random.randint(1, 100) <= self.service_prob.get():
            service = random.choice(self.services)
            person["service"] = {
                "name": service,
                "since": f"{random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(2010, 2023)}"
            }
            if service in ['Яндекс.Такси', 'Яндекс.Еда']:
                person["service"]["rating"] = round(random.uniform(3.5, 5.0), 1)

        # Пересечение границы с вероятностью
        if random.randint(1, 100) <= self.border_prob.get():
            crossing_date = datetime.now() - timedelta(days=random.randint(1, 365))
            person["border_crossing"] = {
                "point": random.choice(self.border_crossings),
                "date": crossing_date.strftime("%d.%m.%Y"),
                "time": f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
                "direction": random.choice(["Въезд", "Выезд"])
            }

        # Микрозайм с вероятностью
        if random.randint(1, 100) <= self.loan_prob.get():
            loan_date = datetime.now() - timedelta(days=random.randint(1, 365))
            person["loan"] = {
                "company": random.choice(self.loan_companies),
                "amount": random.randint(5000, 50000),
                "date": loan_date.strftime("%d.%m.%Y"),
                "due_date": (loan_date + timedelta(days=30)).strftime("%d.%m.%Y"),
                "paid": random.choice([True, False])
            }

        # Уголовное дело с вероятностью
        if random.randint(1, 100) <= self.crime_prob.get():
            crime_date = datetime.now() - timedelta(days=random.randint(30, 365*5))
            person["crime"] = {
                "type": random.choice(self.crime_types),
                "date": crime_date.strftime("%d.%m.%Y"),
                "status": random.choice(["Расследование", "Судебное разбирательство", "Осужден", "Оправдан"]),
                "article": f"ст. {random.randint(100, 400)} УК РФ"
            }
            if person["crime"]["status"] == "Осужден":
                person["crime"]["sentence"] = random.choice(["Условный срок", "Штраф", f"{random.randint(1, 15)} лет лишения свободы"])

        return person

    def generate_family(self):
        family_id = random.randint(1000, 9999)
        family_size = random.randint(2, 4)
        return [self.generate_person(family_id) for _ in range(family_size)]

    def generate_data(self):
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число (целое положительное)")
            return

        # Сохраняем параметры генерации для истории
        params = {
            "quantity": quantity,
            "job_prob": self.job_prob.get(),
            "salary_prob": self.salary_prob.get(),
            "social_prob": self.social_prob.get(),
            "family_prob": self.family_prob.get(),
            "patronymic_prob": self.patronymic_prob.get(),
            "service_prob": self.service_prob.get(),
            "border_prob": self.border_prob.get(),
            "loan_prob": self.loan_prob.get(),
            "crime_prob": self.crime_prob.get(),
            "sex_distribution": self.sex_var.get()
        }

        data = []
        remaining = quantity

        # Генерация с учетом вероятности семей
        while remaining > 0:
            if random.randint(1, 100) <= self.family_prob.get() and remaining > 1:
                family = self.generate_family()
                family_size = len(family)
                if family_size <= remaining:
                    if self.group_family_var.get():
                        data.append({"type": "family", "members": family})
                    else:
                        data.extend(family)
                    remaining -= family_size
            else:
                data.append(self.generate_person())
                remaining -= 1

        self.generated_count += len(data)
        self.last_generation_time = datetime.now()
        self.save_generation_stats(len(data), params)

        self.status.config(text=f"Сгенерировано {len(data)} записей. Всего: {self.generated_count}")
        self.update_preview(data)

        # Вывод данных в выбранном формате
        output_type = self.output_var.get()

        if output_type == 1:
            self.save_as_txt(data)
        elif output_type == 2:
            self.save_as_html(data)
        elif output_type == 3:
            self.save_as_separate_txt(data)
        elif output_type == 4:
            self.save_as_separate_html(data)
        elif output_type == 5:
            self.save_as_json(data)
        elif output_type == 6:
            self.save_as_csv(data)
        elif output_type == 7:
            self.save_as_separate_json(data)

    def update_preview(self, data):
        self.preview_text.delete(1.0, END)

        if not data:
            self.preview_text.insert(END, "Нет данных для предпросмотра")
            return

        sample = data[:3]  # Показываем первые 3 записи для предпросмотра

        for person in sample:
            if isinstance(person, dict) and person.get("type") == "family":
                self.preview_text.insert(END, f"=== Семья из {len(person['members'])} человек ===\n\n")
                for member in person["members"]:
                    self.add_person_to_preview(member)
                self.preview_text.insert(END, "\n")
            else:
                self.add_person_to_preview(person)
                self.preview_text.insert(END, "\n")

    def add_person_to_preview(self, person):
        self.preview_text.insert(END, f"{person['surname']} {person['name']} {person.get('patronymic', '')}\n")
        self.preview_text.insert(END, f"Паспорт: {person['passport']}\n")
        self.preview_text.insert(END, f"Адрес: {person['city']}, ул. {person['street']}, д. {person['home_num']}, кв. {person['apart_num']}\n")

        if 'job' in person:
            self.preview_text.insert(END, f"Работа: {person['job']} ({person.get('job_position', 'Должность не указана')})\n")

    def save_as_txt(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_folder, f"people_data_{timestamp}.txt")

        with open(filename, "w", encoding="utf-8") as f:
            for item in data:
                if isinstance(item, dict) and item.get("type") == "family":
                    f.write(f"=== Семья из {len(item['members'])} человек ===\n\n")
                    for person in item["members"]:
                        self.write_person_to_txt(f, person)
                    f.write("\n")
                else:
                    self.write_person_to_txt(f, item)
                    f.write("\n")

        messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        self.status.config(text=f"Данные сохранены в {filename}")

    def write_person_to_txt(self, file, person):
        file.write(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}\n")
        file.write(f"Паспорт: {person['passport']}\n")
        file.write(f"Адрес: {person['city']}, ул. {person['street']}, д. {person['home_num']}, кв. {person['apart_num']}\n")
        file.write(f"Телефон: {person['phone']}\n")
        file.write(f"Дата рождения: {person['birth']}\n")

        if 'job' in person:
            file.write(f"Работа: {person['job']} ({person.get('job_position', 'Должность не указана')})\n")
        if 'salary' in person:
            file.write(f"Зарплата: {person['salary']} руб.\n")
        if 'social_networks' in person:
            for network, url in person['social_networks'].items():
                file.write(f"{network.upper()}: {url}\n")
        if 'service' in person:
            file.write(f"Клиент сервиса: {person['service']['name']} (с {person['service']['since']})")
            if 'rating' in person['service']:
                file.write(f", рейтинг: {person['service']['rating']}")
            file.write("\n")
        if 'border_crossing' in person:
            bc = person['border_crossing']
            file.write(f"Пересечение границы: {bc['point']}, {bc['date']} {bc['time']} ({bc['direction']})\n")
        if 'loan' in person:
            loan = person['loan']
            file.write(f"Микрозайм: {loan['company']}, сумма: {loan['amount']} руб., дата: {loan['date']}, срок: {loan['due_date']}, {'погашен' if loan['paid'] else 'не погашен'}\n")
        if 'crime' in person:
            crime = person['crime']
            file.write(f"Уголовное дело: {crime['type']} ({crime['article']}), дата: {crime['date']}, статус: {crime['status']}")
            if 'sentence' in crime:
                file.write(f", приговор: {crime['sentence']}")
            file.write("\n")

    def save_as_html(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_folder, f"people_data_{timestamp}.html")

        html = """<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Сгенерированные данные</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                th { background-color: #4CAF50; color: white; }
                .family-header { background-color: #e6f7ff; padding: 10px; margin: 20px 0 10px 0; border-left: 4px solid #1890ff; }
                .person-photo { width: 100px; height: auto; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>Сгенерированные данные</h1>
            <p>Сгенерировано: {timestamp}</p>
        """

        for item in data:
            if isinstance(item, dict) and item.get("type") == "family":
                html += f"""
                <div class="family-header">
                    <h3>Семья из {len(item['members'])} человек</h3>
                </div>
                """
                for person in item["members"]:
                    html += self.get_person_html(person)
            else:
                html += self.get_person_html(item)

        html += """
        </body>
        </html>
        """

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        self.status.config(text=f"Данные сохранены в {filename}")
        webbrowser.open("file://" + os.path.abspath(filename))

    def get_person_html(self, person):
        # Генерация фото (заглушка или реальное изображение)
        photo_html = ""
        if self.include_photo_var.get():
            sex = person.get('sex', 'male')
            photo_url = f"https://randomuser.me/api/portraits/{'men' if sex == 'male' else 'women'}/{random.randint(1, 99)}.jpg"
            photo_html = f'<img src="{photo_url}" class="person-photo" alt="Фото">'

        social_html = ""
        if 'social_networks' in person:
            social_links = []
            for network, url in person['social_networks'].items():
                social_links.append(f'<a href="{url}">{network.upper()}</a>')
            social_html = f"<tr><td>Соцсети</td><td>{" ".join(social_links)}</td></tr>"

        html = f"""
        <table>
            <tr><th colspan="2">{person['surname']} {person['name']} {person.get('patronymic', '')} {photo_html}</th></tr>
            <tr><td>Паспорт</td><td>{person['passport']}</td></tr>
            <tr><td>Адрес</td><td>{person['city']}, ул. {person['street']}, д. {person['home_num']}, кв. {person['apart_num']}</td></tr>
            <tr><td>Телефон</td><td>{person['phone']}</td></tr>
            <tr><td>Дата рождения</td><td>{person['birth']}</td></tr>
        """

        if 'job' in person:
            html += f"""
            <tr><td>Работа</td><td>{person['job']} ({person.get('job_position', 'Должность не указана')})</td></tr>
            """
        if 'salary' in person:
            html += f"""
            <tr><td>Зарплата</td><td>{person['salary']} руб.</td></tr>
            """

        html += social_html

        if 'service' in person:
            html += f"""
            <tr><td>Клиент сервиса</td><td>{person['service']['name']} (с {person['service']['since']}"""
            if 'rating' in person['service']:
                html += f""", рейтинг: {person['service']['rating']}"""
            html += """)</td></tr>
            """

        if 'border_crossing' in person:
            bc = person['border_crossing']
            html += f"""
            <tr><td>Пересечение границы</td><td>{bc['point']}, {bc['date']} {bc['time']} ({bc['direction']})</td></tr>
            """

        if 'loan' in person:
            loan = person['loan']
            html += f"""
            <tr><td>Микрозайм</td><td>{loan['company']}, сумма: {loan['amount']} руб., дата: {loan['date']}, срок: {loan['due_date']}, {'погашен' if loan['paid'] else 'не погашен'}</td></tr>
            """

        if 'crime' in person:
            crime = person['crime']
            html += f"""
            <tr><td>Уголовное дело</td><td>{crime['type']} ({crime['article']}), дата: {crime['date']}, статус: {crime['status']}"""
            if 'sentence' in crime:
                html += f""", приговор: {crime['sentence']}"""
            html += """)</td></tr>
            """

        html += "</table><br>"
        return html

    def save_as_separate_txt(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.output_folder, f"people_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        counter = 1
        for item in data:
            if isinstance(item, dict) and item.get("type") == "family":
                for person in item["members"]:
                    filename = os.path.join(folder, f"person_{counter}.txt")
                    with open(filename, "w", encoding="utf-8") as f:
                        self.write_person_to_txt(f, person)
                    counter += 1
            else:
                filename = os.path.join(folder, f"person_{counter}.txt")
                with open(filename, "w", encoding="utf-8") as f:
                    self.write_person_to_txt(f, item)
                counter += 1

        messagebox.showinfo("Успех", f"Данные сохранены в папке {folder}")
        self.status.config(text=f"Данные сохранены в папке {folder}")
        webbrowser.open(folder)

    def save_as_separate_html(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.output_folder, f"people_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        counter = 1
        for item in data:
            if isinstance(item, dict) and item.get("type") == "family":
                for person in item["members"]:
                    filename = os.path.join(folder, f"person_{counter}.html")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.get_person_html(person, standalone=True))
                    counter += 1
            else:
                filename = os.path.join(folder, f"person_{counter}.html")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.get_person_html(person, standalone=True))
                counter += 1

        messagebox.showinfo("Успех", f"Данные сохранены в папке {folder}")
        self.status.config(text=f"Данные сохранены в папке {folder}")
        webbrowser.open(folder)

    def save_as_json(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_folder, f"people_data_{timestamp}.json")

        # Преобразуем данные в формат, пригодный для JSON
        json_data = []
        for item in data:
            if isinstance(item, dict) and item.get("type") == "family":
                json_data.append({
                    "type": "family",
                    "members": item["members"]
                })
            else:
                json_data.append(item)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        self.status.config(text=f"Данные сохранены в {filename}")

    def save_as_csv(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_folder, f"people_data_{timestamp}.csv")

        # Собираем все возможные поля для заголовков
        all_fields = set()
        for item in data:
            if isinstance(item, dict) and item.get("type") == "family":
                for person in item["members"]:
                    all_fields.update(person.keys())
            else:
                all_fields.update(item.keys())

        fieldnames = sorted(all_fields)

        with open(filename, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in data:
                if isinstance(item, dict) and item.get("type") == "family":
                    for person in item["members"]:
                        writer.writerow(person)
                else:
                    writer.writerow(item)

        messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        self.status.config(text=f"Данные сохранены в {filename}")

    def save_as_separate_json(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.output_folder, f"people_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        counter = 1
        for item in data:
            if isinstance(item, dict) and item.get("type") == "family":
                for person in item["members"]:
                    filename = os.path.join(folder, f"person_{counter}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(person, f, ensure_ascii=False, indent=2)
                    counter += 1
            else:
                filename = os.path.join(folder, f"person_{counter}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(item, f, ensure_ascii=False, indent=2)
                counter += 1

        messagebox.showinfo("Успех", f"Данные сохранены в папке {folder}")
        self.status.config(text=f"Данные сохранены в папке {folder}")
        webbrowser.open(folder)

if __name__ == "__main__":
    root = Tk()
    app = PeopleGenerator(root)
    root.mainloop()