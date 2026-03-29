from mf_xray.backend.pdf_parser import *

context = {'funds': {}, 'current_fund': None, 'as_of_date': None, 'max_txn_date': None}

line1 = "15-Apr-23   SIP Installment   1,000  10.00 100.00"
line1b = "15-Apr-2023    Purchase    20,000    200.000    100.00"

context['current_fund'] = "Test Fund"
context['funds']["Test Fund"] = {"isin": None, "transactions": []}

_parse_detailed_transaction_strategy(line1, context)
_parse_detailed_transaction_strategy(line1b, context)
print("Transactions in Test Fund:", context['funds']["Test Fund"]["transactions"])

line_sum = "12-Aug-24    Aditya Birla Sun Life Liquid Fund    10,000    100    100.00"
_parse_summary_strategy(line_sum, context['funds'])
print("Funds:", list(context['funds'].keys()))
if "Aditya Birla Sun Life Liquid Fund" in context["funds"]:
    print("Liquid fund:", context["funds"]["Aditya Birla Sun Life Liquid Fund"])

