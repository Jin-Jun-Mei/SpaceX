# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique()
sites_option = [{'label': site, 'value': site} for site in launch_sites]
sites_option.append({'label':'All Sites', 'value':'All'})
# print(sites_option)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown'
                                    ,options = sites_option
                                    ,value = 'all'
                                    ,placeholder = 'Select a Launch Site here'
                                    ,searchable = True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider'
                                                , min = 0 ,max = 10000, step = 1000 #kg
                                                , marks = {0:'0', 5000: '5000' , 10000: '10000'}
                                                , value = [min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id = 'success-pie-chart', component_property = 'figure'),
    Input(component_id = 'site-dropdown', component_property = 'value')
)

def get_pie_chart(entered_site):
    if entered_site == 'All':
        data = spacex_df.groupby('Launch Site')['class'].mean().reset_index()
        fig = px.pie(data
                    ,values = 'class'
                    ,names = 'Launch Site'
                    ,title = 'Total Success Lauches By Sites'
                    )
    else:
        data = spacex_df[spacex_df['Launch Site'] == entered_site]['class'].value_counts().reset_index()
        #print(data)
        fig = px.pie(data
                    ,values = 'count'
                    ,names = 'class'
                    ,title = 'Total Success Lauches for Sites' + entered_site
                    )
    return fig   

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id = 'success-payload-scatter-chart', component_property = 'figure'),
    [Input(component_id = 'site-dropdown', component_property = 'value')
    , Input(component_id='payload-slider', component_property='value')
    ]
)

def get_scatter_plot (entered_site,payload_value):
    if entered_site != 'All':
        data = spacex_df[spacex_df['Launch Site'] == entered_site][['Payload Mass (kg)','class','Booster Version Category']].reset_index()
    else:
        data = spacex_df

    data = data[(data['Payload Mass (kg)'] >= payload_value[0])
                & (data['Payload Mass (kg)'] <= payload_value[1])
                ]
    #print(data)
    fig = px.scatter(data
                    , x='Payload Mass (kg)'
                    , y='class'
                    ,color='Booster Version Category'
                    ,title = 'Correlation between Paylaod and Success for Sites' + entered_site
                    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
