    # Model Metrics

This document defines the evaluation metrics for each model category used in the Global Search benchmarking pipeline. It provides a clear, per-model breakdown of the metrics, their rationale, and target thresholds.

---

## Embedding Models

| Model Name                                | Metrics                                                                                                   | Rationale                                                                                                                      | Target Thresholds                                                                                         |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `text-embedding-ada-002`                  | - Recall\@10<br>- Recall\@50<br>- MRR<br>- Cosine Similarity Mean<br>- Latency (ms)<br>- Throughput (QPS) | Measures retrieval effectiveness, ranking quality, embedding clustering tightness, real-time performance, and bulk throughput. | ≥0.80 (Recall\@10), ≥0.90 (Recall\@50), ≥0.50 (MRR), ≥0.75 (Cosine Similarity), ≤100 ms latency, ≥100 QPS |
| `sentence-transformers/all-mpnet-base-v2` | - Recall\@10<br>- Recall\@50<br>- MRR<br>- Cosine Similarity Mean<br>- Latency (ms)<br>- Throughput (QPS) | High-quality sentence embeddings for semantic search; same effectiveness and performance metrics.                              | ≥0.80 (Recall\@10), ≥0.90 (Recall\@50), ≥0.50 (MRR), ≥0.75 (Cosine Similarity), ≤100 ms latency, ≥100 QPS |

---

## Generation Models

| Model Name      | Metrics                                                                                | Rationale                                                                                                          | Target Thresholds                                                         |
| --------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `gpt-3.5-turbo` | - BLEU<br>- ROUGE-L<br>- Distinct-2<br>- Latency (ms)<br>- Average Tokens per Response | Evaluates surface-level and sequence-level similarity, diversity of outputs, response speed, and token usage cost. | ≥0.15 BLEU, ≥0.25 ROUGE-L, ≥0.30 Distinct-2, ≤300 ms latency, ≤150 tokens |
| `llama-2-chat`  | - BLEU<br>- ROUGE-L<br>- Distinct-2<br>- Latency (ms)<br>- Average Tokens per Response | Open-source chat model; same generation quality and performance metrics.                                           | ≥0.15 BLEU, ≥0.25 ROUGE-L, ≥0.30 Distinct-2, ≤300 ms latency, ≤150 tokens |

