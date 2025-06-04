import requests
from typing import List, Dict, Optional


def fetch_vacancies_by_company(company_id: str) -> Optional[List[Dict]]:
    """
    Получить все вакансии компании с пагинацией из API hh.ru.

    :param company_id: ID работодателя (employer_id) на hh.ru
    :return: список вакансий (каждая — словарь) или None при ошибке
    """
    vacancies = []
    page = 0
    per_page = 100  # Максимум вакансий на страницу по API hh.ru

    while True:
        url = f"https://api.hh.ru/vacancies"
        params = {
            'employer_id': company_id,
            'page': page,
            'per_page': per_page
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка запроса вакансий для компании {company_id}: {e}")
            return None

        data = response.json()
        vacancies.extend(data.get('items', []))

        if page >= data.get('pages', 0) - 1:
            break
        page += 1

    return vacancies


def fetch_companies_and_vacancies(companies: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
    """
    Получить вакансии для списка компаний.

    :param companies: список словарей с ключами 'id' и 'name'
    :return: словарь {company_id: [вакансии]}
    """
    all_vacancies = {}
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


if __name__ == "__main__":
    companies = [
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

    vacancies_data = fetch_companies_and_vacancies(companies)

    # Пример вывода количества вакансий для каждой компании
    for company in companies:
        count = len(vacancies_data.get(company['id'], []))
        print(f"{company['name']}: {count} вакансий")
