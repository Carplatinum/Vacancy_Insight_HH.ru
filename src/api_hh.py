import requests
from typing import List, Dict

class HHApi:
    """Класс для работы с API hh.ru."""

    BASE_URL = 'https://api.hh.ru'

    def get_company_vacancies(self, employer_id: str, per_page: int = 100) -> List[Dict]:
        """
        Получить список вакансий компании по её ID.

        :param employer_id: ID работодателя
        :param per_page: Количество вакансий на страницу (по умолчанию 100)
        :return: Список словарей с вакансиями
        """
        vacancies: List[Dict] = []
        page: int = 0
        while True:
            params = {
                'employer_id': employer_id,
                'page': page,
                'per_page': per_page
            }
            response = requests.get(f'{self.BASE_URL}/vacancies', params=params)
            response.raise_for_status()
            data = response.json()
            vacancies.extend(data['items'])
            if page >= data['pages'] - 1:
                break
            page += 1
        return vacancies

    def get_employer(self, employer_id: str) -> Dict:
        """
        Получить информацию о работодателе по его ID.

        :param employer_id: ID работодателя
        :return: Словарь с информацией о работодателе
        """
        response = requests.get(f'{self.BASE_URL}/employers/{employer_id}')
        response.raise_for_status()
        return response.json()
