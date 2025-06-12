import re
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Hardcoded keywords relevant to business domain
_KEYWORDS = [
    "order",
    "invoice",
    "subscription",
    "customer",
    "region",
    "amount",
    "billing",
    "usage",
]

# Regex pattern to match known formats like "order 1234"
_ORDER_PATTERN = re.compile(r"order\s+\d+", re.IGNORECASE)


def is_valid_prompt(sentence: str) -> bool:
    """Return True if sentence contains relevant keywords or patterns."""
    lower_sentence = sentence.lower()
    # Keyword search
    keyword_found = any(keyword in lower_sentence for keyword in _KEYWORDS)
    # Regex search
    pattern_found = bool(_ORDER_PATTERN.search(sentence))

    is_valid = keyword_found or pattern_found

    if is_valid:
        logging.info("Prompt accepted: %s", sentence)
    else:
        logging.info("Prompt rejected: %s", sentence)

    return is_valid


if __name__ == "__main__":
    samples = [
        "Order 1234 for region NA",
        "Random gibberish text",
        "Subscription invoice for customer 9",
        "Check billing usage",
    ]
    for sample in samples:
        print(sample, "->", is_valid_prompt(sample))
