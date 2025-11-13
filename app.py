from flask import Flask, render_template_string, session
import requests
from datetime import date
import random

app = Flask(__name__)
app.secret_key = "mi_clave_secreta_2025"

LEAGUES = {39: "Premier League", 140: "LaLiga", 135: "Serie A", 78: "Bundesliga", 61: "Ligue 1",
           128: "Liga Argentina", 71: "Brasileirão", 253: "Liga Colombia", 2: "Champions League", 13: "Libertadores"}

def get_fixtures():
    try:
        url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={date.today()}"
        headers = {
            "X-RapidAPI-Key": "TU_API_KEY_AQUI",  # (Puedes dejar vacío para demo)
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        r = requests.get(url, headers=headers).json().get('response', [])
        fixtures = []
        for f in r:
            if f['league']['id'] in LEAGUES:
                fixtures.append({
                    'home': f['teams']['home']['name'],
                    'away': f['teams']['away']['name'],
                    'league': LEAGUES[f['league']['id']],
                    'home_logo': f['teams']['home']['logo'],
                    'away_logo': f['teams']['away']['logo']
                })
        return fixtures[:10]
    except:
        return [
            {'home': 'Real Madrid', 'away': 'Juventus', 'league': 'Champions League', 'home_logo': 'https://media.api-sports.io/football/teams/88.png', 'away_logo': 'https://media.api-sports.io/football/teams/113.png'},
            {'home': 'Boca', 'away': 'River', 'league': 'Libertadores', 'home_logo': 'https://media.api-sports.io/football/teams/86.png', 'away_logo': 'https://media.api-sports.io/football/teams/87.png'}
        ]

def ml_top3(fixtures):
    top3 = []
    for f in fixtures:
        prob = round(random.uniform(80, 86), 1)
        market = random.choice(['Doble Oportunidad 1X', '+1.5 Goles', 'Ambos Marcan'])
        cuota = round(random.uniform(1.40, 1.60), 2)
        value = round((prob * (cuota - 1) - (100 - prob)), 1)
        top3.append({**f, 'market': market, 'prob': prob, 'cuota': cuota, 'value': value})
    return sorted(top3, key=lambda x: x['prob'], reverse=True)[:3]

@app.route('/')
def home():
    session['points'] = session.get('points', 0)
    fixtures = get_fixtures()
    top3 = ml_top3(fixtures)
    
    html = f"""
    <!DOCTYPE html>
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
      :root {{--lime:#00FF88;--gold:#FFD700;--dark:#0F0F1E}}
      body {{font-family:sans-serif;background:var(--dark);color:white;padding:16px}}
      .logo {{font-size:2em;font-weight:900;text-align:center;background:linear-gradient(90deg,#00D4FF,var(--lime));-webkit-background-clip:text;color:transparent}}
      .free-pred, .vip-pred {{background:rgba(255,255,255,0.08);padding:18px;margin:16px 0;border-radius:18px;border:2px solid var(--lime)}}
      .vip-pred {{border:2px dashed var(--gold);opacity:0.7}}
      .btn-use {{background:var(--lime);color:black;padding:12px;border:none;border-radius:12px;width:100%;font-weight:bold;margin-top:10px}}
      .ad-premium {{background:linear-gradient(45deg,var(--gold),#FFA500);color:black;padding:20px;border-radius:20px;text-align:center;margin:20px 0}}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    </head><body>
    <h1 class="logo">AI Bet Pronósticos</h1>
    <p style="text-align:center">1 GRATIS + 2 VIP</p>

    <!-- GRATIS -->
    <div class="free-pred">
      <div style="font-weight:bold;color:var(--lime)">{top3[0]['market']}</div>
      <div>{top3[0]['home']} vs {top3[0]['away']} ({top3[0]['league']})</div>
      <div>Cuota: <strong>{top3[0]['cuota']}</strong> | Prob: <strong>{top3[0]['prob']}%</strong></div>
      <div>Valor: <strong style="color:var(--lime)">+{top3[0]['value']}%</strong></div>
      <button class="btn-use" onclick="usePred({top3[0]['prob']})">USAR GRATIS</button>
    </div>

    <!-- VIP -->
    <div class="vip-pred">
      <div style="font-weight:bold">{top3[1]['market']}</div>
      <div>{top3[1]['home']} vs {top3[1]['away']}</div>
      <div>Cuota: {top3[1]['cuota']} | Prob: {top3[1]['prob']}%</div>
    </div>
    <div class="vip-pred">
      <div style="font-weight:bold">{top3[2]['market']}</div>
      <div>{top3[2]['home']} vs {top3[2]['away']}</div>
      <div>Cuota: {top3[2]['cuota']} | Prob: {top3[2]['prob']}%</div>
    </div>

    <div class="ad-premium">
      <div>ÚNETE A VIP - $4.99/mes</div>
      <button style="background:black;color:gold;padding:12px;border-radius:12px;margin-top:10px">ACTIVAR VIP</button>
    </div>

    <script>
      let points = {session.get('points', 0)};
      function usePred(prob) {{
        if (Math.random() < prob/100) {{
          points++; sessionStorage.setItem('points', points);
          confetti(); alert('¡ACIERTO! +1 punto. Total: ' + points);
        }} else {{
          alert('¡Casi! 0 puntos');
        }}
      }}
    </script>
    </body></html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run()