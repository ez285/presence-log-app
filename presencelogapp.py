from __future__ import annotations
import gspread as gs
from google.oauth2.service_account import Credentials
import streamlit as sl
from datetime import date

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

@sl.cache_resource
def get_worksheet():
    creds = Credentials.from_service_account_info(sl.secrets['gcp_service_account'], scopes=SCOPES)
    gc = gs.authorize(creds)
    sh = gc.open_by_key(sl.secrets['sheet_id'])
    return sh.worksheet(sl.secrets['worksheet_name'])

class PresenceLog:
    def __init__(self) -> None:
        self.Sheet = get_worksheet()
        
    def AddRows(self, rows:list[list]) -> None:
        self.Sheet.append_rows(rows, insert_data_option=gs.utils.InsertDataOption.insert_rows, table_range='A1')

pl = PresenceLog()
pl.AddRows([['10/02/2026', 'KAMERIS', 'Mitsaras', 'Arxontidis']])

with sl.form('presence log'):
    selected_date = sl.date_input('Date', value=date.today())
    note = sl.text_input('Note (for now)')
    submitted = sl.form_submit_button("Save")
if submitted:

    sl.success('Saved')
