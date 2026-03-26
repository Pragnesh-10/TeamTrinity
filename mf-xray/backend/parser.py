import pdfplumber
import re
from datetime import datetime

def parse_pdf(file_path):
    """
    Parse CAMS/KFintech PDF to extract transactions and fund names.
    Returns: {
      "status": "success",
      "funds": {
          "Fund Name 1": [
            {"date": datetime.date, "amount": float, "units": float, "nav": float, "type": "BUY" | "SELL"}
          ]
      }
    }
    """
    funds = {}
    current_fund = None
    
    date_regex = re.compile(r'^(\d{2}-[A-Za-z]{3}-\d{4})\s+')
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for idx, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                        
                    # 1. Summary Format Line check
                    # Look for date in the middle of line (Summary table format)
                    match_summary = re.search(r'(\d{2}-[A-Za-z]{3}-\d{4})', line)
                    if not date_regex.match(line) and match_summary:
                        date_str = match_summary.group(1)
                        try:
                            txn_date = datetime.strptime(date_str, "%d-%b-%Y").date()
                            
                            # Extract numbers before date (Cost Value, Unit Balance)
                            parts = line.split(date_str)
                            name_part = parts[0].strip()
                            
                            # Remove Folio/ISIN at start
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
                                        funds[fund_name] = []
                                    funds[fund_name].append({
                                        "date": txn_date,
                                        "amount": amount,
                                        "units": units,
                                        "nav": nav,
                                        "type": "BUY"
                                    })
                                    current_fund = fund_name # track it just in case
                        except:
                            pass
                        continue

                    # 2. Detailed format - identify fund name header
                    if ("Folio No" in line) or ("Fund" in line and "Option" in line) or ("Plan" in line and "Growth" in line):
                        if "Folio Number:" in line:
                            current_fund = line.split("Folio Number:")[0].strip()
                        elif "Folio No" in line:
                            current_fund = line.split("Folio No")[0].strip()
                        else:
                            current_fund = line
                            
                        current_fund = re.sub(r'[^a-zA-Z0-9 &\-]', '', current_fund).strip()
                        if current_fund and current_fund not in funds:
                            funds[current_fund] = []
                        continue
                    
                    # 3. Detailed format - transaction line
                    match = date_regex.search(line)
                    if match and current_fund:
                        date_str = match.group(1)
                        try:
                            txn_date = datetime.strptime(date_str, "%d-%b-%Y").date()
                        except ValueError:
                            continue
                            
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
                                funds[current_fund].append({
                                    "date": txn_date,
                                    "amount": amount,
                                    "units": units,
                                    "nav": nav,
                                    "type": txn_type
                                })
                                
        # Add next line details if fund_name spans multiple lines (simplified logic above)
        filtered_funds = {k: v for k, v in funds.items() if len(v) > 0}
        
        return {"status": "success", "funds": filtered_funds}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}
