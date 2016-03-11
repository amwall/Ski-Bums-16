
import pandas as pd
import seaborn as sb
import plotly.offline as py
from directions import compute_time_between, haversine


PATH = "CSVs/ski-resorts.txt"

def read_data(PATH):
    
    df = pd.read_csv(PATH)
    df.set_index(['ID'], inplace=True)
    return df

    
def snowfall_map(df):
    
    df['text'] = (df['name'] + ' ' + df['city'] + ', ' + df['state'] + ' Avg. Snowfall: ' + df['avg_snowfall'].astype(str))
    
    scl = [ [0,"#C90D34"],[0.1,"#AD1A4C"],[0.2,"#91275F"],[0.3,'#753472'],
            [0.4,"#594184"],[0.55,"#3D4E97"],[.8,"#215BAA"],[1, '#0569BD' ]]
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
             title ='US Ski Resorts <br>(Hover for information)',
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
    for i in range(1, len(df.index + 1)):
        paths.append(
            dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = [cur_lon, df['lon'][i] ],
                lat = [cur_lat, df['lat'][i] ],
                mode = 'lines',
                line = dict(
                    width = 1,
                    color = '#21A14A',
                ),
                opacity = 0.5
            )
        )
        
    layout = dict(
            title = 'Your location to Resorts <br> (Hover information)',
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
    
        