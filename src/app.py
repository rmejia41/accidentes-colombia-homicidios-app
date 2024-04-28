import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from src.app_a import layout_a, register_callbacks_a
from src.app_b import layout_b, register_callbacks_b

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Nav(
        [
            dbc.NavLink("Mapa Interactivo", href="/", active="exact"),
            dbc.NavLink("Tendencia de Homicidios", href="/tendencia-homicidios", active="exact")
        ],
        pills=True,
    ),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/tendencia-homicidios':
        return layout_b
    else:
        return layout_a

# Register callbacks for each app
register_callbacks_a(app)
register_callbacks_b(app)

if __name__ == '__main__':
    app.run_server(debug=False, port=8051)
