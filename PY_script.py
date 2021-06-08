# https://github.com/not-my-account/nutrition_dashboard
# import code modules
from bokeh.io import output_file, show
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, CustomJS, MultiChoice
from bokeh.models.widgets import DataTable, TableColumn
from zipfile import ZipFile

import os
import pandas as pd
import requests

# get key from https://fdc.nal.usda.gov/api-key-signup.html
api_key = input()
url = 'https://api.nal.usda.gov/fdc/v1/foods?api_key='+api_key

r = requests.get('https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_survey_food_csv_2020-10-30.zip', allow_redirects=True)
with open('FDC_data.zip', 'wb') as file:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            file.write(chunk)

with ZipFile('FDC_data.zip', 'r') as zipObj:
    zipObj.extract('food.csv')

os.remove('FDC_data.zip')

foods = pd.read_csv('food.csv')
foods = foods[['fdc_id', 'description']]
foods = foods.rename(columns={'description': 'Description'})

# set and load data on three food items to test the code
data = {"fdcIds": [1100417, 1103276, 1102653],
        "format": "abridged"}
r = requests.post(url, json=data)

nutrients = [n['name'] for n in r.json()[0]['foodNutrients']]
data = pd.DataFrame(columns=['Food Name']+nutrients)

for i in r.json():
    food_info = {'Food Name': i['description']}

    for n in i['foodNutrients']:
        food_info[n['name']] = n['amount']

    data = data.append(food_info, ignore_index=True)

# create dashboard
initial_nutrients = nutrients[:4]

original_data = ColumnDataSource(data)
source = ColumnDataSource(data[['Food Name']+initial_nutrients])

columns = [TableColumn(field=Ci, title=Ci) for Ci in ['Food Name']+nutrients] # bokeh columns
nutrient_table = DataTable(columns=columns, source=source, index_position=None, frozen_columns=1) # bokeh table

nutrient_selector_callback = CustomJS(args=dict(original_data=original_data, columns=columns, source=source), code="""    
    var original = original_data.data;
    var col = columns.data;
    console.log(original_data);
    console.log(original);
    console.log(columns);
    console.log(col);
    
    
    
    var data = source.data;
    var data_keys = Object.keys(data)
    var selected_nutrients = cb_obj.value;
    selected_nutrients.push('index');
    selected_nutrients.push('Food Name');
    
    if (data_keys.length < selected_nutrients.length) {
        var add_nut = selected_nutrients.filter(nut => !data_keys.includes(nut));
        data[add_nut] = original[add_nut];
    } else {
        var del_nut = data_keys.filter(nut => !selected_nutrients.includes(nut));
        delete data[del_nut];
    }
    source.change.emit();
""")

food_selector = MultiChoice(value=[], options=list(foods['Description']))
nutrient_selector = MultiChoice(value=initial_nutrients, options=nutrients)
nutrient_selector.js_on_change('value', nutrient_selector_callback)

output_file("nutrition_dashboard.html")
show(column(food_selector, nutrient_selector, nutrient_table))

# https://docs.bokeh.org/en/latest/docs/user_guide/interaction/linking.html
# https://stackoverflow.com/questions/32418045/running-python-code-by-clicking-a-button-in-bokeh