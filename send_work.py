import requests

APP = "https://app.cells.es"
SERVICE = "employment-office-services/person_status"

AT_ALBA = "at_alba"
FROM_HOME = "from_home"
ID = 316
PERSON = 319

def _update_status(person, id, status):
    url = f"{APP}/{SERVICE}/{person}/update/"
    data = dict(
        id=id,
        current_status=status,
        last_sync_absence_id=None,
        last_sync_date=None,
        person=person)
    return requests.put(url, json=data)

def at_alba():
    return _update_status(PERSON, ID, AT_ALBA)

def from_home():
    return _update_status(PERSON, ID, FROM_HOME)
