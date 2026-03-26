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
        try:
            parsed_data = {}
            
            if isinstance(payload, dict) and "portfolio" in payload:
                for item in payload["portfolio"]:
                    fund = item["fund_name"]
                    if fund not in parsed_data:
                        parsed_data[fund] = []
                    parsed_data[fund].append({
                        "date": item["date"],
                        "amount": float(item["amount"]),
                        "units": float(item.get("units", item["amount"] / 100.0)),
                        "nav": float(item.get("nav", 100.0)),
                        "type": item.get("type", "BUY")
                    })
                return {"status": "success", "funds": parsed_data}
                
            elif hasattr(payload, "read"):
                job_id = str(uuid.uuid4())
                os.makedirs("/tmp/mf-xray", exist_ok=True)
                file_path = f"/tmp/mf-xray/{job_id}.pdf"
                content = await payload.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                    
                import sys
                backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                from pdf_parser import parse_pdf
                result = parse_pdf(file_path)
                return result
                
            return {"status": "error", "funds": {}, "message": f"Invalid input format: {type(payload)}"}
        except Exception as e:
            # Absolute crash safety — never let the parser bring down the pipeline
            return {"status": "error", "funds": {}, "message": f"Parser exception: {str(e)}"}
