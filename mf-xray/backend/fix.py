with open('/Users/ypragnesh/Desktop/ ET_Hackathon/mf-xray/backend/main.py', 'r') as f:
    text = f.read()
print('pipeline' in text.lower())
print('Pipeline error' in text)
