import os, yaml

Root = "D:\\ArgusAI - DEMO DAY\\data\\raw_downloads"

for folder in os.listdir(Root):
    yaml_path = None
    for f in os.listdir(os.path.join(Root, folder)):
        if f.endswith(".yaml"):
            yaml_path = os.path.join(Root, folder, f)
            break
    if yaml_path:
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        print(f"\n{folder}: {data.get('names' , 'no names found')}")