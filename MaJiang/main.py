from collections import Counter

from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder='src/static')


def parse_hand(hand_str):
    hand = []
    tiles = hand_str.split()
    for tile in tiles:
        num = int(tile[1:])
        if tile.startswith('w'):
            hand.append(num)
        elif tile.startswith('b'):
            hand.append(num + 10)
        elif tile.startswith('t'):
            hand.append(num + 20)
    return hand


def dfs_melds(cards, path=[]):
    if not cards:
        return [path]

    unique_cards = sorted(set(cards))
    all_results = []

    # 处理刻子
    for card in unique_cards:
        if cards.count(card) >= 3:
            new_cards = cards.copy()
            for _ in range(3):
                new_cards.remove(card)
            results = dfs_melds(new_cards, path + [(card, card, card)])
            for result in results:
                all_results.append(result)

    # 处理顺子
    for i in range(len(unique_cards) - 2):
        if unique_cards[i] + 1 in unique_cards and unique_cards[i] + 2 in unique_cards:
            seq_start = unique_cards[i]
            if cards.count(seq_start) > 0 and cards.count(seq_start + 1) > 0 and cards.count(seq_start + 2) > 0:
                new_cards = cards.copy()
                new_cards.remove(seq_start)
                new_cards.remove(seq_start + 1)
                new_cards.remove(seq_start + 2)
                results = dfs_melds(new_cards, path + [(seq_start, seq_start + 1, seq_start + 2)])
                for result in results:
                    all_results.append(result)

    return all_results if all_results else []


def dfs_pairs(cards):
    pairs = [c for c in set(cards) if cards.count(c) >= 2]
    pairs_combinations = {}
    for pair in pairs:
        hand_copy = cards[:]
        hand_copy.remove(pair)
        hand_copy.remove(pair)
        results = dfs_melds(hand_copy)
        if results:
            pairs_combinations[tuple([pair, pair])] = results
    return pairs_combinations


def check_hu(cards):
    if len(cards) % 3 != 2:
        return False

    pairs = [c for c in set(cards) if cards.count(c) >= 2]
    for pair in pairs:
        hand_copy = cards[:]
        hand_copy.remove(pair)
        hand_copy.remove(pair)
        melds_result = dfs_melds(hand_copy)
        if melds_result:
            return True
    return False


def is_all_same_suit(cards):
    """检查所有牌是否为同一花色"""
    suits = set()
    for card in cards:
        if 1 <= card <= 9:
            suits.add('wan')
        elif 11 <= card <= 19:
            suits.add('tong')
        elif 21 <= card <= 29:
            suits.add('tiao')
    return len(suits) == 1


def calculate_score_and_type(combination, is_qingyise):
    """计算得分和牌型"""
    base_score = 2
    score = base_score
    hu_type = "平胡"

    if is_qingyise:
        score *= 2
        hu_type = "清一色"

    is_pengpenghu = all(len(set(meld)) == 1 for meld in combination)
    if is_pengpenghu:
        score *= 2
        hu_type = "碰碰胡"

    is_dandiao = len(combination) == 1
    if is_dandiao:
        score = 4
        hu_type = "单吊"

    if is_qingyise and is_pengpenghu and not is_dandiao:
        hu_type = "清碰"

    i = []  # 将所有组合放在一起
    for combo in combination:
        for j in combo:
            i.append(j)
    counts = Counter(i)
    gang_count = sum(1 for count in counts.values() if count >= 4)  # 计算杠的数量

    if gang_count > 0:
        score *= (2 ** gang_count)
        hu_type += " 带" + str(gang_count) + "杠"

    return score, hu_type


def find_hu_combinations_for_each_possible_hu(cards):
    possible_hus = find_possible_hu(cards)
    best_combinations = []
    remaining_counts = {x: 4 - cards.count(x) for x in range(1, 30) if x not in [10, 20]}

    for hu in possible_hus:
        test_hand = cards + [hu]
        is_qingyise = is_all_same_suit(test_hand)
        pairs_combinations = dfs_pairs(test_hand)
        highest_score = 0
        best_combination_for_hu = None
        best_pair_for_hu = None
        best_hu_type_for_hu = ""

        # 遍历所有可能的对子及其对应的组合结果
        for pair, results in pairs_combinations.items():
            for result in results:
                score, hu_type = calculate_score_and_type(result + [pair[:]], is_qingyise)
                if score > highest_score:
                    highest_score = score
                    best_combination_for_hu = result
                    best_pair_for_hu = pair
                    best_hu_type_for_hu = hu_type

        if best_combination_for_hu is not None:
            best_combinations.append({
                '胡牌': hu,
                '将': list(best_pair_for_hu),
                '组合': best_combination_for_hu,
                '分数': highest_score,
                '剩余张数': remaining_counts[hu],
                '牌型': best_hu_type_for_hu,
            })

    return possible_hus, best_combinations


def find_possible_hu(cards):
    possible_hu = []
    for i in range(1, 30):  # 检查所有可能的牌（1-9万，11-19筒，21-29条）
        if i in [10, 20]:
            continue
        if cards == [i] and len(cards + [i]) == 2:
            possible_hu.append(i)
            return possible_hu
        if check_hu(cards + [i]):
            possible_hu.append(i)
    return possible_hu


@app.route('/')
def index():
    return render_template('HTML_PAGE.html')


@app.route('/mahjong', methods=['GET'])
def mahjong_api():
    hand_str = request.args.get('hand', '')
    hand = parse_hand(hand_str)

    # 如果hand中的牌有三种花色，那么这手牌一定不能胡 具体规则为 如果1-9之间，11-19之间，21-29之间都有牌，那么一定不能胡
    suits = set()
    for card in hand:
        if 1 <= card <= 9:
            suits.add('wan')
        elif 11 <= card <= 19:
            suits.add('tong')
        elif 21 <= card <= 29:
            suits.add('tiao')
    if len(suits) == 3:
        return jsonify({'error': '有花猪!'}), 400

    if len(hand) % 3 != 1 and len(hand) != 0:
        return jsonify({'error': '你小相公了!'}), 400

    possible_hu, combinations = find_hu_combinations_for_each_possible_hu(hand)
    if not possible_hu and len(hand) != 0:
        return jsonify({'error': '这牌胡不了一点!'}), 400

    combinations_data = []
    for combo in combinations:
        combinations_data.append({
            '胡牌': combo['胡牌'],
            '将': combo['将'],
            '组合': combo['组合'],
            '分数': combo['分数'],
            '剩余张数': combo['剩余张数'],
            '牌型': combo['牌型']
        })
    return jsonify({'possible_hu': possible_hu, 'combinations': combinations_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=False)



