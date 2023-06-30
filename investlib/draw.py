from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd 

def run_dashboard(p, bench):
    ############################ RENDER ######################à
    app = Dash(__name__)
    eq_fig = px.line(y=p.eq, x=p.eq.index, labels=dict(y='Equity',x='Years'))
    eq_fig.add_trace(go.Scatter(x=p.eq.index, y=p.eq, name="Portfolio", line=dict(color='blue')))

    print(type(p).__name__)

    bench_fig = go.Scatter(y=bench.eq, x=bench.eq.index, line=dict(color='#999'), name="Benchmark")
    dd_bench_fig = go.Scatter(y=bench.dd, x=bench.dd.index, line=dict(color='#999'),name="Benchmark")
    
    eq_fig.add_trace(bench_fig)
    dd_fig = px.line(y=p.dd, x=p.dd.index, labels=dict(y='DD',x='Years'))
    dd_fig.add_trace(go.Scatter(x=p.dd.index, y=p.dd, name="Portfolio", line=dict(color='blue')))
    dd_fig.add_trace(dd_bench_fig)

    stats = pd.DataFrame(p.get_stats(), index=['Value']).transpose().reset_index()
    stats_bech = pd.DataFrame(bench.get_stats(), index=['Value']).transpose().reset_index()

    stats['Benchmark'] = stats_bech['Value']
    stats = stats.to_dict('records')

    periods = p.periods.reset_index()
    bench_periods = bench.periods.reset_index()
    periods[['bTot','bdd']] = bench_periods[['Tot','dd']]
    app.layout = html.Div(
        style={'display': 'flex'},  # Imposta display:flex per allineamento orizzontale
        children=[
            html.Div(
                style={'width': '40%'},
                children=[
                    dash_table.DataTable(
                        css=[{"selector": ".dash-spreadsheet tr", "rule": "height: 20px;"}],
                        id='periods_table',
                        columns=[{"name":"Years", "id":"years"}] + [{"name": col.__str__(), "id": col.__str__()} for col in periods.columns.tolist()[1:]],
                        data=periods.to_dict('records'),
                        style_data_conditional= [
                            {
                                'if': {
                                    'column_id': col.__str__(),
                                    'filter_query': '{{{}}} < 0'.format(col.__str__())  # Condizione comune per tutti gli elementi della lista column_id
                                },
                                'backgroundColor': '#f51f1f',
                                'color':'white',
                                'fontWeight':'bold' , 
                            }
                            for col in periods.columns[1:13]
                        ]
                        + [
                            {
                                'if': {
                                    'column_id': col.__str__(),
                                    'filter_query': '{{{}}} > 0'.format(col.__str__())  # Condizione comune per tutti gli elementi della lista column_id
                                },
                                'backgroundColor': '#018700',
                                'color':'white' ,
                                'fontWeight':'bold'  
                            }
                            for col in periods.columns[1:13]
                        ]
                        + [
                            {
                                'if': {
                                    'column_id': ['Tot'],
                                    'filter_query': '{Tot}<0'
                                },
                                'color': '#f51f1f',
                                'fontWeight':'bold'  
                            },
                            {
                                'if': {
                                    'column_id': ['Tot'],
                                    'filter_query': '{Tot}>0'
                                },
                                'color': '#018700',
                                'fontWeight':'bold'  
                            },
                            {
                                'if': {
                                    'column_id': ['dd'],
                                },
                                'color': '#f51f1f',
                                'fontWeight':'bold'  
                            },
                            {
                                'if': {
                                    'column_id': 'years',
                                },
                                'backgroundColor': '#fafafa',
                            }
                        
                        ]
                    ),
                    dash_table.DataTable(
                        data=stats,
                        style_table={'margin-top':'10px','width':'50%'},
                        columns=[
                            {'name': 'Metric', 'id': 'index'},
                            {'name': 'Value', 'id': 'Value'},
                            {'name': 'Benchmark', 'id': 'Benchmark'},
                        ]
                    ),
                ]
            ),

            html.Div(
                style={'width': '60%'},
                children=[
                    dcc.Graph(
                        id='equity-graph',
                        figure=eq_fig
                    ),
                    dcc.Graph(
                        id='dd-graph',
                        figure=dd_fig
                    )
                ]
            ),
            
        ]
    )
    


    app.run_server(debug=True)
