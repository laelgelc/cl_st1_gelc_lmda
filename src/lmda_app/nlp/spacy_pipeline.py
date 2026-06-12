from __future__ import annotations

import csv
from pathlib import Path

import spacy

from lmda_app.nlp.normalisation import is_usable_lemma, normalise_lemma
from lmda_app.nlp.processed_tokens import ProcessedToken, ProcessingSummary


DEFAULT_SPACY_MODEL = "en_core_web_sm"


class SpacyPipelineError(RuntimeError):
    """Raised when spaCy processing fails."""


def load_spacy_model(model_name: str = DEFAULT_SPACY_MODEL):
    """Load the configured spaCy model."""
    try:
        return spacy.load(model_name)
    except OSError as exc:
        msg = (
            f"Could not load spaCy model '{model_name}'. "
            "Install it or ensure it is available in the current environment."
        )
        raise SpacyPipelineError(msg) from exc


def process_corpus_from_text_id_mapping(
        text_id_mapping_path: Path,
        corpus_root: Path,
        spacy_model: str = DEFAULT_SPACY_MODEL,
) -> tuple[list[ProcessedToken], ProcessingSummary]:
    """Process all texts listed in the text ID mapping file."""
    nlp = load_spacy_model(spacy_model)

    tokens: list[ProcessedToken] = []
    warnings: list[str] = []

    processed_texts = 0
    skipped_texts = 0
    processed_tokens = 0
    retained_tokens = 0

    for row in _read_text_id_mapping(text_id_mapping_path):
        text_id = row["text_id"]
        subcorpus = row["subcorpus"]
        relative_path = Path(row["path"])
        source_path = corpus_root / relative_path

        try:
            text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            skipped_texts += 1
            warnings.append(f"Could not read {source_path}: {exc}")
            continue
        except UnicodeDecodeError as exc:
            skipped_texts += 1
            warnings.append(f"Could not decode {source_path} as UTF-8: {exc}")
            continue

        if not text.strip():
            skipped_texts += 1
            warnings.append(f"Skipped empty text: {source_path}")
            continue

        doc = nlp(text)
        processed_texts += 1

        for token_index, token in enumerate(doc, start=1):
            processed_tokens += 1

            lemma = normalise_lemma(token.lemma_)

            if not is_usable_lemma(lemma):
                continue

            tokens.append(
                ProcessedToken(
                    text_id=text_id,
                    subcorpus=subcorpus,
                    token_index=token_index,
                    surface=token.text,
                    pos=token.pos_,
                    lemma=lemma,
                )
            )
            retained_tokens += 1

    summary = ProcessingSummary(
        processed_texts=processed_texts,
        skipped_texts=skipped_texts,
        processed_tokens=processed_tokens,
        retained_tokens=retained_tokens,
        warnings=warnings,
    )

    return tokens, summary


def _read_text_id_mapping(text_id_mapping_path: Path) -> list[dict[str, str]]:
    """Read the text ID mapping TSV file."""
    with text_id_mapping_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        return list(reader)