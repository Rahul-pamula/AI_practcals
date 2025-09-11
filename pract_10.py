import spacy
from spellchecker import SpellChecker
from wordfreq import zipf_frequency
import textdistance
import numpy as np

# --------- Load spaCy model ---------
def load_nlp():
    for model in ["en_core_web_md", "en_core_web_lg", "en_core_web_sm"]:
        try:
            return spacy.load(model)
        except OSError:
            pass
    raise RuntimeError(
        "No spaCy English model found. Install one: "
        "`python -m spacy download en_core_web_md`"
    )

nlp = load_nlp()  # ✅ store it globally

# --------- Helper functions ---------
def has_vector(tok):
    return tok.has_vector and np.linalg.norm(tok.vector) > 0

def cosine(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na and nb else 0.0

def context_vector(doc, i, window=3):
    vecs = [t.vector for j, t in enumerate(doc) if j != i and has_vector(t) and abs(j - i) <= window]
    return np.mean(vecs, axis=0) if vecs else np.zeros(doc[i].vector.shape)

def pos_bonus(left_pos, right_pos, cand_pos, left_text):
    bonus = 0.0
    if left_pos == "DET" and right_pos in {"NOUN", "PROPN"} and cand_pos in {"ADJ", "NOUN"}:
        bonus += 0.15
    if left_text.lower() == "to" and cand_pos in {"VERB", "AUX"}:
        bonus += 0.15
    if right_pos in {"AUX", "VERB"} and cand_pos == "ADV":
        bonus += 0.1
    return bonus

def preserve_case(src, cand):
    if src.isupper():
        return cand.upper()
    if src.istitle():
        return cand.title()
    return cand

# --------- Scoring ---------
def score_candidate(doc, idx, candidate):
    original = doc[idx].text
    edit_sim = 1 - textdistance.levenshtein.normalized_distance(original.lower(), candidate.lower())
    freq_norm = max(0, min(1, (zipf_frequency(candidate, "en") - 1) / 6))

    ctx_vec = context_vector(doc, idx)
    cand_doc = nlp(candidate)
    cand_vec = cand_doc[0].vector if cand_doc and len(cand_doc) > 0 else np.zeros_like(ctx_vec)
    sem_score = cosine(ctx_vec, cand_vec)

    left_pos = doc[idx - 1].pos_ if idx > 0 else ""
    right_pos = doc[idx + 1].pos_ if idx + 1 < len(doc) else ""
    left_text = doc[idx - 1].text if idx > 0 else ""
    cand_pos = cand_doc[0].pos_ if len(cand_doc) else ""

    syntax = pos_bonus(left_pos, right_pos, cand_pos, left_text)

    total = 0.25 * edit_sim + 0.20 * freq_norm + 0.40 * sem_score + 0.15 * syntax
    return total, {
        "edit_sim": round(edit_sim, 3),
        "freq_norm": round(freq_norm, 3),
        "semantic": round(sem_score, 3),
        "syntax_bonus": round(syntax, 3),
        "cand_pos": cand_pos
    }

# --------- Suggestion ---------
def suggest_for_token(doc, i, speller, max_candidates=5):
    tok = doc[i]
    text = tok.text

    if not text.isalpha() or len(text) == 1:
        return None
    if tok.pos_ == "PROPN" and text[0].isupper():
        return None
    if text.lower() not in speller.unknown([text.lower()]):
        return None

    cands = list(speller.candidates(text))
    if not cands:
        return None

    scored = [(score_candidate(doc, i, c), c) for c in cands]
    scored.sort(key=lambda x: x[0][0], reverse=True)

    uniq = []
    seen = set()
    for (s, details), c in scored:
        if c.lower() not in seen:
            seen.add(c.lower())
            uniq.append((s, c, details))
        if len(uniq) >= max_candidates:
            break

    return {
        "token": text,
        "index": i,
        "best": uniq[0][1],
        "suggestions": [{"candidate": c, "score": round(s, 3), **d} for s, c, d in uniq]
    }

# --------- Main program ---------
if __name__ == "__main__":
    speller = SpellChecker(language="en")
    text = input("Enter your text: ").strip()
    doc = nlp(text)

    issues = []
    for i in range(len(doc)):
        res = suggest_for_token(doc, i, speller)
        if res:
            issues.append(res)

    if not issues:
        print("✅ No obvious spelling issues found.")
    else:
        print("\nSuggestions:")
        for item in issues:
            print(f"  '{item['token']}' → best: '{item['best']}'")
            for sug in item["suggestions"]:
                print(f"    {sug}")

        corrected_tokens = [t.text for t in doc]
        for item in issues:
            corrected_tokens[item["index"]] = preserve_case(corrected_tokens[item["index"]], item["best"])
        corrected_text = " ".join(corrected_tokens)
        print("\nAuto-corrected text:\n", corrected_text)

