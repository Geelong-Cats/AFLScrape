from bs4 import BeautifulSoup
import requests
import pandas as pd

def make_soup(website):
    if 'https' in website:
        page = requests.get(website, timeout=120)
    else:
        page = requests.get('https://' + website, timeout=120)
    soup = BeautifulSoup(page.content, 'html.parser')
    page.close()
    return soup


def clean_text(a):
    return a.replace('\xa0', '').rstrip().lstrip()


def get_pids(row_data):
    ids = [a.find('a')['href'] for a in row_data if a.find('a') is not None]
    player_id = [x.replace("pp-", "") for x in ids if "pp-" in x][0].split('--')[1]
    return clean_text(player_id)

def get_tids(row_data):
    ids = [a.find('a')['href'] for a in row_data if a.find('a') is not None]
    team_id = [x.replace("tb-", "") for x in ids if "tb-" in x][0].split('?')[0]
    return clean_text(team_id)


def parse_row_data_bl(row_data, headers):
    data_dict = {headers[i]: clean_text(row_data[i].text) for i in range(len(row_data))}
    pid = get_pids(row_data)
    tid = get_tids(row_data)
    data_dict['player_id'] = pid
    data_dict['team_id'] = tid
    return data_dict

def parse_row_data_con(row_data,headers,team):
    data_dict = {headers[i]:clean_text(row_data[i].text) for i in range(len(row_data))}
    pid = get_pids(row_data)
    data_dict['player_id'] = clean_text(pid)
    data_dict['team_id'] = clean_text(team)
    return data_dict


def get_con_team(team,rd):
    with rd.stdout(format='markdown'):
        print(f'Scraping contracts for {team}')

    # Get the URL
    URL = "https://www.footywire.com/afl/footy/to-" + team
    soup = make_soup(URL)

    # Extract out the table. we search for the table that's exactly 688
    contract_table_html = [a for a in soup.find_all('table') if a.get('width') == '688'][0]
    flat_table_data = [a for a in contract_table_html.find_all('td')]

    header_elements = flat_table_data[0:4]
    body_elements = flat_table_data[4:]

    headers = [clean_text(a.text) for a in header_elements]
    data_list = []
    for e in range(0, len(body_elements), len(headers)):
        row_data = body_elements[e:e + len(headers)]
        data_list.append(parse_row_data_con(row_data, headers, team))

    return pd.DataFrame(data_list)


def get_brownlow_year(year,rd):

    with rd.stdout(format='markdown'):
        print(f'Scraping brownlow for year {year}')

    # Get the URL
    URL = "https://www.footywire.com/afl/footy/brownlow_medal?year=" + str(year) + "&s=V"
    soup = make_soup(URL)

    # Extract out the table. we search for the table that's exactly 688
    brownlow_table_html = [a for a in soup.find_all('table') if a.get('width') == '688'][0]
    flat_table_data = [a for a in brownlow_table_html.find_all('td')]
    header_elements = flat_table_data[0:9]
    body_elements = flat_table_data[9:]
    headers = [clean_text(a.text) for a in header_elements]
    data_list = []
    for e in range(0, len(body_elements), len(headers)):
        row_data = body_elements[e:e + len(headers)]
        data_list.append(parse_row_data_bl(row_data, headers))
    return pd.DataFrame(data_list)

