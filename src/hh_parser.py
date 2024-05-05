import requests
import psycopg2


def get_employees(company_name):
    """
    Получение id компании работодателя на hh.ru
    """
    url = 'https://api.hh.ru/employers'
    params = {'text': company_name}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        employers_data = response.json()
        if 'items' in employers_data and len(employers_data['items']) > 0:
            for employer in employers_data['items']:
                if employer['name'] == company_name:
                    return employer['id']
        else:
            print("Компания не найдена.")
            return None
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None


def get_employees_vacancies(employer_id):
    """
    Получение вакансии конкретной компании по id не больше 1500 вакансий
    """
    all_vacancies = []
    url = 'https://api.hh.ru/vacancies'
    page = 0
    per_page = 100  # Максимальное количество вакансий на одной странице
    while page < 20:
        params = {'employer_id': employer_id, 'per_page': per_page, 'page': page}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            vacancies_data = response.json()
            if vacancies_data['items']:
                all_vacancies.extend(vacancies_data['items'])
                page += 1
                # for vacancies in vacancies_data['items']:
                #     print(vacancies['name'])
            else:
                break  # Если больше нет вакансий, прерываем цикл
        else:
            print(f"Ошибка {response.status_code}: {response.text}")
            return None
    return all_vacancies


def save_database(company_name: str, data, database_name: str, params: dict):
    """Сохранение данных в базу данных."""

    conn = psycopg2.connect(**params)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO company (employer)
            VALUES (%s)
            RETURNING  company_id
            """,
            (company_name,)
        )
        company_id = cur.fetchone()[0]
        for vacancy_data in data:
            if vacancy_data['salary'] == None:
                cur.execute(
                    """
                    INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """,
                    (company_id, vacancy_data['name'], vacancy_data['published_at'],
                     vacancy_data['alternate_url'], 0, 0),
                )
                continue
            elif vacancy_data['salary'] != None:
                if vacancy_data['salary']['from'] != None:
                    if vacancy_data['salary']['to'] != None:
                        cur.execute(
                            """
                            INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                            VALUES (%s,%s,%s,%s,%s,%s)
                        """,
                            (company_id, vacancy_data['name'], vacancy_data['published_at'],
                             vacancy_data['alternate_url'],
                             vacancy_data['salary']['from'], vacancy_data['salary']['to'])
                        )
                        continue
                    elif vacancy_data['salary']['to'] == None:
                        cur.execute(
                            """
                            INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                            VALUES (%s,%s,%s,%s,%s,%s)
                        """,
                            (company_id, vacancy_data['name'], vacancy_data['published_at'],
                             vacancy_data['alternate_url'],
                             vacancy_data['salary']['from'], 0)
                        )
                        continue
                elif vacancy_data['salary']['to'] != None:
                    cur.execute(
                        """
                        INSERT INTO vacancy (company_id, name_vacancy, publish_date, url, salary_from, salary_to)
                        VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                        (company_id, vacancy_data['name'], vacancy_data['published_at'],
                         vacancy_data['alternate_url'],
                         0, vacancy_data['salary']['to'])
                    )
                    continue

    conn.commit()
    conn.close()