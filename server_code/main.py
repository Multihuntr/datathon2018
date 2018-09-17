import flask

import dash
import dash_core_components as dcc
import dash_html_components as html

import car_speeds
import journey_dist


external_scripts = []

external_stylesheets = [
  "https://fonts.googleapis.com/css?family=Kosugi+Maru",
  "https://fonts.googleapis.com/css?family=Roboto:300,400",
  {
    'href': 'https://use.fontawesome.com/releases/v5.3.1/css/solid.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-VGP9aw4WtGH/uPAOseYxZ+Vz/vaTb1ehm1bwx92Fm8dTrE+3boLfF1SpAtB1z7HW',
    'crossorigin': 'anonymous'
  },
  {
    'href': 'https://use.fontawesome.com/releases/v5.3.1/css/fontawesome.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-1rquJLNOM3ijoueaaeS5m+McXPJCGdr5HcA03/VHXxcp2kX2sUrQDmFc3jR5i/C7',
    'crossorigin': 'anonymous'
  }
]


app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
  car_speeds.div(),
  journey_dist.div()
], style={'height': '100%'})

car_speeds.callbacks(app)
journey_dist.callbacks(app)

if __name__ == '__main__':
  app.run_server(debug=True, host='0.0.0.0')