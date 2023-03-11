from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
import streamlit as st
import redirect as rd
from scraping_functions import make_soup, get_con_team, get_brownlow_year
import pandas as pd
import numpy as np


TEAMS ={"adelaide-crows":"Crows",
"brisbane-lions":"Lions",
"carlton-blues":"Blues",
"collingwood-magpies":"Magpies",
"essendon-bombers":"Bombers",
"fremantle-dockers":"Dockers",
"gold-coast-suns":"Suns",
"greater-western-sydney-giants":"Giants",
"hawthorn-hawks":"Hawks",
"kangaroos":"Kangaroos",
"st-kilda-saints":"Saints",
"sydney-swans":"Swans",
"west-coast-eagles":"Eagles",
"western-bulldogs":"Bulldogs",
"port-adelaide-power":"Power",
"melbourne-demons":"Demons",
"geelong-cats":'Cats',
"richmond-tigers":"Tigers"}

BROWNLOW_YEAR = 2022

st.set_page_config(
    page_title="Footy Wire",
    page_icon="🏉",
    layout="wide"
)

# Initialisation
np.random.seed(42)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({})


st.title('Footywire scraping tool')


def join_on_brownlow(contract_data,brownlow_data):
    df = pd.merge(contract_data,
                     brownlow_data,
                     left_on='player_id',
                     right_on='player_id',
                     how='left',
                     suffixes=('_contract', '_brownlow'))
    df = df.fillna("",inplace=False)
    return df


def get_contract_teams(teams_list,rd):
    return pd.concat([get_con_team(team,rd) for team in teams_list], axis=0)



# Widgets
team_selection = st.multiselect(label = 'Select team to scrape',options  = TEAMS.keys(), default  = TEAMS.keys())
add_brownlow = st.checkbox('Add 2022 Brownlow stats')
button = st.button('Scrape!',key = 'scrape_button')

# When the button is pressed, do stuff
if button:
    st.session_state.data = get_contract_teams(team_selection,rd)
    if add_brownlow:
        brownlow_data = get_brownlow_year(BROWNLOW_YEAR,rd)
        st.session_state.data = join_on_brownlow(st.session_state.data,brownlow_data)

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
                   file_name='footy_wire.csv')
