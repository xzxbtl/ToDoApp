import sys
import time
import flet as ft
import sqlite3
from ctypes import *
from flet_core import Column, \
    MainAxisAlignment, Row, Text, IconButton, icons, Divider, UserControl, Container, ClipBehavior, border

font_path = r"windowslocker/assets/fonts/OpenSans-SemiBold.ttf"


class DataBase:
    @staticmethod
    def ConnectToDatabase():
        """Подключение к базе данных SQLite."""
        try:
            db = sqlite3.connect('base.sqlite3')
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS todo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    Task VARCHAR(255) NOT NULL, 
                    Count INTEGER NOT NULL
                )
            """)
            db.commit()
            return db
        except Exception as err:
            print(f"Ошибка подключения к базе данных: {err}")
            return None

    @staticmethod
    def ReadDataBase(db):
        """Чтение всех записей из таблицы todo."""
        c = db.cursor()
        c.execute("SELECT Task, Count FROM todo")
        rec = c.fetchall()
        return rec

    @staticmethod
    def InsertDataBase(db, values):
        """Добавление новой записи в таблицу todo."""
        c = db.cursor()
        c.execute("INSERT INTO todo (Task, Count) VALUES (?, ?)", values)
        db.commit()

    @staticmethod
    def DeleteDataBase(db, value):
        """Удаление записи из таблицы todo по Task и Count."""
        c = db.cursor()
        c.execute("DELETE FROM todo WHERE Task = ? AND Count = ?", value)
        db.commit()


class CreateTask(UserControl):
    def __init__(self, task: str, count: str, func1, func2, func3):
        self.task = task
        self.count = count
        self.func1 = func1
        self.func2 = func2
        self.func3 = func3
        super().__init__()

    def TaskDeleteEdit(self, name, color, func):
        return IconButton(
            icon=name,
            width=30,
            icon_size=18,
            icon_color=color,
            opacity=0,
            animate_opacity=200,
            on_click=lambda e: func(self.GetContainerInstance()),
        )

    def GetContainerInstance(self):
        return self

    def ShowIcons(self, e):
        delete_icon = e.control.content.controls[1].controls[0]
        edit_icon = e.control.content.controls[1].controls[1]
        check_icon = e.control.content.controls[1].controls[2]
        if e.data == "true":
            delete_icon.opacity = 1
            edit_icon.opacity = 1
            check_icon.opacity = 1
        else:
            delete_icon.opacity = 0
            edit_icon.opacity = 0
            check_icon.opacity = 0
        self.update()

    def build(self):
        return Container(
            width=750,
            height=100,
            border=border.all(0.85, "white54"),
            border_radius=8,
            on_hover=lambda e: self.ShowIcons(e),
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=10,
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(value=self.task, size=24),
                            Text(value=self.count, size=22, color="white54"),
                        ],
                    ),
                    Row(
                        spacing=0,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            self.TaskDeleteEdit(ft.icons.CHECK_CIRCLE_ROUNDED, 'green700', self.func3),
                            self.TaskDeleteEdit(ft.icons.DELETE_ROUNDED, 'red500', self.func1),
                            self.TaskDeleteEdit(ft.icons.EDIT_ROUNDED, 'white70', self.func2),
                        ]
                    )
                ]
            )
        )


def main(page: ft.Page):
    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    def open_dlg_to_do(e):
        task_input.value = ""
        quantity_input.value = ""
        input_form.visible = True
        add_button.visible = True
        close_button.visible = True
        page.dialog = dlg_to_do
        dlg_to_do.open = True
        page.update()

    def close_to_do(e):
        dlg_to_do.open = False
        page.update()

    def close_to_do_edit(e):
        dlg_to_do_edit.open = False
        page.update()

    def added_to_do(e):
        task_name = task_input.value
        task_quantity = quantity_input.value
        db = DataBase.ConnectToDatabase()
        DataBase.InsertDataBase(db, (task_name, task_quantity))
        db.close()
        _main_column_.controls.append(
            CreateTask(
                task_name,
                task_quantity,
                DeleteFunc,
                EditFunc,
                StartFunc,
            )
        )
        input_form.visible = False
        add_button.visible = False
        dlg_to_do.open = False
        page.update()

    def DeleteFunc(e):
        _main_column_.controls.remove(e)
        _main_column_.update()

    def EditFunc(e):
        task_input_edit.value = e.task
        quantity_input_edit.value = e.count
        input_form_edit.visible = True
        edit_button.visible = True
        close_button_edit.visible = True
        page.dialog = dlg_to_do_edit
        dlg_to_do_edit.open = True
        page.update()

    def edit_apply(e):
        dlg_to_do_edit.open = False
        page.update()

    def StartFunc(e):
        page.dialog = dlg
        dlg.open = True

        page.update()

        while True:
            windll.user32.BlockInput(True)
            time.sleep(10)
            windll.user32.BlockInput(False)
            break

        dlg.open = False
        _main_column_.controls.remove(e)
        _main_column_.update()
        page.update()

    task_input = ft.TextField(label="Название задачи")
    task_input_edit = ft.TextField(label="Название задачи")
    quantity_input_edit = ft.TextField(label="Количество", keyboard_type=ft.KeyboardType.NUMBER)
    quantity_input = ft.TextField(label="Количество", keyboard_type=ft.KeyboardType.NUMBER)
    input_form = ft.Column(
        [
            task_input,
            quantity_input,
        ],
        visible=False
    )
    input_form_edit = ft.Column(
        [
            task_input_edit,
            quantity_input_edit,
        ],
        visible=False
    )
    add_button = ft.ElevatedButton("Добавить",
                                   on_click=added_to_do,
                                   visible=False,
                                   color="#ffffff",
                                   bgcolor="#21db56")
    close_button = ft.ElevatedButton("Выйти", on_click=close_to_do,
                                     visible=False,
                                     color="#ffffff",
                                     bgcolor="#ff3636")
    edit_button = ft.ElevatedButton("Изменить",
                                    on_click=edit_apply,
                                    visible=False,
                                    color="#ffffff",
                                    bgcolor="#21db56")
    close_button_edit = ft.ElevatedButton("Выйти", on_click=close_to_do_edit,
                                          visible=False,
                                          color="#ffffff",
                                          bgcolor="#ff3636")

    dlg = ft.AlertDialog(
        title=ft.Text("Вы начали выполнение задачи \n В течении 5 минут доступ к пк ограничен")
    )

    dlg_to_do = ft.AlertDialog(
        modal=True,
        title=ft.Text("Добавить задачу"),
        content=ft.Column(
            [
                input_form,
                Row(
                    [
                        ft.Column(),
                        add_button,
                        close_button
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            spacing=230,
        ),
    )
    dlg_to_do_edit = ft.AlertDialog(
        modal=True,
        title=ft.Text("Изменить задачу"),
        content=ft.Column(
            [
                input_form_edit,
                Row(
                    [
                        ft.Column(),
                        edit_button,
                        close_button_edit
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            spacing=230,
        ),
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cоздание Заметки"),
        content=ft.Text("Вы точно желаете создать заметку?"),
        actions=[
            ft.TextButton("Да", on_click=open_dlg_to_do),
            ft.TextButton("Нет", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.title = "TO-DO"
    page.window_resizable = False
    page.window_center()
    page.window_height = 600
    page.window_width = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.auto_scroll = True
    page.fonts = {
        "OpenSans": font_path
    }
    _main_column_ = Column(
        scroll="hidden",
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Text(
                        "To-Do Items",
                        size=30,
                        font_family="OpenSans",
                        weight="bold"
                    ),
                    IconButton(
                        icons.ADD_CIRCLE_ROUNDED,
                        icon_size=48,
                        on_click=open_dlg_modal
                    )
                ]
            ),
            Divider(height=8, color="white24")
        ]
    )

    page.add(_main_column_)
    page.update()

    db = DataBase.ConnectToDatabase()
    for task in DataBase.ReadDataBase(db):
        print(task)


"""ЗАПУСК СКРИПТА ОТ АДМИНА"""


def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False


if is_admin():
    sys.coinit_flags = 2
    pass
else:
    sys.coinit_flags = 2
    windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit(0)

if __name__ == "__main__":
    ft.app(target=main)
