from src.api_hh import (fetch_companies_and_vacancies,
                        fetch_vacancies_by_company)


def test_fetch_vacancies_by_company_valid():
    # Используйте ID реально существующей компании или мок
    vacancies = fetch_vacancies_by_company('3529')
    assert vacancies is None or isinstance(vacancies, list)


def test_fetch_vacancies_by_company_invalid():
    vacancies = fetch_vacancies_by_company('invalid_id')
    assert vacancies is None or isinstance(vacancies, list)


def test_fetch_companies_and_vacancies():
    companies = [
        {"id": "3529", "name": "СБЕР"},
        {"id": "invalid", "name": "Неизвестная"}
    ]
    data = fetch_companies_and_vacancies(companies)
    assert isinstance(data, dict)
    for cid in data:
        assert isinstance(data[cid], list)
