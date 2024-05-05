from src.config import config
from src.dbmanager import DBManager
from src.hh_parser import get_employees, get_employees_vacancies, save_database
from src.utils import printing


companies = ["Триал-Спорт", "Мой чай", "СТЦ", "Спортмарафон", "DPD в России", "Ozon", "ПК Лаваш", "1C-Рарус", "Delta Computers", "СБЕР"]


def main():
    params = config()
    dbmanager = DBManager('hh_vacancy', params)
    dbmanager.create_db()
    dbmanager.create_table()
    dbmanager.close_connection()

    for company_name in companies:
        employers_id = get_employees(company_name)

        if employers_id:
            print(f"Идентификатор компании '{company_name}': {employers_id}")
            all_vacancies = get_employees_vacancies(employers_id)
            if all_vacancies:
                print(f"Общее количество вакансий компании '{company_name}': {len(all_vacancies)}")

                save_database(company_name, all_vacancies, 'hh_vacancy', params)
                print("Вакансии успешно записаны в базу данных")
            else:
                print(f"Не удалось получить вакансии компании '{company_name}'.")
        else:
            print(f"Не удалось найти компанию '{company_name}'.")

    printing(dbmanager)


if __name__ == '__main__':
    main()