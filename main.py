import os
import sys
from typing import Dict, List

from dotenv import load_dotenv

from src.api_hh import fetch_companies_and_vacancies
from src.db_manager import DBManager

load_dotenv()


def user_interface(db: DBManager) -> None:
    """
    Текстовый интерфейс взаимодействия с пользователем.

    Args:
        db (DBManager): Экземпляр класса для работы с базой данных.
    """
    while True:
        print("\nМеню:")
        print("1. Показать компании и количество вакансий")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Найти вакансии по ключевому слову")
        print("0. Выйти")
        choice = input("Выберите действие: ")

        if choice == "1":
            for company_name, count in db.get_companies_and_vacancies_count():
                print(f"{company_name}: {count}")
        elif choice == "2":
            for company, vacancy, salary_from, salary_to, currency, url in db.get_all_vacancies():
                salary_str = f"{salary_from} - {salary_to} {currency}" if salary_from and salary_to else "не указана"
                print(f"{vacancy} ({company}) - зарплата: {salary_str}\nСсылка: {url}\n")
        elif choice == "3":
            avg_salary = db.get_avg_salary()
            if avg_salary:
                print(f"Средняя зарплата по вакансиям: {avg_salary:.2f}")
            else:
                print("Средняя зарплата не рассчитана.")
        elif choice == "4":
            for company, vacancy, salary_from, salary_to, url in db.get_vacancies_with_higher_salary():
                print(f"{vacancy} ({company}) - зарплата: {salary_from} - {salary_to}\nСсылка: {url}\n")
        elif choice == "5":
            keyword = input("Введите ключевое слово: ")
            for company, vacancy, url in db.get_vacancies_with_keyword(keyword):
                print(f"{vacancy} ({company})\nСсылка: {url}\n")
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Некорректный выбор! Попробуйте снова.")


if __name__ == '__main__':
    DB_NAME: str = os.getenv('DB_NAME') or ''
    DB_USER: str = os.getenv('DB_USER') or ''
    DB_PASSWORD: str = os.getenv('DB_PASSWORD') or ''
    DB_HOST: str = os.getenv('DB_HOST') or 'localhost'
    DB_PORT: int = int(os.getenv('DB_PORT') or '5432')

    if not all([DB_NAME, DB_USER, DB_PASSWORD]):
        print("Не заданы необходимые переменные окружения: DB_NAME, DB_USER, DB_PASSWORD")
        sys.exit(1)

    DBManager.create_database(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

    with DBManager(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT) as db:
        db.create_tables()

        companies: List[Dict[str, str]] = [
            {"id": "3529", "name": "СБЕР"},
            {"id": "117712", "name": "ГСП-2"},
            {"id": "5599", "name": "Лаборатория Гемотест"},
            {"id": "1655568", "name": "Пингвин"},
            {"id": "913808", "name": "CarMoney"},
            {"id": "1466637", "name": "Davines Russia"},
            {"id": "3447886", "name": "Крекер"},
            {"id": "3383990", "name": "Жёлтый слон"},
            {"id": "1706785", "name": "Центр Афродита"},
            {"id": "2949717", "name": "Кировский Шинный Завод"},
        ]

        company_ids = {}
        for company in companies:
            company_id = db.insert_company(company['id'], company['name'])
            company_ids[company['id']] = company_id

        vacancies_data = fetch_companies_and_vacancies(companies)

        for company in companies:
            company_id = company_ids[company['id']]
            vacancies = vacancies_data.get(company['id'], [])
            for vacancy in vacancies:
                db.insert_vacancy(company_id, vacancy)

        print("Данные загружены в базу.")

        user_interface(db)
