import uuid
import os
from fastapi import UploadFile

class ParserAgent:
    @staticmethod
    async def parse(payload):
        """
        Accepts either a JSON dict with 'portfolio' array or an UploadFile.
        Normalizes into a standard list of holdings with cashflows.
        """
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
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from pdf_parser import parse_pdf
            return parse_pdf(file_path)
            
        return {"status": "error", "message": f"Invalid input format: {type(payload)}"}
