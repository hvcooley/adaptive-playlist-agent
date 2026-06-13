import os

from wikipedia_semantic_data_extract import collect_artist_corpus

if __name__ == "__main__":
    SMALL_TEST_ARTISTS = [
        "Blink-182",
        "Kings_of_Leon",
        "Kendrick_Lamar",
        "Taylor_Swift",
        "The_Beatles",
        "Daft_Punk",
        "Treaty_Oak_Revival",
        "Imagine_Dragons",
        "Tame_Impala",
        "Billie_Eilish",
        "MGK",
        "Yungblud"
    ]

    chunks = collect_artist_corpus(SMALL_TEST_ARTISTS)
    print(f"\nCollected {len(chunks)} chunks across {len(SMALL_TEST_ARTISTS)} artists.")

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "small_corpus_preview.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Collected {len(chunks)} chunks across {len(SMALL_TEST_ARTISTS)} artists.\n\n")
        for chunk in chunks:
            f.write(f"[{chunk['metadata']['artist']} / {chunk['metadata']['section']}]\n")
            f.write(chunk["text"])
            f.write("\n\n" + "-" * 80 + "\n\n")
    print(f"Full corpus written to {output_path}")