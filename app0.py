
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

external_stylesheets = ["https://codepen.io/chriddyp/pen/dZVMbK.css"]



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)

df=pd.read_csv('data.csv')
df['created']=pd.to_datetime(df['created']) 
df['month_created']=df.created.dt.strftime(' %Y-%m') 
best5=df.groupby(['mesoregion'])['sla_compliant'].mean().sort_values(ascending=False).reset_index()
best5=best5[best5.sla_compliant<1].head(5)#Some values were omitted
worst5=df.groupby(['mesoregion'])['sla_compliant'].mean().sort_values(ascending=True).reset_index()
worst5=worst5[worst5.sla_compliant>0.4].head(5)#Some values were omitted
#Some values were omitted
best5.sla_compliant,worst5.sla_compliant=round(100*best5.sla_compliant,1),round(100*worst5.sla_compliant,1)
#This line just for checking
#print(df[:5])

# ------------------------------------------------------------------------------
# This is the App layout


app.layout = html.Div([

    html.H1("Loggi: Team 1 BA", style={'text-align': 'center'}),

    #Making unavailable some options
    dcc.Dropdown(id="select_region",
                 options=[
                    #{"label":"Americana", "value":"Americana"},
                    {"label":"Baixada Santista", "value":"Baixada Santista"},
                    {"label":"Belo Horizonte", "value":"Belo Horizonte"},
                    {"label":"Brasília","value":"Brasília"},
                    {"label":"Campinas","value":"Campinas"},
                    {"label":"Cubatão","value":"Cubatão"},
                    {"label":"Curitiba","value":"Curitiba"},
                    {"label":"Florianópolis","value":"Florianópolis"},
                    {"label":"Fortaleza","value":"Fortaleza"},
                    {"label":"Goiânia","value":"Goiânia"},
                    #{"label":"Indaiatuba","value":"Indaiatuba"},
                    #{"label":"Itaquaquecetuba","value":"Itaquaquecetuba"},
                    {"label":"Joinville","value":"Joinville"},
                    #{"label":"Limeira","value":"Limeira"},
                    {"label":"Manaus","value":"Mana us"},
                    {"label":"Piracicaba","value":"Piracicaba"},
                    {"label":"Porto Alegre","value":"Porto Alegre"},
                    {"label":"Recife","value":"Recife"},
                    #{"label":"Ribeirão Pires","value":"Ribeirão Pires"},
                    {"label":"Ribeirão Preto","value":"Ribeirão Preto"},
                    {"label":"Rio de Janeiro","value":"Rio de Janeiro"},
                    {"label":"Salvador","value":"Salvador"},
                    {"label":"Sorocaba","value":"Sorocaba"},
                    #{"label":"Suzano","value":"Suzano"},
                    {"label":"São José do Rio Preto","value":"São José do Rio Preto"},
                    {"label":"São José dos Campos","value":"São José dos Campos"},
                    {"label":"São Paulo","value":"São Paulo"},
                    {"label":"Uberlândia","value":"Uberlândia"},
                    {"label":"Vitória", "value":"Vitória"}],
                 multi=False,
                 value="Rio de Janeiro",
                 style={'width': "40%"}
                 ),

    #html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_histogram',style={'width': 600, 'overflowY': 'scroll'}),
    dcc.Graph(id='my_gauge',style={'width': 600, 'overflowY': 'scroll'}),
    dcc.Graph(id='worst5',style={'width': 600, 'height':300,'overflowY': 'scroll'}),
    dcc.Graph(id='best5',style={'width': 600, 'height':300,'overflowY': 'scroll'}),
    html.Iframe(id='map',srcDoc=open('delay_map.html','r').read(),width=800,height=800),

    html.Br(),
    html.Div([
        dcc.Graph(id='my_scatter',style={'width': 600, 'overflowY': 'scroll'})
    ])
])


# ------------------------------------------------------------------------------
# Connecting the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='my_histogram', component_property='figure'),
    Output(component_id='my_gauge', component_property='figure'),
    Output(component_id='my_scatter', component_property='figure'),
    Output(component_id='worst5', component_property='figure'),
    Output(component_id='best5', component_property='figure')
     ],
    [Input(component_id='select_region', component_property='value')]
)
def update_graph(option_selected):
    #print(option_selected)
    #print(type(option_selected))

    df_hist= df.copy()
    #Histogram filters the outliers, as precalculated
    df_hist = df_hist[(df_hist["mesoregion"] == option_selected)&(~df_hist.is_outlier)]
    df_meso= df_hist[(df_hist["mesoregion"] == option_selected)]
    df_sla_ev=df_meso.groupby(['month_created'])['sla_compliant'].mean().reset_index() 


    if len(df_meso)!=0:
        SLA=round(100*len(df_meso[df.sla_compliant==True])/len(df_meso),1)
    else:
        SLA=None
    
    fig1 = px.histogram(
        data_frame=df_hist,
        x='elapsed_time',
        labels={'elapsed_time': 'Service Time, Minutes','count':'# of Packages delivered'},
        title='# Packages Sent',
        template='xgridoff'
    )
 
    fig1.update_layout(xaxis_showgrid=False)

    fig2= go.Figure(go.Indicator(
        mode = "gauge+number",
        value = SLA,
        title = {'text': "SLA"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#5052f9'},
            'bar':{'color': "#5052f9"},
            'steps': [
                {'range': [0, 95], 'color': '#e8e8e8'},
                {'range': [95, 100], 'color': 'dark blue'}]}
    ))

   

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_sla_ev.month_created, 
                    y=round(100*df_sla_ev.sla_compliant,2),
                    mode='markers+lines',
                    line = dict(color='#5052f9', width=3))
                    )
    
    reds=5*['red']
    greens=5*['green']


    fig4=go.Figure(data=[go.Bar(x=worst5.mesoregion,y=worst5.sla_compliant,marker_color=reds)])
    fig4.update_layout(title_text='Worst 5 Mesoregions')
    fig5=go.Figure(data=[go.Bar(x=best5.mesoregion,y=best5.sla_compliant,marker_color=greens)])
    fig5.update_layout(title_text='Best 5 Mesoregions')
    




    return fig1,fig2,fig3,fig4,fig5


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
