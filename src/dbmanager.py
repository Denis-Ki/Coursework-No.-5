import psycopg2


class DBManager:

    def __init__(self, database_name, params):
        self.params = params
        self.database_name = database_name
        self._connection = None

    def create_db(self, database_name='hh_vacancy'):
        """
        Создает базу данных
        """
        conn = psycopg2.connect(**self.params, dbname='postgres')
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
            cur.execute(f"CREATE DATABASE {database_name}")

    def create_table(self):
        """
        Создает две таблице с рабоодателем и вакансиямии связываем их по id
        """
        self.params['dbname'] = 'hh_vacancy'
        conn = psycopg2.connect(**self.params)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE company (
                    company_id SERIAL PRIMARY KEY,
                    employer VARCHAR(50) NOT NULL
                )
            """)

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE vacancy(
                    vacancy_id SERIAL PRIMARY KEY,
                    company_id INT REFERENCES company(company_id),
                    name_vacancy VARCHAR NOT NULL,
                    publish_date DATE,
                    url TEXT,
                    salary_from INTEGER,
                    salary_to INTEGER
                )
            """)
        conn.commit()
        conn.close()

    def create_connection(self):
        if self._connection is None:
            with psycopg2.connect(**self.params) as conn:
                self._connection = conn
        return self._connection

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """

        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT company.employer, COUNT(vacancy.vacancy_id) as vacancies_count
            FROM company 
            JOIN vacancy  ON company.company_id = vacancy.company_id
            GROUP BY company.employer
            ORDER BY vacancies_count DESC
            """)

        # Получение результатов
        companies_vacancies_count = cur.fetchall()
        cur.close()
        conn.close()

        return companies_vacancies_count

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.
        """

        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT employer, name_vacancy, salary_from, salary_to,url 
            FROM vacancy
            JOIN company  ON company.company_id = vacancy.company_id
            ORDER BY salary_from DESC
            """)
        all_vacancies = cur.fetchall()
        cur.close()
        conn.close()
        return all_vacancies

    def get_avg_salary(self):
        """
        Получает среднюю зарплату по вакансиям.
        """
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute(
            """
            select AVG(salary_from) from vacancy
            """)
        avg_salary = cur.fetchall()
        cur.close()
        conn.close()
        return avg_salary

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        """
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute("SELECT name_vacancy, salary_from, salary_to,"
                    "url FROM vacancy WHERE salary_from > %s", (self.get_avg_salary()), )
        vacancies = cur.fetchall()

        cur.close()
        conn.close()

        return vacancies

    def get_vacancies_with_keyword(self, name_vacancy):
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова.
        """
        conn = psycopg2.connect(**self.params)
        cur = conn.cursor()

        cur.execute("select name_vacancy, salary_from, "
                    "salary_to,url  from vacancy where name_vacancy LIKE %s", ('%' + name_vacancy + '%',))
        vacancies = cur.fetchall()
        cur.close()
        conn.close()
        return vacancies

    def close_connection(self):
        conn = self.create_connection()
        conn.close()
