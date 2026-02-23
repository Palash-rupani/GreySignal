import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax
import torch
from tqdm import tqdm

# ── Config ──────────────────────────────────────────────────────────────
INPUT_PATH  = "data/processed/ipo_tagged_news.csv"
OUTPUT_PATH = "data/processed/ipo_sentiment_scored.csv"
MODEL_NAME  = "ProsusAI/finbert"
BATCH_SIZE  = 8   # keep low for CPU
MAX_LENGTH  = 512
# ────────────────────────────────────────────────────────────────────────

def load_model():
    print("Loading FinBERT model (first run downloads ~440MB)...")
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    model     = BertForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model

def get_text_column(df):
    """Auto-detect the right text column."""
    for col in ["clean_text", "text", "summary", "title"]:
        if col in df.columns:
            return col
    raise ValueError(f"No usable text column found. Columns: {df.columns.tolist()}")

def score_batch(texts, tokenizer, model):
    inputs = tokenizer(
        texts,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=MAX_LENGTH
    )
    with torch.no_grad():
        outputs = model(**inputs)
    probs = softmax(outputs.logits, dim=1).numpy()
    # FinBERT label order: positive=0, negative=1, neutral=2
    return probs

def score_dataframe(df, tokenizer, model, text_col):
    positives, negatives, neutrals, labels, scores = [], [], [], [], []

    texts = df[text_col].fillna("").tolist()

    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Scoring sentiment"):
        batch = texts[i : i + BATCH_SIZE]
        # Replace empty strings with a placeholder so FinBERT doesn't choke
        batch = [t if t.strip() else "no text" for t in batch]
        probs = score_batch(batch, tokenizer, model)

        for p in probs:
            pos, neg, neu = float(p[0]), float(p[1]), float(p[2])
            positives.append(round(pos, 4))
            negatives.append(round(neg, 4))
            neutrals.append(round(neu, 4))

            label = ["positive", "negative", "neutral"][p.argmax()]
            labels.append(label)

            # Compound-style score: +1 fully positive, -1 fully negative
            scores.append(round(pos - neg, 4))

    df = df.copy()
    df["sentiment_label"]    = labels
    df["sentiment_score"]    = scores   # range: -1 to +1
    df["sentiment_positive"] = positives
    df["sentiment_negative"] = negatives
    df["sentiment_neutral"]  = neutrals
    return df

def main():
    print(f"Reading {INPUT_PATH}...")
    df = pd.read_csv(INPUT_PATH)
    print(f"  → {len(df)} articles loaded")

    text_col = get_text_column(df)
    print(f"  → Using text column: '{text_col}'")

    tokenizer, model = load_model()

    df_scored = score_dataframe(df, tokenizer, model, text_col)

    df_scored.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ Saved scored data to {OUTPUT_PATH}")
    print(df_scored[["ipo_name", "sentiment_label", "sentiment_score"]].head(10))

if __name__ == "__main__":
    main()