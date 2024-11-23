import asyncio
import aiohttp
import ssl
import json

api_url = "https://m.vodafone.com.tr/maltgtwaycbu/api?method=getC2dTariffs&id="
current_tariff = 0  # Başlangıç tarife ID'si
found_tariffs = []  # Bulunan tarifeleri saklamak için
max_queries = 45618  # Maksimum sorgu sayısı
queries_count = 0  # Şu ana kadar yapılan sorgu sayısı

# SSL Sertifika doğrulamasını geçersiz kılmak
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def fetch_tariff(session, tariff_id):
    global queries_count
    try:
        async with session.get(api_url + str(tariff_id), ssl=ssl_context) as response:
            response.raise_for_status()  # HTTP hatası varsa bir exception fırlatır
            data = await response.json()

            if data['result']['result'] == "SUCCESS":
                tariff = data['tariffList'][0]
                found_tariffs.append({
                    'id': tariff['id'],
                    'name': tariff['name'],
                    'summaryPriceInfo': tariff['summaryPriceInfo'],
                    'tariffType': tariff['tariffType'],
                    'activationStartDate': tariff['activationStartDate'],
                    'activationEndDate': tariff['activationEndDate']
                })
                print(f"Bulunan Tarife: ID: {tariff['id']}, Adı: {tariff['name']}, Fiyat: {tariff['summaryPriceInfo']}")
            else:
                print(f"ID {tariff_id}: Tarife bulunamadı.")

            queries_count += 1  # Sorgu sayısını arttır
            if queries_count >= max_queries:
                print(f"Max sorgu sayısına {max_queries} ulaşıldı. İşlem durduruluyor.")
                return False  # Bu durumda işlemi durduracak

    except Exception as e:
        print(f"ID {tariff_id} Hata: {e}")
    return True  # Sorgu başarılıysa devam et

async def fetch_all_tariffs():
    global current_tariff
    async with aiohttp.ClientSession() as session:
        while queries_count < max_queries:
            # Her seferinde yalnızca 10 tarife sorgulayıp işlemi devam ettiriyoruz
            tasks = [fetch_tariff(session, tariff_id) for tariff_id in range(current_tariff, current_tariff + 10)]
            results = await asyncio.gather(*tasks)  # Paralel olarak görevleri çalıştırıyoruz

            if not all(results):  # Eğer bir sorgu sonucu False dönerse (yani işlem durdurulmuşsa)
                break  # Durdur
            current_tariff += 10  # Sonraki tarife ID'sine geçiyoruz

async def download_json():
    if not found_tariffs:
        print("Henüz indirilecek bir tarife bulunamadı.")
        return
    with open('tariffs1.json', 'w', encoding='utf-8') as f:
        json.dump(found_tariffs, f, ensure_ascii=False, indent=2)
    print("Tarifeler JSON olarak indirildi: tariffs.json")

# Asenkron işlevi çalıştır
async def main():
    await fetch_all_tariffs()
    await download_json()

# Ana işlevi çalıştır
asyncio.run(main())
