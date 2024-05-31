import requests
import json
import time

# Función para obtener las métricas del partido desde la nueva URL
def get_match_metrics(game_id):
    metrics_url = f"https://webws.365scores.com/web/game/stats/?appTypeId=5&langId=29&timezoneName=America/Santiago&userCountryId=28&games={game_id}"
    for attempt in range(5):
        try:
            response = requests.get(metrics_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener métricas del juego {game_id}: {e}. Reintentando en 5 segundos ({attempt + 1}/5)...")
            time.sleep(5)
    return None

# Función para extraer estadísticas de los jugadores
def extract_player_stats(player):
    # Verificar si el objeto tiene estadísticas útiles
    if 'stats' not in player or not player['stats']:
        return None

    # Verificar si el objeto no es un cambio o management
    if player['statusText'] in ['Substitute', 'Management']:
        return None

    # Inicializar diccionario para agregar estadísticas
    aggregated_stats = {}
    # Función auxiliar para agregar valores al diccionario de estadísticas
    def add_stat_value(stat_name, stat_value):
        if stat_name not in aggregated_stats:
            aggregated_stats[stat_name] = 0
        try:
            # En caso de que el valor sea una fracción o un porcentaje, extraer solo el número
            if isinstance(stat_value, str):
                stat_value = stat_value.split(' ')[0].split('/')[0].split('(')[0].replace("'", "")
            aggregated_stats[stat_name] += int(stat_value)
        except ValueError:
            pass  # Ignorar valores que no se pueden convertir a entero

    # Recorrer las estadísticas del jugador y agregarlas
    for stat in player['stats']:
        add_stat_value(stat['name'], stat['value'])

    return {
        'name': player.get('name', 'N/A'),
        'position': player['position']['name'],
        'aggregated_stats': aggregated_stats
    }

# Función para extraer estadísticas del partido
def extract_match_stats(match_stats):
    stats = {}
    for stat in match_stats:
        stat_name = stat['name']
        if stat_name not in stats:
            stats[stat_name] = {'home': 0, 'away': 0}
        stats[stat_name]['home'] = stat.get('home', 0)
        stats[stat_name]['away'] = stat.get('away', 0)
    return stats

# Función para obtener los detalles de cada juego
def get_game_details(game_id, matchup_id):
    details_url = f"https://webws.365scores.com/web/game/?appTypeId=5&langId=29&timezoneName=America/Santiago&userCountryId=28&gameId={game_id}&matchupId={matchup_id}&topBookmaker=47"
    for attempt in range(5):
        try:
            response = requests.get(details_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener detalles del juego {game_id}: {e}. Reintentando en 5 segundos ({attempt + 1}/5)...")
            time.sleep(5)
    return None

# Función para obtener el resumen del partido
def get_match_summary(game_data, metrics):
    game = game_data['game']
    general_info = {
        'gameId': game['id'],
        'competition': game['competitionDisplayName'],
        'startTime': game['startTime'],
        'status': game['statusText'],
        'homeTeam': {
            'name': game['homeCompetitor']['name'],
            'score': game['homeCompetitor']['score']
        },
        'awayTeam': {
            'name': game['awayCompetitor']['name'],
            'score': game['awayCompetitor']['score']
        }
    }
    # Verificar si existen estadísticas de los jugadores
    home_team_stats = []
    away_team_stats = []
  
    if 'lineups' in game['homeCompetitor'] and 'members' in game['homeCompetitor']['lineups']:
        home_team_players = game['homeCompetitor']['lineups']['members']
        home_team_stats = [extract_player_stats(player) for player in home_team_players if extract_player_stats(player) is not None]

    if 'lineups' in game['awayCompetitor'] and 'members' in game['awayCompetitor']['lineups']:
        away_team_players = game['awayCompetitor']['lineups']['members']
        away_team_stats = [extract_player_stats(player) for player in away_team_players if extract_player_stats(player) is not None]


    # Compilar el resumen del partido
    match_summary = {
        'general_info': general_info,
        'home_team_stats': home_team_stats,
        'away_team_stats': away_team_stats,
        'metrics': metrics.get('statistics', [])  # Añadir solo el objeto 'statistics'
    }
    
    return match_summary

# Código principal (ajustado para utilizar las funciones anteriores)
if __name__ == "__main__":
    # Inicializar variables
    base_url = "https://webws.365scores.com"
    initial_url = "/web/games/results/?appTypeId=5&langId=29&timezoneName=America/Santiago&userCountryId=28&competitions=135&showOdds=true&includeTopBettingOpportunity=1&topBookmaker=47"
    games = []
    game_details = []
    next_page = initial_url
    max_retries = 5

    # Función para obtener los resultados y eliminar duplicados
    def get_games(url, games):
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url + url)
                response.raise_for_status()  # Verifica si la solicitud fue exitosa
                data = response.json()
                if 'games' in data:
                    new_games = data['games']
                    
                    # Eliminar duplicados
                    existing_game_ids = {game['id'] for game in games}
                    unique_games = [game for game in new_games if game['id'] not in existing_game_ids]
                    
                    # Agregar los nuevos juegos únicos a la lista de juegos
                    games.extend(unique_games)
                    return data.get('paging', {}).get('previousPage')
                else:
                    print("La clave 'games' no está en la respuesta.")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Error al realizar la solicitud: {e}. Reintentando en 5 segundos ({attempt + 1}/{max_retries})...")
                time.sleep(5)
        return None

    # Bucle para obtener las páginas manualmente
    while next_page:
        input("Presiona Enter para obtener la siguiente página de resultados...")
        next_page = get_games(next_page, games)
        print(f"Total de juegos obtenidos hasta ahora: {len(games)}")
        if not next_page:
            print("No hay más páginas disponibles o no se pudo obtener más datos.")

    # Obtener los detalles de cada juego y generar el resumen
    i = 1
    for game in games:
        game_id = game['id']
        home_id = game['homeCompetitor']['id']
        away_id = game['awayCompetitor']['id']
        matchup_id = f"{home_id}-{away_id}-135"
        print(f"obteniendo game:{i} de {len(games)}\n")
        #details = get_game_details(game_id, matchup_id)
        metrics = get_match_metrics(game_id)
        if metrics:
           #match_summary = get_match_summary(details, metrics)
            #game_details.append(match_summary)
            game['metrics'] = metrics.get('statistics', [])
        i = i + 1

    # Imprimir la cantidad de detalles obtenidos
    print(f"Total de detalles de juegos obtenidos: {len(game_details)}")

    # Guardar los resultados y los detalles en un archivo JSON
    with open('resultados.json', 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=4, ensure_ascii=False)

    with open('detalles_juegos.json', 'w', encoding='utf-8') as f:
        json.dump(game_details, f, indent=4, ensure_ascii=False)
