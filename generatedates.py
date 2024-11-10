#!/bin/python3

from datetime import datetime, timedelta

# Počáteční a koncové datum
start_date = datetime.strptime("01-07-2024", "%d-%m-%Y")
end_date = datetime.strptime("17-12-2024", "%d-%m-%Y")

# Generování seznamu dat
date_list = []
current_date = start_date
while current_date <= end_date:
    date_list.append(current_date.strftime("%d-%m-%Y"))
    current_date += timedelta(days=1)


# Uložení do souboru
with open("done.csv", "w") as file:
    file.write('date;state;link;souhrn;diplomacie;ekonomika;tresnicka;\n')

    exit(0)

    for date in date_list:
        file.write(f'{date};no; ; ; ; ;\n')