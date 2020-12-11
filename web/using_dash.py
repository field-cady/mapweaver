import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import flask
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__) # define flask app.server

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server) # call flask server

# run following in command
# gunicorn graph:app.server -b :8000

df = pd.read_csv('/home/taco/paris.csv')
lat_eps = np.random.uniform(-0.002, 0.002, size=df.shape[0])
lon_eps = np.random.uniform(-0.002, 0.002, size=df.shape[0])
df['lat'] += lat_eps
df['lon'] += lon_eps
df['idx'] = df.index.astype(str)

df['record'] = df.to_dict(orient='records')

# Category column
main_categories = ['Monitoring Violations', 'Effluent Violations', 'Reporting Violations']
category_checklist_div = html.Div([
    html.H3('Categories'),
    dcc.Checklist(
        id='category_checklist',
        options=[{'label': c, 'value': c} for c in main_categories] + [{'label': 'Other', 'value': ''}],
        value=main_categories+['']
    )
], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'})

# Permit Type column
main_types = [
    'Municipal NPDES IP',
    'Industrial NPDES IP',
    'Industrial (IU) to POTW/PRIVATE SWDP IP',
    'Municipal to ground SWDP IP',
    'Industrial to ground SWDP IP',
    'Sand and Gravel GP',
    'Reclaimed Water IP'
]
type_checklist_div = html.Div([
    html.H3('Permit Types'),
    dcc.Checklist(
        id='type_checklist',
        options=[{'label': c, 'value': c} for c in main_types] + [{'label': 'Other', 'value': ''}],
        value=main_types+['']
    )
], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'})

def make_row(elems):
    elems_new = [
        html.Div(e, style={'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': '0vw', 'margin-top': '0vw'})
        for e in elems]
    return html.Div(elems_new, style={'className': 'row'})

app.layout = html.Div([
    html.H1('PARIS Violations in Last Year'),
    html.Div(id='text-content'),
    html.Div([
        category_checklist_div,
        type_checklist_div
    ], style={'className': 'row'}),
    html.Div([
        html.Div([dcc.Graph(id='map', figure={
            'data': [{
                'lat': df['lat'],
                'lon': df['lon'],
                'marker': {
                    #'color': df['YEAR'],
                    'size': 8,
                    'opacity': 0.6
                },
                'customdata': df['idx'],
                'type': 'scattermapbox'
            }],
            'layout': {
                'mapbox': {
                    'center': {'lon':-120, 'lat': 48},
                    'accesstoken': 'pk.eyJ1IjoiZmllbGRjYWR5IiwiYSI6ImNqd3Rmb2d3bjBkMDA0OW5yamYxNnRwdGwifQ.kBilx8iMkTn8RUyrO7ZHGA',
                    'zoom': 5
                },
                'hovermode': 'closest',
                'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
            }
        })
        ], style={'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': '0vw', 'margin-top': '0vw', 'width':'70%'}),
        html.Div(id='violation-summary',
                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw', 'margin-top': '0vw'})
    ], style={'className': 'row'})
])



@app.callback(
    dash.dependencies.Output('violation-summary', 'children'),
    [dash.dependencies.Input('map', 'clickData')])
def update_summary_text(clickData):
    print('\n**In update_summary_text')
    print(clickData)
    #s = df.iloc[clickData['points'][0]['pointNumber']]
    s = df[df.idx==clickData['points'][0]['customdata']].iloc[0]
    rec = dict(zip(s.index, s))
    print('rec:', rec)
    print('\n--B\n')
    fac_url = 'https://apps.ecology.wa.gov/paris/FacilitySummary.aspx?FacilityId='+str(rec['FacilityId'])
    fac_link = html.A(rec['Facility Name'], href=fac_url)
    violation_url = 'https://apps.ecology.wa.gov/paris/ComplianceAndViolations/PopupViolationTrigger.aspx?ViolationId='+str(rec['ViolationId'])
    violation_link = html.A(rec['ViolationId'], href=violation_url)
    print('\n--C\n')
    return html.Div([
        html.H3('Details'),
        make_row([html.H6('Facility: '), fac_link]),
        make_row([html.H6('Violation: '), violation_link]),
        make_row([html.H6('Category: '), rec['Category']]),
        make_row([html.H6('Date: '), rec['Violation Date']])
    ])




@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [
        dash.dependencies.Input('category_checklist', 'value'),
        dash.dependencies.Input('type_checklist', 'value')
    ])
def update_map(category_checklist_value, type_checklist_value):
    print('\n** In update_map')
    print('making new map w scale down', category_checklist_value, 'w other fix')
    print('  making new map w scale down', type_checklist_value, 'w other fix')
    #df['lat'] = df['lat'] / 2
    df['False'] = False
    to_keep_category = df['False']
    for v in category_checklist_value:
        if v in main_categories:
            to_keep_category = to_keep_category | df['Category'].str.contains(v)
        else:
            is_other = ~df['Category'].isin(main_categories)
            to_keep_category = to_keep_category | is_other
    to_keep_type = df['False']
    for v in type_checklist_value:
        if v in main_types:
            to_keep_type = to_keep_type | df['Permit Type'].str.contains(v)
        elif v=='':
            is_other = ~df['Permit Type'].isin(main_types)
            to_keep_type = to_keep_type | is_other
        else: raise Exception('Problem w type', v)
    to_keep = to_keep_category & to_keep_type
    print('keeping', to_keep.sum())
    ddf = df[to_keep]
    figure={
        'data': [{
            'lat': ddf['lat'],
            'lon': ddf['lon'],
            'customdata': ddf['idx'],
            'marker': {
                #'color': df['YEAR'],
                'size': 8,
                'opacity': 0.6
            },
            'idx': ddf['idx'],
            'type': 'scattermapbox'
        }],
        'layout': {
            'mapbox': {
                'center': {'lon':-120, 'lat': 48},
                'accesstoken': 'pk.eyJ1IjoiZmllbGRjYWR5IiwiYSI6ImNqd3Rmb2d3bjBkMDA0OW5yamYxNnRwdGwifQ.kBilx8iMkTn8RUyrO7ZHGA',
                'zoom': 5
            },
            'hovermode': 'closest',
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
        }
    }
    return figure

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)



'''
@app.callback(
    dash.dependencies.Output('text-content', 'children'),
    [dash.dependencies.Input('map', 'hoverData')])
def update_text(hoverData):
    #s = df[df['storenum'] == hoverData['points'][0]['customdata']]
    s = df[df['FacilityId'] == hoverData['points'][0]['customdata']]
    #return html.H3(s.iloc[0]['FacilityId'])
    return html.H3(str(s.iloc[0]['Category']) + '--' + str(s.iloc[0]['FacilityId']))
    return html.H3(
        'The {}, {} {} opened in {}'.format(
            s.iloc[0]['STRCITY'],
            s.iloc[0]['STRSTATE'],
            s.iloc[0]['type_store'],
            s.iloc[0]['YEAR']
        )
    )
'''