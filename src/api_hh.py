from typing import Any, Dict, List, Optional, Union

import requests


def fetch_vacancies_by_company(company_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Получает список вакансий для заданной компании с hh.ru.

    Args:
        company_id (str): Идентификатор компании hh.ru.

    Returns:
        Optional[List[Dict[str, Any]]]: Список вакансий или None при ошибке.
    """
    vacancies: List[Dict[str, Any]] = []
    page = 0
    per_page = 100

    while True:
        url = "https://api.hh.ru/vacancies"
        params: Dict[str, Union[str, int]] = {
            'employer_id': company_id,
            'page': page,
            'per_page': per_page
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка при запросе вакансий для компании {company_id}: {e}")
            return None

        data = response.json()
        vacancies.extend(data.get('items', []))

        if page >= data.get('pages', 0) - 1:
            break
        page += 1

    return vacancies


def fetch_companies_and_vacancies(companies: List[Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Получает вакансии для списка компаний.

    Args:
        companies (List[Dict[str, str]]): Список компаний с ключами 'id' и 'name'.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Словарь с id компании как ключом и списком вакансий как значением.
    """
    all_vacancies: Dict[str, List[Dict[str, Any]]] = {}
    for company in companies:
        print(f"Получаем вакансии для компании: {company['name']} (ID: {company['id']})")
        vacancies = fetch_vacancies_by_company(company['id'])
        if vacancies is not None:
            all_vacancies[company['id']] = vacancies
            print(f"Получено вакансий: {len(vacancies)}")
        else:
            all_vacancies[company['id']] = []
            print(f"Не удалось получить вакансии для компании {company['name']}")
    return all_vacancies
