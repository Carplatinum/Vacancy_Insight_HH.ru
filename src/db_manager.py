from typing import List, Optional, Tuple

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DBManager:
    def __init__(self, dbname: str, user: str, password: str,
                 host: str = 'localhost', port: int = 5432) -> None:
        """
        Инициализация подключения к базе данных.

        Args:
            dbname (str): Имя базы данных.
            user (str): Пользователь базы данных.
            password (str): Пароль пользователя.
            host (str, optional): Хост базы данных. Defaults to 'localhost'.
            port (int, optional): Порт базы данных. Defaults to 5432.
        """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = True

    @staticmethod
    def create_database(dbname: str, user: str, password: str,
                        host: str = 'localhost', port: int = 5432) -> None:
        """
        Создает базу данных, если она не существует.

        Args:
            dbname (str): Имя базы данных.
            user (str): Пользователь базы данных.
            password (str): Пароль пользователя.
            host (str, optional): Хост базы данных. Defaults to 'localhost'.
            port (int, optional): Порт базы данных. Defaults to 5432.
        """
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f'CREATE DATABASE "{dbname}";')
                print(f"База данных '{dbname}' создана.")
            else:
                print(f"База данных '{dbname}' уже существует.")
        conn.close()

    def create_tables(self) -> None:
        """
        Создает таблицы companies и vacancies, если они не существуют.
        """
        sql = """
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            hh_id VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            company_id INTEGER REFERENCES companies(id),
            name VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            salary_currency VARCHAR(10),
            url TEXT NOT NULL
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(sql)
        print("Таблицы созданы или уже существуют.")

    def insert_company(self, hh_id: str, name: str) -> int:
        """
        Вставляет компанию или обновляет, возвращает id компании.

        Args:
            hh_id (str): Идентификатор компании hh.ru.
            name (str): Название компании.

        Returns:
            int: ID компании в БД.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO companies (hh_id, name)
                VALUES (%s, %s)
                ON CONFLICT (hh_id) DO UPDATE SET name = EXCLUDED.name
                RETURNING id;
                """,
                (hh_id, name)
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("Не удалось получить ID компании после вставки")
            return row[0]

    def insert_vacancy(self, company_id: int, vacancy: dict) -> None:
        """
        Вставляет вакансию, если её нет.

        Args:
            company_id (int): ID компании в БД.
            vacancy (dict): Словарь с данными вакансии.
        """
        salary = vacancy.get('salary')
        salary_from = salary.get('from') if salary else None
        salary_to = salary.get('to') if salary else None
        salary_currency = salary.get('currency') if salary else None
        name = vacancy.get('name')
        url = vacancy.get('alternate_url')

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vacancies (company_id, name, salary_from, salary_to, salary_currency, url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """,
                (company_id, name, salary_from, salary_to, salary_currency, url)
            )

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список компаний и количество вакансий у каждой компании.

        Returns:
            List[Tuple[str, int]]: Список кортежей (название компании, количество вакансий).
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(v.id)
                FROM companies c
                LEFT JOIN vacancies v ON c.id = v.company_id
                GROUP BY c.name
                ORDER BY c.name;
            """)
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """
        Получает список всех вакансий с деталями.

        Returns:
            List[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
            Кортежи с данными (название компании, название вакансии, зарплата от, зарплата до, валюта, ссылка).
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.name, v.salary_from, v.salary_to, v.salary_currency, v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.id
                ORDER BY c.name, v.name;
            """)
            return cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        """
        Рассчитывает среднюю зарплату по вакансиям с указанным диапазоном.

        Returns:
            Optional[float]: Средняя зарплата или None, если данных нет.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((salary_from + salary_to) / 2.0)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
            """)
            row = cur.fetchone()
            return row[0] if row and row[0] is not None else None

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """
        Получает вакансии с зарплатой выше средней.

        Returns:
            List[Tuple[str, str, Optional[int], Optional[int], str]]:
            Кортежи с данными (название компании, название вакансии, зарплата от, зарплата до, ссылка).
        """
        avg_salary = self.get_avg_salary()
        if avg_salary is None:
            return []
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.id
                WHERE ((v.salary_from + v.salary_to) / 2.0) > %s
                ORDER BY ((v.salary_from + v.salary_to) / 2.0) DESC;
            """, (avg_salary,))
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, str]]:
        """
        Получает вакансии, в названии которых содержится ключевое слово.

        Args:
            keyword (str): Ключевое слово для поиска.

        Returns:
            List[Tuple[str, str, str]]: Кортежи с данными (название компании, название вакансии, ссылка).
        """
        pattern = f'%{keyword.lower()}%'
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.name, v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.id
                WHERE LOWER(v.name) LIKE %s
                ORDER BY c.name, v.name;
            """, (pattern,))
            return cur.fetchall()

    def close(self) -> None:
        """
        Закрывает соединение с базой данных.
        """
        self.conn.close()

    def __enter__(self) -> "DBManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
