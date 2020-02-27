import dash
from dash.dependencies import Input, Output


@app.callback(
    Output('possession-visualizer','figure'),
    [Input('game-select', 'value'),
     Input('possession-select', 'value'),
     Input('court-color', 'value'),
     Input('offensive-color', 'value'),
     Input('defensive-color', 'value'),
     Input('showball-toggle', 'value'),
     Input('possession-slider', 'value')
     ]
)
def update_visualilzer(game_selected, possession_index):
    