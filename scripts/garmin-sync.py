#!/usr/bin/env python3
"""
garmin-sync.py — Busca dados do Garmin Connect e salva no vault.

Setup (uma vez):
  pip3 install garth requests
  python3 garmin-sync.py --setup

Uso (cron diário às 7h):
  python3 /opt/cabecao/scripts/garmin-sync.py

Dados coletados: sono, HRV, passos, distância, calorias, atividades, estresse.
"""

import json
import os
import sys
import subprocess
from datetime import date, timedelta
from pathlib import Path

VAULT = "/opt/cabecao/vault"
CREDS_FILE = "/root/.garmin-credentials"
SAVE_SCRIPT = "/opt/cabecao/scripts/save-note.sh"


def setup():
    """Configura credenciais Garmin (executa uma vez)."""
    print("=== Setup Garmin Sync ===")
    email = input("Email da conta Garmin Connect: ").strip()
    password = input("Senha: ").strip()
    creds = {"email": email, "password": password}
    Path(CREDS_FILE).write_text(json.dumps(creds))
    os.chmod(CREDS_FILE, 0o600)
    print(f"Credenciais salvas em {CREDS_FILE}")


def load_creds():
    if not Path(CREDS_FILE).exists():
        print(f"ERRO: credenciais não encontradas. Execute: python3 {__file__} --setup")
        sys.exit(1)
    return json.loads(Path(CREDS_FILE).read_text())


def fetch_garmin_data(email, password, target_date):
    """Busca dados do Garmin Connect para a data informada."""
    try:
        import garth
    except ImportError:
        subprocess.run(["pip3", "install", "garth", "-q"], check=True)
        import garth

    garth.login(email, password)

    date_str = target_date.strftime("%Y-%m-%d")
    data = {"date": date_str}

    # Sono
    try:
        sleep = garth.connectapi(f"/wellness-service/wellness/dailySleepData/{email}?date={date_str}&nonSleepBufferMinutes=60")
        sd = sleep.get("dailySleepDTO", {})
        data["sleep_hours"] = round(sd.get("sleepTimeSeconds", 0) / 3600, 1)
        data["sleep_score"] = sd.get("sleepScores", {}).get("overall", {}).get("value", None)
        data["deep_sleep_min"] = round(sd.get("deepSleepSeconds", 0) / 60)
        data["rem_sleep_min"] = round(sd.get("remSleepSeconds", 0) / 60)
    except Exception:
        data["sleep_hours"] = None

    # HRV
    try:
        hrv = garth.connectapi(f"/hrv-service/hrv/{date_str}")
        data["hrv"] = hrv.get("hrvSummary", {}).get("lastNight", None)
        data["hrv_status"] = hrv.get("hrvSummary", {}).get("status", None)
    except Exception:
        data["hrv"] = None

    # Steps + distância + calorias
    try:
        daily = garth.connectapi(f"/usersummary-service/usersummary/daily/{email}?calendarDate={date_str}")
        data["steps"] = daily.get("totalSteps", 0)
        data["distance_km"] = round(daily.get("totalDistanceMeters", 0) / 1000, 1)
        data["calories"] = daily.get("totalKilocalories", 0)
        data["active_calories"] = daily.get("activeKilocalories", 0)
        data["stress_avg"] = daily.get("averageStressLevel", None)
        data["body_battery_low"] = daily.get("minBodyBattery", None)
        data["body_battery_high"] = daily.get("maxBodyBattery", None)
    except Exception:
        data["steps"] = None

    # Atividades
    try:
        activities = garth.connectapi(f"/activitylist-service/activities/search/activities?startDate={date_str}&endDate={date_str}&limit=5")
        acts = []
        for a in activities:
            acts.append({
                "name": a.get("activityName", ""),
                "type": a.get("activityType", {}).get("typeKey", ""),
                "duration_min": round(a.get("duration", 0) / 60),
                "distance_km": round(a.get("distance", 0) / 1000, 1),
                "calories": a.get("calories", 0),
                "avg_hr": a.get("averageHR", None),
            })
        data["activities"] = acts
    except Exception:
        data["activities"] = []

    return data


def build_note(d):
    """Constrói o conteúdo da nota de saúde para o vault."""
    lines = [
        f"---",
        f"date: {d['date']}",
        f"type: health",
        f"source: garmin",
        f"tags: [saude, garmin]",
        f"---",
        f"",
        f"## Dados Garmin — {d['date']}",
        f"",
    ]

    # Sono
    if d.get("sleep_hours") is not None:
        score = f" (score: {d['sleep_score']})" if d.get("sleep_score") else ""
        lines += [
            f"### Sono",
            f"- Total: **{d['sleep_hours']}h**{score}",
            f"- Profundo: {d.get('deep_sleep_min', '?')} min | REM: {d.get('rem_sleep_min', '?')} min",
            f"",
        ]

    # HRV
    if d.get("hrv") is not None:
        status = f" ({d['hrv_status']})" if d.get("hrv_status") else ""
        lines += [f"### HRV", f"- **{d['hrv']} ms**{status}", f""]

    # Movimento
    if d.get("steps") is not None:
        lines += [
            f"### Movimento",
            f"- Passos: {d['steps']:,} | Distância: {d['distance_km']} km",
            f"- Calorias: {d['calories']} total ({d['active_calories']} ativas)",
            f"",
        ]

    # Stress / Body Battery
    if d.get("stress_avg") is not None:
        lines += [
            f"### Stress & Body Battery",
            f"- Stress médio: {d['stress_avg']} | Body Battery: {d.get('body_battery_low', '?')}–{d.get('body_battery_high', '?')}",
            f"",
        ]

    # Atividades
    if d.get("activities"):
        lines.append("### Atividades")
        for a in d["activities"]:
            dist = f" | {a['distance_km']} km" if a['distance_km'] > 0 else ""
            hr = f" | FC média: {a['avg_hr']} bpm" if a.get("avg_hr") else ""
            lines.append(f"- **{a['name']}** ({a['type']}): {a['duration_min']} min{dist}{hr}")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup()
        return

    creds = load_creds()
    target = date.today() - timedelta(days=1)  # dados de ontem (Garmin atrasa 1 dia)

    print(f"Buscando dados Garmin para {target}...")
    data = fetch_garmin_data(creds["email"], creds["password"], target)

    content = build_note(data)
    rel_path = f"2-Areas/Saude/garmin/{target.strftime('%Y-%m-%d')}.md"

    result = subprocess.run(
        [SAVE_SCRIPT, "idea", rel_path, content],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"OK: dados salvos em {rel_path}")

        # Sumário no Telegram via OpenClaw
        sleep_str = f"Sono: {data.get('sleep_hours', '?')}h" if data.get('sleep_hours') else ""
        hrv_str = f"HRV: {data.get('hrv', '?')}ms" if data.get('hrv') else ""
        steps_str = f"Passos: {data.get('steps', 0):,}" if data.get('steps') else ""
        acts = data.get('activities', [])
        act_str = f"Treino: {acts[0]['name']} {acts[0]['duration_min']}min" if acts else "Sem treino registrado"

        summary_parts = [x for x in [sleep_str, hrv_str, steps_str, act_str] if x]
        print("Resumo: " + " | ".join(summary_parts))
    else:
        print(f"ERRO ao salvar: {result.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
