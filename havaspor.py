import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import smtplib
from email.message import EmailMessage
import argparse

def fetch_programs():
    url = "https://www.sporekrani.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Veri çekme hatası: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    event_items = soup.find_all("div", class_="row")

    seen = set()
    programs = []

    for item in event_items:
        time_tag = item.find("span", class_="text-body3-medium q-mr-md")
        time = time_tag.get_text(strip=True) if time_tag else ""

        title_tag = item.find("p", class_="q-mb-xs text-body3-bold")
        title = title_tag.get_text(strip=True) if title_tag else ""

        desc_tag = item.find("p", class_="q-mb-none text-body3-medium text-grey-6")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        channel = ""
        channel_img = item.find("div", class_="channel-img")
        if channel_img:
            img_tag = channel_img.find("img")
            if img_tag and img_tag.has_attr("alt"):
                channel = img_tag["alt"]

        record = (time, title, description, channel)
        if all(record) and record not in seen:
            seen.add(record)
            programs.append(list(record))

    return programs

def generate_html_table(data, headers):
    html = "<table border='1' cellspacing='0' cellpadding='5' style='border-collapse:collapse;'>"
    html += "<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"
    for row in data:
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    html += "</tbody></table>"
    return html

def fetch_weather(city="Istanbul"):
    url = "https://api.open-meteo.com/v1/forecast"
    coords = {
        "Istanbul": (41.0082, 28.9784),
        "Ankara": (39.9208, 32.8541),
        "Izmir": (38.4192, 27.1287)
    }
    lat, lon = coords.get(city, (41.0082, 28.9784))

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        weather = data.get("current_weather", {})
        return {
            "temperature": weather.get("temperature"),
            "windspeed": weather.get("windspeed"),
            "winddirection": weather.get("winddirection"),
            "weathercode": weather.get("weathercode")
        }
    except requests.RequestException as e:
        print(f"Hava durumu verisi alınamadı: {e}")
        return None

def weather_description_from_code(code):
    codes = {
        0: "Açık",
        1: "Az bulutlu",
        2: "Parçalı bulutlu",
        3: "Kapalı",
        45: "Sisli",
        48: "Buz sisli",
        51: "Hafif çiseleme",
        61: "Hafif yağmur",
        71: "Hafif kar",
        80: "Hafif sağanak",
        95: "Fırtına"
    }
    return codes.get(code, "Bilinmeyen")

def print_weather_info(city):
    weather = fetch_weather(city)
    if weather:
        desc = weather_description_from_code(weather.get("weathercode"))
        print(f"\n {city} için Güncel Hava Durumu")
        print("-" * 40)
        print(f"Açıklama   : {desc}")
        print(f"Sıcaklık   : {weather['temperature']}°C")
        print(f"Rüzgar     : {weather['windspeed']} km/h")
        print(f"Yön        : {weather['winddirection']}°")
    else:
        print(" Hava durumu verisi alınamadı.")

def send_local_email_html(to_email, subject, html_body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "haldenanlayan-sistemyonetimi@sahibinden.com"
    msg["To"] = to_email
    msg.set_content("Bu e-posta HTML desteklemeyen istemcilerde görüntülenemez.")
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP("10.212.254.61", 25) as smtp:
            smtp.send_message(msg)
            print(f"✅ HTML formatında e-posta gönderildi: {to_email}")
    except Exception as e:
        print(f" E-posta gönderilemedi: {e}")

def list_unique_channels(programs):
    channels = sorted(set(row[3] for row in programs))
    print("\n Yayıncı Kanallar")
    print("-" * 40)
    for ch in channels:
        print(f"- {ch}")

def main():
    parser = argparse.ArgumentParser(description="sporekrani.com günlük maç programı")
    parser.add_argument("--search", type=str, help="Kelimeye göre program ara")
    parser.add_argument("--kanal", type=str, help="Belirtilen kanala göre programları filtrele")
    parser.add_argument("--list-channels", action="store_true", help="Kanal listesini göster")
    parser.add_argument("--email", type=str, help="Eşleşen satırı e-posta ile gönder")
    parser.add_argument("--havadurum", type=str, help="Sadece hava durumunu göster (örn: Istanbul)")
    parser.add_argument("--havadurum-email", nargs=2, metavar=("CITY", "EMAIL"), help="Şehir ve e-posta adresi ile hava durumu bilgisini gönder")
    args = parser.parse_args()

    if args.havadurum:
        print_weather_info(args.havadurum)
        return

    if args.havadurum_email:
        city, email = args.havadurum_email
        weather = fetch_weather(city)
        if weather:
            desc = weather_description_from_code(weather.get("weathercode"))
            weather_html = f"""
                <h2>{city} Hava Durumu</h2>
                <ul>
                    <li><strong>Açıklama:</strong> {desc}</li>
                    <li><strong>Sıcaklık:</strong> {weather['temperature']}°C</li>
                    <li><strong>Rüzgar:</strong> {weather['windspeed']} km/h</li>
                    <li><strong>Yön:</strong> {weather['winddirection']}°</li>
                </ul>
                <h4>by bigdata</h4>
            """
            html_body = f"<html><body>{weather_html}</body></html>"
            send_local_email_html(email, f"{city} Hava Durumu", html_body)
        else:
            print(" Hava durumu verisi alınamadı.")
        return

    programs = fetch_programs()
    if not programs:
        print("Hiç geçerli program bulunamadı.")
        return

    if args.list_channels:
        list_unique_channels(programs)
        return

    filtered = programs
    filter_label = "Tüm Programlar"

    if args.kanal:
        kanal = args.kanal.lower()
        filtered = [row for row in programs if kanal in row[3].lower()]
        filter_label = f"'{args.kanal}' Kanalındaki Programlar"

    if args.search:
        keyword = args.search.lower()
        filtered = [row for row in filtered if any(keyword in cell.lower() for cell in row)]
        filter_label = f"'{args.search}' Araması"

    if not filtered:
        print(f" Filtre ile eşleşen bir program bulunamadı.")
        return

    print(f"\n {filter_label}:")
    print(tabulate(filtered, headers=["Saat", "Program", "Detay", "Kanal"], tablefmt="pretty"))

    if args.email:
        html_body = f"""
            <html>
                <body>
                    <h2>{filter_label}</h2>
                    {generate_html_table(filtered, ["Saat", "Program", "Detay", "Kanal"])}
                </body>
            </html>
        """

        send_local_email_html(args.email, f"Program Bilgisi - {filter_label}", html_body)

if __name__ == "__main__":
    main()
