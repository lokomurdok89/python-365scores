import pandas as pd
import matplotlib.pyplot as plt

# Datos normalizados para los equipos (basado en estadísticas previas)
normalized_stats = {
    "team": ["Everton", "Universidad de Chile"],
    "Goles": [0.5, 0.3],
    "Asistencias": [0.4, 0.2],
    "Total Remates": [0.6, 0.5],
    "Fueras de Juego": [0.3, 0.2],
    "Pases claves": [0.5, 0.4],
    "Pases en el último tercio": [0.7, 0.6],
    "Pases hacia atrás": [0.6, 0.5],
    "Pases completados": [0.8, 0.7],
    "Despejes": [0.4, 0.5],
    "Intercepciones": [0.5, 0.6],
    "Faltas recibidas": [0.6, 0.4],
    "Faltas cometidas": [0.4, 0.5],
    "Tarjetas Amarillas": [0.3, 0.2],
    "Tarjetas Rojas": [0.1, 0.2]
}

# Crear DataFrame
match_df = pd.DataFrame(normalized_stats)

# Extraer las estadísticas de los equipos
everton_stats = match_df[match_df['team'] == 'Everton'].drop(columns='team').values.flatten()
udechile_stats = match_df[match_df['team'] == 'Universidad de Chile'].drop(columns='team').values.flatten()

# Promedio ponderado para las predicciones
predicted_stats = 0.6 * everton_stats + 0.4 * udechile_stats

# Crear un DataFrame para visualizar las predicciones
predicted_df = pd.DataFrame([predicted_stats], columns=match_df.columns[1:])

# Crear gráfica del pronóstico del partido
plt.figure(figsize=(12, 8))
plt.barh(predicted_df.columns, predicted_stats, color='skyblue')
plt.xlabel('Valores Predichos')
plt.title('Pronóstico del Partido: Everton vs Universidad de Chile')
plt.grid(True)

# Mostrar gráfica
plt.tight_layout()
plt.show()

print(predicted_df)