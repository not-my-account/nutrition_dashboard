# bokeh test
import pandas as pd
import numpy as np
from bokeh.layouts import column, row
from bokeh.plotting import figure, output_file, show
from bokeh.models.widgets import Panel, Slider, Spinner, Tabs, TextInput
from bokeh.models import ColumnDataSource, CustomJS, Div

div_vitamin_a = Div(text='unkown',
                    style={'width': '120px', 'max-width': '120px',
                           'display': 'inline-block',
                           'text-align': 'center',
                           'background-color': 'red',
                           'border': '2px solid', 'border-color': 'black'})

update_vitamin_a = CustomJS(args=dict(div=div_vitamin_a), code="""
    var vit_a = vitamin_a.value;
    console.log(vit_a);
    div.text = vit_a.toString();
    div.style.backgroundColor = 'rgb(255,'+vit_a+','+vit_a+')';

""")

selector_vitamin_a = Slider(title='Vit A', start=0, end=255, step=1, value=50)
update_vitamin_a.args['vitamin_a'] = selector_vitamin_a
selector_vitamin_a.js_on_change('value', update_vitamin_a)

show(row(selector_vitamin_a, div_vitamin_a))

# test datatable updating
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import DataTable, TableColumn, Select
from bokeh.plotting import save, output_file
from pandas_datareader import wb

df = wb.download(indicator='NY.GDP.PCAP.KD', country=['US', 'CA', 'MX'], start=2005, end=2008)
df = df.reset_index()

source = ColumnDataSource(df)
original_source = ColumnDataSource(df)
columns = [
   TableColumn(field="country", title="Country"),
   TableColumn(field="year", title="Year"),
   TableColumn(field="NY.GDP.PCAP.KD", title="NY.GDP.PCAP.KD"),
]
data_table = DataTable(source=source, columns=columns)

# callback code to be used by all the filter widgets
# requires (source, original_source, country_select_obj, year_select_obj, target_object)
combined_callback_code = """
var data = source.data;
var original_data = original_source.data;
var country = country_select_obj.value;
console.log("country: " + country);
var year = year_select_obj.value;
console.log("year: " + year);
for (var key in original_data) {
    data[key] = [];
    for (var i = 0; i < original_data['country'].length; ++i) {
        if ((country === "ALL" || original_data['country'][i] === country) &&
            (year === "ALL" || original_data['year'][i] === year)) {
            data[key].push(original_data[key][i]);
        }
    }
}

source.change.emit();
target_obj.change.emit();
"""

# define the filter widgets, without callbacks for now
country_list = ['ALL'] + df['country'].unique().tolist()
country_select = Select(title="Country:", value=country_list[0], options=country_list)
year_list = ['ALL'] + df['year'].unique().tolist()
year_select = Select(title="Year:", value=year_list[0], options=year_list)

# now define the callback objects now that the filter widgets exist
generic_callback = CustomJS(
    args=dict(source=source,
              original_source=original_source,
              country_select_obj=country_select,
              year_select_obj=year_select,
              target_obj=data_table),
    code=combined_callback_code
)

# finally, connect the callbacks to the filter widgets
country_select.js_on_change('value', generic_callback)
year_select.js_on_change('value', generic_callback)

p = column(country_select,year_select,data_table)
output_file('datatable_filter.html')
show(p)

#-----------------------------------------------------------

from bokeh.layouts import column
from bokeh.models import Slider
from bokeh.plotting import figure, show

plot = figure(plot_width=400, plot_height=400)
r = plot.circle([1,2,3,4,5,], [3,2,5,6,4], radius=0.2, alpha=0.5)

slider = Slider(start=0.1, end=2, step=0.01, value=0.2)
slider.js_link('value', r.glyph, 'radius')

show(column(plot, slider))

#-----------------------------------------------------------

import bokeh.embed
import bokeh.io
import bokeh.models
import bokeh.models.widgets
import bokeh.plotting
import pandas as pd
from pandas_datareader import wb

bokeh.plotting.output_notebook()

df = wb.download(indicator='NY.GDP.PCAP.KD', country=['US', 'CA', 'MX'], start=2005, end=2008)
df = df.reset_index()

source = bokeh.models.ColumnDataSource(df)
original_source = bokeh.models.ColumnDataSource(df)
columns = [
    bokeh.models.widgets.TableColumn(field="country", title="Country"),
    bokeh.models.widgets.TableColumn(field="year", title="Year"),
    bokeh.models.widgets.TableColumn(field="NY.GDP.PCAP.KD", title="NY.GDP.PCAP.KD"),
]
data_table = bokeh.models.widgets.DataTable(source=source, columns=columns)

# callback code to be used by all the filter widgets
# requires (source, original_source, country_select_obj, year_select_obj, target_object)
combined_callback_code = """
var data = source.get('data');
var original_data = original_source.get('data');
var country = country_select_obj.get('value');
console.log("country: " + country);
var year = year_select_obj.get('value');
console.log("year: " + year);
for (var key in original_data) {
    data[key] = [];
    for (var i = 0; i < original_data['country'].length; ++i) {
        if ((country === "ALL" || original_data['country'][i] === country) &&
            (year === "ALL" || original_data['year'][i] === year)) {
            data[key].push(original_data[key][i]);
        }
    }
}
target_obj.trigger('change');
source.trigger('change');
"""

# define the filter widgets, without callbacks for now
country_list = ['ALL'] + df['country'].unique().tolist()
country_select = bokeh.models.widgets.Select(title="Country:", value=country_list[0], options=country_list)
year_list = ['ALL'] + df['year'].unique().tolist()
year_select = bokeh.models.widgets.Select(title="Year:", value=year_list[0], options=year_list)

# now define the callback objects now that the filter widgets exist
generic_callback = bokeh.models.CustomJS(
    args=dict(source=source,
              original_source=original_source,
              country_select_obj=country_select,
              year_select_obj=year_select,
              target_obj=data_table),
    code=combined_callback_code
)

# finally, connect the callbacks to the filter widgets
country_select.js_on_change('value', generic_callback)
year_select.js_on_change('value', generic_callback)

show(column(country_select, year_select, data_table))
p = bokeh.io.vplot(country_select, year_select, data_table)
bokeh.plotting.show(p)


#-----------------------------------------------------------

# import code modules
from bokeh.io import output_file, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS, MultiChoice
from bokeh.models.widgets import DataTable, TableColumn

import pandas as pd

data = pd.DataFrame({'Name': ['A', 'B', 'C', 'D'],
                     'Age': [10, 20, 30, 40],
                     'Sex': ['M', 'F', 'X', 'Y']})

vars = list(data.columns)
initial_vars = vars[:1]

original_data = ColumnDataSource(data)
source = ColumnDataSource(data[initial_vars])

columns = [TableColumn(field=Ci, title=Ci) for Ci in vars]  # bokeh columns
data_table = DataTable(columns=columns, source=source)  # bokeh table

var_selector_callback = CustomJS(args=dict(original_data=original_data, columns=columns, source=source), code="""    
    var original = original_data.data;
    var data = source.data;
    var data_keys = Object.keys(data)
    var selected_vars = cb_obj.value;
    selected_vars.push('index');

    if (data_keys.length < selected_vars.length) {
        var add_var = selected_vars.filter(nut => !data_keys.includes(nut));
        data[add_var] = original[add_var];
    } else {
        var del_var = data_keys.filter(nut => !selected_vars.includes(nut));
        delete data[del_var];
    }
    source.change.emit();
""")

var_selector = MultiChoice(value=initial_vars, options=vars)
var_selector.js_on_change('value', var_selector_callback)
# nutrient_selector.js_link('value', data_table.columns)

output_file("var_selector.html")
show(column(var_selector, data_table))