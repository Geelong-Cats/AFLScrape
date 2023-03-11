from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
import streamlit as st
import pandas as pd
import numpy as np
from scraping_functions import get_provisional_draft_year
import redirect as rd

st.set_page_config(
    page_title="Draft Guru",
    page_icon="📝",
    layout="wide"
)

YEARS = [2018,2019,2020,2021,2022,2023]
# Initialisation
np.random.seed(42)
if 'provisional_data' not in st.session_state:
    st.session_state.provisional_data = pd.DataFrame({})


st.title('Draft Guru Provisional Draft Scraping Tool')

years_selection = st.multiselect(label = 'Select years to scrape',options  = YEARS, default  = YEARS[-1])

button = st.button('Scrape!',key = 'scrape_button')

def get_provisional_draft_years(years):
    return pd.concat([get_provisional_draft_year(y,rd) for y in years], axis=0)

if button:
    st.session_state.provisional_data = get_provisional_draft_years(years_selection)
    st.session_state.button_pressed = True

gb = GridOptionsBuilder.from_dataframe(st.session_state.provisional_data)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
gb.configure_grid_options(domLayout='normal')
st.session_state.gridOptions = gb.build()

grid_response = AgGrid(st.session_state.provisional_data,
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
                   file_name='provisional_draft.csv')
