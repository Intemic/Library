import csv
from datetime import datetime
import os
from dataclasses import dataclass, asdict
import enum
from random import getrandbits


class BadMinValue(Exception):
    pass


class BadMaxValue(Exception):
    pass


class Status(enum.Enum):
    in_stock = "в наличии"
    issued = "выдана"


@dataclass
class Book:
    """Представляет запись о книге."""

    PRINT_TEMPLATE = "{id:15}{title:50} {author:30} {year:10} {status:20}"

    id: int = None
    title: str = None
    author: str = None
    year: int = None
    status: Status = None

    def get_info(self) -> str:
        """Вывод записи."""
        return self.PRINT_TEMPLATE.format(**asdict(self))

    def __eq__(self, other):
        # в наших условиях сравниваем объект из базы со всеми заполнеными
        # полями с частично заполненым
        return isinstance(other, Book) and all(
            getattr(self, attr) == getattr(other, attr)
            for attr, val in vars(other).items()
            if val
        )


class Library:
    """Класс предоставляет основную функцион. по работе с библиотекой."""

    # имя файла с данными
    FILE_NAME = "library.txt"
    # заголовок таблицы
    HEADER = "{:4} {:15} {:50} {:30} {:10} {:20}".format(
        "№",
        "Id",
        "Название",
        "Автор",
        "Год",
        "Статус",
    )
    # основное меню
    MAIN_MENU = {
        0: ("Выход из программы", None),
        1: ("Добавление книги", "add_book"),
        2: ("Удаление книги", "delete_book"),
        3: ("Поиск книги", "search_book"),
        4: ("Отображение всех книг", "show_all_books"),
        5: ("Изменение статуса книги", "change_status"),
    }
    # меню поиска
    RECORD_MENU_KEY = {
        1: "title",
        2: "author",
        3: "year",
    }
    # текстовка к меню поиска
    RECORD_MENU_TEXT = {
        "title": "Название",
        "author": "Автор",
        "year": "Год",
    }

    @staticmethod
    def get_records() -> list[Book]:
        """Возращает перечень книг."""

        records = []
        try:
            with open(Library.FILE_NAME, encoding="utf-8") as f:
                records = [
                    Book(**record) for record in csv.DictReader(f, delimiter=";")
                ]
        except Exception:
            # не удалось открыть файл, библиотека пуста
            pass

        return records

    @staticmethod
    def output_records(records: list[Book]) -> None:
        """Отображает список книг."""

        indx = 0
        print(Library.HEADER)
        for record in records:
            indx += 1
            print(f"{indx:<5}", record.get_info())

    @staticmethod
    def show_all_books():
        """Вывод данных библиотеки."""

        records = Library.get_records()
        if not records:
            print("Нет данных")
        else:
            Library.output_records(records)

    @staticmethod
    def get_non_empty_value(text: str, value: str) -> str:
        """Получение не пустого значения, имитация "обязательного" поля."""

        while not value:
            value = input(text).strip()
        return value

    @staticmethod
    def get_non_empty_value_int(
        text: str, value, min_value: int = None, max_value: int = None
    ) -> str:
        """Получение не пустого значения, имитация "обязательного" поля."""

        while not value:
            try:
                value = int(input(text).strip())
                if value:
                    if min_value and value < min_value:
                        raise BadMinValue
                    if max_value and value > max_value:
                        raise BadMaxValue
            except BadMinValue:
                value = None
                print(f"Значение не может быть меньше {min_value}")
            except BadMaxValue:
                value = None
                print(f"Значение не может быть больше {max_value}")
            except ValueError:
                value = None
                print("Ошибка, введите число")
        return value

    @staticmethod
    def get_select_items_menu(menu: dict, text: str, convert: bool = True) -> list[int]:
        """Обработка выбора пользователя из предоставленного меню."""

        while True:
            sel = []
            try:
                inpt = input(text).strip()
                if not inpt:
                    continue

                for item in inpt.split():
                    if convert:
                        item = int(item)

                    if item in menu:
                        sel.append(item)
                    else:
                        raise KeyError("Некорректный ключ")

                return sel

            except (ValueError, KeyError):
                print(
                    "Выберите действительное значение",
                )

    @staticmethod
    def add_book():
        """Добавление новой записи."""

        while True:
            print("\nВведите следующие данные:")
            title, author, year = None, None, None
            title = Library.get_non_empty_value("Название:", title)
            author = Library.get_non_empty_value("Автор:", author)
            # будем отсчитывать мин год от книги "Слово о полку Игореве"
            year = Library.get_non_empty_value_int(
                "Год:", year, min_value=1185, max_value=datetime.now().year
            )

            obj = Book(getrandbits(32), title, author, year, Status.in_stock.value)

            file_exist = os.path.exists(Library.FILE_NAME)

            with open(Library.FILE_NAME, encoding="utf-8", mode="a+") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=list(obj.__dict__.keys()),
                    quoting=csv.QUOTE_NONE,
                    delimiter=";",
                    dialect=csv.unix_dialect,
                )
                if not file_exist:
                    writer.writeheader()
                writer.writerow(asdict(obj))

            sel = Library.get_select_items_menu(
                {"y": None, "n": None},
                "\nВвести еще одну запись(y/n)?: ",
                convert=False,
            )

            if sel[0] == "n":
                break

    @staticmethod
    def delete_book():
        """Удаление книги."""

        # выведем все записи, для выбора
        records = Library.get_records()
        if not records:
            print("Отсутствуют записи для удаления")
            return

        Library.output_records(records)

        # получим выбор пользователя
        sel = Library.get_select_items_menu(
            {int(rec.id): None for rec in records},
            "\nВыберите id записи для удаления: ",
        )

        shablon = Book(id=sel[0])
        obj_del = None
        for indx, rec in enumerate(records):
            if rec == shablon:
                obj_del = records.pop(indx)
                exit

        if not obj_del:
            print("Не найдены данные для удаления")
            return
        else:
            print("Книга удалена")

        # сохраним изменения
        with open(Library.FILE_NAME, encoding="utf-8", mode="w") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=list(records[0].__dict__.keys()),
                quoting=csv.QUOTE_NONE,
                delimiter=";",
                dialect=csv.unix_dialect,
            )
            writer.writeheader()
            for rec in records:
                writer.writerow(asdict(rec))

    @staticmethod
    def change_status():
        """Изменить статус."""

        # выведем все записи, для выбора
        records = Library.get_records()
        if not records:
            print("Отсутствуют записи для изменения")
            return

        Library.output_records(records)

        while True:
            # получим выбор пользователя
            sel = Library.get_select_items_menu(
                {i + 1: None for i in range(len(records))},
                "\nВыберите номер записи для изменения: ",
            )

            obj = records[sel[0] - 1]
            # выберем что меняем
            print("\nКакой статус установить:")
            indx = 0
            status_dict = {}
            for status in Status:
                indx = indx + 1
                status_dict[indx] = status.value
                print(f"{indx:1}: {status.value}")

            sel = Library.get_select_items_menu(
                status_dict,
                "\nВыберите номер: ",
            )

            obj.status = status_dict[sel[0]]

            sel = Library.get_select_items_menu(
                {"y": None, "n": None},
                "\nИзменить другую запись(y/n)?: ",
                convert=False,
            )

            if sel[0] == "n":
                break

        # сохраним изменения
        with open(Library.FILE_NAME, encoding="utf-8", mode="w") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=list(records[0].__dict__.keys()),
                quoting=csv.QUOTE_NONE,
                delimiter=";",
                dialect=csv.unix_dialect,
            )
            writer.writeheader()
            for rec in records:
                writer.writerow(asdict(rec))

    @staticmethod
    def search_book():
        """Поиск книг по параметрам."""

        records = Library.get_records()
        if not records:
            print("Нет данных, нечего искать")
        else:
            while True:
                print("\nВыберите критерии поиска:", "\n")
                for key, item in Library.RECORD_MENU_KEY.items():
                    print(key, "-", Library.RECORD_MENU_TEXT[item])
                print("Можно выбрать несколько пунктов, через пробел")

                sel_items = Library.get_select_items_menu(
                    Library.RECORD_MENU_KEY, "\nВыберите пункт(ы) меню: "
                )

                #  сформируем перечень пунктов для заполнения
                dict_search = {}
                for item in sel_items:
                    dict_search[Library.RECORD_MENU_KEY[item]] = None

                for item in dict_search:
                    dict_search[item] = input(
                        f"Введите {Library.RECORD_MENU_TEXT[item]}: "
                    )

                result = []
                shablon = Book(**dict_search)
                result = [rec for rec in records if rec == shablon]

                print(f"\nНайдено {len(result)} соответствий:")
                if len(result):
                    Library.output_records(result)

                sel = Library.get_select_items_menu(
                    {"y": None, "n": None},
                    "\nХотите продолжить поиск(y/n)?: ",
                    convert=False,
                )

                if sel[0] == "n":
                    break

    @staticmethod
    def show_menu():
        """Вывод меню и вызов обработчика для пункта меню."""

        while True:
            print("\nБиблиотека, возможные операции:", "\n")
            for key, item in Library.MAIN_MENU.items():
                print(key, "-", item[0])
            print("")

            try:
                result = int(input("Выберите пункт меню: ").strip())
                if not result:
                    break

                getattr(globals()["Library"], Library.MAIN_MENU[result][1])()
            except ValueError:
                print(
                    "Выберите действительное значение",
                )
            except Exception:
                print("Что то пошло нет так: ")
                break


if __name__ == "__main__":
    Library.show_menu()
