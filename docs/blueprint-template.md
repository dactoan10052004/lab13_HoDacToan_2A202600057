# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: HoDacToan_2A202600057
- [REPO_URL]: https://github.com/dactoan10052004/lab13_HoDacToan_2A202600057
- [MEMBERS]:
  - Member A: Ho Dac Toan | Role: Logging & PII | Student ID: 2A202600057

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 50+
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Chụp từ data/logs.jsonl — mỗi dòng có correlation_id dạng req-xxxxxxxx]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Chụp từ logs — u01 gửi email student@vinuni.edu.vn → xuất hiện [REDACTED_EMAIL] trong payload.message_preview]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Chụp từ cloud.langfuse.com → Traces → click 1 trace → xem span agent.run]
- [TRACE_WATERFALL_EXPLANATION]: Span `agent.run` bao gồm toàn bộ pipeline: RAG retrieval (retrieve()) → LLM generation (FakeLLM.generate()) → quality scoring. Input hiển thị message preview đã scrub PII, output là answer preview. Metadata ghi lại doc_count, latency_ms, cost_usd, quality_score để debug khi cần.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Chụp dashboard 6 panel từ GET /metrics + Langfuse]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 150ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.04 |
| Quality Score Avg | > 0.75 | 28d | 0.88 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Chụp config/alert_rules.yaml]
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 tăng từ ~150ms lên ~2650ms (×17). Quan sát được qua GET /metrics (latency_p95 tăng đột biến) và load_test output hiển thị thời gian response > 2500ms.
- [ROOT_CAUSE_PROVED_BY]: Langfuse trace waterfall cho thấy span `agent.run` kéo dài 2500ms+ do `time.sleep(2.5)` trong `mock_rag.retrieve()` khi `STATE["rag_slow"] == True`. Log line: `event: response_sent, latency_ms: 2651`. Tắt incident bằng `POST /incidents/rag_slow/disable` → latency trở về bình thường ngay lập tức.
- [FIX_ACTION]: Gọi `POST /incidents/rag_slow/disable` hoặc `python scripts/inject_incident.py --disable rag_slow`. Trong production: fallback retrieval source, truncate long queries, giảm timeout RAG.
- [PREVENTIVE_MEASURE]: Alert rule `high_latency_p95` đã cấu hình (`latency_p95_ms > 5000 for 30m`, severity P2). Cần thêm circuit breaker cho RAG calls và health check riêng cho vector store.

---

## 5. Individual Contributions & Evidence

### Ho Dac Toan (2A202600057)
- [TASKS_COMPLETED]:
  - Implement Correlation ID middleware (`app/middleware.py`) — generate `req-<8hex>`, bind structlog contextvars, propagate to response headers
  - Log enrichment in `/chat` endpoint (`app/main.py`) — bind user_id_hash, session_id, feature, model, env
  - Activate PII scrubber processor (`app/logging_config.py`) — scrub_event trong structlog pipeline
  - Extend PII patterns (`app/pii.py`) — thêm passport, vn_address; fix CCCD/phone_vn ordering bug
  - Fix Langfuse v3 API compatibility (`app/tracing.py`, `app/agent.py`) — migrate từ `langfuse.decorators` (v2) sang `get_client()` + `start_as_current_span` (v3)
  - Add `load_dotenv()` và shutdown flush handler (`app/main.py`)
  - Implement audit logging (`app/logging_config.py`) — tách incident/error events vào `data/audit.jsonl`
  - Write 41 new tests (`tests/test_pii.py`, `tests/test_metrics.py`, `tests/test_middleware.py`, `tests/test_logging_config.py`)
  - Fix `mkdir` performance issue in logging pipeline
  - Update `config/slo.yaml` với measured values
- [EVIDENCE_LINK]: https://github.com/dactoan10052004/lab13_HoDacToan_2A202600057/commit/8ffa98f

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Không có số liệu trước/sau tối ưu — FakeLLM không cho phép thay đổi model. Trong production: route easy requests to cheaper model, apply prompt cache.
- [BONUS_AUDIT_LOGS]: Implemented — `data/audit.jsonl` ghi riêng các events: `incident_enabled`, `incident_disabled`, `request_failed`. Xem `app/logging_config.py:_AUDIT_EVENTS`. Test: `POST /incidents/rag_slow/enable` → audit.jsonl có entry mới ngay lập tức.
- [BONUS_CUSTOM_METRIC]: `/admin/flush` endpoint cho phép flush Langfuse traces on-demand — hữu ích trên Windows nơi graceful shutdown không hoạt động.
