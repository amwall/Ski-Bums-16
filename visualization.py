import pandas as pd
import plotly.offline as py

import plotly.graph_objs as go
import pandas as pd
import numpy as np
import colorlover as cl
from scipy.stats import gaussian_kde

PATH = "CSVs/ski-resorts.txt"

def read_data(PATH):

    df = pd.read_csv(PATH)
    df.set_index(['ID'], inplace=True)
    return df

def snowfall_map(df):
    '''
    Create an interactive map showing the location of resorts color coded based
    on the annual average snowfall
    '''

    df['text'] = (df['name'] + ' (' + df['city'] + ', ' + df['state'] + ')  Avg. Snowfall: ' + df['avg_snowfall'].astype(str))

    scl = [ [0,"#C90D34"],[0.15,"#AD1A4C"],[0.2,"#91275F"],[0.3,'#753472'],
            [0.4,"#594184"],[0.5,"#3D4E97"],[.7,"#215BAA"],[1, '#0569BD' ]]
    data = [dict(
            type ='scattergeo',
            locationmode = 'USA-states',
            lon = df['lon'],
            lat = df['lat'],
            text = df['text'],
            mode ='markers',
            marker = dict(
                            size=8,
                            opacity=0.8,
                            symbol='circle',
                            colorscale = scl,
                            cmin = 0,
                            color = df['avg_snowfall'],
                            cmax = df['avg_snowfall'].max(),
                            colorbar=dict(
                            title="Average Yearly Snowfall"
                                            ))
            )]

    layout = dict(
             title ='US Ski Resorts <br> (Hover for information)',
             geo = dict(
                    scope = 'usa',
                    projection = dict(type='albers usa'),
                    showland = True,
                    landcolor = "rgb(235,235,235)",
                    subunitcolor = "rgb(200, 200, 200)",
                    countrycolor = 'rgb(200, 200, 200)',
                    countrywidth = 0.5,
                    subunitwidth = 0.5
                    ),
             )

    fig = dict(data=data, layout=layout )
    url = py.plot(fig, validate=False, filename='d3-ski-resorts' )


def network_map(cur_lat, cur_lon, df):


    resorts = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = df['lon'],
        lat = df['lat'],
        hoverinfo = 'text',
        text = df['name'],
        mode = 'markers',
        marker = dict(
            size=2,
            color='#1979D2',
            line = dict(
                width=2,
                color='rgba(68, 68, 68, 0)'
            )
        ))]

    paths = []
    # for i in range(1, len(df.index + 1)):
    for i, row in df.iterrows():
        paths.append(
            dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = [cur_lon, row['lon'] ],
                lat = [cur_lat, row['lat'] ],
                mode = 'lines',
                line = dict(
                    width = 1,
                    color = '#21A14A',
                ),
                opacity = 0.5
            )
        )

    layout = dict(
            title = 'Resort Network <br> (Hover for Name)',
            showlegend = False,
            geo = dict(
                    scope = 'usa',
                    projection = dict(type='albers usa'),
                    showland = True,
                    landcolor = "rgb(235,235,235)",
                    subunitcolor = "rgb(200, 200, 200)",
                    countrycolor = 'rgb(200, 200, 200)',
                    countrywidth = 0.5,
                    subunitwidth = 0.5
                    )
            )

    fig = dict( data=paths + resorts, layout=layout )
    url = py.plot(fig, filename='network.html')
    

def density_plot():
    '''
    Use a density plot to explore the realtionship 
    '''

    df = pd.read_csv('CSVs/city_score.csv')
    df.fillna(0,inplace=True)
    # print(df.head())
    
    scl = cl.scales['9']['seq']['Blues']
    colorscale = [ [ float(i)/float(len(scl)-1), scl[i] ] for i in range(len(scl)) ]
    colorscale
    
    def kde_scipy(x, x_grid, bandwidth=0.2 ):
        kde = gaussian_kde(x, bw_method=bandwidth / x.std(ddof=1) )
        return kde.evaluate(x_grid)
    
    x_grid = np.linspace(df['number'].min(), df['number'].max(), 100)
    y_grid = np.linspace(df['area'].min(), df['area'].max(), 100)
    
    trace1 = go.Histogram2dContour(
        x=df['number'],
        y=df['area'],
        name='density',
        ncontours=20,
        colorscale=colorscale,
        showscale=False
    )
    trace2 = go.Histogram(
        x=df['number'],
        name='x density',
        yaxis='y2',
        histnorm='probability density',
        marker=dict(color='rgb(217, 217, 217)'),
        nbinsx=25
    )
    trace2s = go.Scatter(
        x=x_grid,
        y=kde_scipy( df['number'].as_matrix(), x_grid ),
        yaxis='y2',
        line = dict( color='rgb(31, 119, 180)' ),
        fill='tonexty',
    )
    trace3 = go.Histogram(
        y=df['area'],
        name='y density',
        xaxis='x2',
        histnorm='probability density',
        marker=dict(color='rgb(217, 217, 217)'),
        nbinsy=50
    )
    trace3s = go.Scatter(
        y=y_grid,
        x=kde_scipy( df['area'].as_matrix(), y_grid ),
        xaxis='x2',
        line = dict( color='rgb(31, 119, 180)' ),
        fill='tonextx',
    )
    
    data = [trace1, trace2, trace2s, trace3, trace3s]
    
    layout = go.Layout(
        showlegend=False,
        autosize=False,
        width=700,
        height=700,
        hovermode='closest',
        bargap=0,
    
        xaxis=dict(domain=[0, 0.746], linewidth=2, linecolor='#444', title='Time',
                   showgrid=False, zeroline=False, ticks='', showline=True, mirror=True),
    
        yaxis=dict(domain=[0, 0.746],linewidth=2,linecolor='#444', title='Area',
                   showgrid=False, zeroline=False, ticks='', showline=True, mirror=True),
    
        xaxis2=dict(domain=[0.75, 1], showgrid=False, zeroline=False, ticks='',
                    showticklabels=False ),
    
        yaxis2=dict(domain=[0.75, 1], showgrid=False, zeroline=False, ticks='',
                    showticklabels=False ),
    )
    
    fig = go.Figure(data=data, layout=layout)
    
    url = py.plot(fig, filename='visualization/density-plot')
