# Project layout and runtime

GitHub renders the diagrams below if you view this file on the site.

### Runtime (who talks to whom)

```mermaid
flowchart LR
  subgraph Client
    UI[dialog.py or your app]
  end
  subgraph Port8080
    GW[start.py Flask-SocketIO]
  end
  subgraph LocalBERT
    R7[reject_infer :8007]
    I8[intent_infer :8008]
  end
  subgraph NLU
    N9[chatnlu_infer :8009]
    FN[function.py tools]
  end
  subgraph RemoteLLM
    LLM[Groq / OpenAI-compatible API]
  end
  RD[(Redis)]
  UI <-->|Socket.IO request_nlu| GW
  GW --> RD
  GW -->|HTTP| R7
  GW -->|HTTP| I8
  GW -->|HTTP| N9
  N9 --> FN
  N9 -->|HTTP| LLM
  GW -->|HTTP| LLM
```

### Repository tree (main pieces)

```mermaid
flowchart TB
  ROOT[robot_agent_project]
  ROOT --> ST[start.py entry]
  ROOT --> PR[prompts.py]
  ROOT --> CF[config/ class.txt slot_intent.json]
  ROOT --> CL[client/ arbitration rewrite nlu reject stream_chat ...]
  ROOT --> FC[function_call/]
  FC --> CH[chatnlu_infer.py]
  FC --> FU[function.py tools]
  FC --> SL[slot_process.py]
  FC --> DM[dm/ weather music maps factory]
  ROOT --> TR[train/]
  TR --> RI[reject_infer.py intent_infer.py run.py]
  TR --> MD[models/ bert.py]
  TR --> DT[data/ intent reject]
  TR --> CR[core/ tokenization modeling]
  ROOT --> UT[utils/ logger redis_tool]
  ROOT --> RS[results/ samples.jsonl summary report.html]
  ROOT --> SC[scripts/ collect build report]
```

### Typical request path (simplified)

```mermaid
sequenceDiagram
  participant C as Client
  participant S as start.py
  participant Redis as Redis
  participant B as BERT services
  participant N as chatnlu 8009
  participant L as Remote LLM
  C->>S: emit request_nlu
  S->>Redis: session keys
  par parallel
    S->>B: reject + intent
    S->>N: NLU + tools
    S->>L: arbitration, rewrite, chat
  end
  S-->>C: emit request_nlu JSON frames
```

There is no automatic PNG screenshot in the repo. After `python scripts/collect_submission_results.py`, run `python scripts/build_results_report.py` and open `results/report.html` in a browser to screenshot the formatted table.
