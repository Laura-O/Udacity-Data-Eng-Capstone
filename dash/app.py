from datetime import date
import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State
from db import connect_to_db, query_fg, query_tokens
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "Select timespan", className="lead"
        ),
        dbc.Nav(
            [
                dcc.Dropdown(
                    options=[
                        {'label': '7 days', 'value': 7},
                        {'label': '1 month', 'value': 31},
                        {'label': '1 year', 'value': 365}
                    ],
                    value=7,
                    id='dropdown'
                )
            ],
            vertical=True,
            pills=True,
        ),
        html.P(
            "Select tokens", className="lead"
        ),
        dcc.Dropdown(
            options=[
                {'label': 'Bitcoin', 'value': 'btc-bitcoin'},
                {'label': 'Ethereum', 'value': 'eth-ethereum'},
                {'label': 'Solana', 'value': 'sol-solana'},
                {'label': 'Cardano', 'value': 'ada-cardano'},
                {'label': 'XRP', 'value': 'xrp-xrp'},
                {'label': 'Doge', 'value': 'doge-dogecoin'},
                {'label': 'Dot', 'value': 'dot-polkadot'},
                {'label': 'Uniswap', 'value': 'uni-uniswap'},
                {'label': 'Litecoin', 'value': 'ltc-litecoin'},
                {'label': 'Luna', 'value': 'luna-terra'},
                {'label': 'Link', 'value': 'link-chainlink'},
                {'label': 'ICP', 'value': 'icp-internet-computer'},
                {'label': 'Matic', 'value': 'matic-polygon'},
                {'label': 'Avax', 'value': 'avax-avalanche'},
                {'label': 'Vechain', 'value': 'vet-vechain'}
            ],
            value=['btc-bitcoin'],
            id='dropdown-tokens'
        )
    ],
    style=SIDEBAR_STYLE,
)


content = html.Div([
    dcc.Graph(id='fg'),
    dcc.Graph(id='tokens')
], id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

db = connect_to_db()


@app.callback(
    Output('fg', 'figure'),
    Output('tokens', 'figure'),
    Input('dropdown', 'value'),
    Input("dropdown-tokens", "value"),)
def update_output(day_value, token_value):
    df_fg, df_filtered_tokens = query_fg(day_value, token_value, db)
    df_tokens = query_tokens(day_value, db)

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(
        go.Scatter(x=df_filtered_tokens['date'], y=df_filtered_tokens['price'], name="Price"),
        secondary_y=False,
    )
    fig1.add_trace(
        go.Scatter(x=df_fg['ts'], y=df_fg['value'], name="Fear & Greed"),
        secondary_y=True,
    )
    fig1.update_layout(
        title_text="Token + Fear & Greed"
    )
    fig1.update_layout(showlegend=False)
    fig1.update_yaxes(
        title_text="Token",
        secondary_y=False)
    fig1.update_yaxes(
        title_text="Fear & Greed",
        secondary_y=True)


    reshape = df_tokens.pivot(index='date', columns='symbol', values='price')
    corrM = reshape.corr()
    fig2 = px.imshow(corrM)
    fig2.update_xaxes(side="top")
    fig2.update_layout(width=700, height=700)

    return fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=True)
