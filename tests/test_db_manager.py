from typing import Generator

import pytest

from src.db_manager import DBManager


@pytest.fixture(scope='module')
def db() -> Generator[DBManager, None, None]:
    # Настройте параметры для вашей тестовой базы данных
    db = DBManager(
        dbname='hh_test_db',
        user='postgres',
        password='12Reg369!',
        host='localhost',
        port=5432
    )
    db.create_tables()
    # Очистка таблиц перед тестами
    with db.conn.cursor() as cur:
        cur.execute("TRUNCATE vacancies, companies RESTART IDENTITY CASCADE;")
    yield db
    # Очистка после тестов
    with db.conn.cursor() as cur:
        cur.execute("TRUNCATE vacancies, companies RESTART IDENTITY CASCADE;")
    db.close()


def test_insert_and_get_companies_and_vacancies_count(db: DBManager):
    company_id = db.insert_company('test_hh_id', 'TestCompany')
    assert isinstance(company_id, int)

    count_list = db.get_companies_and_vacancies_count()
    assert any(name == 'TestCompany' for name, _ in count_list)


def test_insert_and_get_all_vacancies(db: DBManager):
    company_id = db.insert_company('test_hh_id2', 'TestCompany2')
    vacancy = {
        'name': 'Python Developer',
        'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
        'alternate_url': 'http://example.com/vacancy1'
    }
    db.insert_vacancy(company_id, vacancy)

    vacancies = db.get_all_vacancies()
    assert any('Python Developer' in v for v in [vac[1] for vac in vacancies])


def test_get_avg_salary(db: DBManager):
    avg_salary = db.get_avg_salary()
    assert avg_salary is None or isinstance(avg_salary, float)


def test_get_vacancies_with_higher_salary(db: DBManager):
    results = db.get_vacancies_with_higher_salary()
    assert isinstance(results, list)


def test_get_vacancies_with_keyword(db: DBManager):
    results = db.get_vacancies_with_keyword('python')
    assert isinstance(results, list)
