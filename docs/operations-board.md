# Khukra Operations Board

**Last updated:** 2026-06-30

Single tracker for suggestions, decisions, and work across **Khukra Finance** and **Khukra Logistics**.  
The chat is not the source of truth — **this file and the GitHub Project are**.

| Resource | Location |
|----------|----------|
| Machine-readable items | [`board.manifest.json`](../board.manifest.json) |
| Sync to GitHub | `.\scripts\sync-operations-board.ps1` |
| GitHub Project | **Khukra Operations** (#4) — [open board](https://github.com/users/Claymorrr/projects/4) |

---

## Todo

| ID | Item | Repo |
|----|------|------|
| — | _(none — pick from backlog)_ | — |

---

## In Progress

| ID | Item | Repo |
|----|------|------|
| ops-012 | Push khukra-logistics to GitHub + link board | logistics |
| ops-013 | Maintain Operations board as canonical tracker | ops |

---

## Backlog (suggestions)

| ID | Item | Repo |
|----|------|------|
| ops-004 | Macro regime feeds (FRED/ECB + VSTOXX) | khukra |
| ops-005 | Corporate actions for .DE backtests | khukra |
| ops-006 | Expand beyond DAX 32 (MDAX / Euro Stoxx) | khukra |
| ops-010 | Port congestion + geopolitical event feeds | logistics |
| ops-011 | Calibrate sim model from composite risk panel | logistics |

---

## Done (recent)

| ID | Item | Repo |
|----|------|------|
| ops-001 | Stabilize local dev (startup sync, DuckDB locks) | khukra |
| ops-002 | DAX data: Stooq → Yahoo Finance | khukra |
| ops-003 | Full-universe refresh + 15y history | khukra |
| ops-007 | Scaffold khukra-logistics repo | logistics |
| ops-008 | Disruption ingest + statistical discovery | logistics |
| ops-009 | Discovery cockpit UI | logistics |

---

## How to add items

1. Add an entry to `board.manifest.json` (`status`: Backlog | Todo | In Progress | Done).
2. Run `.\scripts\sync-operations-board.ps1` to create/update GitHub issues and the project board.
3. Move cards in GitHub Project as work progresses.

## Columns (GitHub Project)

`Backlog` → `Todo` → `In Progress` → `Done` (or `Won't do`)
