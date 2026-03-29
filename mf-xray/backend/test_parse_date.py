from datetime import datetime
def parse_date(date_str):
    try:
        if len(date_str.split('-')[-1]) == 2:
            return datetime.strptime(date_str, "%d-%b-%y").date()
        else:
            return datetime.strptime(date_str, "%d-%b-%Y").date()
    except ValueError:
        return None
print(parse_date("15-Apr-23"))
print(parse_date("15-Apr-2023"))
