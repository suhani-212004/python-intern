
import re
import string
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "of", "to",
    "in", "on", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "from",
    "up", "down", "is", "are", "was", "were", "be", "been", "being", "am",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "them", "my", "your", "his", "its", "our", "their", "this", "that",
    "these", "those", "as", "so", "than", "too", "very", "can", "will",
    "just", "do", "does", "did", "doing", "have", "has", "had", "having",
    "not", "no", "nor", "only", "own", "same", "such", "there", "here",
    "what", "which", "who", "whom", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "out", "over", "under", "again",
    "further", "once", "off", "itself",
}




def clean_text(text):
    """Lowercase, strip punctuation, and split into words."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()
    return words


def remove_stopwords(words):
    return [w for w in words if w not in STOPWORDS]




def split_sentences(text):
    """Split text into sentences using ., !, ? as delimiters."""
    raw = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in raw if s.strip()]
    return sentences


def word_count_stats(words):
    return {
        "total_words": len(words),
        "unique_words": len(set(words)),
    }


def top_n_words(words, n=5):
    counter = Counter(words)
    return counter.most_common(n)


def sentence_length_stats(sentences):
    """Returns word-count stats per sentence."""
    if not sentences:
        return {
            "sentence_count": 0,
            "avg_words_per_sentence": 0,
            "shortest_sentence_words": 0,
            "longest_sentence_words": 0,
        }
    lengths = [len(s.split()) for s in sentences]
    return {
        "sentence_count": len(sentences),
        "avg_words_per_sentence": round(sum(lengths) / len(lengths), 2),
        "shortest_sentence_words": min(lengths),
        "longest_sentence_words": max(lengths),
    }


def analyze_text(text):
    """Run the full analysis pipeline and return a results dict."""
    raw_words = clean_text(text)
    meaningful_words = remove_stopwords(raw_words)
    sentences = split_sentences(text)

    results = {
        "word_stats": word_count_stats(raw_words),
        "top_words": top_n_words(meaningful_words, 5),
        "sentence_stats": sentence_length_stats(sentences),
    }
    return results




def format_report(text, results):
    lines = []
    lines.append("=" * 50)
    lines.append("TEXT ANALYSIS REPORT")
    lines.append("=" * 50)
    lines.append("")
    lines.append("Original Text:")
    lines.append(text.strip())
    lines.append("")
    lines.append("-" * 50)
    lines.append("WORD COUNT")
    lines.append("-" * 50)
    lines.append(f"Total words   : {results['word_stats']['total_words']}")
    lines.append(f"Unique words  : {results['word_stats']['unique_words']}")
    lines.append("")
    lines.append("-" * 50)
    lines.append("TOP 5 FREQUENT WORDS (stopwords excluded)")
    lines.append("-" * 50)
    if results["top_words"]:
        for rank, (word, count) in enumerate(results["top_words"], start=1):
            lines.append(f"{rank}. {word:<15} {count} occurrence(s)")
    else:
        lines.append("No significant words found.")
    lines.append("")
    lines.append("-" * 50)
    lines.append("SENTENCE STATISTICS")
    lines.append("-" * 50)
    ss = results["sentence_stats"]
    lines.append(f"Sentence count           : {ss['sentence_count']}")
    lines.append(f"Avg words per sentence   : {ss['avg_words_per_sentence']}")
    lines.append(f"Shortest sentence (words): {ss['shortest_sentence_words']}")
    lines.append(f"Longest sentence (words) : {ss['longest_sentence_words']}")
    lines.append("=" * 50)
    return "\n".join(lines)


def export_report(report_text, filename="analysis_results.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"\nResults exported to '{filename}'.")
    except OSError as e:
        print(f"[Error] Could not export results: {e}")




def get_input_text():
    """Ask the user whether to type text directly or load it from a file."""
    print("How would you like to provide the text?")
    print("1. Type/paste a paragraph directly")
    print("2. Load text from a file")
    choice = input("Select an option (1-2): ").strip()

    if choice == "2":
        path = input("Enter the file path: ").strip()
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            if not text.strip():
                print("The file is empty. Please provide text.")
                return get_input_text()
            return text
        except OSError as e:
            print(f"[Error] Could not read file: {e}")
            return get_input_text()
    else:
        text = input("\nEnter/paste your paragraph:\n> ").strip()
        while not text:
            print("Input cannot be empty.")
            text = input("> ").strip()
        return text




def main():
    print("=" * 50)
    print("       TEXT ANALYZER TOOL")
    print("=" * 50)

    text = get_input_text()
    results = analyze_text(text)
    report = format_report(text, results)

    print("\n" + report)

    export_choice = input("\nExport results to a text file? [y/N]: ").strip().lower()
    if export_choice == "y":
        filename = input("Enter output filename (default: analysis_results.txt): ").strip()
        if not filename:
            filename = "analysis_results.txt"
        export_report(report, filename)

    print("\nDone.")


if __name__ == "__main__":
    main()
