
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Load and preprocess the data
data_path = 'https://github.com/rmejia41/open_datasets/raw/main/Cleaned_Homicidios_Accidentes_Trafico_C.xlsx'
data = pd.read_excel(data_path)
data['DEPARTAMENTO'] = data['DEPARTAMENTO'].str.upper().str.strip()
data['FECHA HECHO'] = pd.to_datetime(data['FECHA HECHO'])
data['GRUPO ETARÍO'] = data['GRUPO ETARÍO'].replace('NO REPOTADO', 'NO REPORTADO')

label_style_b = {
    'fontSize': '18px',
    'fontFamily': 'Arial, sans-serif',
    'fontWeight': 'bold',
    'color': 'white',
    'backgroundColor': '#007BFF',  # Blue background for the label
    'padding': '5px',
    'borderRadius': '5px',
    'marginBottom': '10px',  # Increased spacing between dropdowns
}

dropdown_style_b = {
    'width': '50%',
    'marginLeft': '0',
    'backgroundColor': 'white',  # Clear/white background for the dropdown
    'marginBottom': '10px',  # Increased spacing between dropdowns
}

title_style = {
    'fontSize': '28px',
    'fontFamily': 'Arial, sans-serif',
    'textAlign': 'center',
    'marginBottom': '10px'
}

layout_b = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Tendencias de Accidentes de Tráfico y Homicidios en Colombia", style=title_style), width=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.Label("Seleccione el Año", style=label_style_b),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(data['Año'].unique())],
                value='Todos los Años',
                clearable=False,
                style=dropdown_style_b
            ),
        ], width=6, style={'textAlign': 'left'}),
    ]),
    dbc.Row([
        dbc.Col([
            html.Label("Seleccione el Departamento", style=label_style_b),
            dcc.Dropdown(
                id='departamento-dropdown',
                options=[{'label': depto, 'value': depto} for depto in sorted(data['DEPARTAMENTO'].unique())],
                value='Todos los Departamentos',
                clearable=False,
                style=dropdown_style_b
            ),
        ], width=6, style={'textAlign': 'left'}),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart'), width=12),
    ])
], fluid=True)
def register_callbacks_b(app):
    @app.callback(
        Output('line-chart', 'figure'),
        [Input('year-dropdown', 'value'),
         Input('departamento-dropdown', 'value')]
    )
    def update_line_chart(selected_year, selected_departamento):
        filtered_data = data.copy()

        if selected_year != 'Todos los Años':
            filtered_data = filtered_data[filtered_data['Año'] == selected_year]

        if selected_departamento != 'Todos los Departamentos':
            filtered_data = filtered_data[filtered_data['DEPARTAMENTO'] == selected_departamento]

        # Group data by date and calculate total number of cases
        aggregated_data = filtered_data.groupby(filtered_data['FECHA HECHO'].dt.date).agg(
            {'CANTIDAD': 'sum'}).reset_index()

        # Calculate the percentage of each category
        total_cases = filtered_data['CANTIDAD'].sum()
        gender_percentage = filtered_data.groupby('GENERO')['CANTIDAD'].sum().div(total_cases).mul(100).round(2)
        arms_percentage = filtered_data.groupby('ARMAS MEDIOS')['CANTIDAD'].sum().div(total_cases).mul(100).round(2)

        # Define maximum cases and buffer for better chart scaling
        max_cases = aggregated_data['CANTIDAD'].max() if not aggregated_data.empty else 0
        y_axis_buffer = max_cases * 0.1  # 10% buffer

        # Ensure gender and arms percentages are calculated correctly
        filtered_data['Gender Percentage'] = filtered_data['GENERO'].apply(lambda x: gender_percentage.get(x, 0))
        filtered_data['Arms Percentage'] = filtered_data['ARMAS MEDIOS'].apply(lambda x: arms_percentage.get(x, 0))

        custom_hover_data = filtered_data.apply(
            lambda row: [row['GENERO'], row['Gender Percentage'], row['ARMAS MEDIOS'], row['Arms Percentage'],
                         row['GRUPO ETARÍO']],
            axis=1
        ).tolist()

        # Create the line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=aggregated_data['FECHA HECHO'],
            y=aggregated_data['CANTIDAD'],
            mode='lines',
            line=dict(width=2),
            customdata=custom_hover_data  # Set customdata for the hover template
        ))

        # Update layout to adjust y-axis range based on the max_cases and buffer
        fig.update_layout(
            title='Tendencia Total de Accidentes de Tráfico y Homicidios con el Tiempo',
            xaxis_title='Fecha',
            yaxis_title='Total de Casos',
            yaxis=dict(range=[0, max_cases + y_axis_buffer]),
            hovermode='x',
            template='plotly_white'
        )

        # Update hover template to use custom data
        hover_template = '<b>Fecha</b>: %{x}<br>' \
                         '<b>Total de Casos</b>: %{y}<br>' \
                         '<b>Género</b>: %{customdata[0]} - %{customdata[1]}% <br>' \
                         '<b>Armas y Medios</b>: %{customdata[2]} - %{customdata[3]}%'
        fig.update_traces(hovertemplate=hover_template)

        return fig
