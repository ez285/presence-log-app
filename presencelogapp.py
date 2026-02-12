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
    selDat = sl.session_state.selDat.__str__()
    newComp = sl.session_state.newComp.strip()
    fNam = sl.session_state.fNam.strip()
    lNam = sl.session_state.lNam.strip()
    toAppend = [selDat, newComp, '', fNam, lNam]
    flag = any([itm is not None and itm != '' for itm in [fNam, lNam]])
    if flag:
        sl.session_state.newNames.append(toAppend)
    sl.session_state.fNam = ''
    sl.session_state.lNam = ''

def Submit():
    pl.AddRows(sl.session_state.newNames)
    sl.session_state.newNames = []

def AddNameKnown():
    selDat = sl.session_state.selDat.__str__()
    comp = sl.session_state.comp.strip()
    fNam = sl.session_state.fNamK.strip()
    lNam = sl.session_state.lNamK.strip()
    toAppend = [selDat, comp, '', fNam, lNam]
    flag = any([itm is not None and itm != '' for itm in [fNam, lNam]])
    if flag:
        sl.session_state.newNamesKnown.append(toAppend)
    sl.session_state.fNamK = ''
    sl.session_state.lNamK = ''

def SubmitKnown(selected):
    if 'newNamesKnown' in sl.session_state:
        pl.AddRows(selected + sl.session_state.newNamesKnown)
    else:
        pl.AddRows(selected)
    sl.session_state.newNamesKnown = []
    for person in selected:
        sl.session_state[f'cb_{person[1]}_{person[2]}'] = False

sl.date_input('Date', value=date.today(), format='DD/MM/YYYY', key='selDat')
sl.selectbox('Company', pl.Companies + ['Add New...'], key='comp')
if sl.session_state.comp == 'Add New...':
    if 'addPersonellUI' not in sl.session_state:
        sl.session_state.addPersonellUI = False
    if 'newNames' not in sl.session_state:
        sl.session_state.newNames = []
    left, right = sl.columns([4, 1], vertical_alignment='bottom')
    with left:
        sl.text_input(label='Company name', key='newComp')
    with right:
        sl.button(label='Add personell', use_container_width=True, on_click=lambda:sl.session_state.update(addPersonellUI=True))
    if sl.session_state.addPersonellUI:
        left, middle, right = sl.columns([4, 4, 1], vertical_alignment='bottom')
        with left:
            sl.text_input(label='First Name', key='fNam')
        with middle:
            sl.text_input(label='Last Name', key='lNam')
        with right:
            sl.button('Add', use_container_width=True, on_click=AddName)
        sl.markdown('**** Names added ****')
        if sl.session_state.newNames:
            sl.text('\n'.join(['\t'.join(itm) for itm in sl.session_state.newNames]))
        else:
            sl.text('No names')
    sl.button('Submit', use_container_width=True, on_click=Submit)
elif sl.session_state.comp:
    people = pl.GetPersonellForCompany(sl.session_state.comp)
    selected = []
    for person in people:
        sl.checkbox('\t'.join([itm.__str__() for itm in person]), key=f'cb_{sl.session_state.comp}_{person[0]}')
        if sl.session_state.get(f'cb_{sl.session_state.comp}_{person[0]}'):
            selected.append([sl.session_state.selDat.__str__(), sl.session_state.comp] + person)
    sl.checkbox('Add New...', key='person_custom')
    if sl.session_state.person_custom:
        if 'newNamesKnown' not in sl.session_state:
            sl.session_state.newNamesKnown = []
        left, middle, right = sl.columns([4, 4, 1], vertical_alignment='bottom')
        with left:
            sl.text_input(label='First Name', key='fNamK')
        with middle:
            sl.text_input(label='Last Name', key='lNamK')
        with right:
            sl.button('Add', use_container_width=True, on_click=AddNameKnown)
        sl.markdown('**** Names added ****')
        if sl.session_state.newNamesKnown:
            sl.text('\n'.join(['\t'.join(itm) for itm in sl.session_state.newNamesKnown]))
        else:
            sl.text('No names')
    sl.button('Submit', use_container_width=True, on_click=lambda selected=selected: SubmitKnown(selected))
