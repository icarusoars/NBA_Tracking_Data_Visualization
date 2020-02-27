import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import dash_daq as daq

import pandas as pd

game_df = pd.read_csv('./test.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

title = html.Div(
    children = [
        dbc.Row(
            id = 'top',
            children = [
                dbc.Col(
                    id = 'title',
                    width = {'offset': 2, 'size': 8},
                    children = [
                        html.H2(
                            "NBA Possession Visualizer",
                            style = {'text-align': 'center'}
                        )
                    ]
                ),
                dbc.Col(
                    id = 'github',
                    width = 2,
                    children = [
                        dbc.Button(
                            "Github", outline=True, color="secondary", className="mr-1",
                            id = "github-button"
                        ),
                    ]
                )
            ]
        )
    ]
)


content_left = dbc.Col(
    id = 'content-left',
    width = 3,
    children = [
        html.Div(
            className = 'wrapper-panel',
            id = 'panel-prelims-filter',
            children = [
                html.H5(
                    'Possession Select'
                ),
                html.P(
                    "Select Game:"
                ),
                dcc.Dropdown(
                    id = 'game-select',
                    options  = [
                        {'label': 'ECF Game 1', 'value': 'ECF1'},
                        {'label': 'ECF Game 2', 'value': 'ECF2'},
                        {'label': 'ECF Game 3', 'value': 'ECF3'}
                    ]
                ),
                html.P(
                    "Select Possession:"
                ),
                dcc.Dropdown(
                    id = 'possession-select',
                    options  = [
                        {'label': '{}'.format(i), 'value': i} for i in game_df['poss_idx'].unique()
                    ]
                )
            ]
        ),
        html.Div(
            className = 'wrapper-panel',
            id = 'panel-visuals',
            children = [
                html.H5(
                    'Visuals'
                ),
                html.P(
                    'Court Lines'
                ),
                dcc.Input(
                    id = 'court-color',
                    type = 'text',
                    value = '#444444'
                ),
                html.P(
                    'Offensive Players'
                ),
                dcc.Input(
                    id = 'offensive-color',
                    type = 'text',
                    value = '#b82601'
                ),
                html.P(
                    'Defensive Players'
                ),
                dcc.Input(
                    id = 'defensive-color',
                    type = 'text',
                    value = '#888888'
                ),
                html.P(
                    'Show Ball'
                ),
                daq.BooleanSwitch(
                    id='showball-toggle',
                    on=False
                )
            ]
        )
    ]
)



content_right = dbc.Col(
    id = 'content-right',
    width = 9,
    children = [
        html.Div(
            className = 'wrapper-panel',
            id = 'panel-visualizer',
            children = [
                dcc.Graph(
                    id = 'possession-visualizer',
                    figure = {
                        'layout': go.Layout(
                            margin = {'t': 0, 'b': 20, 'l': 0, 'r': 0, 'pad': 5},
                            plot_bgcolor = '#f9f9f9',
                            legend = go.layout.Legend(
                                bgcolor = '#f9f9f9'
                            ),
                            paper_bgcolor = '#f9f9f9'
                        ),
                        'data': [
                            {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Montréal'},
                        ],
                    }
                )
            ]
        ),
        html.Div(
            className = 'wrapper-panel',
            children = [
                dcc.Slider(
                    id = 'possession-slider',
                    step = None
                )
            ]
        )
    ]
)



content = html.Div(
    children = [
        dbc.Row(
            id = 'content',
            children = [
                content_left,
                content_right
            ]
        )
    ]
)

app.layout = html.Div([
    title,
    content
])


@app.callback(
    Output('possession-visualizer','figure'),
    [Input('game-select', 'value'),
     Input('possession-select', 'value'),
     Input('court-color', 'value'),
     Input('offensive-color', 'value'),
     Input('defensive-color', 'value'),
     Input('showball-toggle', 'on'),
     Input('possession-slider', 'value')
     ]
)
def update_visualilzer(game_select, poss_select, court_color,
                       off_color, def_color, showball, poss_slider):
    print(game_select, poss_select, court_color, off_color,
                       def_color, showball, poss_slider)

    return {}


@app.callback(
    [Output('possession-slider','disabled'),
     Output('possession-slider','marks'),
     Output('possession-slider','min'),
     Output('possession-slider','max'),
     Output('possession-slider','value'),
    ],
    [Input('game-select', 'value'),
     Input('possession-select', 'value')
    ]
)
def update_slider(game_select, poss_select):
    if game_select is None or poss_select is None:
        return True, {}, 0, 10, 0
    else:
        filter_df = game_df[game_df.poss_idx == poss_select]
        start_time = filter_df.shotClock.max()
        end_time = filter_df.shotClock.min()
        print(start_time, end_time)
        markers = {(24 - time): '' for time in filter_df['shotClock'].unique()}
        markers[(24 - start_time)] = str(start_time) + 's'
        markers[(24 - end_time)] = str(end_time) + 's'

        return False, markers, 24-start_time, 24-end_time, 24-start_time


if __name__ == '__main__':
    app.run_server(debug=True)