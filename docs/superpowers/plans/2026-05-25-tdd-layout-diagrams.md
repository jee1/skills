# TDD Layout & Diagrams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move TOC/reader paths to H2 front matter, enforce paragraph breaks in Ch.2–4, and require four mermaid diagrams under `--narrative`.

**Architecture:** Extend `validate-tdd.py` with `check_front_matter()` (strict), paragraph + diagram checks (narrative); update SKILL/template/samples.

**Tech Stack:** Python 3 validator, Markdown TDD docs, prd-to-tdd skill package

**Spec:** [2026-05-25-tdd-layout-diagrams-design.md](../specs/2026-05-25-tdd-layout-diagrams-design.md)

---

## Status: Completed 2026-05-25

- [x] `check_front_matter`, paragraph checks, diagram checks in `validate-tdd.py`
- [x] Tests + sample TDD migration
- [x] SKILL, template, narrative-rules, design-sections, subagent-prompts
