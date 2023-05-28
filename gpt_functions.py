import csv
import os
import openai
import time

class ChatGPT:
    def __init__(self, api_key):
        openai.api_key = api_key
    def make_response(self, system_message, user_message):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.75,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0.3,
                presence_penalty=0
            )
            response_message = response.choices[0].message['content'].strip()
            return response_message
        except ValueError as ve:
            if "tokens" in str(ve):
                print(f"Context length error : {ve}. Skipping...")
                return None
            else:
                raise ve

    def generate_category_ids(self, product_title, product_description):
        message_content = f"Basierend auf dem Produkttitel '{product_title}' und der Produktbeschreibung '{product_description}' finde die passenden Kategorien und gib als Liste zurück. Beispiele für den erwarteten Ausgabewerte: '1061','1065','1067' oder '1031', '1029', '1067' oder '1062','1042','1033'"
        category_ids = "id;description\n95;Hauttyp\n504;Gratis-Proben\n787;Gesicht\n788;Körper\n790;Top-Seller\n792;Neu\n793;Sale 40%\n810;Gesichtsreinigung\n811;Gesichtspflege\n812;Super Anti-Aging\n813;Sonne\n814;Zubehör, Sets\n815;Männer\n816;Cleanser\n817;Peeling\n818;Gesichtswasser\n819;Tagescreme\n820;getönte Tagescreme\n821;Nachtcreme\n822;Augenpflege\n823;Lippenpflege\n825;Serum & Kur\n826;Maske\n827;Spezialpflege\n828;Hyaluron Produkte\n829;Anti-Aging Gesicht\n830;Augen\n831;Lippen\n832;Lichtschutz Gesicht\n833;After Sun\n834;Self Tan\n835;Bräunungsverstärker\n836;Zubehör\n837;Sets\n838;Reinigungstücher\n839;Pflege\n840;Rasur\n841;Body\n842;Hände & Füße\n843;Super Anti-Aging\n844;Sonne\n845;Zubehör & Sets\n846;Männer\n847;Bodylotion\n848;Bodycreme\n849;Bodyöl\n850;Körperpeeling\n851;Duschen\n852;Baden\n853;Deo\n854;Handpflege\n855;Fußpflege\n857;Nägel\n858;Spezialprodukte\n859;Hyaluronprodukte\n860;Anti-Aging Körper\n861;Lichtschutz Körper\n862;After Sun\n863;Selbstbräuner\n864;Bräunungsverstärker\n865;Zubehör\n866;Sets\n867;Duschen\n868;Gesichtspflege\n869;Körperpflege\n870;Gesichtspflege\n871;Körperpflege\n872;Gesichtspflege\n873;Körperpflege\n874;Make-up\n875;Hauttypen\n876;Normale Haut\n877;Trockene Haut\n878;Mischhaut\n879;Ölige Haut\n880;Empfindliche Haut\n886;Problemlösungen\n887;Akne\n888;Unreinheiten\n889;Rosacea\n890;Neurodermitis\n891;Couperose\n892;Hyperpigmentierungen\n893;Empfindlichkeit\n894;Trockenheit\n899;Haare\n900;Shampoo\n901;Conditioner\n902;Spezialprodukte\n903;Sets\n904;Make-up\n905;Teint\n906;Lippen\n907;Augen\n910;Lifestyle\n917;Schönheitsergänzung\n1182;TEST Amelie\n1188;Campaign\n1231;Anti-Virus\n1261;Kurzes MHD\n1267;Kurzes MHD\n1278;Geschenke\n1280;Düfte\n1281;Geschenk-Sets\n1282;Accessoires\n1283;Nahrungsergänzung\n1289;limitierte Editionen\n1304;Zubehör\n1308;Haarfarbe\n1309;Haarwachstum\n1310;Kopfhautpflege\n1314;Nahrungsergänzung\n1316;Serum & Spray\n1317;Körperbutter\n1319;Haarserum/Haaröl\n1328;Haarmaske/Haarkur\n1349;Zahnpflege\n1358;Inhaltsstoffe\n1359;Bakuchiol\n1360;Hyaluron\n1361;Retinol\n1362;Vitamin C\n1363;Niacinamid\n1365;Alle Artikel\n1391;Geschenke\n1397;Kerzen\n1398;Kosmetik Bags\n1401;Zahnpflege\n1403;Supersale 60%\n1404;Gesichtspflege\n1405;Körperpflege\n1406;Make-up\n1407;Nahrungsergänzung\n1408;Kurzes MHD\n1409;Düfte\n1410;Geschenke\n1411;Düfte\n1412;Limited Editions\n1413;Bags\n1414;Düfte\n1415;Kerzen\n1418;Super Anti-Aging\n1419;Gesicht\n1424;Körper\n1431;Reife Haut\n1433;Sale einzelne Produkte\n1434;Sale Einzelprodukte\n1438;Peptide\n1442;Ceramide\n1446;CBD\n1450;Pflegeroutine\n2251;Nagellack\n"
        messages = [
            {"role": "system", "content": "You are a beauty product category classifier. Your task is to analyze a cosmetic product's description on german and title on german to determine the relevant categories it belongs to. The categories are represented by a Python string"+category_ids+"Your goal is to extract the appropriate categories based on the product's information. Remember to consider both the description and the title when determining the categories, all inputs are on german. Your response should be a simple list of categories that the product belongs to. Examples : -'880,873,852,846'\n -1406, 1403, 1363, 1309, 1261"},
            {"role": "user", "content": message_content}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.75,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0.3,
                presence_penalty=0
            )
            category_ids = response.choices[0].message['content'].strip()
            return category_ids
        except ValueError as ve:
            if "tokens" in str(ve):
                print(f"Context length error for product {product_title}: {ve}. Skipping...")
                return None
            else:
                raise ve
    def generate_scc_category_ids(self, product_title, product_description):
        categories_scc = "id;description\n1030;Gesicht\n1031;Gesichtsreinigung\n1032;Gesichtspflege\n1033;Super Anti-Aging\n1034;Sonne\n1035;Zubehör, Sets\n1036;Männer\n1037;Cleanser\n1038;Peeling\n1039;Gesichtswasser\n1040;Tagescreme\n1041;getönte Tagescreme\n1042;Nachtcreme\n1043;Augenpflege\n1044;Lippenpflege\n1045;Serum & Kur\n1046;Maske\n1047;Spezialpflege\n1048;Hyaluron Produkte\n1049;Anti-Aging Gesicht\n1050;Augen\n1051;Lippen\n1052;Lichtschutz Gesicht\n1053;After Sun\n1054;Self Tan\n1055;Bräunungsverstärker\n1056;Zubehör\n1057;Sets\n1058;Reinigungstücher\n1059;Pflege\n1060;Rasur\n1061;Körper\n1062;Body\n1063;Hände & Füße\n1064;Super Anti-Aging\n1065;Sonne\n1066;Zubehör & Sets\n1067;Männer\n1068;Haare\n1069;Bodylotion\n1070;Bodycreme\n1071;Bodyöl\n1072;Körperpeeling\n1073;Duschen\n1074;Baden\n1075;Deo\n1076;Handpflege\n1077;Fußpflege\n1078;Nägel\n1079;Spezialprodukte\n1080;Hyaluronprodukte\n1081;Anti-Aging Körper\n1082;Lichtschutz Körper\n1083;After Sun\n1084;Selbstbräuner\n1085;Bräunungsverstärker\n1086;Zubehör\n1087;Sets\n1088;Duschen\n1089;Shampoo\n1090;Conditioner\n1091;Spezialprodukte\n1092;Sets\n1093;Top-Seller\n1094;Gesichtspflege\n1095;Körperpflege\n1096;Neu\n1097;Gesichtspflege\n1098;Körperpflege\n1099;Schönheitsergänzung\n1100;Marken\n1123;Make-up\n1124;Teint\n1125;Lippen\n1126;Augen\n1127;Sale 40%\n1128;Gesichtspflege\n1129;Körperpflege\n1130;Make-up\n1131;Hauttest\n1134;Problemlösungen\n1135;Akne\n1136;Unreinheiten\n1137;Rosacea\n1138;Neurodermitis\n1139;Couperose\n1140;Hyperpigmentierungen\n1141;Empfindlichkeit\n1142;Trockenheit\n1143;Lifestyle\n1233;Anti-Virus\n1262;Kurzes MHD\n1268;Kurzes MHD\n1279;Geschenke\n1284;Düfte\n1285;Geschenk-Sets\n1286;Accessoires\n1287;Limited Editions\n1288;Nahrungsergänzung\n1305;Zubehör\n1311;Haarfarbe\n1312;Haarwachstum\n1313;Kopfhautpflege\n1315;Serum & Spray\n1318;Körperbutter\n1320;Haarserum/Haaröl\n1329;Haarmaske/Haarkur\n1350;Zahnpflege\n1364;Nahrungsergänzung\n1383;Inhaltsstoffe\n1384;Bakuchiol\n1385;Hyaluron\n1386;Retinol\n1387;Vitamin C\n1388;Niacinamid\n1389;Alle Artikel\n1392;Lifestyle\n1399;Kerzen\n1400;Bags\n1402;Zahnpflege\n1441;Peptide\n1445;Ceramide\n1449;CBD\n1631;Pflegeroutine\n2175;Hauttypen\n2176;Normale Haut\n2177;Trockene Haut\n2178;Mischhaut\n2179;Ölige Haut\n2180;Empfindliche Haut\n2254;Nagellack\n2300;Super Anti-Aging\n2301;Anti-Aging Serum\n2302;Anti-Aging Augen\n2303;Anti-Aging Creme\n2304;Anti-Aging Ernährung\n2348;Bürsten/Kämme\n2370;Nagellack\n2378;Sale Einzelprodukte\n2379;Düfte\n2380;Geschenke\n"
        message_content = f"Basierend auf dem Produkttitel '{product_title}' und der Produktbeschreibung '{product_description}' finde die passenden Kategorien und gib als Liste zurück. Beispiele für den erwarteten Ausgabewerte: '1061','1065','1067' or '1031', '1029', '1067' or '1062','1042','1033'  "
        messages = [
            {"role": "system", "content": "You are a beauty product category classifier. Your task is to analyze a cosmetic product's description on german and title on german to determine the relevant categories it belongs to. The categories are represented by a Python string"+categories_scc+"Your goal is to extract the appropriate categories based on the product's information. Remember to consider both the description and the title when determining the categories, all inputs are on german. Your response should be a simple list of categories that the product belongs to. Examples : -'1031,1033,1061' or 1048\n 1049, 1050, 1082, 1305 "},
            {"role": "user", "content": message_content}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.75,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0.3,
                presence_penalty=0
            )
            category_ids = response.choices[0].message['content'].strip()
            return category_ids
        except ValueError as ve:
            if "tokens" in str(ve):
                print(f"Context length error for product {product_title}: {ve}. Skipping...")
                return None
            else:
                raise ve

    def generate_meta_title(self, product_title, product_description):
        message_content = f"Generate a meta title on german for the product with title '{product_title}' and description '{product_description}'"

        messages = [
            {"role": "system", "content": "You are given a product title and description. Your task is to generate a suitable short meta title on german for this product. Use informal style like 'du'."},
            {"role": "user", "content": message_content}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.5,
                max_tokens=50,
                top_p=1,
                frequency_penalty=0.3,
                presence_penalty=0
            )
            meta_title = response.choices[0].message['content'].strip()
            return meta_title
        except ValueError as ve:
            if "tokens" in str(ve):
                print(f"Context length error for product {product_title}: {ve}. Skipping...")
                return None
            else:
                raise ve
    def generate_skin_type(self, product_title, product_description, product_attributes):
        message_content = f"title: '{product_title}' description : '{product_description}' attributes: '{product_attributes}' "

        messages = [
            {"role": "system", "content": "Let's think step by step. You are analyzing product {title} (string), {description} (string)and {attributes}(json) on german to find out if this product is good for this 6 types of skin : sensitive, dry, normal, mix, fett, old or all types of skin. Keep in mind to check context to make right decision\nGive a list without any comments back.\n---\nEXPECTED OUTPUT:\n'sensitive, fett,mix'\n\nOR\n'mixed, fett,'\n\nOR\n 'sensitive, fett,mix'\n\nOR\n'all'\n---\nAfter you have the list, make sure there are only 6 skin types mentioned in the task on english divided by comma and enclosed in double quotes\n"},
            {"role": "user", "content": message_content}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.75,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            skin_type = response.choices[0].message['content'].strip()
            return skin_type
        except ValueError as ve:
            if "tokens" in str(ve):
                print(f"Context length error for product's skin_type {product_title}: {ve}. Skipping...\n\n")
                return None
            else:
                raise ve
def save_to_error_log(ean, error, error_log_file):
    error_log_file.write(f"{ean} : {error}\n")
    error_log_file.flush()

if __name__ == "__main__":
    with open("api.key", "r") as api_key_file:
        api_key = api_key_file.read()
    chat_gpt = ChatGPT(api_key)

    with open("inputs/compagnie_de_provence_extended.csv", "r") as csv_file, \
         open("outputs/updated_extended_cdp_products_de.csv", "w", newline='') as new_csv_file, \
         open('error_log.txt', 'w') as error_log_file:

        reader = csv.DictReader(csv_file, delimiter=";")
        fieldnames = reader.fieldnames + ["category_ids", "meta_title", "scc_category_ids", "skin_type"]
        writer = csv.DictWriter(new_csv_file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for row in reader:
            success = False
            retries = 15
            ean = row['EAN ']
            while not success and retries > 0:
                try:
                    category_ids = chat_gpt.generate_category_ids(row["Produkt"], row["product_description"])
                    scc_category_ids = chat_gpt.generate_scc_category_ids(row["Produkt"], row["product_description"])
                    meta_title = chat_gpt.generate_meta_title(row["Produkt"], row["product_description"])
                    skin_type = chat_gpt.generate_skin_type(row["Produkt"], row["product_description"], row["product_attributes"])
                    row["category_ids"] = category_ids
                    row["scc_category_ids"] = scc_category_ids
                    row["meta_title"] = meta_title
                    row["skin_type"] = skin_type
                    writer.writerow(row)
                    new_csv_file.flush()
                    success = True
                except openai.error.RateLimitError as e:
                    print(f"Rate limit error: {e}. Retrying in 5 seconds...")
                    retries -= 1
                    time.sleep(5)
                    save_to_error_log(ean, e, error_log_file)
                except openai.error.APIError as e:
                    print(f"API error: {e}. Retrying in 5 seconds...")
                    retries -= 1
                    time.sleep(5)
                    save_to_error_log(ean, e, error_log_file)
                except Exception as e:
                    print(f"Unexpected error: {e}. Retrying in 5 seconds...")
                    retries -= 1
                    time.sleep(5)
                    print(f"No data returned from API for product with EAN {ean}.")
                    save_to_error_log(ean, e, error_log_file)