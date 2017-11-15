import sys 
import json 

# pass in the JSON object retrieved from LORIS's API 
with open(sys.argv[1], 'r') as data_file: 
	data = json.load(data_file) 

t1w_data = {}

j = 0 
for i in range(0, (len(data["Images"]) - 1)):
	image = data["Images"][i]["link"] 
	if image.find("t1w") == -1:  
		continue 
	else:
		t1w_data[j] = image
		j += 1

with open('image_list_v1_t1w.json', 'w') as data_file:
	data = json.dump(t1w_data, data_file)
