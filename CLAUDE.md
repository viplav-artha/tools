# tools — Project Memory

## What this project is
A learning project to understand how "tools" (function calling) work for LLMs, by building a
small repo of general-purpose tools (search first, more later — calculator, file I/O, SQL, etc.)
in pure Python, with no LLM framework in the loop. Tool schemas are hand-written JSON-schema
dicts, and the model is called directly via AWS Bedrock's `boto3` Converse API. This is
explicitly a learning/demo project, not production-intent — but it's also meant to become a
reusable personal library of tools going forward, so code should stay clean and self-contained
even though rigor (error handling, retries, auth hardening) is intentionally kept light for now.

## Repo
- GitHub: https://github.com/viplav-artha/tools (public, account `viplav-artha`, no org)
- Local path: /Users/viplavsingh/Desktop/project/tool

## How this project is being taught/built (rules for any session, including a fresh one)
- Teacher/student mode. Before writing any new file: explain WHY the file needs to
  exist and WHAT logic goes in it, in plain language, as if teaching someone new to
  the language/framework. Analogies are fine and encouraged in chat explanations.
- One file at a time. Do not start the next file until the user has studied the
  current one and explicitly says they're ready to move on. Never auto-chain
  multiple files in one turn.
- After every file is created: update this file's "Current status" and
  "Files created so far" sections, AND add a matching entry to NOTES.md
  (Timeline graph + Routes Graph if applicable + logic/motive note).
  Do this immediately, without being asked again each time.
- NOTES.md must never use analogies — plain logic/motive explanations only.
  (This file, CLAUDE.md, and chat teaching CAN use analogies.)
- Repo is public: never put real secrets/credentials in any tracked file —
  `.env` stays git-ignored; only `.env.example` with placeholders is committed.
  AWS auth uses a local SSO profile (`AWS_PROFILE`), not a static key, which
  helps here, but the Tavily API key still must never be committed.
- Git/GitHub commands (init, repo create, add, commit, push) always get explicit
  user go-ahead before running, regardless of permission mode — show the exact
  command first.
- No LLM framework (no LangChain, no agent frameworks) — tool schemas, the tool
  registry/dispatch, and the agent loop are all hand-written plain Python. The
  point of this project is to see the raw mechanics.

## Current status
Stage: Lesson 4 (`agent.py`) done — all four planned files for the search-tool
slice are now written. `tools/registry.py` and `tools/search_tool.py` were
revised mid-build to be async (see standing rule below), and `agent.py`
handles a single tool-call round only (ask → tool → final answer), not a
general loop — reverted from an initial general `while True` version per
explicit user request. Multiple simultaneous `toolUse` blocks in one turn
still run concurrently via `asyncio.gather`, but a model wanting to chain a
*second* round of tool calls after seeing the first result isn't supported —
would need the loop reinstated later if that's ever needed.

**Blocked on AWS permissions, not code**: the live end-to-end test hit
`AccessDeniedException` — the `Artha-stg-dev` SSO role lacks
`bedrock:InvokeModel` permission. Every code path (env config, `boto3`
session/client, request building, the agent loop) executed correctly up to
the actual AWS call. Logged under Known gaps; re-test once permissions are
granted or a working profile is supplied. Waiting on user for what's next —
either fix AWS access and confirm a live run, or move on to planning
additional tools.

Also: an earlier mistake pasted the real `TAVILY_API_KEY` into
`.env.example` instead of `.env` — caught and fixed before any commit
reached GitHub (see `.env.example` is still tracked/committable, `.env` is
git-ignored and holds the real value).

## Standing rule addition
- All tool functions (anything registered via `@tool(...)`) must be
  `async def`. `call_tool()` in the registry always `await`s them. Async I/O
  libraries only inside tool implementations (e.g. `httpx`, not `requests`).
- `agent.py`'s loop is single-round by design (not a general loop) — this was
  an explicit user choice, not a default to "improve" without asking first.

## Planned build order
1. `llm.py` — pure-`boto3` Bedrock Converse API wrapper (rewrite of the
   LangChain version), same `get_llm()` calling convention. — **DONE**
2. `tools/registry.py` — hand-written JSON-schema tool spec format + a
   registry/dispatch pattern (schema list for `toolConfig`, name → function
   lookup for execution), async `call_tool()`. — **DONE**
3. `tools/search_tool.py` — the search tool itself: schema + async function
   that calls the Tavily API via `httpx`. — **DONE**
4. `agent.py` — single-round agent loop: send message + tools, detect
   `toolUse`, execute via registry (concurrently if multiple), send
   `toolResult` back, print final answer. — **DONE** (untested live, blocked
   on AWS Bedrock permissions — see Current status)
5. (Future) additional tools under `tools/` — calculator, file I/O, SQL, etc.
   — each one lesson, following the Lesson 3 pattern. Not yet planned in
   detail. — **NEXT (once user decides)**

## Files created so far (chronological)
1. `.gitignore` — standard Python gitignore (from init-project bootstrap)
2. `README.md` — minimal starter README (from init-project bootstrap)
3. `requirements.txt` — empty, header comment only (from init-project bootstrap)
4. `.env.example` — placeholder env var names for Bedrock config (added
   alongside `llm.py`, not separately numbered as its own lesson)
5. `llm.py` — pure-`boto3` Bedrock Converse API wrapper; exposes `get_llm()`
   returning a `BedrockLLM` with `.invoke(messages, tools=None)`
6. `tools/registry.py` — `@tool(...)` decorator + `get_tool_specs()` /
   `call_tool()`; doesn't import `llm.py` (it's consumed by it via
   `agent.py`, not the other way around)
7. `tools/search_tool.py` — `web_search` tool: imports `tool` from
   `tools/registry.py`, calls Tavily's REST API via `httpx` (async; revised
   from an initial sync `requests` version)
8. `agent.py` — single-round agent loop; imports `get_llm` from `llm.py` and
   `call_tool`/`get_tool_specs` from `tools/registry.py` (plus
   `tools/search_tool.py` for its registration side effect)

(`tools/__init__.py` was also created, as an empty package marker — not
numbered, per the usual convention.)

(`.venv/` was also created during bootstrap but is a directory, not a tracked
file, so it isn't numbered here.)

## Environment
- Activate venv: `source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt` (currently `boto3`,
  `python-dotenv`, `httpx`)
- Run: `python agent.py`, then type a question at the `Ask something:`
  prompt. Currently blocked on AWS Bedrock permissions (see Current status).
- Copy `.env.example` to `.env` and fill in real values (AWS profile, model
  ID, region, and a Tavily API key from https://tavily.com) before `llm.py`
  or `tools/search_tool.py` can be used live.
- External services: AWS Bedrock (via AWS SSO profile, env var `AWS_PROFILE`)
  for the LLM; Tavily API (env var `TAVILY_API_KEY`) for the search tool.
  Both keys/config live in a git-ignored `.env` (a `.env.example` with
  placeholder names will be added alongside `llm.py`).

## Known gaps / deliberately deferred (be honest, don't hide these)
- No tests yet.
- No retry/error-handling around Bedrock or Tavily API calls yet — first pass
  is about seeing the mechanics work, not production hardening.
- No license chosen yet for the public repo (README has a TODO for this).
- `agent.py` handles only a single tool-call round — a model wanting to
  chain a second round of tool calls after seeing the first result isn't
  supported yet (deliberate, per user request, not an oversight).
- Live end-to-end run is blocked: current AWS SSO role
  (`AWSReservedSSO_ArthaStgEksDeveloper`, profile `Artha-stg-dev`) lacks
  `bedrock:InvokeModel` permission — confirmed via `aws sts
  get-caller-identity` (valid creds) plus `bedrock:ListFoundationModels` /
  `bedrock:InvokeModel` denied in every region tested (us-east-1, us-west-2,
  ap-south-1 — the profile's own default region). This is a flat IAM policy
  gap on this role, not a regional restriction. Code has not been verified
  against a real Bedrock response yet — only against the request-building
  path.
  - Root cause understood: a separate deployed API (a text-to-SQL service)
    that also calls an LLM works fine — it runs under a different identity
    (likely an EKS pod/service-account IAM role via IRSA), not the personal
    SSO login role used here. Personal dev roles and service roles commonly
    have different permissions by design. Fix requires an Artha AWS admin to
    grant Bedrock permissions to the `ArthaStgEksDeveloper` SSO role (or
    provide an alternate profile that already has them) — not fixable from
    this repo's code.

## Companion file
See `NOTES.md` for the plain-language, no-analogy study notes, the file-creation
Timeline graph, and the import-dependency Routes Graph.

## Maintenance instructions — MUST run after every new file is created
1. **Update `CLAUDE.md`** (this file): move the finished item's build-order entry
   to done, mark the new next item, update "Current status", append to "Files
   created so far".
2. **Update `NOTES.md` — Timeline graph**: append the new file as the next node,
   connected with `|` / `v` to the previous node, in strict creation order —
   except empty/near-empty `__init__.py` package markers, which are omitted
   entirely (no Timeline node, no File notes entry) since there's nothing in
   them worth studying.
3. **Update `NOTES.md` — Routes Graph**: only touch this if the new file contains
   actual import-relevant logic (skip config/text files and any `__init__.py`,
   even one with imports for side effects like table registration — that's
   plumbing, not something a reader needs to trace). This is a Mermaid (` ```mermaid graph TD `) diagram, rendered as a
   real flowchart by GitHub/VS Code — do not use hand-drawn ASCII arrows, they
   don't scale. There is exactly ONE Routes Graph diagram in NOTES.md — add the
   new node and its edges to that SAME diagram in place; never create a second,
   separate one elsewhere in the file. Assign the next number in the Routes
   Graph's OWN sequence as part of the node's label (independent from the
   Timeline number for the same file — the two graphs use different numbering,
   and NOTES.md must say so explicitly). Label each new edge with what it
   imports (e.g. `n2 -->|get_db| n6`) instead of maintaining a separate
   connections list.
4. **Update `NOTES.md` — File notes**: add a new `### [N] filename` entry with a
   `Motive` line and a `Logic` line. No analogies, short and factual.

Do all four every time, without waiting to be asked again.
