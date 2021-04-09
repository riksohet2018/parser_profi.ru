import pandas as pd
import pymysql

con = pymysql.connect('g982255e.beget.tech', 'g982257e_iot', 'Pablo228', 'g982257e_iot')
# self.con = pymysql.connect(config.DB_HOST, config.DB_USERNAME, config.DB_PASSWORD, config.DB_NAME)

def main():
    cursor = con.cursor()

    # Читаем собранные данные
    df = pd.read_csv('data.csv', sep=',', encoding='utf-8')
    # Проходимся по всем наблюдениям
    for item in range(len(df)):
        row = df.loc[item].to_dict()

        fullname_value = row['Fullname']
        rate_value = int(row['CountRate'])
        rate_value2 = float(row['TotalRate'])
        rate_value3 = float(row['FiveRate'])
        rate_value4 = float(row['FourRate'])
        rate_value5 = float(row['ThreeRate'])
        rate_value6 = float(row['TwoRate'])
        rate_value7 = float(row['OneRate'])
        subject_value = row['Subject']
        add_sub = row['AddSub']
        price = row['Price']

        # Вставляем в БД новую строку
        query = f"INSERT INTO ProfiRu (fullname,countRate,totalRate,fiveRate," \
                f"fourRate,threeRate,twoRate,oneRate, subject) VALUES " \
                f"('{fullname_value}', '{rate_value}', '{rate_value2}', " \
                f"'{rate_value3}', '{rate_value4}','{rate_value5}'," \
                f"'{rate_value6}','{rate_value7}', '{subject_value}'," \
                f"'{add_sub}','{price}')"
        cursor.execute(query)

        print(f"{item + 1} is ready")

    con.commit()
    con.close()

if __name__ == '__main__':
    main()
