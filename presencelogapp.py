from __future__ import annotations
import gspread as gs
from google.oauth2.service_account import Credentials
import streamlit as sl
from datetime import date

class PresenceLog:
    def __init__(self) -> None:
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        SERVICE_ACCOUNT_FILE = 'singular-ally-472620-m4-7ca5b5f2a5ae.json'
        SPREADSHEET_ID = '1yLfco4jfgtXT_HTm_gylPWxtWbxLkdcEAdVlmK_aOPE'
        WORKSHEET_NAME = 'Presence log'
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gs.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        self.Sheet = sh.worksheet(WORKSHEET_NAME)
    
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