from reportlab.pdfgen import canvas

c = canvas.Canvas("test_portfolio.pdf")
c.drawString(100, 750, "Folio Number: 12345678")
c.drawString(100, 730, "01-Jan-2023    1000.0   10.0   100.0")
c.save()
