#!/usr/bin/env python3
"""
garmin-sync.py — Busca dados do Garmin Connect e salva no vault.

Setup (uma vez):
  python3 /opt/cabecao/scripts/garmin-sync.py --setup

Uso (cron diário às 7h):
  python3 /opt/cabecao/scripts/garmin-sync.py
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
    email = input("Email da conta Garmin Connect: ").strip()
    password = input("Senha: ").strip()
    Path(CREDS_FILE).write_text(json.dumps({"email": email, "password": password}))
    os.chmod(CREDS_FILE, 0o600)
    print(f"Credenciais salvas em {CREDS_FILE}")


def load_creds():
    if not Path(CREDS_FILE).exists():
        print(f"ERRO: execute python3 {__file__} --setup")
        sys.exit(1)
    return json.loads(Path(CREDS_FILE).read_text())


def get_display_name(creds):
    import garth
    garth.login(creds["email"], creds["password"])
    try:
        profile = garth.connectapi("/userprofile-service/socialProfile")
        return garth, profile.get("displayName", creds["email"])
    except Exception:
        return garth, creds["email"]


def fetch_garmin_data(garth_client, display_name, target_date):
    date_str = target_date.strftime("%Y-%m-%d")
    data = {"date": date_str}

    # Sono
    try:
        sleep = garth_client.connectapi(
            f"/wellness-service/wellness/dailySleepData/{display_name}"
            f"?date={date_str}&nonSleepBufferMinutes=60"
        )
        sd = sleep.get("dailySleepDTO", {}) or {}
        secs = sd.get("sleepTimeSeconds")
        data["sleep_hours"] = round(secs / 3600, 1) if secs else None
        data["sleep_score"] = (sd.get("sleepScores") or {}).get("overall", {}).get("value")
        deep = sd.get("deepSleepSeconds")
        rem = sd.get("remSleepSeconds")
        data["deep_sleep_min"] = round(deep / 60) if deep else None
        data["rem_sleep_min"] = round(rem / 60) if rem else None
    except Exception:
        data["sleep_hours"] = None

    # HRV
    try:
        hrv = garth_client.connectapi(f"/hrv-service/hrv/{date_str}") or {}
        summary = hrv.get("hrvSummary") or {}
        data["hrv"] = summary.get("lastNight")
        data["hrv_status"] = summary.get("status")
    except Exception:
        data["hrv"] = None

    # Steps + distância + calorias
    try:
        daily = garth_client.connectapi(
            f"/usersummary-service/usersummary/daily/{display_name}?calendarDate={date_str}"
        ) or {}
        steps = daily.get("totalSteps")
        dist = daily.get("totalDistanceMeters")
        data["steps"] = steps if steps else None
        data["distance_km"] = round(dist / 1000, 1) if dist else None
        data["calories"] = daily.get("totalKilocalories")
        data["active_calories"] = daily.get("activeKilocalories")
        stress = daily.get("averageStressLevel")
        data["stress_avg"] = stress if stress and stress > 0 else None
        data["body_battery_low"] = daily.get("minBodyBattery")
        data["body_battery_high"] = daily.get("maxBodyBattery")
    except Exception:
        data["steps"] = None

    # Atividades
    try:
        activities = garth_client.connectapi(
            f"/activitylist-service/activities/search/activities"
            f"?startDate={date_str}&endDate={date_str}&limit=5"
        ) or []
        acts = []
        for a in activities:
            dist_m = a.get("distance") or 0
            acts.append({
                "name": a.get("activityName", ""),
                "type": (a.get("activityType") or {}).get("typeKey", ""),
                "duration_min": round((a.get("duration") or 0) / 60),
                "distance_km": round(dist_m / 1000, 1),
                "calories": a.get("calories", 0),
                "avg_hr": a.get("averageHR"),
            })
        data["activities"] = acts
    except Exception:
        data["activities"] = []

    return data


def build_note(d):
    lines = [
        "---",
        f"date: {d['date']}",
        "type: health",
        "source: garmin",
        "tags: [saude, garmin]",
        "---",
        "",
        f"## Dados Garmin — {d['date']}",
        "",
    ]

    if d.get("sleep_hours") is not None:
        score = f" (score: {d['sleep_score']})" if d.get("sleep_score") else ""
        deep = f"{d['deep_sleep_min']} min" if d.get("deep_sleep_min") else "?"
        rem = f"{d['rem_sleep_min']} min" if d.get("rem_sleep_min") else "?"
        lines += [
            "### Sono",
            f"- Total: **{d['sleep_hours']}h**{score}",
            f"- Profundo: {deep} | REM: {rem}",
            "",
        ]

    if d.get("hrv") is not None:
        status = f" ({d['hrv_status']})" if d.get("hrv_status") else ""
        lines += ["### HRV", f"- **{d['hrv']} ms**{status}", ""]

    if d.get("steps") is not None:
        lines += [
            "### Movimento",
            f"- Passos: {d['steps']:,} | Distância: {d['distance_km']} km",
            f"- Calorias: {d.get('calories', '?')} total ({d.get('active_calories', '?')} ativas)",
            "",
        ]

    if d.get("stress_avg") is not None:
        bb_low = d.get("body_battery_low", "?")
        bb_high = d.get("body_battery_high", "?")
        lines += [
            "### Stress & Body Battery",
            f"- Stress médio: {d['stress_avg']} | Body Battery: {bb_low}–{bb_high}",
            "",
        ]

    if d.get("activities"):
        lines.append("### Atividades")
        for a in d["activities"]:
            dist = f" | {a['distance_km']} km" if a["distance_km"] > 0 else ""
            hr = f" | FC média: {a['avg_hr']} bpm" if a.get("avg_hr") else ""
            lines.append(f"- **{a['name']}** ({a['type']}): {a['duration_min']} min{dist}{hr}")
        lines.append("")

    has_data = any([
        d.get("sleep_hours"), d.get("hrv"), d.get("steps"), d.get("activities")
    ])
    if not has_data:
        lines.append("_Sem dados registrados para este dia (relógio não usado ou sincronização pendente)._")

    return "\n".join(lines)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup()
        return

    creds = load_creds()
    target = date.today() - timedelta(days=1)

    print(f"Buscando dados Garmin para {target}...")
    garth, display_name = get_display_name(creds)
    print(f"Usuário: {display_name}")

    data = fetch_garmin_data(garth, display_name, target)
    content = build_note(data)
    rel_path = f"2-Areas/Saude/garmin/{target.strftime('%Y-%m-%d')}.md"

    result = subprocess.run(
        [SAVE_SCRIPT, "idea", rel_path, content],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        parts = []
        if data.get("sleep_hours"):
            parts.append(f"Sono: {data['sleep_hours']}h")
        if data.get("hrv"):
            parts.append(f"HRV: {data['hrv']}ms")
        if data.get("steps"):
            parts.append(f"Passos: {data['steps']:,}")
        if data.get("activities"):
            a = data["activities"][0]
            parts.append(f"Treino: {a['name']} {a['duration_min']}min")
        summary = " | ".join(parts) if parts else "Sem dados registrados"
        print(f"OK: {rel_path}")
        print(f"Resumo: {summary}")
    else:
        print(f"ERRO: {result.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
