import json
from difflib import SequenceMatcher

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_pair(pair):
    return (
        pair['span-s']['span'], pair['span-s']['attr'],
        pair['rel'],
        pair['span-e']['span'], pair['span-e']['attr']
    )

def compare_pairs(pairs1, pairs2):
    pairs1_fmt = [format_pair(p) for p in pairs1]
    pairs2_fmt = [format_pair(p) for p in pairs2]

    matches = 0
    matched_entities = set()

    for p1 in pairs1_fmt:
        if p1 in pairs2_fmt:
            matches += 1
            matched_entities.add(p1[0])
            matched_entities.add(p1[3])

    return matches, len(matched_entities)

def find_best_match(sentence, sentences_set, threshold=0.8):
    """Find the best fuzzy match for a sentence from a set of sentences."""
    best_match = None
    best_ratio = 0
    for s in sentences_set:
        ratio = SequenceMatcher(None, sentence, s).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = s
    if best_ratio >= threshold:
        return best_match
    return None

def compare_json_files(file1, file2, fuzzy_threshold=0.8):
    data1 = load_json(file1)
    data2 = load_json(file2)

    # Build lookup dictionaries
    dict1 = {item['sentence']: item for item in data1}
    dict2 = {item['sentence']: item for item in data2}

    stats = []
    total_sentences = 0
    sentences_fully_matched = 0
    total_pairs_matched = 0
    total_entities_matched = 0
    sum_pair_match_rate = 0
    sum_entity_match_rate = 0

    # Fuzzy match sentences
    used_sentences2 = set()
    common_sentences = []

    for s1 in dict1.keys():
        match = find_best_match(s1, set(dict2.keys()) - used_sentences2, threshold=fuzzy_threshold)
        if match:
            common_sentences.append((s1, match))
            used_sentences2.add(match)

    for sent1_text, sent2_text in common_sentences:
        sent1 = dict1[sent1_text]
        sent2 = dict2[sent2_text]

        total_sentences += 1
        num_pairs, num_entities = compare_pairs(sent1['pairs'], sent2['pairs'])
        total_entities_in_sentence = len(sent1['pairs']) * 2
        pair_match_rate = num_pairs / len(sent1['pairs']) if sent1['pairs'] else 0
        entity_match_rate = num_entities / total_entities_in_sentence if total_entities_in_sentence else 0

        if num_pairs == len(sent1['pairs']) and num_pairs == len(sent2['pairs']):
            sentences_fully_matched += 1

        total_pairs_matched += num_pairs
        total_entities_matched += num_entities
        sum_pair_match_rate += pair_match_rate
        sum_entity_match_rate += entity_match_rate

        stats.append({
            'sentence_file1': sent1_text,
            'sentence_file2': sent2_text,
            'total_pairs_file1': len(sent1['pairs']),
            'total_pairs_file2': len(sent2['pairs']),
            'matching_pairs': num_pairs,
            'matching_entities': num_entities,
            'pair_match_rate': round(pair_match_rate, 2),
            'entity_match_rate': round(entity_match_rate, 2)
        })

    overall_stats = {
        'total_sentences_compared': total_sentences,
        'sentences_fully_matched': sentences_fully_matched,
        'total_pairs_matched': total_pairs_matched,
        'total_entities_matched': total_entities_matched,
        'average_pair_match_rate': round(sum_pair_match_rate / total_sentences, 2) if total_sentences else 0,
        'average_entity_match_rate': round(sum_entity_match_rate / total_sentences, 2) if total_sentences else 0,
        'sentences_only_in_file1': list(set(dict1.keys()) - set(s1 for s1, _ in common_sentences)),
        'sentences_only_in_file2': list(set(dict2.keys()) - set(s2 for _, s2 in common_sentences))
    }

    return stats, overall_stats

if __name__ == "__main__":
    file1 = 'test.json'
    file2 = 'test_predictions.json'
    per_sentence_stats, overall_stats = compare_json_files(file1, file2)

    print("\nPer-sentence stats:")
    for s in per_sentence_stats:
        print(json.dumps(s, indent=2, ensure_ascii=False))

    print("\nOverall stats:")
    print(json.dumps(overall_stats, indent=2, ensure_ascii=False))