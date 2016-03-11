
import pandas as pd
import seaborn as sb
import plotly.offline as py


PATH = "CSVs/ski-resorts.txt"

def read_data(PATH):
    
    df = pd.read_csv(PATH)
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
    
    return url
        

def network_map(df): 
        
    pass
        


    