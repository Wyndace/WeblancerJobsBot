# -*- coding: utf-8 -*-
from aiohttp import ClientSession
from asyncio import gather, run, create_task
from bs4 import BeautifulSoup
from urllib.parse import quote
from json import dump

jobs_list = []

async def get_data(session, page, query):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)", "Accept": "*"}
    async with session.get(
            f'https://www.weblancer.net/jobs/?action=search&query={quote(query, encoding="windows-1251")}&page={page}', headers=headers) as response:
        jobs = BeautifulSoup(await response.text(), 'lxml').find_all(name='div',
                                                                     class_='row click_container-link set_href')
        for job in jobs:
            try:
                name = BeautifulSoup(str(job), 'lxml').find(name='div', class_='title').a.text.strip()
            except Exception as ex:
                name = 'Блок Имя не найден'
                print(ex)

            try:
                link = 'https://weblancer.net' + BeautifulSoup(str(job), 'lxml').find(name='div', class_='title').a['href'].strip()
            except Exception as ex:
                link = 'Блок Ссылка не найден'
                print(ex)

            try:
                if BeautifulSoup(str(job), 'lxml').find(name='div', class_='collapse') is not None:
                    description = ''.join(str(item).replace('<br/>', '') for item in BeautifulSoup(str(job), 'lxml').find(name='div', class_='collapse').contents[0:-1]).strip()
                else:
                    description = BeautifulSoup(str(job), 'lxml').find(name='div', class_='text-inline').text.strip()
            except Exception as ex:
                description = 'Блок Описание не найден'
                print(ex, 'name')

            try:
                bids_count = BeautifulSoup(str(job), 'lxml').find(name='div', class_='float-left float-sm-none text_field').text.strip()
            except Exception as ex:
                bids_count = 'Блок Заявки не найден'
                print(ex, 'bids')

            try:
                amount = {
                    'USD': BeautifulSoup(str(job), 'lxml').find(name='div', class_='amount').span.text.strip(),
                    'RUB': BeautifulSoup(str(job), 'lxml').find(name='div', class_='amount').span.get('title').split(' • ')[1].strip(),
                    'UAH': BeautifulSoup(str(job), 'lxml').find(name='div', class_='amount').span.get('title').split(' • ')[0].strip()
                }
            except Exception as ex:
                amount = 'Цена не указана'
                print(ex, 'price')

            try:
                time_ago = BeautifulSoup(str(job), 'lxml').find(name='span', class_='time_ago').text.strip()
            except Exception as ex:
                time_ago = 'Блок Время не найден'
                print(ex, 'time_ago')

            try:
                date = BeautifulSoup(str(job), 'lxml').find(name='span', class_='time_ago')['title'].strip()
            except Exception as ex:
                date = 'Блок Дата не найден'
                print(ex, 'time_ago')

            try:
                type_time = BeautifulSoup(str(job), 'lxml').find(name='span', class_='text-muted').contents[0].strip()
            except Exception as ex:
                type_time = 'Блок Тип Времени не найден'
                print(ex, 'time_ago')

            try:
                type = BeautifulSoup(str(job), 'lxml').find(name='span', class_='text-nowrap').a.text.strip()
            except Exception as ex:
                type = 'Блок Тип Заказа не найден'
                print(ex, 'type')

            job_dict = {}
            job_dict['name'] = name
            job_dict['url'] = link
            if type_time != 'Закрыт':
                job_dict['time'] = {
                    'type': type_time,
                    'timeAgo': time_ago,
                    'date': date,
                }
            else:
                job_dict['time'] = type_time
            job_dict['bidsCount'] = bids_count
            job_dict['amount'] = amount
            job_dict['type'] = type
            job_dict['description'] = description
            jobs_list.append(job_dict)


async def get_gather_data(query="Парсер, парсинг, парсить, пропарсить, спарсить"):
    tasks = []
    async with ClientSession() as session:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)", "Accept": "*"}
        response = await session.get(
            f"https://www.weblancer.net/jobs/?action=search&query={quote(query, encoding='windows-1251')}",
            headers=headers)
        last_page = BeautifulSoup(await response.text(), 'lxml').find(
            name='div', class_='col-1 col-sm-2 text-right').a['href'].split('page=')[1]
        with open('jobs.json', 'w') as file:
            file.write('')
        for page in range(1, int(last_page)+1):
            task = create_task(get_data(session, page, query))
            tasks.append(task)
        await gather(*tasks)


def main():
    run(get_gather_data())
    with open('jobs.json', 'w') as file:
        dump(jobs_list, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
