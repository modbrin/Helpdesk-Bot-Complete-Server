import os
import requests
import json
import xlwt

FOLDER_NAME = 'user_statistics'
FILE_NAME = 'actual_data'


def get_width(num_characters):
    return int((1 + num_characters) * 256)


def update():
    book = xlwt.Workbook(encoding="utf-8")

    xlwt.add_palette_colour("custom_colour", 0x21)
    book.set_colour_RGB(0x21, 251, 228, 228)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')

    sheet = book.add_sheet("User Activation Statistics", cell_overwrite_ok=True)

    sheet.write(0, 0, "Email", style)
    sheet.write(0, 1, "Activation Dates", style)
    row_number = 1

    users = requests.get("http://127.0.0.1:8000/db/users/").json()

    max_length_1 = 10
    max_length_2 = 10
    for user in users:
        email = user['email'] + "@innopolis.ru"
        if len(email) > max_length_1:
            max_length_1 = len(email)
        try:
            dates = json.loads(user['activationDate'])
        except Exception:
            dates = []
        sheet.write(row_number, 0, email)
        for date in dates:
            sheet.write(row_number, 1, date)
            row_number += 1
            if len(date) > max_length_2:
                max_length_2 = len(date)
        if not dates:
            row_number += 1
    sheet.col(0).width = get_width(max_length_1)
    sheet.col(1).width = get_width(max_length_2)

    if not os.path.exists(FOLDER_NAME):
        os.makedirs(FOLDER_NAME)
    if os.path.exists(FOLDER_NAME + "/" + FILE_NAME + ".xls"):
        os.remove(FOLDER_NAME + "/" + FILE_NAME + ".xls")

    book.save(FOLDER_NAME + "/" + FILE_NAME + ".xls")
update()