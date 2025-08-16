import json
with open(r"C:\Users\bhaskarahemanth.gant\OneDrive - Providence St. Joseph Health\Documents\testing\Acute Care Expected Discharge Date Original.Report\report.json", 'r') as f:
    json_data = json.load(f)
extracted_values = {
    "bookmarks": json_data.get("config", {}),
    "section_configs": [],
    "section_display_names": [],
    "visual_container_configs": [],
    "visualType":[],
    "columnProperties":[],
    "prototypeQuery":[]
}
for section in json_data.get("sections", []):
    extracted_values["section_configs"].append(section.get("config", {}))
    extracted_values["section_display_names"].append(section.get("displayName", ""))
    for vc in section.get("visualContainers", []):
        extracted_values["visual_container_configs"].append(vc.get("config", {}))

for i in extracted_values["visual_container_configs"]:
    valid_json=json.loads(i)
    print(valid_json.keys())
    if "singleVisual" not in valid_json.keys():
        continue
    if("visualType" in (valid_json["singleVisual"].keys())):
        extracted_values["visualType"].append(valid_json["singleVisual"]["visualType"])
    if("columnProperties" in (valid_json["singleVisual"].keys())):
        extracted_values["columnProperties"].append(valid_json["singleVisual"]["columnProperties"])
    if("prototypeQuery" in (valid_json["singleVisual"].keys())):
        extracted_values["prototypeQuery"].append(valid_json["singleVisual"]["prototypeQuery"])
    
print(extracted_values)

