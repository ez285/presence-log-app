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
    return sh.worksheet(sl.secrets['worksheet_name_daily']), sh.worksheet(sl.secrets['worksheet_name_list'])

class PresenceLog:
    def __init__(self) -> None:
        self.SheetDaily, self.SheetList = get_worksheet()
        self.PersonellList = self.SheetList.get_all_records()
        self.Companies = list(set(rec['Contractor'] for rec in self.PersonellList))
        
    def AddRows(self, rows:list[list]) -> None:
        self.SheetDaily.append_rows(rows, insert_data_option=gs.utils.InsertDataOption.insert_rows, table_range='A1')
    
    def GetPersonellForCompany(self, company:str) -> list:
        return [[rec['Local ID'], rec['First Name'], rec['Last Name']] for rec in self.PersonellList if rec['Contractor'] == company]


pl = PresenceLog()

selDat = sl.date_input('Date', value=date.today(), format='DD/MM/YYYY')
cont = sl.selectbox('Company', pl.Companies + ['Add New...'])
if cont == 'Add New...':
    pass
elif cont is not None:
    selPres = sl.multiselect('Presence', pl.GetPersonellForCompany(str(cont)) + ['Add New...'])

submitted = sl.form_submit_button("Save")

if submitted:
    sl.success('Saved')
