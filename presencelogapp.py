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

def AddName():
    newComp = sl.session_state.newComp.strip()
    fNam = sl.session_state.fNam.strip()
    lNam = sl.session_state.lNam.strip()
    toAppend = [newComp, fNam, lNam]
    flag = any([itm is not None and itm != '' for itm in toAppend])
    if flag:
        sl.session_state.newNames.append(toAppend)
    sl.session_state.fNam = ''
    sl.session_state.lNam = ''

def SendNanes():
    pass

sl.date_input('Date', value=date.today(), format='DD/MM/YYYY', key='selDat')
sl.selectbox('Company', pl.Companies + ['Add New...'], key='comp')
if sl.session_state.comp == 'Add New...':
    if 'addPersonellUI' not in sl.session_state:
        sl.session_state.addPersonellUI = False
    if 'newNames' not in sl.session_state:
        sl.session_state.newNames = []
    left, right = sl.columns([4, 1])
    with left:
        sl.text_input(label='Company name', key='newComp')
    with right:
        sl.button(label='Add personell', use_container_width=True, on_click=lambda:sl.session_state.update(addPersonellUI=True))
    if sl.session_state.addPersonellUI:
        left, middle, rightAdd, rightEnd = sl.columns([4, 4, 1, 1])
        with left:
            sl.text_input(label='First Name', key='fNam')
        with middle:
            sl.text_input(label='Last Name', key='lNam')
        with rightAdd:
            sl.button('Add', use_container_width=True, on_click=AddName)
        with rightEnd:
            sl.button('End', use_container_width=True, on_click=SendNanes)
        sl.markdown('**** Names added ****')
        if sl.session_state.newNames:
            sl.text('\n'.join([f'{itm[0]}\t{itm[1]}\t{itm[2]}' for itm in sl.session_state.newNames]))
        else:
            sl.text('No names')
else:
    if 'addPersonellUI' in sl.session_state:
        sl.session_state.pop('addPersonellUI')
    if 'newNames' in sl.session_state:
        sl.session_state.pop('newNames')
