import json
import html

# 定義例外映射
EXCEPTION_PACK_MAPPING = {
    'CRZ-GG': {
        'path_pack': 'CRZ',
        'filename_prefix': 'CRZ_GG'
    },
    # 其他例外情況可以在這裡添加
}

def process_raw_data_to_json(raw_data):
    lines = raw_data.strip().splitlines()

    data = {"pokemon": [], "trainer": [], "energy": [], 'total_cards': 0}
    section = None

    for line in lines:
        if line.startswith("Pokémon:"):
            section = "pokemon"
        elif line.startswith("Trainer:"):
            section = "trainer"
        elif line.startswith("Energy:"):
            section = "energy"
        elif line.startswith("Total Cards:"):
            break
        else:
            parts = line.split()
            if len(parts) == 0:
                continue

            last_entity = parts[-1]
            # 預處理：檢查最後一個區段是否為數字，否則移除
            if not last_entity.isdigit():
                parts = parts[0:-1]

            quantity = int(parts[0])
            name = " ".join(parts[1:-2])
            card_type = parts[-2]
            series_num = parts[-1]

            # 處理例外情況
            if card_type in EXCEPTION_PACK_MAPPING:
                ext_pack = EXCEPTION_PACK_MAPPING[card_type]['path_pack']
                filename_prefix = EXCEPTION_PACK_MAPPING[card_type]['filename_prefix']
                # 根據例外情況生成 card_img_url
                card_img_url = f'https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/{ext_pack}/{filename_prefix}{series_num}_R_EN.png'
                page_url = f'https://limitlesstcg.com/cards/{ext_pack}/{series_num}'
            else:
                if card_type == 'Energy':
                    ext_pack = 'SVE'
                else:
                    ext_pack = card_type
                filename_prefix = ext_pack
                # 生成 card_img_url
                card_img_url = f'https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/{ext_pack}/{filename_prefix}_{str(series_num).zfill(3)}_R_EN.png'
                page_url = f'https://limitlesstcg.com/cards/{ext_pack}/{series_num}'

            card = {
                "name": name,
                "type": card_type,
                "series_num": series_num,
                "quantity": quantity,
                'page_url': page_url,
                'card_img_url': card_img_url,
            }

            data['total_cards'] += quantity
            data[section].append(card)

    return data

def add_cards_to_html(html_content, cards):
    for card in cards:
        name = html.escape(card['name'])
        page_url = html.escape(card['page_url'])
        card_img_url = html.escape(card['card_img_url'])
        quantity = card['quantity']
        html_content += f"""
        <div class="card">
            <a target="_blank" href="{page_url}"><img src="{card_img_url}" alt="{name}"></a>
            <div class="quantity-overlay">{quantity}</div>
        </div>
        """
    return html_content

def generate_html(data):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Card Collection</title>
    <style>
        .cards {
            display: flex;
            flex-wrap: wrap;
        }
        .card {
            flex: 0 0 10%; /* 每张图片占据10%的宽度 */
            text-align: center;
            box-sizing: border-box;
            /* padding: 5px; */ /* 正確的註解方式 */
            margin-bottom: 20px; /* 增加每行的行距 */
            position: relative; /* 為數量信息做定位 */
        }
        .card img {
            max-width: 100%;
            height: auto;
        }
        .quantity-overlay {
            position: absolute;
            bottom: 5px; /* 距離底部5px */
            left: 5px;   /* 距離左邊5px */
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            padding: 2px 5px;
            font-size: 18px; /* 添加單位 px */
            border-radius: 1px;
            display: flex;
            align-items: center; /* 垂直居中 */
            justify-content: center; /* 水平居中 */
            width: calc(100% - 10px); /* 宽度减去边距 */
            box-sizing: border-box; /* 包括内边距在内的宽度计算 */
        }
    </style>
</head>
<body>
    <div class="cards">
"""
    html_content = add_cards_to_html(html_content, data['pokemon'])
    html_content = add_cards_to_html(html_content, data['trainer'])
    html_content = add_cards_to_html(html_content, data['energy'])

    html_content += """
    </div>
    </body>
    </html>
    """
    with open("card_collection.html", "w", encoding='utf-8') as file:
        file.write(html_content)

    print("HTML 文件已生成")

def main():
    raw_data = """
Pokémon: 13
2 Pidgeot ex PAF 221
2 Pidgey OBF 207
1 Lumineon V CRZ-GG 39
1 Fezandipiti ex SFA 92
3 Drakloak TWM 129
1 Manaphy CRZ-GG 6
4 Dreepy TWM 128
1 Duskull SFA 68
1 Rotom V LOR 177
1 Dusclops SFA 69
1 Dusknoir SFA 70
1 Radiant Alakazam SIT 59
3 Dragapult ex TWM 200

Trainer: 20
4 Buddy-Buddy Poffin TWM 223
1 Crispin SCR 164
1 Iono PAL 254
1 Pokémon League Headquarters OBF 192
1 Super Rod PAL 276
1 Forest Seal Stone SIT 156
1 Rescue Board TEF 159
1 Nest Ball SVI 255
1 Earthen Vessel SFA 96
4 Arven PAF 235
1 Iono PAF 237
1 Switch MEW 206
2 Boss's Orders PAL 265
1 Technical Machine: Devolution PAR 177
1 Roxanne ASR 188
1 Counter Catcher PAR 264
1 Nest Ball PAF 84 PH
3 Ultra Ball SVI 196
1 Sparkling Crystal SCR 142
4 Rare Candy SVI 191

Energy: 2
3 Basic {R} Energy SVE 2
3 Basic {P} Energy SVE 5

Total Cards: 60
"""
    data = process_raw_data_to_json(raw_data)
    json_output = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_output)

    # 提取原始數據中的總卡片數量
    lines = raw_data.strip().splitlines()
    total_cards_raw = 0
    for line in lines:
        if line.startswith("Total Cards:"):
            total_cards_raw = int(line.split(":")[1].strip())
            break

    if data['total_cards'] != total_cards_raw:
        print(f"警告：計算出的總卡片數量 ({data['total_cards']}) 與原始數據中的總數量 ({total_cards_raw}) 不一致。")

    generate_html(data)

if __name__ == '__main__':
        main()
