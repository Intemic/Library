import csv
import os
from dataclasses import dataclass, asdict
from random import getrandbits


@dataclass
class Book:
    """Представляет запись о книге."""

    PRINT_TEMPLATE = "{id:15} {title:50} {author:30} {year:4} {staus:^20}"

    id: int = None
    title: str = None
    author: str = None
    year: int = None
    status: str = None

    def get_info(self) -> str:
        """Вывод записи."""
        return self.PRINT_TEMPLATE.format(**asdict(self))


class Library:
    """Класс предоставляет основную функциональность по работе с библиотекой."""

    # имя файла с данными
    FILE_NAME = "library.txt"
    # заголовок таблицы
    HEADER = "{:^15} {:^50} {:^30} {:4} {:^20}".format(
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
        3: ("Поиск книги", "find_book"),
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
    def get_non_empty_value(text: str, value: str) -> str:
        """Получение не пустого значения, имитация "обязательного" поля."""

        while not value:
            value = input(text).strip()
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
            year = Library.get_non_empty_value("Год:", year)

            obj = Book(getrandbits(32), title, author, year)

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
