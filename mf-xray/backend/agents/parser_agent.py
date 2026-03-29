import uuid
import os

class ParserAgent:
    @staticmethod
    async def parse(payload):
        """
        Accepts either a JSON dict with 'portfolio' array or an UploadFile.
        Normalizes into a standard list of holdings with cashflows.
        Always returns a dict with 'status' and 'funds' keys - never crashes.
        """
        def safe_float(val, default=0.0):
            if val is None or val == "":
                return default
            try:
                return float(str(val).replace(',', '').replace(' ', ''))
            except ValueError:
                return default

        try:
            parsed_data = {}
            
            if isinstance(payload, dict) and "portfolio" in payload:
                for item in payload["portfolio"]:
                    fund = item["fund_name"]
                    if fund not in parsed_data:
                        parsed_data[fund] = []
                        
                    # Handle new format: transactions array inside fund object
                    if "transactions" in item:
                        for txn in item["transactions"]:
                            amt = safe_float(txn.get("amount"), 0.0)
                            parsed_data[fund].append({
                                "date": txn["date"],
                                "amount": amt,
                                "units": safe_float(txn.get("units"), amt / 100.0 if amt else 0.0),
                                "nav": safe_float(txn.get("nav"), 100.0),
                                "type": txn.get("type", "BUY")
                            })
                    else:
                        # Handle flat format
                        amt = safe_float(item.get("amount"), 0.0)
                        parsed_data[fund].append({
                            "date": item["date"],
                            "amount": amt,
                            "units": safe_float(item.get("units"), amt / 100.0 if amt else 0.0),
                            "nav": safe_float(item.get("nav"), 100.0),
                            "type": item.get("type", "BUY")
                        })
                return {"status": "success", "funds": parsed_data}
                
            elif hasattr(payload, "read"):
                import tempfile
                import json
                
                # Check if it's a JSON file uploaded via form data
                filename = getattr(payload, "filename", "")
                if filename.lower().endswith('.json'):
                    content = await payload.read()
                    try:
                        json_payload = json.loads(content)
                        return await ParserAgent.parse(json_payload)
                    except Exception as e:
                        return {"status": "error", "funds": {}, "message": f"Invalid JSON file: {e}"}

                job_id = str(uuid.uuid4())
                file_path = os.path.join(tempfile.gettempdir(), f"mf_xray_{job_id}.pdf")
                content = await payload.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                    
                import sys
                backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                from pdf_parser import parse_pdf
                result = parse_pdf(file_path)
                
                # Clean up the file after parsing
                try:
                    os.remove(file_path)
                except Exception:
                    pass
                    
                return result
                
            return {"status": "error", "funds": {}, "message": f"Invalid input format: {type(payload)}"}
        except Exception as e:
            # Absolute crash safety — never let the parser bring down the pipeline
            return {"status": "error", "funds": {}, "message": str(e)}
