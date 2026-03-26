with open("mf-xray/frontend/vite.config.js", "r") as f:
    text = f.read()

# Add base component properly
if "base:" not in text:
    text = text.replace("defineConfig({", "defineConfig({\n  base: '/TeamTrinity/',")

with open("mf-xray/frontend/vite.config.js", "w") as f:
    f.write(text)
