import pdfplumber
import re
from datetime import datetime
import traceback

DATE_REGEX = re.compile(r'^(\d{2}-[A-Za-z]{3}-\d{4})\s+')

def _parse_summary_strategy(line, funds):
    """Strategy: Extract data from the summary table format."""
    match_summary = re.search(r'(\d{2}-[A-Za-z]{3}-\d{4})', line)
    if DATE_REGEX.match(line) or not match_summary:
        return False

    date_str = match_summary.group(1)
    try:
        txn_date = datetime.strptime(date_str, "%d-%b-%Y").date()
        parts = line.split(date_str)
        name_part = parts[0].strip()

        isin_match = re.match(r'^(INF[A-Z0-9]{9,12})(?:/\S+)?\s+', name_part)
        extracted_isin = isin_match.group(1) if isin_match else None

        name_part = re.sub(r'^\S+(/\S+)?\s+', '', name_part)
        nums_before = re.findall(r'(?<!\S)[\d,]+\.\d+(?!\S)', name_part)
        
        fund_name = name_part
        for n in nums_before:
            fund_name = fund_name.replace(n, '').strip()

        fund_name = re.sub(r'[^a-zA-Z0-9 &\-]', '', fund_name).strip()

        if len(nums_before) >= 2 and fund_name:
            amount = float(nums_before[-2].replace(',', ''))
            units = float(nums_before[-1].replace(',', ''))

            nums_after = re.findall(r'[\d,]+\.\d+', parts[1])
            nav = float(nums_after[0].replace(',', '')) if nums_after else (amount/units if units>0 else 100.0)

            if amount > 0 and units > 0:
                if fund_name not in funds:
                    funds[fund_name] = {"isin": extracted_isin, "transactions": []}
                elif extracted_isin and not funds[fund_name].get("isin"):
                    funds[fund_name]["isin"] = extracted_isin
                    
                funds[fund_name]["transactions"].append({
                    "date": txn_date,
                    "amount": amount,
                    "units": units,
                    "nav": nav,
                    "type": "BUY"
                })
        return True
    except Exception:
        return False


def _parse_detailed_header_strategy(line, context):
    """Strategy: Detect fund headers in the detailed statement section."""
    if ("Folio No" in line) or ("Fund" in line and "Option" in line) or ("Plan" in line and "Growth" in line):
        if "Folio Number:" in line:
            current_fund = line.split("Folio Number:")[0].strip()
        elif "Folio No" in line:
            current_fund = line.split("Folio No")[0].strip()
        else:
            current_fund = line

        current_fund = re.sub(r'[^a-zA-Z0-9 &\-]', '', current_fund).strip()
        if current_fund:
            context['current_fund'] = current_fund
            if current_fund not in context['funds']:
                context['funds'][current_fund] = {"isin": None, "transactions": []}
        return True
    return False


def _parse_detailed_transaction_strategy(line, context):
    """Strategy: Parse individual transaction data line."""
    match = DATE_REGEX.search(line)
    current_fund = context.get('current_fund')
    
    if match and current_fund:
        date_str = match.group(1)
        try:
            txn_date = datetime.strptime(date_str, "%d-%b-%Y").date()
        except ValueError:
            return False
            
        parts = line[match.end():].split()
        numbers = []
        for part in reversed(parts):
            clean_part = part.replace(',', '')
            is_negative = False
            if clean_part.startswith('(') and clean_part.endswith(')'):
                is_negative = True
                clean_part = clean_part[1:-1]
            
            try:
                val = float(clean_part)
                if is_negative: val = -val
                numbers.append(val)
            except ValueError:
                break
                
        numbers.reverse()
        
        if len(numbers) >= 3:
            amount = numbers[0]
            units = numbers[1]
            nav = numbers[2]
            
            txn_type = "BUY"
            if "Redemption" in line or "Switch Out" in line or "Payout" in line or amount < 0 or units < 0:
                txn_type = "SELL"
                amount = -abs(amount)
                units = -abs(units)
                
            if amount != 0 and units != 0:
                context['funds'][current_fund]["transactions"].append({
                    "date": txn_date,
                    "amount": amount,
                    "units": units,
                    "nav": nav,
                    "type": txn_type
                })
        return True
    return False


def parse_pdf(file_path):
    """
    Parse CAMS/KFintech PDF to extract transactions and fund names.
    Applies several named parsing strategies line-by-line.
    """
    context = {
        'funds': {},
        'current_fund': None
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Apply regex parsing strategies sequentially
                    if _parse_summary_strategy(line, context['funds']):
                        continue
                    if _parse_detailed_header_strategy(line, context):
                        continue
                    if _parse_detailed_transaction_strategy(line, context):
                        continue

        # Filter out parsed funds that lack transaction records
        filtered_funds = {
            k: v for k, v in context['funds'].items() 
            if len(v.get("transactions", [])) > 0
        }
        
        return {"status": "success", "funds": filtered_funds}
        
    except Exception as e:
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}