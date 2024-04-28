
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Load the data
data_path = 'https://github.com/rmejia41/open_datasets/raw/main/Cleaned_Homicidios_Accidentes_Trafico_C.xlsx'
#C:/Users/Biu9/Desktop/Homicidios Accidentes Colombia/Cleaned_Homicidios_Accidentes_Trafico_C.xlsx
data = pd.read_excel(data_path)
data['MUNICIPIO'] = data['MUNICIPIO'].str.upper().str.strip()
data['GENERO'] = data['GENERO'].replace({'NO REPORTADO': 'NO REPORTA', 'NO REPOTADO': 'NO REPORTA'})

# Define custom CSS styles for the title, subtitle, and labels
title_style = {
    'fontSize': '28px',
    'fontFamily': 'Arial, sans-serif',
    'textAlign': 'center',
    'marginBottom': '10px'
}
subtitle_style = {
    'fontSize': '22px',
    'fontFamily': 'Arial, sans-serif',
    'textAlign': 'center',
    'marginBottom': '10px',
    'color': 'red'
}
label_style_a = {
    'fontSize': '18px',
    'fontFamily': 'Arial, sans-serif',
    'fontWeight': 'bold',
    'color': 'white',
    'backgroundColor': '#007BFF',  # Blue background for the label
    'padding': '5px',
    'borderRadius': '5px',
    'marginBottom': '5px'
}
dropdown_style_a = {
    'width': '50%',
    'textAlign': 'left',
    'marginRight': '20px',
    'backgroundColor': 'white',  # Clear/white background for the dropdown
}

# Define the link to Datos Abiertos: Policia Nacional
link = html.A(
    'Datos Abiertos: Policia Nacional',
    href='https://www.datos.gov.co/Seguridad-y-Defensa/Homicidios-accidente-de-tr-nsito-Polic-a-Nacional/ha6j-pa2r/about_data',
    target='_blank',
    style={'color': 'blue', 'fontSize': '50%'}
)
layout_a = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1(
            [html.Div(link, style={'textAlign': 'right'}), "CASOS DE HOMICIDIO POR ACCIDENTES DE TRANSITO EN COLOMBIA"],
            style=title_style, className="text-center mb-4"), width=12)
    ]),
    html.H2("Homicidio Culposo", style=subtitle_style, className="text-center mb-3"),
    dbc.Row([
        dbc.Col([
            html.Label("Seleccione el Año", style=label_style_a),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': 'Todos Los Casos', 'value': 'Todos Los Casos'}] + [{'label': x, 'value': x} for x in sorted(data['Año'].unique())],
                value='Todos Los Casos',
                clearable=False,
                style=dropdown_style_a
            )
        ], width=6)
    ], style={'marginBottom': 5, 'marginTop': 5}),
    dbc.Row([
        dbc.Col([
            html.Label("Seleccione el Municipio", style=label_style_a),
            dcc.Dropdown(
                id='municipio-dropdown',
                options=[{'label': 'Todos Los Casos', 'value': 'Todos Los Casos'}] + [{'label': x, 'value': x} for x in sorted(data['MUNICIPIO'].unique())],
                value='Todos Los Casos',
                clearable=False,
                style=dropdown_style_a
            )
        ], width=6)
    ], style={'marginBottom': 5, 'marginTop': 5}),
    dbc.Row([
        dbc.Col(dcc.Graph(
            id='map-graph',
            style={'height': '650px', 'width': '85%', 'marginLeft': 'auto', 'marginRight': 'auto', 'marginTop': '-4px'}
        ), width=14)
    ], justify='center')
], fluid=True)

def register_callbacks_a(app):
    @app.callback(
        Output('map-graph', 'figure'),
        [Input('year-dropdown', 'value'),
         Input('municipio-dropdown', 'value')]
    )
    def update_map(selected_year, selected_municipio):
        filtered_data = data.copy()
        if selected_year != 'Todos Los Casos':
            filtered_data = filtered_data[filtered_data['Año'] == selected_year]
        if selected_municipio != 'Todos Los Casos':
            filtered_data = filtered_data[filtered_data['MUNICIPIO'] == selected_municipio]

        if selected_year != 'Todos Los Casos' or selected_municipio != 'Todos Los Casos':
            filtered_data = filtered_data.groupby(['LATITUDE', 'LONGITUDE', 'MUNICIPIO', 'Año', 'GENERO']).agg({
                'CANTIDAD': 'sum',
                'ARMAS MEDIOS': lambda x: ', '.join([f"{k}: {v:.2%}" for k, v in pd.Series(x).value_counts(normalize=True).items()])
            }).reset_index()

        hover_data = ['MUNICIPIO', 'Año', 'GENERO', 'CANTIDAD', 'ARMAS MEDIOS']
        fig = px.scatter_mapbox(
            filtered_data,
            lat='LATITUDE',
            lon='LONGITUDE',
            color='GENERO',
            size='CANTIDAD',
            hover_data=hover_data,
            zoom=5,
            title="Casos de Homicidio según su Localización Geográfica",
            size_max=13  # Size of the markers
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_geos(fitbounds="locations")
        return fig

