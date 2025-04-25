from config import UK_TO_US_SIZE, MALE_SIZE_GUIDE, FEMALE_SIZE_GUIDE


def estimate_clothing_size(measurements, gender='male'):
    """Estimate clothing size based on measurements"""
    size_guide = MALE_SIZE_GUIDE if gender.lower() == 'male' else FEMALE_SIZE_GUIDE

    size_scores = {}
    for size in size_guide['shoulder_width'].keys():
        score = 0
        for measurement, value in measurements.items():
            if measurement in size_guide:
                min_val, max_val = size_guide[measurement][size]
                if value < min_val:
                    score += (min_val - value)
                elif value > max_val:
                    score += (value - max_val)
        size_scores[size] = score

    best_size = min(size_scores, key=size_scores.get)
    return best_size, UK_TO_US_SIZE.get(best_size, best_size)