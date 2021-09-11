import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State
from db import connect_to_db, query_fg, query_tokens, query_futures
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

CONTAINER_STYLE = {
    "margin": "5rem 18rem",
    "padding": "2rem 1rem",
}

content = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label(
                    "Select token"
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
            ], width=3)
        ], style={"padding-top": "1em"})
    ]),
    dcc.Graph(id='fg')
], id="page-content")

heatmap = html.Div(
    [dbc.Row([
        dbc.Col([
            dcc.Graph(id='heatmap')
        ], align="center")
    ], style={"margin": "auto", "width": "50%" })]
)

futures = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Label(
                    "Select token"
            ),
            dcc.Dropdown(
                    options=[
                        {'label': 'Bitcoin', 'value': 'BTC-PERP'},
                        {'label': 'Ethereum', 'value': 'ETH-PERP'},
                        {'label': 'XRP', 'value': 'XRP-PERP'},
                        {'label': 'Chainlink', 'value': 'LINK-PERP'},
                        {'label': 'Litecoin', 'value': 'LTC-PERP'},
                        {'label': 'Cardano', 'value': 'ADA-PERP'},
                        {'label': 'EOS', 'value': 'EOS-PERP'},
                        {'label': 'BNB', 'value': 'BNB-PERP'}
                    ],
                    value=['btc-bitcoin'],
                    id='dropdown-futures'
                ),
        ], width=3)
    ], style={"padding-top": "1em", "padding-bottom": ".5em"}),
    dcc.Graph(id='futures')
])

app.layout = dbc.Container([
    html.H2("Crypto Dashboard"),
    dcc.Store(id="store"),
        dbc.Row([
            dbc.Col([
                dbc.Label(
                    "Select timeframe"
                ),
                dcc.Dropdown(
                    options=[
                             {'label': '7 days', 'value': 7},
                             {'label': '1 month', 'value': 31},
                             {'label': '1 year', 'value': 365}
                        ],
                        value=7,
                        id='dropdown'
                    ),
            ], width='auto')
        ], style={"padding-bottom": "2em"}),
        dbc.Tabs(
            [
                dbc.Tab(futures, label="Futures", tab_id="futures"),
                dbc.Tab(content, label="Fear & Greed", tab_id="fg"),
                dbc.Tab(heatmap, label="Heatmap", tab_id="heatmap"),
            ],
            id="tabs",
            active_tab="futures",
        ),
        html.Div(id="tab-content", className="p-4"),
        dcc.Location(id="url"),
], style=CONTAINER_STYLE)

db = connect_to_db()

# Generating the fear and greed tba
@app.callback(
    Output('fg', 'figure'),
    Input('dropdown', 'value'),
    Input("dropdown-tokens", "value"),)
def update_output(day_value, token_value):
    df_fg, df_filtered_tokens = query_fg(day_value, token_value, db)

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(
        go.Scatter(x=df_filtered_tokens['date'], y=df_filtered_tokens['price'], name="Price"),
        secondary_y=False
    )
    fig1.add_trace(
        go.Scatter(x=df_fg['ts'], y=df_fg['value'], name="Fear & Greed"),
        secondary_y=True,
    )

    fig1.layout.template = 'plotly_dark'

    fig1.update_layout(
        title_text="Token + Fear & Greed"
    )
    fig1.update_layout(showlegend=False,  paper_bgcolor='rgb(6,6,6)')
    fig1.update_yaxes(
        title_text="Token",
        secondary_y=False)
    fig1.update_yaxes(
        title_text="Fear & Greed",
        secondary_y=True)

    return fig1

# Generating the heatmap tab
@app.callback(
    Output('heatmap', 'figure'),
    Input('dropdown', 'value'))
def generate_heatmap(day_value):
    df_tokens = query_tokens(day_value, db)

    reshape = df_tokens.pivot(index='date', columns='symbol', values='price')
    corrM = reshape.corr()
    fig2 = px.imshow(corrM)
    fig2.layout.template = 'plotly_dark'
    fig2.update_xaxes(side="top")
    fig2.update_layout(width=700, height=700, paper_bgcolor='rgb(6,6,6)')

    return fig2

# Generating the futures tab plot
@app.callback(
    Output('futures', 'figure'),
    Input('dropdown', 'value'),
    Input('dropdown-futures', 'value'))
def generate_futures(days, value):
    df_tokens = query_futures(days, value, db)

    fig = px.line(df_tokens,
                  x="date", y="open", color='exchange', template='plotly_dark')
    fig.update_layout(paper_bgcolor='rgb(6,6,6)')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
