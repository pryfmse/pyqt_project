import sys
import sqlite3
from Успеваемость import Ui_Form

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QInputDialog, QMessageBox


class Project(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ПРОЕКТ главное.ui', self)  # Загружаем дизайн
        self.setWindowTitle('Fast learn')
        self.btn_start.clicked.connect(self.less)
        self.btn_res.clicked.connect(self.result)
        self.con = sqlite3.connect('ПРОЕКТ_уроки')
        self.cur = self.con.cursor()
        [self.names.addItem(i[0]) for i in self.cur.execute("SELECT имя_пользователя FROM пользователи")]
        self.btn_avatar.clicked.connect(self.avatar)
        self.original = False
        self.btn_add.clicked.connect(self.input)
        self.table = self.names.currentText() + '_answers'

        self.foto = self.cur.execute(f"SELECT фото FROM пользователи"
                                     f" WHERE таблица_пользователя = '{self.table}'").fetchone()
        if self.foto:
            with open('data.png', 'wb') as file:
                file.write(self.foto[0])
            self.photo.setPixmap(QPixmap(QImage('data.png')))

        else:
            self.photo.setPixmap(QPixmap())

        self.names.currentIndexChanged.connect(self.on_combo_box_activated)

    def less(self):
        self.lesson = Lessons(self.table)
        self.lesson.show()

    def result(self):
        self.res = Results(self.table)
        self.res.show()

    def avatar(self):  # загружать аватары в баз
        self.fname = QFileDialog.getOpenFileName(self, 'Выберите картинку', '')[0]
        self.original = QImage(self.fname)
        self.imagePixmap = QPixmap(self.original)
        try:
            with open(self.fname, 'rb') as file:
                data = file.read()
                file.close()
        except Exception:
            pass

        self.cur.execute("UPDATE пользователи SET фото = ? WHERE таблица_пользователя = ?", (data, self.table))
        self.con.commit()

        self.photo.setPixmap(self.imagePixmap)

    def input(self):  # введние нового пользователя
        name, ok_pressed = QInputDialog.getText(self, "Введите имя нового пользователя",
                                                "Как тебя зовут?")
        if ok_pressed:
            self.names.addItem(name)
            self.table = name + '_answers'
            try:
                self.cur.execute(f"""CREATE TABLE {name}_answers (
                id         INTEGER UNIQUE,    task1,    task2,    answer3_1,   answer3_2,    answer3_3,
                            task4,   code5_1,    code5_2,    code5_3,    code5_4)""")
            except Exception:
                pass
            self.cur.execute(f"INSERT INTO {self.table}(id) VALUES (1), (2), (3), (4), (5), (6), (7), (8)")
            self.cur.execute(f"""INSERT INTO пользователи(имя_пользователя, таблица_пользователя)
             VALUES ('{name}', '{self.table}')""")
            self.con.commit()

    def on_combo_box_activated(self):
        self.table = self.names.currentText() + '_answers'
        self.foto = self.cur.execute(f"SELECT фото FROM пользователи"
                                     f" WHERE таблица_пользователя = '{self.table}'").fetchone()
        if self.foto[0]:
            with open('data.png', 'wb') as file:
                file.write(self.foto[0])
            self.photo.setPixmap(QPixmap(QImage('data.png')))
        else:
            self.photo.setPixmap(QPixmap())


class Lessons(QWidget):
    def __init__(self, table):
        super(Lessons, self).__init__()
        self.table = table
        uic.loadUi('ПРОЕКТ уроки.ui', self)  # Загружаем дизайн
        self.setWindowTitle('Fast learn. Lessons')
        self.con = sqlite3.connect('ПРОЕКТ_уроки')
        self.cur = self.con.cursor()
        self.out_lesons = self.cur.execute(f"SELECT * FROM пользователи"
                                           f" WHERE таблица_пользователя = '{self.table}'").fetchone()

        btns = [self.btn1, self.btn2, self.btn3, self.btn4, self.btn5, self.btn6, self.btn7, self.btn8]
        n = 0
        for i in range(8):
            if self.out_lesons[i + 3]:
                j = btns[i]
                j.setText('Выполнено')
                n += 1
        self.lessons_count.setText(str(n))
        for i in [self.btn1, self.btn2, self.btn3, self.btn4, self.btn5, self.btn6, self.btn7, self.btn8]:
            i.clicked.connect(self.lesson)

    def lesson(self):
        self.l = Teoria(self.sender().objectName(), self.table)
        self.l.show()


class Results(QWidget, Ui_Form):
    def __init__(self, table):
        super(Results, self).__init__()
        self.table = table
        self.con = sqlite3.connect('ПРОЕКТ_уроки')
        self.cur = self.con.cursor()
        self.res = self.cur.execute(f"SELECT * FROM пользователи WHERE таблица_пользователя = '{self.table}'")
        self.res = list(*self.res)[-8:]
        self.setupUi(self)

        self.progressBar.setValue(self.res[0]) if self.res[0] else True
        self.progressBar_2.setValue(self.res[1]) if self.res[1] else True
        self.progressBar_8.setValue(self.res[2]) if self.res[2] else True
        self.progressBar_7.setValue(self.res[3]) if self.res[3] else True
        self.progressBar_6.setValue(self.res[4]) if self.res[4] else True
        self.progressBar_5.setValue(self.res[5]) if self.res[5] else True
        self.progressBar_4.setValue(self.res[6]) if self.res[6] else True
        self.progressBar_3.setValue(self.res[7]) if self.res[7] else True
        self.setWindowTitle('Fast learn. Results')

        # Загрузить результаты в статус бары циклом, находя процент правильных решений
        self.table.plot([i for i in range(1, 9)],
                        [int(i.value()) for i in [self.progressBar, self.progressBar_2,
                                                  self.progressBar_8, self.progressBar_7,
                                                  self.progressBar_6, self.progressBar_5,
                                                  self.progressBar_4, self.progressBar_3]], pen='r')


class Teoria(QWidget):
    def __init__(self, now, table):
        super(Teoria, self).__init__()
        uic.loadUi('ПРОЕКТ теория.ui', self)  # Загружаем дизайн
        self.now = now
        self.table = table
        tema = {1: 'Структура и первые программы', 2: 'Переменные и типы данных', 3: 'Математические операции',
                4: 'Условные конструкции', 5: 'Конструкция SWITCH', 6: 'Циклы while', 7: 'Циклы for',
                8: 'Контрольная точка'}
        self.label.setText(tema[int(self.now[-1])])

        with open('my progress.txt', 'w', encoding='utf8') as f:
            f.write(tema[int(self.now[-1])])

        con = sqlite3.connect('ПРОЕКТ_уроки')
        cur = con.cursor()
        text = cur.execute(f"""SELECT теория FROM teory WHERE id = {int(self.now[-1])}""").fetchone()
        code1 = cur.execute(f"""SELECT код FROM teory WHERE id = {int(self.now[-1])}""").fetchone()
        code2 = cur.execute(f"""SELECT код2 FROM teory WHERE id = {int(self.now[-1])}""").fetchone()
        code1 = [*code1][0]
        code1 = code1.split('&')
        code2 = [*code2][0]
        code2 = code2.split('&')
        text = [*text][0]
        text = text.split('&')

        self.setWindowTitle(f"Fast learn. Lesson{int(self.now[-1])}")
        self.code1.setFont(QFont("Courier New", 12))
        self.code2.setFont(QFont("Courier New", 12))
        self.teory.setFont(QFont("Times new roman", 16))
        self.teory.setStyleSheet("color: white;")
        self.code1.setStyleSheet("color: white;")
        self.code2.setStyleSheet("color: white;")
        self.code1.setText('\n'.join(code1))
        self.code2.setText('\n'.join(code2))
        self.teory.setText('\n'.join(text))
        self.code1.setReadOnly(True)
        self.code2.setReadOnly(True)
        self.teory.setReadOnly(True)
        self.to_practika.clicked.connect(self.do)

    def do(self):
        self.p = Practice(self.now, self.table)
        self.p.show()


class Practice(QWidget):
    def __init__(self, now, table):
        super(Practice, self).__init__()
        uic.loadUi('ПРОЕКТ тесты.ui', self)  # Загружаем дизайн
        self.now = now
        self.table = table
        self.setWindowTitle(f"Fast learn. Practice{int(self.now[-1])}")
        con = sqlite3.connect('ПРОЕКТ_уроки')
        cur = con.cursor()
        self.tasks = cur.execute(f"""SELECT * FROM test WHERE id = {int(self.now[-1])}""").fetchone()
        self.task1.setReadOnly(True)
        self.task1.setText(self.tasks[1])
        self.radioBTN1_1.setText(str(self.tasks[2]))
        self.radioBTN1_2.setText(str(self.tasks[3]))
        self.radioBTN1_3.setText(str(self.tasks[4]))
        self.task2.setText(self.tasks[5])
        self.code2.setText('\n'.join(self.tasks[6].split('&')))
        self.code2.setReadOnly(True)
        self.task2_2.setText(self.tasks[7])
        self.task2_2.setReadOnly(True)
        self.task3_1.setText(self.tasks[8])
        self.task3_2.setText(self.tasks[9])
        self.task3_3.setText(self.tasks[10])
        self.task3_4.setText(self.tasks[11])
        self.answer3_1.addItem(self.tasks[12])
        self.answer3_1.addItem(self.tasks[13])
        self.answer3_1.addItem(self.tasks[14])
        self.answer3_2.addItem(self.tasks[15])
        self.answer3_2.addItem(str(self.tasks[16]))
        self.answer3_2.addItem(str(self.tasks[17]))
        self.answer3_3.addItem(self.tasks[18])
        self.answer3_3.addItem(self.tasks[19])
        self.answer3_3.addItem(self.tasks[20])
        self.task4.setText(self.tasks[21])
        self.task4.setReadOnly(True)
        self.btn4_1.setText(self.tasks[22])
        self.btn4_2.setText(self.tasks[23])
        self.btn4_3.setText(str(self.tasks[24]))
        self.btn4_4.setText(str(self.tasks[25]))
        self.task5.setText(self.tasks[26])
        self.task5.setReadOnly(True)
        self.task5_1.setText(self.tasks[27])
        self.task5_2.setText(self.tasks[28])
        self.task5_3.setText(self.tasks[29])
        self.task5_4.setText(self.tasks[30])
        self.task5_5.setText(self.tasks[31])
        self.task5_6.setText(self.tasks[32])

        self.con = sqlite3.connect('ПРОЕКТ_уроки')
        self.cur = self.con.cursor()
        self.cur.execute(f"DELETE FROM пользователь_answers WHERE id = {int(self.now[-1])}")
        self.cur.execute(f"INSERT INTO пользователь_answers(id) VALUES ({int(self.now[-1])})")
        self.con.commit()
        self.string = self.cur.execute(f"SELECT * FROM {self.table} WHERE id = {int(self.now[-1])}")
        self.string = list(*self.string)
        for i in [self.btn1, self.btn2, self.btn3, self.btn4_1, self.btn4_2, self.btn4_3, self.btn4_4, self.btn5]:
            i.clicked.connect(self.handler)

    def handler(self):
        try:
            btn = self.sender().objectName()

            if btn == 'btn1':
                self.cur.execute(f"UPDATE {self.table} SET task1 = '{self.RadioBTNGroup.checkedButton().text()}'"
                             f" WHERE id = {int(self.now[-1])}")

            elif btn == 'btn2':
                self.cur.execute(f"UPDATE {self.table} SET task2 = '{self.answer2.text()}'"
                                 f" WHERE id = {int(self.now[-1])}")

            elif btn == 'btn3':
                self.cur.execute(f"UPDATE {self.table} SET answer3_1 = '{self.answer3_1.currentText()}'"
                                 f" WHERE id = {int(self.now[-1])}")
                self.cur.execute(f"UPDATE {self.table} SET answer3_2 = '{self.answer3_2.currentText()}'"
                                 f" WHERE id = {int(self.now[-1])}")
                self.cur.execute(f"UPDATE {self.table} SET answer3_3 = '{self.answer3_3.currentText()}'"
                                 f" WHERE id = {int(self.now[-1])}")

            elif btn == 'btn4_1' or btn == 'btn4_2' or btn == 'btn4_3' or btn == 'btn4_4':
                i = self.btn4_1 if btn == 'btn4_1' else self.btn4_2\
                    if btn == 'btn4_2' else self.btn4_3 if btn == 'btn4_3' else self.btn4_4
                self.cur.execute(f"UPDATE {self.table} SET task4 = '{i.text()}' WHERE id = {int(self.now[-1])}")

            elif btn == 'btn5':
                self.cur.execute(f"UPDATE {self.table} SET code5_1 = '{self.answer5_1.text()}'"
                                 f" WHERE id = {int(self.now[-1])}")
                self.cur.execute(f"UPDATE {self.table} SET code5_2 = '{self.answer5_2.text()}'"
                                 f" WHERE id = {int(self.now[-1])}")
                self.cur.execute(f"UPDATE {self.table} SET code5_3 = '{self.answer5_3.text()}'"
                                 f" WHERE id = {int(self.now[-1])}")
                self.cur.execute(f"UPDATE {self.table} SET code5_4 = '{self.answer5_4.text()}'"
                                 f" WHERE id = {int(self.now[-1])}")
                
        except Exception:
            pass

        self.con.commit()
        self.string = self.cur.execute(f"SELECT * FROM {self.table} WHERE id = {int(self.now[-1])}")
        self.string = list(*self.string)

        if all(self.string):
            self.end()

    def end(self):
        self.answers = self.cur.execute(f"SELECT * FROM test_answers WHERE id = {int(self.now[-1])}")
        self.answers = list(*self.answers)
        res = sum(1 for i in range(1, 9) if self.answers[i] == self.string[i])
        a = 'результат' + self.now[-1]
        self.cur.execute(f"UPDATE пользователи SET {a} = {res * 10}"
                         f" WHERE таблица_пользователя = '{self.table}'")
        self.con.commit()
        QMessageBox.question(self, '', "Процент верных решений равен " + str(res * 10),
            QMessageBox.Yes)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Project()
    ex.show()
    sys.exit(app.exec_())