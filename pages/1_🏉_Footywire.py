from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
import streamlit as st
import redirect as rd
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np


TEAMS = [
"adelaide-crows",
"brisbane-lions",
"carlton-blues",
"collingwood-magpies",
"essendon-bombers",
"fremantle-dockers",
"gold-coast-suns",
"greater-western-sydney-giants",
"hawthorn-hawks",
"kangaroos",
"st-kilda-saints",
"sydney-swans",
"west-coast-eagles",
"western-bulldogs",
"port-adelaide-power",
"melbourne-demons",
"geelong-cats",
"richmond-tigers"]


st.set_page_config(
    page_title="Footy Wire",
    page_icon="🏉",
)

# Initialisation
np.random.seed(42)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({})


st.title('Footywire scraping tool')

def make_soup(website):
    if 'https' in website:
        page = requests.get(website, timeout=120)
    else:
        page = requests.get('https://' + website, timeout=120)
    soup = BeautifulSoup(page.content, 'html.parser')
    page.close()
    return soup

def get_table_team(team):
    with rd.stdout(format='markdown'):
        print(f'Scraping contracts for {team}')

    # Get the URL
    URL = "https://www.footywire.com/afl/footy/to-" + team
    soup = make_soup(URL)

    # Extract out the table. we search for the table that's exactly 688
    contract_table_html = [a for a in soup.find_all('table') if a.get('width') == '688'][0]

    # For each element, we extract the text and replace the 'xa0' (non-breaking character) with ''
    flat_table_data = [a.text.replace('\xa0', '') for a in contract_table_html.find_all('td')]

    # Assume the first 4 entries are the data header
    header = flat_table_data[0:4]

    # Body
    body = flat_table_data[4:]

    # Iteratively create the dictionary (to be turned into a dataframe)
    # Every 4th row cycles goes back to the beginning
    #TODO: This could be vectorised using better indexing
    data_dict = {j: [] for j in header}
    for counter, i in enumerate(range(len(body))):
        h_name = header[counter % len(header)]
        data_dict[h_name].append(body[counter])

    data_dict['team'] = [team] * len(data_dict[header[0]])

    return pd.DataFrame(data_dict)

def get_contract_teams(teams_list):
    return pd.concat([get_table_team(team) for team in teams_list], axis=0)


team_selection = st.multiselect(label = 'Select team to scrape',options  = TEAMS, default  = TEAMS)
button = st.button('Scrape!',key = 'scrape_button')

if button:
    data_load_state = st.text('Loading data...')
    st.session_state.data = get_contract_teams(team_selection)
    data_load_state.text('Loading data...Done!')
    st.session_state.button_pressed = True

gb = GridOptionsBuilder.from_dataframe(st.session_state.data)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
gb.configure_grid_options(domLayout='normal')
st.session_state.gridOptions = gb.build()

grid_response = AgGrid(st.session_state.data,
                       gridOptions=st.session_state.gridOptions,
                       update_mode=GridUpdateMode.GRID_CHANGED,
                        height=700,
                        width='100%',
                        fit_columns_on_grid_load=True,
                        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
                        enable_enterprise_modules=False,
                        editable = True)

st.download_button("Download data",
                   data=grid_response['data'].to_csv(index = False),
                   file_name='test_data.csv')
