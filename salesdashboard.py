import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
import io

# Initialize Dash app
app = dash.Dash(__name__)
# Read the CSV data into a pandas dataframe
data = pd.read_csv('historical_automobile_sales.csv')

# Ensure that the columns are as expected

# Layout of the app
app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard", style={'textAlign': 'center', 'color': '#503D36', 'font-size': '24px'}),
    
    # Dropdown for report type
    dcc.Dropdown(
        id='dropdown-statistics',
        options=[
            {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
            {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
        ],
        value='Select Statistics',
        placeholder='Select a report type',
        style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
    ),
    
    # Dropdown for selecting year
    dcc.Dropdown(
        id='select-year',
        options=[{'label': i, 'value': i} for i in range(1980, 2024)],
        value='Select Year',
        placeholder='Select Year',
        style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
    ),
    
    # Output container for displaying graphs
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})
    ])
])

# Callback for enabling/disabling the year dropdown based on report type selection
@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False  # Enable year dropdown
    else:
        return True  # Disable year dropdown

# Callback for updating the output container with graphs
@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'), Input('select-year', 'value')]
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':
        # Filter data for recession periods
        recession_data = data[data['Recession'] == 1]
        
        # Plot 1: Automobile sales fluctuate over Recession Period (year-wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', title="Average Automobile Sales fluctuation over Recession Period"))
        
        # Plot 2: Average number of vehicles sold by vehicle type
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales', title="Average Vehicles Sold by Vehicle Type"))
        
        # Plot 3: Pie chart for total expenditure share by vehicle type
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type', title="Total Expenditure Share by Vehicle Type"))
        
        # Plot 4: Effect of unemployment rate on vehicle type and sales
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type', 
                                          labels={'unemployment_Rate': 'unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                                          title='Effect of Unemployment Rate on Vehicle Type and Sales'))
        
        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)], style={'display': 'flex'})
        ]
    
    elif selected_statistics == 'Yearly Statistics' and input_year:
        # Filter data for the selected year
        yearly_data = data[data['Year'] == input_year]
        
        # Plot 1: Yearly Automobile sales using line chart
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales', title="Yearly Automobile Sales"))
        
        # Plot 2: Total Monthly Automobile sales using line chart
        mas = data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(mas, x='Month', y='Automobile_Sales', title="Total Monthly Automobile Sales"))
        
        # Plot 3: Average number of vehicles sold during the year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales', title=f"Average Vehicles Sold by Vehicle Type in {input_year}"))
        
        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type', title=f"Total Advertisement Expenditure for Each Vehicle in {input_year}"))
        
        return [
            html.Div(className='chart-item', children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)], style={'display': 'flex'})
        ]
    
    return None

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
