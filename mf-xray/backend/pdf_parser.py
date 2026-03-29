import pdfplumber
import re
from datetime import datetime
import traceback

DATE_REGEX = re.compile(r'(\d{2}-[A-Za-z]{3}-\d{2,4})')

def _parse_date(date_str):
    try:
        if len(date_str.split('-')[-1]) == 2:
            return datetime.strptime(date_str, "%d-%b-%y").date()
        else:
            return datetime.strptime(date_str, "%d-%b-%Y").date()
    except ValueError:
        return None

def _parse_summary_strategy(line, funds):
    """Strategy: Extract data from the summary table format."""
    match_summary = re.search(r'(\d{2}-[A-Za-z]{3}-\d{2,4})', line)
    if not match_summary:
        return False

    date_str = match_summary.group(1)
    txn_date = _parse_date(date_str)
    if not txn_date:
        return False
    try:
        parts = line.split(date_str)
        # If date is at the start of the line, the fund name is in parts[1]
        name_part = parts[0].strip()
        nav_part = parts[1] if len(parts) > 1 else ""
        
        if not name_part and len(parts) > 1:
            name_part = parts[1].strip()
            nav_part = "" # Everything is squished in name_part

        isin_match = re.search(r'(INF[A-Z0-9]{9,12})', name_part)
        extracted_isin = isin_match.group(1) if isin_match else None

        # Only strip the first word if it contains digits (like a Folio or ISIN)
        # to avoid stripping the first word of a mutual fund name
        first_word_match = re.match(r'^(\S+(?:\/\S+)?)\s+', name_part)
        if first_word_match and any(char.isdigit() for char in first_word_match.group(1)):
            name_part = re.sub(r'^\S+(/\S+)?\s+', '', name_part)

        nums_before = re.findall(r'(?<!\S)[\d,]+(?:\.\d+)?(?!\S)', name_part)
        
        fund_name = name_part
        for n in nums_before:
            # Avoid replacing numbers that are part of the fund name like 'Nifty 50'
            # by strictly replacing from the end or just using split
            pass # We'll handle this safer
            
        # Safer fund name extraction
        for n in nums_before:
            # split from right to ensure we don't break '50' in 'Nifty 50' if 50 is a unit
            fund_name = fund_name.rsplit(n, 1)[0].strip()
            
        if extracted_isin:
            fund_name = fund_name.replace(extracted_isin, '').strip()

        fund_name = re.sub(r'[^a-zA-Z0-9 &\-]', '', fund_name).strip()

        if len(nums_before) >= 2 and fund_name:
            amount = float(nums_before[-2].replace(',', ''))
            units = float(nums_before[-1].replace(',', ''))

            nums_after = re.findall(r'[\d,]+(?:\.\d+)?', nav_part) if nav_part else []
            if not nums_after and len(nums_before) >= 3:
                # If there was no nav_part because the date was at the beginning,
                # the 3rd last number might logically be the amount, and last is NAV.
                # However, usually the sequence is: Amount, Units, NAV.
                amount = float(nums_before[-3].replace(',', ''))
                units = float(nums_before[-2].replace(',', ''))
                nav = float(nums_before[-1].replace(',', ''))
            elif nums_after:
                nav = float(nums_after[0].replace(',', ''))
            else:
                nav = amount / units if units > 0 else 100.0

            if amount > 0 and units > 0:
                if fund_name not in funds:
                    funds[fund_name] = {"isin": extracted_isin, "transactions": [], "current_nav": nav, "current_value": amount}
                elif extracted_isin and not funds[fund_name].get("isin"):
                    funds[fund_name]["isin"] = extracted_isin
                    
                # Update current NAV from summary without polluting transactions cache
                funds[fund_name]["current_nav"] = nav
                return True
                
        return False
    except Exception:
        return False


def _parse_detailed_header_strategy(line, context):
    """Strategy: Detect fund headers in the detailed statement section."""
    if ("Folio No" in line) or ("Folio Number" in line) or ("Fund" in line and "Option" in line) or ("Plan" in line and "Growth" in line) or ("Account No" in line):
        if "Folio Number:" in line:
            parts = line.split("Folio Number:")
            current_fund = parts[0].strip() if parts[0].strip() else parts[1].strip()
        elif "Folio No" in line:
            parts = line.split("Folio No")
            current_fund = parts[0].strip() if parts[0].strip() else parts[1].strip()
        else:
            current_fund = line

        current_fund = re.sub(r'[^a-zA-Z0-9 &\-]', '', current_fund).strip()
        # Clean up common noise in fund names
        current_fund = re.sub(r'\s+', ' ', current_fund)

        if current_fund and len(current_fund) > 5:
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
        txn_date = _parse_date(date_str)
        if not txn_date:
            return False
            
        # Update internal latest date tracker for fallback as-of-date
        if not context['max_txn_date'] or txn_date > context['max_txn_date']:
            context['max_txn_date'] = txn_date
            
        # Extract numbers using a more robust approach that doesn't rely solely on whitespace
        # We look for amounts, units, and NAV which are typically at the end of the line
        numbers = re.findall(r'\(?[\d,]+(?:\.\d+)?\)?', line[match.end():])
        clean_numbers = []
        for n in numbers:
            is_neg = n.startswith('(') and n.endswith(')')
            val = float(n.replace('(', '').replace(')', '').replace(',', ''))
            clean_numbers.append(-val if is_neg else val)
                
        if len(clean_numbers) >= 2:
            # Usually: Amount, Units, NAV are towards the end. Might include Balance at the very end.
            if len(clean_numbers) >= 4:
                amount = clean_numbers[-4]
                units = clean_numbers[-3]
                nav = clean_numbers[-2]
            elif len(clean_numbers) == 3:
                amount = clean_numbers[-3]
                units = clean_numbers[-2]
                nav = clean_numbers[-1]
            else:
                amount = clean_numbers[-2]
                units = clean_numbers[-1]
                nav = abs(amount/units) if units != 0 else 0
            
            line_lower = line.lower()
            txn_type = "BUY"
            if any(kw in line_lower for kw in ["redemption", "switch out", "payout", "sell"]):
                txn_type = "SELL"
                amount = -abs(amount) # Cash flow from user's perspective (negative if reinvesting, but here we normalize)
                # For XIRR, internal logic usually expects:
                # Investment: NEGATIVE cash flow
                # Redemption: POSITIVE cash flow
                # However, our parser returns numbers which analysis_agent will sign.
                # Standardizing:
                amount = -abs(amount) # Parser says 'Investment'
                if txn_type == "SELL": amount = abs(amount) # Parser says 'Inflow'
            elif any(kw in line_lower for kw in ["reinvest", "idcw", "dividend"]):
                txn_type = "REINVEST"
            
            context['funds'][current_fund]["transactions"].append({
                "date": txn_date,
                "amount": float(amount),
                "units": float(units),
                "nav": float(nav),
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
        'current_fund': None,
        'as_of_date': None,
        'max_txn_date': None
    }
    
    # Common prefixes for the statement end date (as-of date)
    PERIOD_END_REGEX = re.compile(r'(?:To|to|as of)\s+(\d{2}-[A-Za-z]{3}-\d{2,4})')

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
                    
                    # Try to capture the statement as-of date (period end)
                    if not context['as_of_date']:
                        period_match = PERIOD_END_REGEX.search(line)
                        if period_match:
                            parsed_d = _parse_date(period_match.group(1))
                            if parsed_d:
                                context['as_of_date'] = parsed_d

                    # Apply regex parsing strategies sequentially
                    if _parse_summary_strategy(line, context['funds']):
                        continue
                    if _parse_detailed_header_strategy(line, context):
                        continue
                    if _parse_detailed_transaction_strategy(line, context):
                        continue

        # If a fund has summary data (current_value) but no transaction lines matched,
        # it might just be a summary statement. Keep all funds that have EITHER 
        # transactions OR a documented current_value.
        filtered_funds = {
            k: v for k, v in context['funds'].items() 
            if len(v.get("transactions", [])) > 0 or v.get("current_value", 0) > 0
        }
        
        # Fallback to latest transaction date if period header missing
        final_as_of = context['as_of_date'] or context['max_txn_date']
        
        return {
            "status": "success", 
            "funds": filtered_funds, 
            "as_of_date": final_as_of.strftime("%Y-%m-%d") if final_as_of else None
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}
