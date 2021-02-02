def negative_score_check(score_pairs):
    if not all(list(map(lambda x: x > 0, score_pairs.values()))):
        raise ValueError
