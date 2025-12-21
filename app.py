# dashboard/app.py
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from threading import Timer
import webbrowser

from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State

# --- Load data (CSV recommended) ---
# Make sure cleaned_weather.csv is in the same folder as this file.
df = pd.read_csv("cleaned_weather.csv", parse_dates=['last_updated'], low_memory=False)

# Ensure datetime parsed
df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')

# derive helper columns
df['year'] = df['last_updated'].dt.year
df['month'] = df['last_updated'].dt.month
df['month_name'] = df['last_updated'].dt.strftime('%b')
df['date'] = df['last_updated'].dt.date

# Season mapping (Northern Hemisphere style, but this is a simple global heuristic)
def month_to_season(m):
    if m in [12, 1, 2]:
        return 'Winter'
    if m in [3, 4, 5]:
        return 'Spring'
    if m in [6, 7, 8]:
        return 'Summer'
    return 'Autumn'

df['season'] = df['month'].apply(lambda x: month_to_season(x) if not np.isnan(x) else None)

# Metrics mapping (label -> column)
METRICS = {
    'Temperature (°C)': 'temperature_celsius',
    'Humidity (%)': 'humidity',
    'Wind Speed (kph)': 'wind_kph',
    'Precipitation (mm)': 'precip_mm',
    'Air Quality PM2.5': 'air_quality_PM2.5'  # change if your column name differs
}

# Clean up - drop rows without date
df = df.dropna(subset=['last_updated'])

# Setup app with a Bootstrap stylesheet for nicer default styling
external_stylesheets = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Date range defaults
MIN_DATE = df['last_updated'].min().date()
MAX_DATE = df['last_updated'].max().date()

# Sidebar style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "260px",
    "padding": "20px",
    "background-color": "#f8f9fa"
}

CONTENT_STYLE = {
    "margin-left": "280px",
    "margin-right": "20px",
    "padding": "20px 10px"
}

card_style = {
    'backgroundColor': 'white',
    'padding': '12px',
    'borderRadius': '8px',
    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
    'marginBottom': '12px'
}

# Layout
app.layout = html.Div([
    html.Div([
        html.H3("ClimateScope", style={'color': '#2c3e50'}),
        html.P("Interactive Climate Dashboard", className="text-muted"),
        html.Hr(),

        html.Label("Country"),
        dcc.Dropdown(
            id='country_dropdown',
            options=[{'label': c, 'value': c} for c in sorted(df['country'].dropna().unique())],
            value=sorted(df['country'].dropna().unique())[0],
            clearable=False
        ),
        html.Br(),

        html.Label("Year"),
        dcc.Dropdown(
            id='year_dropdown',
            options=[{'label': str(int(y)), 'value': int(y)} for y in sorted(df['year'].dropna().unique())],
            value=int(df['year'].dropna().unique().max()),
            clearable=True,
            multi=False
        ),
        html.Br(),

        html.Label("Month"),
        dcc.Dropdown(
            id='month_dropdown',
            options=[{'label': m, 'value': i} for i, m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], start=1)],
            placeholder="All months",
            multi=True
        ),
        html.Br(),

        html.Label("Season"),
        dcc.Checklist(
            id='season_checklist',
            options=[{'label': s, 'value': s} for s in df['season'].dropna().unique()],
            value=[],
            labelStyle={'display': 'block'}
        ),
        html.Br(),

        html.Label("Metric"),
        dcc.Dropdown(
            id='metric_dropdown',
            options=[{'label': k, 'value': v} for k, v in METRICS.items() if v in df.columns],
            value='temperature_celsius',
            clearable=False
        ),
        html.Br(),

        html.Label("Date range"),
        dcc.DatePickerRange(
            id='date_range',
            min_date_allowed=MIN_DATE,
            max_date_allowed=MAX_DATE,
            start_date=MIN_DATE,
            end_date=MAX_DATE,
            display_format='YYYY-MM-DD'
        ),
        html.Hr(),
        html.Button("Reset Filters", id='reset_filters', n_clicks=0, className="btn btn-secondary btn-block")
    ], style=SIDEBAR_STYLE),

    html.Div([
        # Header + KPIs
        html.Div([
            html.Div([
                html.H2("ClimateScope — Interactive Dashboard", style={'textAlign': 'center', 'color': '#1f2c56'}),
            ], style={'width': '100%'}),
            html.Div([
                html.Div(id='kpi_avg', className='col-sm-3', style=card_style),
                html.Div(id='kpi_max', className='col-sm-3', style=card_style),
                html.Div(id='kpi_min', className='col-sm-3', style=card_style),
                html.Div(id='kpi_latest', className='col-sm-3', style=card_style)
            ], className='d-flex justify-content-between', style={'marginTop': '16px', 'gap': '10px'})
        ]),

        html.Hr(),

        # Tabs for sections
        dcc.Tabs(id='tabs', value='tab-overview', children=[
            dcc.Tab(label='Overview', value='tab-overview'),
            dcc.Tab(label='Time Series', value='tab-timeseries'),
            dcc.Tab(label='Monthly', value='tab-monthly'),
            dcc.Tab(label='Map', value='tab-map'),
        ]),

        html.Div(id='tab-content', style={'marginTop': '16px'})
    ], style=CONTENT_STYLE)
])

# --- Helpers ---
def filter_df(country, year, months, seasons, start_date, end_date):
    sub = df.copy()
    if country:
        sub = sub[sub['country'] == country]
    if year:
        sub = sub[sub['year'] == int(year)]
    if months and len(months) > 0:
        sub = sub[sub['month'].isin(months)]
    if seasons and len(seasons) > 0:
        sub = sub[sub['season'].isin(seasons)]
    if start_date:
        sub = sub[sub['last_updated'] >= pd.to_datetime(start_date)]
    if end_date:
        sub = sub[sub['last_updated'] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]
    return sub

# --- Callbacks ---

@app.callback(
    Output('month_dropdown', 'value'),
    Input('reset_filters', 'n_clicks'),
    prevent_initial_call=True
)
def reset_months(n):
    # Clear months on reset
    return []

@app.callback(
    Output('year_dropdown', 'value'),
    Input('reset_filters', 'n_clicks'),
    prevent_initial_call=True
)
def reset_year(n):
    return int(df['year'].dropna().unique().max())

@app.callback(
    Output('season_checklist', 'value'),
    Input('reset_filters', 'n_clicks'),
    prevent_initial_call=True
)
def reset_season(n):
    return []

@app.callback(
    Output('date_range', 'start_date'),
    Output('date_range', 'end_date'),
    Input('reset_filters', 'n_clicks'),
    prevent_initial_call=True
)
def reset_dates(n):
    return MIN_DATE, MAX_DATE

@app.callback(
    Output('tab-content', 'children'),
    [
        Input('tabs', 'value'),
        Input('country_dropdown', 'value'),
        Input('year_dropdown', 'value'),
        Input('month_dropdown', 'value'),
        Input('season_checklist', 'value'),
        Input('metric_dropdown', 'value'),
        Input('date_range', 'start_date'),
        Input('date_range', 'end_date')
    ]
)
def render_tab(tab, country, year, months, seasons, metric, start_date, end_date):
    months = months or []
    seasons = seasons or []
    sub = filter_df(country, year, months, seasons, start_date, end_date)

    # Basic empty check
    if sub.empty:
        return html.Div([html.H4("No data for selected filters. Try expanding the date range or clearing filters.")])

    # KPIs values (for selected metric)
    metric_name = [k for k, v in METRICS.items() if v == metric]
    metric_label = metric_name[0] if metric_name else metric

    avg_val = round(sub[metric].mean(), 2) if metric in sub.columns else 'N/A'
    max_val = round(sub[metric].max(), 2) if metric in sub.columns else 'N/A'
    min_val = round(sub[metric].min(), 2) if metric in sub.columns else 'N/A'
    latest_row = sub.sort_values('last_updated').iloc[-1]
    latest_val = round(latest_row[metric], 2) if metric in sub.columns else 'N/A'
    latest_date = latest_row['last_updated'].strftime('%Y-%m-%d %H:%M')

    kpis = html.Div([
        html.Div([
            html.H6("Avg " + metric_label, className="text-muted"),
            html.H3(f"{avg_val}", style={'color':'#2c3e50'})
        ], style={'flex': '1', **card_style}),

        html.Div([
            html.H6("Max " + metric_label, className="text-muted"),
            html.H3(f"{max_val}", style={'color':'#e74c3c'})
        ], style={'flex': '1', **card_style}),

        html.Div([
            html.H6("Min " + metric_label, className="text-muted"),
            html.H3(f"{min_val}", style={'color':'#3498db'})
        ], style={'flex': '1', **card_style}),

        html.Div([
            html.H6("Latest reading"),
            html.H5(f"{latest_val} @ {latest_date}", style={'color':'#16a085'})
        ], style={'flex': '1', **card_style})
    ], className='d-flex', style={'gap': '10px', 'marginBottom': '18px'})

    # Tab: Overview
    if tab == 'tab-overview':
        fig_ts = px.line(sub.sort_values('last_updated'), x='last_updated', y=metric,
                         title=f"{metric_label} over time — {country}", markers=True)
        fig_month = px.bar(
            sub.groupby(sub['month_name']).mean(numeric_only=True).reindex(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']).reset_index(),
            x='month_name', y=metric, title=f"Average by Month — {metric_label}"
        )
        return html.Div([
            kpis,
            dcc.Graph(figure=fig_ts),
            dcc.Graph(figure=fig_month)
        ])

    # Tab: Time Series (detailed)
    if tab == 'tab-timeseries':
        fig = px.line(sub.sort_values('last_updated'), x='last_updated', y=metric,
                      title=f"{metric_label} Time Series — {country}", markers=False)
        fig.update_layout(yaxis_title=metric_label, xaxis_title='Date')
        return html.Div([kpis, dcc.Graph(figure=fig)])

    # Tab: Monthly
    if tab == 'tab-monthly':
        monthly = sub.groupby(['year','month']).mean(numeric_only=True).reset_index()
        monthly['month'] = montwindohly['month'].astype(int)
        monthly = monthly.sort_values(['year','month'])
        fig = px.line(monthly, x='month', y=metric, color=monthly['year'].astype(str),
                      title=f"Monthly trend by year ({metric_label})", markers=True,
                      labels={'month':'Month (1-12)', 'color':'Year'})
        return html.Div([kpis, dcc.Graph(figure=fig)])

    # Tab: Map
    if tab == 'tab-map':
        # Country-level aggregation for map
        country_avg = df.groupby('country', as_index=False).mean(numeric_only=True)
        if metric not in country_avg.columns:
            return html.Div([html.P("Selected metric not available for map.")])
        fig = px.choropleth(
            country_avg,
            locations='country',
            locationmode='country names',
            color=metric,
            title=f"Average {metric_label} — World",
            color_continuous_scale='thermal'
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        return html.Div([kpis, dcc.Graph(figure=fig, style={'height':'700px'})])

    # Fallback
    return html.Div([html.P("Unknown tab")])

# Run server (open browser automatically)
def open_browser():
    url = "http://127.0.0.1:8050/"
    webbrowser.open(url, new=2)

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=False, host='127.0.0.1', port=8050)
