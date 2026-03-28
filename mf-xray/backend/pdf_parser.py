import pdfplumber
import re
from datetime import datetime
import traceback

DATE_REGEX = re.compile(r'(\d{2}-[A-Za-z]{3}-\d{4})')

def _parse_summary_strategy(line, funds):
    """Strategy: Extract data from the summary table format."""
    match_summary = re.search(r'(\d{2}-[A-Za-z]{3}-\d{4})', line)
    if not match_summary:
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
                    funds[fund_name] = {"isin": extracted_isin, "transactions": [], "current_nav": nav, "current_value": amount}
                elif extracted_isin and not funds[fund_name].get("isin"):
                    funds[fund_name]["isin"] = extracted_isin
                    
                # Update current NAV from summary without polluting transactions cache
                funds[fund_name]["current_nav"] = nav
                
        return True
    except Exception:
        return False


def _parse_detailed_header_strategy(line, context):
    """Strategy: Detect fund headers in the detailed statement section."""
    if ("Folio No" in line) or ("Fund" in line and "Option" in line) or ("Plan" in line and "Growth" in line) or ("Account No" in line):
        if "Folio Number:" in line:
            current_fund = line.split("Folio Number:")[1].strip() if "Folio Number:" in line else line
        elif "Folio No" in line:
            current_fund = line.split("Folio No")[0].strip()
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
        try:
            txn_date = datetime.strptime(date_str, "%d-%b-%Y").date()
            # Update internal latest date tracker for fallback as-of-date
            if not context['max_txn_date'] or txn_date > context['max_txn_date']:
                context['max_txn_date'] = txn_date
        except ValueError:
            return False
            
        # Extract numbers using a more robust approach that doesn't rely solely on whitespace
        # We look for amounts, units, and NAV which are typically at the end of the line
        numbers = re.findall(r'\(?[\d,]+\.\d+\)?', line[match.end():])
        clean_numbers = []
        for n in numbers:
            is_neg = n.startswith('(') and n.endswith(')')
            val = float(n.replace('(', '').replace(')', '').replace(',', ''))
            clean_numbers.append(-val if is_neg else val)
                
        if len(clean_numbers) >= 2:
            # Usually: Amount, Units, NAV. If only 2, NAV might be missing or merged.
            amount = clean_numbers[0]
            units = clean_numbers[1]
            nav = clean_numbers[2] if len(clean_numbers) >= 3 else (abs(amount/units) if units != 0 else 0)
            
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
    PERIOD_END_REGEX = re.compile(r'(?:To|to|as of)\s+(\d{2}-[A-Za-z]{3}-\d{4})')

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
                            try:
                                context['as_of_date'] = datetime.strptime(period_match.group(1), "%d-%b-%Y").date()
                            except ValueError:
                                pass

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
        
        # Fallback to latest transaction date if period header missing
        final_as_of = context['as_of_date'] or context['max_txn_date']
        
        return {
            "status": "success", 
            "funds": filtered_funds, 
            "as_of_date": final_as_of.strftime("%Y-%m-%d") if final_as_of else None
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}