import re
from backend.pdf_parser import _parse_detailed_transaction_strategy, _parse_detailed_header_strategy

context = {'funds': {}, 'current_fund': None, 'as_of_date': None, 'max_txn_date': None}
line = "Folio Number: 12345678"
_parse_detailed_header_strategy(line, context)
print("Header test:", context['current_fund'])

context['current_fund'] = 'Test'
context['funds']['Test'] = {'transactions': []}
line2 = "15-Apr-2023 Purchase 1234567 10,000.00 100.000 100.0000 100.000"
_parse_detailed_transaction_strategy(line2, context)
print("Txn test:", context['funds']['Test']['transactions'])
