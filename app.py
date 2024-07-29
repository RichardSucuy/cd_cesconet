import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

import locale
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Ajusta esto según el sistema operativo y disponibilidad


# Cargar datos
# Carga de datos
facturas_df = pd.read_csv('Facturas_CESCONET.csv')
detalles_factura_df = pd.read_csv('Detalles_Factura_CESCONET.csv')
servicios_df = pd.read_csv('Servicios_CESCONET.csv')
clientes_df = pd.read_csv('Clientes_CESCONET.csv')

facturas_df['Fecha_emision'] = pd.to_datetime(facturas_df['Fecha_emision'])
facturas_df['Mes_emision'] = facturas_df['Fecha_emision'].dt.strftime('%B %Y')


# ----------------  PREGUNTA 4 ----------------------
# Convertir fechas y calcular la primera fecha de factura para cada cliente
facturas_df['Fecha_emision'] = pd.to_datetime(facturas_df['Fecha_emision'])
clientes_df = clientes_df.merge(
    facturas_df.groupby('ID_cliente')['Fecha_emision'].min().reset_index().rename(columns={'Fecha_emision': 'Fecha_primera_factura'}),
    on='ID_cliente',
    how='left'
)
clientes_df['Antiguedad'] = (pd.Timestamp.today() - clientes_df['Fecha_primera_factura']).dt.days

# Unir la información de clientes con facturas
facturas_df = facturas_df.merge(clientes_df[['ID_cliente', 'Antiguedad']], on='ID_cliente')

# Calcular la frecuencia de facturación por cliente para cada estado
frecuencia_facturacion = facturas_df.groupby(['ID_cliente', 'Estado']).size().reset_index(name='Frecuencia')

# Unir la información de frecuencia con los clientes para tener el nombre o identificador del cliente si es necesario
frecuencia_facturacion = frecuencia_facturacion.merge(clientes_df[['ID_cliente']], on='ID_cliente', how='left')



# ----------------  PREGUNTA 5 ----------------------
facturass_df = pd.read_csv('Facturas_CESCONET.csv')
detalless_factura_df = pd.read_csv('Detalles_Factura_CESCONET.csv')
servicioss_df = pd.read_csv('Servicios_CESCONET.csv')

# Asegúrate de que la unión con detalles_factura_df y servicios_df esté conservando la columna Monto_total
facturass_df = facturass_df.merge(detalless_factura_df, on='ID_factura', how='left')
facturass_df = facturass_df.merge(servicioss_df[['ID_servicios', 'Nombre_servicio']], left_on='ID_servicio', right_on='ID_servicios', how='left')

# Verificar si la columna Monto_total está presente después de las uniones
print("Columnas en facturas_df después de la unión:", facturas_df.columns)

# Si Monto_total se pierde en alguna parte, necesitas asegurarte de que detalles_factura_df incluya esa columna correctamente
# O tal vez necesitas recalcular Monto_total si se supone que proviene de detalles_factura_df (cantidad * precio_unitario)
if 'Monto_total' not in facturass_df.columns:
    facturass_df['Monto_total'] = detalless_factura_df['Cantidad'] * detalless_factura_df['Precio_unitario']

# Calcular el monto promedio por tipo de servicio y estado
montos_por_servicio = facturass_df.groupby(['Nombre_servicio', 'Estado'])['Monto_total'].mean().reset_index()



# --------------- Pregunta 6 --------------------------
facturasss_df = pd.read_csv('Facturas_CESCONET.csv')
detallesss_factura_df = pd.read_csv('Detalles_Factura_CESCONET.csv')
serviciosss_df = pd.read_csv('Servicios_CESCONET.csv')

# Asegúrate de que la unión con detalles_factura_df y servicios_df esté conservando la columna Monto_total
facturasss_df = facturasss_df.merge(detallesss_factura_df, on='ID_factura', how='left')
facturasss_df = facturasss_df.merge(serviciosss_df[['ID_servicios', 'Nombre_servicio']], left_on='ID_servicio', right_on='ID_servicios', how='left')


# Asegurarse de que la fecha de emisión está en formato datetime
facturasss_df['Fecha_emision'] = pd.to_datetime(facturasss_df['Fecha_emision'])

# Extraer el mes y año de la fecha de emisión para agrupar por mes
facturasss_df['Mes_Año'] = facturasss_df['Fecha_emision'].dt.strftime('%B %Y')

# Agrupar por mes y tipo de servicio para contar las contrataciones
contrataciones_por_mes = facturasss_df.groupby(['Mes_Año', 'Nombre_servicio']).size().reset_index(name='Contrataciones')

# Esto te da un DataFrame con el mes/año, el nombre del servicio y el número de contrataciones en ese mes




# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación ajustado
app.layout = html.Div([
    html.H1("DASHBOARD - CESCONET", style={'text-align': 'center'}),
    html.Div([  # Primera fila de gráficos
        dcc.Graph(id='facturas-mensuales-graph'),
        dcc.Graph(id='monto-total-estado-graph')
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([  # Segunda fila de gráficos
        dcc.Graph(id='antiguedad-vs-estado-graph'),
        dcc.Graph(id='montos-servicio-graph')
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([  # Tercera fila para el gráfico de frecuencia de facturación
        dcc.Graph(id='frecuencia-facturacion-graph')
    ], style={'width': '100%'}),  # Usa el 100% del ancho disponible
    html.Div([  # Tercera fila para el gráfico de frecuencia de facturación
        dcc.Graph(id='tendencias-contratacion-servicios-graph')
    ], style={'width': '100%'})  # Usa el 100% del ancho disponible
])

# Asegúrate de actualizar también cualquier otro estilo o configuración necesaria.


# Callbacks para actualizar los gráficos
@app.callback(
    Output('facturas-mensuales-graph', 'figure'),
    [Input('facturas-mensuales-graph', 'id')]  # Este Input es solo un placeholder
)
def update_facturas_mensuales_graph(_):
    facturas_mensuales = facturas_df.groupby(['Mes_emision', 'Estado']).size().unstack(fill_value=0)
    fig = px.bar(facturas_mensuales, barmode='stack', labels={'value': 'Número de Facturas', 'Mes_emision': 'Mes de Emisión'})
    fig.update_layout(title_text='Actividad Mensual de Facturación: Facturas Emitidas y Pendientes por Mes')
    return fig

@app.callback(
    Output('monto-total-estado-graph', 'figure'),
    [Input('monto-total-estado-graph', 'id')]
)
def update_monto_total_estado_graph(_):
    fig = px.box(facturas_df, x='Estado', y='Monto_total', points="all",
                 labels={'Monto_total': 'Monto Total', 'Estado': 'Estado de Factura'},
                 title='Distribución del Monto Total de Facturas por Estado')
    return fig

@app.callback(
    Output('antiguedad-vs-estado-graph', 'figure'),
    [Input('antiguedad-vs-estado-graph', 'id')]
)
def update_antiguedad_estado_graph(_):
    fig = px.scatter(facturas_df, x='Antiguedad', y='Monto_total', color='Estado',
                     labels={'Antiguedad': 'Antigüedad (días)', 'Monto_total': 'Monto de la Factura'},
                     title='Antigüedad de los Clientes vs. Estado de Factura')
    return fig

# Callback para el nuevo gráfico de frecuencia de facturación
@app.callback(
    Output('frecuencia-facturacion-graph', 'figure'),
    [Input('frecuencia-facturacion-graph', 'id')]
)
def update_frecuencia_facturacion_graph(_):
    fig = px.bar(frecuencia_facturacion, x='ID_cliente', y='Frecuencia', color='Estado',
                 barmode='group',
                 labels={'ID_cliente': 'Cliente', 'Frecuencia': 'Frecuencia de Facturación'},
                 title='Frecuencia de Facturación por Cliente y Estado de Factura')
    return fig


# Callback para el nuevo gráfico de montos por servicio
@app.callback(
    Output('montos-servicio-graph', 'figure'),
    [Input('montos-servicio-graph', 'id')]
)
def update_montos_servicio_graph(_):
    fig = px.bar(montos_por_servicio, x='Nombre_servicio', y='Monto_total', color='Estado',
                 barmode='group',
                 labels={'Nombre_servicio': 'Servicio', 'Monto_total': 'Monto Promedio Facturado ($)', 'Estado': 'Estado de Factura'},
                 title='Montos Promedio Facturados por Servicio y Estado de Factura')
    return fig

# Callback para actualizar el gráfico de tendencias de contratación de servicios
@app.callback(
    Output('tendencias-contratacion-servicios-graph', 'figure'),
    [Input('tendencias-contratacion-servicios-graph', 'id')]
)
def update_tendencias_contratacion_servicios_graph(_):
    fig = px.line(contrataciones_por_mes, x='Mes_Año', y='Contrataciones', color='Nombre_servicio',
                  labels={'Mes_Año': 'Mes', 'Contrataciones': 'Número de Contrataciones'},
                  title='Tendencias Temporales en la Contratación de Servicios')
    return fig

# Correr la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)