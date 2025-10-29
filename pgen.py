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
import requests
import openai
from threading import Thread


class PeopleGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("pgen5 - Улучшенная версия с ИИ")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)

        # Иконка приложения
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass

        # Настройки ChatGPT
        self.openai_api_key = ""
        self.use_chatgpt = False
        self.chatgpt_enabled = False

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

        # Данные для улучшенной генерации
        self.init_enhanced_data()
        self.init_real_db_data()

    def init_enhanced_data(self):
        """Инициализация улучшенных данных для генерации"""
        # Улучшенные списки профессий
        self.enhanced_jobs = {
            "IT": [
                "Frontend разработчик", "Backend разработчик", "Fullstack разработчик", "DevOps инженер",
                "Data Scientist", "ML инженер", "Android разработчик", "iOS разработчик",
                "QA инженер", "Тестировщик", "Системный администратор", "Сетевой инженер",
                "Кибербезопасность специалист", "Бизнес-аналитик", "Product Manager",
                "Project Manager", "Scrum Master", "UX/UI дизайнер", "Геймдизайнер"
            ],
            "Медицина": [
                "Хирург", "Терапевт", "Педиатр", "Кардиолог", "Невролог", "Стоматолог",
                "Офтальмолог", "Дерматолог", "Психиатр", "Психолог", "Медсестра", "Фельдшер",
                "Фармацевт", "Лаборант", "Врач УЗИ", "Рентгенолог", "Анестезиолог"
            ],
            "Финансы": [
                "Бухгалтер", "Экономист", "Финансовый аналитик", "Аудитор", "Налоговый консультант",
                "Инвестиционный аналитик", "Трейдер", "Банковский работник", "Страховой агент",
                "Финансовый директор", "Кредитный специалист", "Казначей"
            ],
            "Образование": [
                "Учитель математики", "Учитель русского языка", "Учитель истории", "Преподаватель вуза",
                "Воспитатель детского сада", "Репетитор", "Методист", "Директор школы",
                "Психолог в образовании", "Социальный педагог"
            ],
            "Торговля": [
                "Продавец-консультант", "Мерчендайзер", "Товаровед", "Супервайзер",
                "Руководитель отдела продаж", "Менеджер по продажам", "Кассир",
                "Администратор магазина", "Закупщик", "Маркетолог"
            ]
        }

        # Улучшенные описания для ChatGPT
        self.personality_traits = [
            "амбициозный", "добросовестный", "креативный", "аналитический", "коммуникабельный",
            "ответственный", "стрессоустойчивый", "лидерский", "исполнительный", "инновационный"
        ]

        self.interests = [
            "программирование", "спорт", "путешествия", "чтение", "музыка", "кино",
            "наука", "технологии", "искусство", "кулинария", "фотография", "игры"
        ]

    def init_real_db_data(self):
        """Инициализация данных для имитации реальных баз"""
        self.db_sources = {
            "Общая сводка": ["Телефон", "СНИЛС", "ИНН", "Email", "Автомобили", "Личности", "Паспорт", "Адрес",
                             "Место рождения", "Водительское удостоверение"],
            "Жители МО и Москвы": ["Паспорт", "ФИО", "Email", "День рождения", "Место рождения", "Полис ОМС", "Адрес",
                                   "Телефон", "СНИЛС", "Адрес проживания"],
            "ФОМС": ["ФИО", "Телефон", "Email", "День рождения", "СНИЛС", "Полис ОМС"],
            "Пациенты поликлиники": ["ФИО", "День рождения", "Адрес", "Адрес регистрации",
                                     "Обслужен мобильной бригадой", "Первый этап закончен", "Направлен на второй этап"],
            "Медицинское страхование": ["ФИО", "День рождения", "Адрес", "Полис ОМС", "СНИЛС"],
            "Росреестр": ["ФИО", "Паспорт", "Дата выдачи паспорта", "Орган, выдавший паспорт", "СНИЛС", "День рождения",
                          "Место рождения", "Адрес регистрации"],
            "Пересечение границы": ["День рождения", "Город прибытия", "Страна прибытия", "Перевозчик",
                                    "Пограничный пункт", "Дата пересечения границы", "Страна выдачи документа",
                                    "Дата выдачи документа", "Дата рейса", "Номер рейса", "Тип операции",
                                    "Тип транспорта", "Паспорт", "ФИО"],
            "Пользователи leader-id.ru": ["День рождения", "Метка кэша", "ФИО", "Последняя активность", "Адрес",
                                          "Часовой пояс адреса", "Название адреса (город)", "Дата создания компании",
                                          "Полное название компании", "Название компании", "Должность"],
            "Назначения лекарств": ["ФИО", "СНИЛС", "День рождения", "Телефон", "Название назначенного препарата",
                                    "Инструкция по применению", "Дата назначения препарата"],
            "Регистрационный учет МВД": ["День рождения", "Дата выдачи паспорта", "Кем выдан паспорт", "Место рождения",
                                         "Адрес", "ФИО", "Паспорт", "Годы проживания"],
            "Недвижимость": ["ФИО", "День рождения", "Адрес места регистрации", "Паспорт", "Адрес"],
            "Собственники": ["ФИО", "День рождения", "Адрес", "Паспорт", "Дата выдачи паспорта", "Кем выдан паспорт",
                             "Гражданство", "Текст из свидетельства", "Субъект права"],
            "Жители России": ["ФИО", "День рождения", "Адрес"],
            "Департамент здравоохранения": ["ФИО", "День рождения", "Регистрация", "Тип документа",
                                            "Свидетельство о рождении"],
            "Родственники": ["ФИО", "День рождения", "ФИО родственника", "День рождения родственника", "Тип родства"],
            "Возможные связи по адресу": ["Адрес", "ФИО", "День рождения", "Связь с лицом"]
        }

        # Дополнительные данные для заполнения
        self.oms_codes = ["2792299725000109", "2792345623000201", "2792456723000302", "2792567823000403"]
        self.drugs = ["Колекальциферол, табл. раствор., 2000 МЕ", "Поливитамины + Минералы, табл. жев.",
                      "Веррукацид, р-р д/наружн. прим., 2 г", "Колекальциферол, табл. раствор., 1000 МЕ"]
        self.drug_instructions = [
            "Принимать 0.5 шт. (таблетка) перорально 1 раз в день в течение 15 дней",
            "Принимать 1 шт. (таблетка) энтерально 1 раз в день в течение 15 дней",
            "Наносить 2 г наружно 1 раз в день в течение 1 дня"
        ]
        self.airlines = ["ТУРЕЦКИЕ АВИАЛИНИИ", "СЕВЕРНЫЙ ВЕТЕР", "РЕД ВИНГС", "ТУРКИШ ЭЙРЛАЙНС"]
        self.flight_numbers = ["TK-3135", "N4-1806", "ИН-9306", "TK-3989"]

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
            "Пункт пропуска Дубовка", "Пункт пропуска Романовская", "Пункт пропуска Мороковская",
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

        Button(toolbar, text="Экспорт данных", command=self.show_export_dialog, bg="#4CAF50", fg="white").pack(
            side=LEFT, padx=5)
        Button(toolbar, text="История", command=self.show_history, bg="#2196F3", fg="white").pack(side=LEFT, padx=5)
        Button(toolbar, text="Настройки", command=self.show_settings, bg="#607D8B", fg="white").pack(side=LEFT, padx=5)

        # Кнопка настройки ChatGPT
        Button(toolbar, text="ChatGPT Настройки", command=self.show_chatgpt_settings, bg="#FF9800", fg="white").pack(
            side=LEFT, padx=5)

        # Панель темы
        theme_frame = Frame(toolbar)
        theme_frame.pack(side=RIGHT, padx=5)
        Label(theme_frame, text="Тема:").pack(side=LEFT)
        self.theme_var = StringVar(value=self.current_theme)
        OptionMenu(theme_frame, self.theme_var, *self.themes.keys(), command=self.change_theme).pack(side=LEFT)

        # Статус ChatGPT
        self.chatgpt_status = Label(toolbar, text="ChatGPT: Выкл", fg="red")
        self.chatgpt_status.pack(side=RIGHT, padx=10)

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
        Label(params_frame, text="Вероятности добавления:").pack(pady=(10, 5))

        self.create_probability_slider(params_frame, "Места работы:", "job_prob", 80)
        self.create_probability_slider(params_frame, "Зарплаты:", "salary_prob", 50)
        self.create_probability_slider(params_frame, "Соцсетей:", "social_prob", 50)
        self.create_probability_slider(params_frame, "Семей:", "family_prob", 30)
        self.create_probability_slider(params_frame, "Отчеств:", "patronymic_prob", 70)
        self.create_probability_slider(params_frame, "Клиентов сервисов:", "service_prob", 40)
        self.create_probability_slider(params_frame, "Пересечений границы:", "border_prob", 20)
        self.create_probability_slider(params_frame, "Микрозаймов:", "loan_prob", 25)
        self.create_probability_slider(params_frame, "Уголовных дел:", "crime_prob", 15)

        # Улучшенная генерация
        Label(params_frame, text="Улучшенная генерация:").pack(pady=(10, 5))

        self.enhanced_generation_var = IntVar(value=0)
        Checkbutton(params_frame, text="Использовать улучшенную генерацию",
                    variable=self.enhanced_generation_var).pack(anchor=W)

        self.chatgpt_generation_var = IntVar(value=0)
        self.chatgpt_checkbox = Checkbutton(params_frame, text="Использовать ChatGPT",
                                            variable=self.chatgpt_generation_var, state=DISABLED)
        self.chatgpt_checkbox.pack(anchor=W)

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
            ("Один файл (TXT как реальная база)", 8),
            ("Один файл (TXT улучшенный)", 9),
            ("Отдельные файлы (TXT)", 3),
            ("Отдельные файлы (HTML)", 4),
            ("Отдельные файлы (JSON)", 7),
            ("Отдельные файлы (TXT как реальная база)", 10),
            ("Отдельные файлы (TXT улучшенный)", 11)
        ]

        for text, value in output_options:
            Radiobutton(format_frame, text=text, variable=self.output_var, value=value).pack(anchor=W)

        # Дополнительные параметры вывода
        Label(output_frame, text="Дополнительные параметры:").pack(pady=(10, 5), anchor=W)

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

    def show_chatgpt_settings(self):
        """Окно настройки ChatGPT"""
        chatgpt_window = Toplevel(self.root)
        chatgpt_window.title("Настройки ChatGPT")
        chatgpt_window.geometry("500x300")

        main_frame = Frame(chatgpt_window)
        main_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

        Label(main_frame, text="Настройки интеграции с ChatGPT", font=('Arial', 12, 'bold')).pack(pady=10)

        # Поле для API ключа
        key_frame = Frame(main_frame)
        key_frame.pack(fill=X, pady=10)
        Label(key_frame, text="API ключ OpenAI:").pack(anchor=W)
        self.api_key_entry = Entry(key_frame, width=50, show="*")
        self.api_key_entry.pack(fill=X, pady=5)
        if self.openai_api_key:
            self.api_key_entry.insert(0, self.openai_api_key)

        # Кнопка проверки
        Button(key_frame, text="Проверить подключение", command=self.test_chatgpt_connection).pack(pady=5)

        # Статус подключения
        self.connection_status = Label(key_frame, text="Не проверено", fg="red")
        self.connection_status.pack()

        # Информация
        info_frame = Frame(main_frame)
        info_frame.pack(fill=X, pady=10)
        Label(info_frame, text="Информация:", font=('Arial', 10, 'bold')).pack(anchor=W)
        Label(info_frame, text="• API ключ можно получить на platform.openai.com", wraplength=450).pack(anchor=W)
        Label(info_frame, text="• Использование ChatGPT улучшит качество генерации", wraplength=450).pack(anchor=W)
        Label(info_frame, text="• Для работы требуется стабильное интернет-подключение", wraplength=450).pack(anchor=W)

        # Кнопки
        button_frame = Frame(main_frame)
        button_frame.pack(pady=20)
        Button(button_frame, text="Сохранить", command=lambda: self.save_chatgpt_settings(chatgpt_window),
               bg="#4CAF50", fg="white").pack(side=LEFT, padx=5)
        Button(button_frame, text="Отмена", command=chatgpt_window.destroy,
               bg="#f44336", fg="white").pack(side=LEFT, padx=5)

    def test_chatgpt_connection(self):
        """Тестирование подключения к ChatGPT"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self.connection_status.config(text="Введите API ключ", fg="red")
            return

        def test_connection():
            try:
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Тестовое сообщение"}],
                    max_tokens=10
                )
                self.root.after(0, lambda: self.connection_status.config(text="Подключение успешно", fg="green"))
            except Exception as e:
                self.root.after(0, lambda: self.connection_status.config(text=f"Ошибка: {str(e)}", fg="red"))

        Thread(target=test_connection).start()
        self.connection_status.config(text="Проверка подключения...", fg="orange")

    def save_chatgpt_settings(self, window):
        """Сохранение настроек ChatGPT"""
        self.openai_api_key = self.api_key_entry.get().strip()
        if self.openai_api_key:
            self.chatgpt_enabled = True
            self.chatgpt_status.config(text="ChatGPT: Вкл", fg="green")
            self.chatgpt_checkbox.config(state=NORMAL)
        else:
            self.chatgpt_enabled = False
            self.chatgpt_status.config(text="ChatGPT: Выкл", fg="red")
            self.chatgpt_checkbox.config(state=DISABLED)
            self.chatgpt_generation_var.set(0)

        window.destroy()

    def generate_with_chatgpt(self, prompt):
        """Генерация текста с помощью ChatGPT"""
        if not self.chatgpt_enabled or not self.openai_api_key:
            return None

        try:
            openai.api_key = self.openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты помогаешь генерировать реалистичные данные для тестирования."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Ошибка ChatGPT: {e}")
            return None

    def generate_enhanced_person(self, family_id=None):
        """Улучшенная генерация персоны с использованием расширенных данных и ChatGPT"""
        # Базовые данные (как в оригинальной функции)
        sex_choice = self.sex_var.get()
        if sex_choice == "random":
            sex = random.randint(0, 1)
        elif sex_choice == "male":
            sex = 0 if random.random() < 0.7 else 1
        else:
            sex = 1 if random.random() < 0.7 else 0

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

        # Улучшенная генерация работы
        if random.randint(1, 100) <= self.job_prob.get():
            job_category = random.choice(list(self.enhanced_jobs.keys()))
            job_title = random.choice(self.enhanced_jobs[job_category])

            if self.chatgpt_generation_var.get() and self.chatgpt_enabled:
                # Генерация описания компании с помощью ChatGPT
                company_prompt = f"Придумай короткое название IT компании в России, максимум 3 слова"
                company_name = self.generate_with_chatgpt(company_prompt)
                if company_name:
                    person["job"] = f'ООО «{company_name}»'
                else:
                    person["job"] = f'ООО «{random.choice(self.words)}»'
            else:
                person["job"] = f'ООО «{random.choice(self.words)}»'

            person["job_position"] = job_title
            person["job_category"] = job_category

            # Улучшенная зарплата в зависимости от профессии
            if random.randint(1, 100) <= self.salary_prob.get():
                base_salaries = {
                    "IT": (80000, 350000),
                    "Медицина": (50000, 250000),
                    "Финансы": (60000, 300000),
                    "Образование": (30000, 120000),
                    "Торговля": (35000, 150000)
                }
                min_salary, max_salary = base_salaries.get(job_category, (30000, 150000))
                person["salary"] = random.randint(min_salary, max_salary)

        # Улучшенные социальные сети
        if random.randint(1, 100) <= self.social_prob.get():
            social_networks = {}
            if random.random() < 0.6:
                social_networks['vk'] = f'https://vk.com/id{random.randint(397251, 17837567)}'
            if random.random() < 0.4:
                social_networks['ok'] = f'https://ok.ru/profile/{random.randint(58357, 765987123123)}'
            if random.random() < 0.3:
                social_networks['telegram'] = f'@{name.lower()}_{surname.lower()}'
            if random.random() < 0.2:
                social_networks['instagram'] = f'https://instagram.com/{name.lower()}_{surname.lower()}'

            if social_networks:
                person["social_networks"] = social_networks

        # Улучшенная генерация с использованием ChatGPT для дополнительных полей
        if self.chatgpt_generation_var.get() and self.chatgpt_enabled:
            # Генерация интересов
            if random.random() < 0.7:
                interests_prompt = f"Перечисли 3-5 хобби или интересов для человека по имени {name} {surname}, разделяя запятыми"
                interests = self.generate_with_chatgpt(interests_prompt)
                if interests:
                    person["interests"] = interests

            # Генерация краткого описания
            if random.random() < 0.5:
                description_prompt = f"Напиши очень краткое описание личности для {name} {surname} {patronymic}, {person.get('job_position', 'безработный')}, в одном предложении"
                description = self.generate_with_chatgpt(description_prompt)
                if description:
                    person["description"] = description

        # Остальные поля (как в оригинальной функции)
        if random.randint(1, 100) <= self.service_prob.get():
            service = random.choice(self.services)
            person["service"] = {
                "name": service,
                "since": f"{random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(2010, 2023)}"
            }
            if service in ['Яндекс.Такси', 'Яндекс.Еда']:
                person["service"]["rating"] = round(random.uniform(3.5, 5.0), 1)

        if random.randint(1, 100) <= self.border_prob.get():
            crossing_date = datetime.now() - timedelta(days=random.randint(1, 365))
            person["border_crossing"] = {
                "point": random.choice(self.border_crossings),
                "date": crossing_date.strftime("%d.%m.%Y"),
                "time": f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
                "direction": random.choice(["Въезд", "Выезд"])
            }

        if random.randint(1, 100) <= self.loan_prob.get():
            loan_date = datetime.now() - timedelta(days=random.randint(1, 365))
            person["loan"] = {
                "company": random.choice(self.loan_companies),
                "amount": random.randint(5000, 50000),
                "date": loan_date.strftime("%d.%m.%Y"),
                "due_date": (loan_date + timedelta(days=30)).strftime("%d.%m.%Y"),
                "paid": random.choice([True, False])
            }

        if random.randint(1, 100) <= self.crime_prob.get():
            crime_date = datetime.now() - timedelta(days=random.randint(30, 365 * 5))
            person["crime"] = {
                "type": random.choice(self.crime_types),
                "date": crime_date.strftime("%d.%m.%Y"),
                "status": random.choice(["Расследование", "Судебное разбирательство", "Осужден", "Оправдан"]),
                "article": f"ст. {random.randint(100, 400)} УК РФ"
            }
            if person["crime"]["status"] == "Осужден":
                person["crime"]["sentence"] = random.choice(
                    ["Условный срок", "Штраф", f"{random.randint(1, 15)} лет лишения свободы"])

        return person

    def generate_person(self, family_id=None):
        """Основная функция генерации персоны (выбирает между обычной и улучшенной)"""
        if self.enhanced_generation_var.get():
            return self.generate_enhanced_person(family_id)
        else:
            # Оригинальная логика генерации
            sex_choice = self.sex_var.get()
            if sex_choice == "random":
                sex = random.randint(0, 1)
            elif sex_choice == "male":
                sex = 0 if random.random() < 0.7 else 1
            else:
                sex = 1 if random.random() < 0.7 else 0

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

            if random.randint(1, 100) <= self.job_prob.get():
                person["job"] = f'ООО <<{random.choice(self.words)}>>'
                person["job_position"] = random.choice(
                    ["Менеджер", "Директор", "Бухгалтер", "Программист", "Аналитик", "Инженер"])

            if random.randint(1, 100) <= self.salary_prob.get():
                person["salary"] = random.randint(10000, 250000)

            if random.randint(1, 100) <= self.social_prob.get():
                social_networks = []
                if random.random() < 0.5:
                    social_networks.append(('vk', f'https://vk.com/id{random.randint(397251, 17837567)}'))
                if random.random() < 0.5:
                    social_networks.append(('ok', f'https://ok.ru/profile/{random.randint(58357, 765987123123)}'))
                if social_networks:
                    person["social_networks"] = dict(social_networks)

            if random.randint(1, 100) <= self.service_prob.get():
                service = random.choice(self.services)
                person["service"] = {
                    "name": service,
                    "since": f"{random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(2010, 2023)}"
                }
                if service in ['Яндекс.Такси', 'Яндекс.Еда']:
                    person["service"]["rating"] = round(random.uniform(3.5, 5.0), 1)

            if random.randint(1, 100) <= self.border_prob.get():
                crossing_date = datetime.now() - timedelta(days=random.randint(1, 365))
                person["border_crossing"] = {
                    "point": random.choice(self.border_crossings),
                    "date": crossing_date.strftime("%d.%m.%Y"),
                    "time": f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
                    "direction": random.choice(["Въезд", "Выезд"])
                }

            if random.randint(1, 100) <= self.loan_prob.get():
                loan_date = datetime.now() - timedelta(days=random.randint(1, 365))
                person["loan"] = {
                    "company": random.choice(self.loan_companies),
                    "amount": random.randint(5000, 50000),
                    "date": loan_date.strftime("%d.%m.%Y"),
                    "due_date": (loan_date + timedelta(days=30)).strftime("%d.%m.%Y"),
                    "paid": random.choice([True, False])
                }

            if random.randint(1, 100) <= self.crime_prob.get():
                crime_date = datetime.now() - timedelta(days=random.randint(30, 365 * 5))
                person["crime"] = {
                    "type": random.choice(self.crime_types),
                    "date": crime_date.strftime("%d.%m.%Y"),
                    "status": random.choice(["Расследование", "Судебное разбирательство", "Осужден", "Оправдан"]),
                    "article": f"ст. {random.randint(100, 400)} УК РФ"
                }
                if person["crime"]["status"] == "Осужден":
                    person["crime"]["sentence"] = random.choice(
                        ["Условный срок", "Штраф", f"{random.randint(1, 15)} лет лишения свободы"])

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
            "sex_distribution": self.sex_var.get(),
            "enhanced_generation": self.enhanced_generation_var.get(),
            "chatgpt_generation": self.chatgpt_generation_var.get()
        }

        # Показываем прогресс
        self.status.config(text="Генерация данных...")
        self.root.update()

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
        elif output_type == 8:
            self.save_as_real_db_txt(data)
        elif output_type == 9:
            self.save_as_enhanced_txt(data)
        elif output_type == 10:
            self.save_as_separate_real_db_txt(data)
        elif output_type == 11:
            self.save_as_separate_enhanced_txt(data)

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
        self.preview_text.insert(END,
                                 f"Адрес: {person['city']}, ул. {person['street']}, д. {person['home_num']}, кв. {person['apart_num']}\n")

        if 'job' in person:
            self.preview_text.insert(END,
                                     f"Работа: {person['job']} ({person.get('job_position', 'Должность не указана')})\n")

        if 'description' in person:
            self.preview_text.insert(END, f"Описание: {person['description']}\n")

        if 'interests' in person:
            self.preview_text.insert(END, f"Интересы: {person['interests']}\n")

    # Методы для улучшенного экспорта
    def save_as_enhanced_txt(self, data):
        """Сохранение в улучшенном формате TXT"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_folder, f"enhanced_people_data_{timestamp}.txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== УЛУЧШЕННАЯ БАЗА ДАННЫХ ===\n")
            f.write(f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"Количество записей: {len(data)}\n")
            f.write("=" * 50 + "\n\n")

            for item in data:
                if isinstance(item, dict) and item.get("type") == "family":
                    f.write(f"=== СЕМЬЯ ИЗ {len(item['members'])} ЧЕЛОВЕК ===\n\n")
                    for person in item["members"]:
                        self.write_enhanced_person_to_txt(f, person)
                        f.write("\n")
                    f.write("=" * 50 + "\n\n")
                else:
                    self.write_enhanced_person_to_txt(f, item)
                    f.write("\n" + "=" * 50 + "\n\n")

        messagebox.showinfo("Успех", f"Улучшенные данные сохранены в {filename}")
        self.status.config(text=f"Улучшенные данные сохранены в {filename}")

    def write_enhanced_person_to_txt(self, file, person):
        """Запись улучшенных данных персоны в файл"""
        file.write(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}\n")
        file.write(f"Пол: {'Мужской' if person.get('sex') == 'male' else 'Женский'}\n")
        file.write(f"Дата рождения: {person['birth']}\n")
        file.write(f"Паспорт: {person['passport']}\n")
        file.write(f"Телефон: {person['phone']}\n")
        file.write(
            f"Адрес: {person['city']}, ул. {person['street']}, д. {person['home_num']}, кв. {person['apart_num']}\n")

        if 'description' in person:
            file.write(f"Описание: {person['description']}\n")

        if 'job' in person:
            file.write(f"Сфера деятельности: {person.get('job_category', 'Не указана')}\n")
            file.write(f"Должность: {person.get('job_position', 'Не указана')}\n")
            file.write(f"Место работы: {person['job']}\n")

        if 'salary' in person:
            file.write(f"Зарплата: {person['salary']} руб.\n")

        if 'interests' in person:
            file.write(f"Интересы: {person['interests']}\n")

        if 'social_networks' in person:
            file.write("Социальные сети:\n")
            for network, url in person['social_networks'].items():
                file.write(f"  - {network}: {url}\n")

        # Остальные поля как в оригинальной функции
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
            file.write(
                f"Микрозайм: {loan['company']}, сумма: {loan['amount']} руб., дата: {loan['date']}, срок: {loan['due_date']}, {'погашен' if loan['paid'] else 'не погашен'}\n")

        if 'crime' in person:
            crime = person['crime']
            file.write(
                f"Уголовное дело: {crime['type']} ({crime['article']}), дата: {crime['date']}, статус: {crime['status']}")
            if 'sentence' in crime:
                file.write(f", приговор: {crime['sentence']}")
            file.write("\n")

    def save_as_separate_enhanced_txt(self, data):
        """Сохранение в отдельных файлах в улучшенном формате"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.output_folder, f"enhanced_people_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        counter = 1
        for item in data:
            if isinstance(item, dict) and item.get("type") == "family":
                for person in item["members"]:
                    filename = os.path.join(folder, f"enhanced_person_{counter}.txt")
                    with open(filename, "w", encoding="utf-8") as f:
                        self.write_enhanced_person_to_txt(f, person)
                    counter += 1
            else:
                filename = os.path.join(folder, f"enhanced_person_{counter}.txt")
                with open(filename, "w", encoding="utf-8") as f:
                    self.write_enhanced_person_to_txt(f, item)
                counter += 1

        messagebox.showinfo("Успех", f"Улучшенные данные сохранены в папке {folder}")
        self.status.config(text=f"Улучшенные данные сохранены в папке {folder}")
        webbrowser.open(folder)

    # Остальные методы остаются без изменений (show_export_dialog, export_data, show_history, show_settings,
    # и все методы для реальной базы данных из предыдущего ответа)

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

        Label(address_frame, text="Диапазон номеров квартир:").pack(anchor=W, pady=(5, 0))
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
        Button(button_frame, text="Сохранить", command=settings_window.destroy, bg="#4CAF50", fg="white").pack(
            side=LEFT, padx=5)
        Button(button_frame, text="Отмена", command=settings_window.destroy, bg="#f44336", fg="white").pack(side=LEFT,
                                                                                                            padx=5)

    # Методы для реальной базы данных (из предыдущего ответа)
    def generate_real_db_export(self, data):
        """Генерация данных в формате реальной базы"""
        output_lines = []

        for person in data[:10]:  # Ограничим 10 персонами для примера
            if isinstance(person, dict) and person.get("type") == "family":
                for member in person["members"]:
                    output_lines.extend(self.generate_person_real_db_data(member))
            else:
                output_lines.extend(self.generate_person_real_db_data(person))

        return "\n".join(output_lines)

    def generate_person_real_db_data(self, person):
        """Генерация данных для одного человека в формате реальной базы"""
        lines = []

        # Общая сводка
        lines.append("=== Общая сводка ===")
        lines.append(f"Телефон: {person.get('phone', '')}")
        lines.append(f"СНИЛС: {self.generate_snils()}")
        lines.append(f"ИНН: {self.generate_inn()}")
        lines.append(f"Email: {self.generate_email(person)}")
        lines.append(f"Автомобили: {self.generate_cars()}")
        lines.append(
            f"Личности: {person['surname'].lower()} {person['name'].lower()} {person.get('patronymic', '').lower()} {person['birth']}")
        lines.append(f"Паспорт: {person.get('passport', '')}")
        lines.append(f"Адрес: {self.generate_address_variants(person)}")
        lines.append(f"Место рождения: {self.generate_birth_place(person)}")
        lines.append(f"Водительское удостоверение: {self.generate_driver_license()}")
        lines.append("")

        # Жители МО и Москвы
        lines.append("=== Жители МО и Москвы 2025 ===")
        lines.append(f"Паспорт: {self.generate_passport_alt()}")
        lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
        lines.append(f"Email: {self.generate_email(person)}")
        lines.append(f"День рождения: {person['birth']}")
        lines.append(f"Место рождения: {self.generate_birth_place(person)}")
        lines.append(f"Полис ОМС: {random.choice(self.oms_codes)}")
        lines.append(f"Адрес: {self.format_address(person)}")
        lines.append(f"Телефон: {person.get('phone', '')}")
        lines.append(f"СНИЛС: {self.generate_snils()}")
        lines.append(f"Адрес проживания: {self.format_address(person)}")
        lines.append("")

        # ФОМС
        for i in range(2):
            lines.append("=== ФОМС 2025 ===")
            lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
            lines.append(f"Телефон: {self.generate_phone_alt() if i == 1 else person.get('phone', '')}")
            lines.append(f"Email: {self.generate_email_alt(person)}")
            lines.append(f"День рождения: {person['birth']}")
            lines.append(f"СНИЛС: {self.generate_snils()}")
            lines.append(f"Полис ОМС: {random.choice(self.oms_codes)}")
            lines.append("")

        # Медицинские данные
        lines.extend(self.generate_medical_data(person))

        # Пограничные данные
        lines.extend(self.generate_border_data(person))

        # Регистрационные данные
        lines.extend(self.generate_registration_data(person))

        # Данные о недвижимости
        lines.extend(self.generate_property_data(person))

        # Связи по адресу
        lines.extend(self.generate_address_connections(person))

        return lines

    def generate_medical_data(self, person):
        """Генерация медицинских данных"""
        lines = []

        # Пациенты поликлиники
        lines.append("=== Пациенты поликлиники Пенза 2025 ===")
        lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
        lines.append(f"День рождения: {person['birth']}")
        lines.append(f"Адрес: {self.format_address_short(person)}")
        lines.append(f"Адрес регистрации: {self.format_address_full(person)}")
        lines.append("Обслужен мобильной бригадой: НЕТ")
        lines.append("Первый этап закончен: НЕТ")
        lines.append("Направлен на второй этап: НЕТ")
        lines.append("")

        # Медицинское страхование
        lines.append("=== Медицинское страхование 2025 ===")
        lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
        lines.append(f"День рождения: {person['birth']}")
        lines.append(f"Адрес: {self.format_address_compact(person)}")
        lines.append(f"Полис ОМС: {random.choice(self.oms_codes)}")
        lines.append(f"СНИЛС: {self.generate_snils()}")
        lines.append("")

        # Назначения лекарств
        for i in range(5):
            lines.append("=== Назначения лекарств 2024 ===")
            lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
            lines.append(f"СНИЛС: {self.generate_snils()}")
            lines.append(f"День рождения: {person['birth']}")
            lines.append(f"Телефон: {person.get('phone', '')}")
            lines.append(f"Название назначенного препарата: {random.choice(self.drugs)}")
            lines.append(f"Инструкция по применению: {random.choice(self.drug_instructions)}")
            lines.append(f"Дата назначения препарата: {self.generate_prescription_date()}")
            lines.append("")

        return lines

    def generate_border_data(self, person):
        """Генерация данных о пересечении границы"""
        lines = []

        for i in range(6):
            lines.append("=== Пересечение границы 2023 ===")
            lines.append(f"День рождения: {person['birth']}")

            if i % 2 == 0:
                lines.append(f"Город прибытия: АНТАЛЬЯ")
                lines.append(f"Страна прибытия: ТУРЦИЯ")
                lines.append(f"Перевозчик: {random.choice(self.airlines)}")
                lines.append(f"Пограничный пункт: МОСКВА (ВНУКОВО)")
                lines.append(f"Дата пересечения границы: {self.generate_border_date()}")
                lines.append("Тип операции: ВЫЕЗД")
            else:
                lines.append(f"Перевозчик: {random.choice(self.airlines)}")
                lines.append(f"Пограничный пункт: {random.choice(['МОСКВА (ШЕРЕМЕТЬЕВО)', 'МОСКВА (ДОМОДЕДОВО)'])}")
                lines.append(f"Дата пересечения границы: {self.generate_border_date()}")
                lines.append(f"Город отправления: АНТАЛЬЯ")
                lines.append(f"Страна отправления: ТУРЦИЯ")
                lines.append("Тип операции: ВЪЕЗД")

            lines.append(f"Страна выдачи документа: РОССИЯ")
            lines.append(f"Дата выдачи документа: {self.generate_doc_issue_date()}")
            lines.append(f"Дата рейса: {self.generate_flight_date()}")
            lines.append(f"Номер рейса: {random.choice(self.flight_numbers)}")
            lines.append("Тип транспорта: АВИАЦИОННЫЙ ТРАНСПОРТ")
            lines.append(f"Паспорт: {person.get('passport', '')}")
            lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")

            if i % 3 == 0:
                lines.append(f"Номер лицензии: {random.choice(['TCJSC', 'ИН-9306', 'TK-3989'])}")

            lines.append("")

        return lines

    def generate_registration_data(self, person):
        """Генерация регистрационных данных"""
        lines = []

        # Росреестр
        lines.append("=== Росреестр 2024 ===")
        lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
        lines.append(f"Паспорт: {self.generate_passport_alt()}")
        lines.append(f"Дата выдачи паспорта: {self.generate_passport_issue_date()}")
        lines.append(
            f"Орган, выдавший паспорт: территориальным отделом ЗАГС Первомайского рйона г.Пензы Управления ЗАГС Пензенской области")
        lines.append(f"СНИЛС: {self.generate_snils()}")
        lines.append(f"День рождения: {person['birth']}")
        lines.append(f"Место рождения: {self.generate_birth_place_full(person)}")
        lines.append(f"Адрес регистрации: {self.generate_military_address()}")
        lines.append("")

        # Регистрационный учет МВД
        for i in range(5):
            lines.append("=== Регистрационный учет МВД 2022 ===")
            lines.append(f"День рождения: {person['birth']}")
            lines.append(f"Дата выдачи паспорта: {self.generate_passport_issue_date()}")
            lines.append(
                f"Кем выдан паспорт: {random.choice(['ОЗАГС Первомайского р-на г. Пензы УЗАГС Пензенской обл.', 'ГУ МВД РОССИИ ПО МОСКОВСКОЙ ОБЛАСТИ', 'озагс первомайского р-на г.пензы'])}")
            lines.append(f"Место рождения: {self.generate_birth_place_variant(person)}")

            if i % 2 == 0:
                lines.append(f"Адрес: {self.generate_military_address()}")
            else:
                lines.append(f"Адрес: {self.format_address_full(person)}")

            lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
            lines.append(f"Паспорт: {random.choice([self.generate_passport_alt(), '4621247664'])}")
            lines.append(f"Годы проживания: {self.generate_years_of_residence()}")
            lines.append("")

        return lines

    def generate_property_data(self, person):
        """Генерация данных о недвижимости"""
        lines = []

        lines.append("=== Недвижимость Москва 2013 ===")
        lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
        lines.append(f"День рождения: {person['birth']}")
        lines.append(f"Адрес места регистрации: {self.generate_birth_place_full(person)}")
        lines.append(f"Паспорт: {self.generate_old_passport()}")
        lines.append(f"Адрес: {self.generate_military_address()}")
        lines.append("")

        for i in range(2):
            lines.append("=== Собственники Москва 2013 ===")
            lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
            lines.append(f"День рождения: {person['birth']}")

            if i == 0:
                lines.append(f"Адрес: {self.generate_military_address()}")
            else:
                lines.append(f"Адрес места регистрации: {self.generate_birth_place_full(person)}")
                lines.append(f"Адрес: {self.generate_military_address()}")

            lines.append(f"Паспорт: {self.generate_old_passport()}")
            lines.append(f"Дата выдачи паспорта: {self.generate_old_passport_date()}")
            lines.append(
                f"Кем выдан паспорт: территориальным отделом ЗАГС Первомайского рйона г.Пензы Управления ЗАГС Пензинской области")
            lines.append("Гражданство: Российской Федерации")
            lines.append(f"Текст из свидетельства: {self.generate_certificate_text(person)}")

            if i == 1:
                lines.append(f"Субъект права: {random.randint(75000000, 76000000)}")

            lines.append("")

        return lines

    def generate_address_connections(self, person):
        """Генерация связей по адресу"""
        lines = []

        addresses = [
            self.generate_military_address(),
            "КИРОВСКИЙ УЛ.СЕРЫШЕВА УЛ. Д.15 К.НД",
            self.format_address_full(person)
        ]

        for i, address in enumerate(addresses):
            lines.append("=== Возможные связи по адресу ===")
            lines.append(f"Адрес: {address}")
            lines.append(f"ФИО: {person['surname']} {person['name']} {person.get('patronymic', '')}")
            lines.append(f"День рождения: {person['birth']}")

            if i == 0:
                lines.append(f"Связь с лицом: {self.generate_family_connections()}")
            else:
                lines.append(f"Связь с лицом: {self.generate_random_connections()}")

            lines.append("")

        return lines

    # Вспомогательные методы для генерации данных реальной базы
    def generate_snils(self):
        return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100, 999)} {random.randint(10, 99)}"

    def generate_inn(self):
        return f"{random.randint(100000000000, 999999999999)}"

    def generate_email(self, person):
        domains = ["mail.ru", "gmail.com", "yandex.ru", "mai.ru"]
        return f"{person['surname']}@{random.choice(domains)}"

    def generate_email_alt(self, person):
        return f"{person['surname']}_{random.randint(20, 40)}@mail.ru"

    def generate_cars(self):
        if random.random() < 0.3:
            letters = "АВЕКМНОРСТУХ"
            return f"{random.choice(letters)}{random.randint(100, 999)}{random.choice(letters)}{random.choice(letters)}"
        return ""

    def generate_address_variants(self, person):
        variants = [
            self.format_address(person),
            self.format_address_short(person),
            self.format_address_full(person),
            self.format_address_compact(person),
            self.generate_military_address()
        ]
        return ", ".join(random.sample(variants, min(3, len(variants))))

    def generate_birth_place(self, person):
        variants = [
            f"г {person['city']}",
            f"г {person['city']} {random.choice(['пензенская область', 'московская область'])}",
            f"г.{person['city']}",
            "россия"
        ]
        return random.choice(variants)

    def generate_birth_place_full(self, person):
        return f"г. {person['city']} {random.choice(['Пензенская область', 'Московская область'])}"

    def generate_birth_place_variant(self, person):
        variants = [
            f"Россия, Пензенская обл, г.{person['city']}",
            f"гОР.{person['city']}",
            f"Россия, г.{person['city']}"
        ]
        return random.choice(variants)

    def generate_driver_license(self):
        if random.random() < 0.4:
            return f"{random.randint(10, 99)} {random.randint(10, 99)} {random.randint(100000, 999999)}"
        return ""

    def generate_phone_alt(self):
        return f"+79{random.randint(10_000_00_00, 99_999_99_99)}"

    def generate_passport_alt(self):
        return f"{random.choice(['IИЗ', 'I-ИЗ'])}{random.randint(600000, 699999)}"

    def generate_old_passport(self):
        return f"{random.randint(600000, 699999)} I-ИЗ территориальным отделом ЗАГС Первомайского рйона г.Пензы Управления ЗАГС Пензенской области {random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(2007, 2008)}"

    def generate_old_passport_date(self):
        return f"{random.randint(1, 28):02d}.{random.randint(1, 12):02d}.{random.randint(2007, 2008)}"

    def format_address(self, person):
        return f"{person['city']}, {person['street']} ул., д. {person['home_num']}, кв. {person['apart_num']}"

    def format_address_short(self, person):
        return f"Г {person['city'].upper()}, {person['street'].upper()} УЛ, Д. {person['home_num']}, КВ. {person['apart_num']}"

    def format_address_full(self, person):
        regions = ["МОСКОВСКАЯ ОБЛ", "ПЕНЗЕНСКАЯ ОБЛ", "ХАБАРОВСКИЙ КРАЙ"]
        return f"{random.choice(regions)}, Г {person['city'].upper()}, {person['street'].upper()} УЛ, Д. {person['home_num']}, КВ. {person['apart_num']}"

    def format_address_compact(self, person):
        return f"{person['city']} {person['street']} {person['home_num']} {person['apart_num']}"

    def generate_military_address(self):
        cities = ["ХАБАРОВСК", "ВЛАДИВОСТОК", "МОСКВА"]
        return f"РОССИЯ, {random.choice(['ХАБАРОВСКИЙ КРАЙ', 'ПРИМОРСКИЙ КРАЙ'])}, Г.{random.choice(cities)}, УЛ.СЕРЫШЕВА, Д.15, В/Ч {random.randint(46500, 46599)}"

    def generate_prescription_date(self):
        year = random.randint(2023, 2024)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"

    def generate_border_date(self):
        year = random.randint(2017, 2021)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"

    def generate_flight_date(self):
        year = random.randint(2017, 2021)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

    def generate_doc_issue_date(self):
        year = random.randint(2015, 2020)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"

    def generate_passport_issue_date(self):
        year = random.randint(2007, 2021)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"

    def generate_years_of_residence(self):
        start = random.randint(2000, 2010)
        end = start + random.randint(1, 5)
        return f"{start}–{end}"

    def generate_family_connections(self):
        surnames = ["СИНЕЛЬНИКОВ", "ИВАНОВ", "ПЕТРОВ"]
        names = ["НАТАЛЬЯ", "ДЕНИС", "ВЛАДИСЛАВ"]
        return f"{random.choice(surnames)}А {random.choice(names)} {random.choice(['ВЛАДИМИРОВНА', 'СЕРГЕЕВИЧ'])}, {random.choice(surnames)} {random.choice(names)} {random.choice(['ДЕНИСОВИЧ', 'СЕРГЕЕВИЧ'])}"

    def generate_random_connections(self):
        surnames = ["НОВИКОВ", "АНИКИН", "АХАТОВ", "ДЕМИДОВ", "ПЕТРОВ"]
        names = ["ВЛАДИМИР", "АРСЕНИЙ", "ТИМУР", "АНАСТАСИЯ", "ДМИТРИЙ"]
        connections = []
        for _ in range(random.randint(3, 8)):
            connections.append(
                f"{random.choice(surnames)} {random.choice(names)} {random.choice(['АЛЕКСЕЕВИЧ', 'ОЛЕГОВИЧ', 'ДМИТРИЕВНА'])}")
        return "; ".join(connections)

    def generate_certificate_text(self, person):
        return f"{person['surname']} {person['name']} {person.get('patronymic', '')}, дата рождения {person['birth']}, место рождения: {self.generate_birth_place_full(person)}, гражданство Российской Федерации, пол: мужской, свидетельство о рождении: серия I-ИЗ № {random.randint(600000, 699999)}, выдан {self.generate_old_passport_date()} территориальным отделом ЗАГС Первомайского рйона г.Пензы Управления ЗАГС Пензенской области; адрес постоянного места жительства: {self.generate_military_address()}"

    def save_as_real_db_txt(self, data):
        """Сохранение в формате TXT как реальная база данных"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_folder, f"real_db_export_{timestamp}.txt")

        real_db_data = self.generate_real_db_export(data)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(real_db_data)

        messagebox.showinfo("Успех", f"Данные в формате реальной базы сохранены в {filename}")
        self.status.config(text=f"Данные в формате реальной базы сохранены в {filename}")

    def save_as_separate_real_db_txt(self, data):
        """Сохранение в отдельных файлах в формате реальной базы данных"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.output_folder, f"real_db_export_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        counter = 1
        for item in data[:5]:  # Ограничим 5 персонами для примера
            if isinstance(item, dict) and item.get("type") == "family":
                for person in item["members"][:2]:  # Ограничим 2 членами семьи
                    filename = os.path.join(folder, f"person_real_db_{counter}.txt")
                    person_data = self.generate_person_real_db_data(person)
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write("\n".join(person_data))
                    counter += 1
            else:
                filename = os.path.join(folder, f"person_real_db_{counter}.txt")
                person_data = self.generate_person_real_db_data(item)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("\n".join(person_data))
                counter += 1

        messagebox.showinfo("Успех", f"Данные в формате реальной базы сохранены в папке {folder}")
        self.status.config(text=f"Данные в формате реальной базы сохранены в папке {folder}")
        webbrowser.open(folder)

    # Оригинальные методы сохранения (без изменений)
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
        file.write(
            f"Адрес: {person['city']}, ул. {person['street']}, д. {person['home_num']}, кв. {person['apart_num']}\n")
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
            file.write(
                f"Микрозайм: {loan['company']}, сумма: {loan['amount']} руб., дата: {loan['date']}, срок: {loan['due_date']}, {'погашен' if loan['paid'] else 'не погашен'}\n")
        if 'crime' in person:
            crime = person['crime']
            file.write(
                f"Уголовное дело: {crime['type']} ({crime['article']}), дата: {crime['date']}, статус: {crime['status']}")
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
                        f.write(self.get_person_html(person))
                    counter += 1
            else:
                filename = os.path.join(folder, f"person_{counter}.html")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.get_person_html(item))
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