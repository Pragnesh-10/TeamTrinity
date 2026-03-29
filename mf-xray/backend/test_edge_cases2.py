import re
from backend.pdf_parser import _parse_detailed_header_strategy

context = {'funds': {}, 'current_fund': None, 'as_of_date': None, 'max_txn_date': None}
line = "Axis Long Term Equity Fund       Folio Number: 12345678"
_parse_detailed_header_strategy(line, context)
print("Header test:", context['current_fund'])

