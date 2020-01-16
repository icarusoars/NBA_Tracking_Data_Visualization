import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go


app = dash.Dash()

app.layout = html.Div(
    
    children = [
        dcc.Graph(
            id = 'possession-visualizer',
        )
    ]
)




@app.callback(
    Output('possession-visualizer','figure'),
    [Input('game-select-dropdown', 'value'),
     Input('possession-select-dropdown', 'value')]
)
def update_main_graph(game_selected, possession_index):
    


if __name__ == '__main__':
    app.run_server(debug=True)