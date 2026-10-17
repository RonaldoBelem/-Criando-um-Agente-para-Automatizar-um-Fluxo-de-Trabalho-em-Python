# 🎯 Trello Board Manager Playbook

Last Updated: 2025-11-13 · Version: 1.4

A comprehensive guide for managing software development projects using our standardized Trello Board system.

## 📋 Table of Contents

- [Overview](#overview)
- [States & Gates](#states--gates)
  - [Definition of Ready (DoR) — To Do](#definition-of-ready-dor--to-do)
  - [QA Gate (Ready for QA)](#qa-gate-ready-for-qa)
  - [Definition of Done (DoD) — Moving to Done](#definition-of-done-dod--moving-to-done)
- [Labels & Classification](#labels--classification)
  - [Task Types](#task-types-primary-labels)
  - [Priority Levels](#priority-levels)
  - [Stack Labels](#stack-labels)
  - [Special Labels](#special-labels)
  - [Sprint Types](#sprint-types)
- [Dependency Management](#dependency-management)
- [Blocker & Expedite Policy](#blocker--expedite-policy)
- [Board Operations](#board-operations)
  - [Create/Refine a Backlog Card](#createrefine-a-backlog-card)
  - [Promote Backlog → To Do](#promote-backlog--to-do)
  - [Choose the Next Task & Start Work](#choose-the-next-task--start-work)
  - [Move to QA](#move-to-qa)
  - [Maintenance](#maintenance)
- [Good Card Guidelines](#good-card-guidelines)
- [Board Ceremonies](#board-ceremonies)
  - [Backlog Refinement](#backlog-refinement)
  - [Replenishment](#replenishment)
- [Templates](#templates)
- [Quick Reference](#quick-reference)
- [Healthy Board Checklist](#healthy-board-checklist)

---

## 🧭 Overview

Purpose: Give the Agent clear, concise rules to operate the Trello Kanban board.

Roles: Agent (executes), User (approves, clarifies, performs final QA sign-off).

Conventions: We refer to Definition of Ready as DoR and Definition of Done as DoD after first mention. List names are written exactly as: "To Do", "In Progress", "QA", "Done", "On Hold".



Kanban columns:

| Column                  | Purpose                          | When to Use                                |
| ----------------------- | -------------------------------- | ------------------------------------------ |
| **Sprint Descriptions** | High-level sprint overview cards | Store sprint metadata and goals            |
| **Backlog**             | Future work not yet prioritized  | Ideas and long-term tasks                  |
| **To Do**               | Ready-to-start tasks             | Work that's been planned and prioritized   |
| **In Progress**         | Currently active work            | Tasks being actively developed (limit WIP) |
| **QA**                  | Reviewed code ready for testing  | Tasks undergoing quality assurance         |
| **Done**                | Completed and deployed           | Successfully finished work                 |
| **On Hold**             | Temporarily paused work          | Blocked or deprioritized tasks             |


---

Workflow:

```
To Do → In Progress → QA → Done
           ↓
        On Hold (if blocked)
```

Rules:
- WIP limit: 2–3 tasks in In Progress
- One-task focus; finish before starting new
- Manual tasks first when they unblock others
- Blocked tasks stay in To Do

---

## ✅ States & Gates

### Definition of Ready (DoR) — To Do

A card may enter the `To Do` list only if ALL are present:

- Clear title following naming convention: `SXXX.TYYY {clean_task_name}` (e.g., `S001.T001 Setup Database Schema`).
- Description includes: Context, Scope/Out of Scope, Business Value, User Story, Technical Context, and a filled **Dependencies** checklist.
- Dependencies use FULL PREFIXED NAMES (e.g., "S001.T001 Database Setup", "S001.T002 Environment Config").
- Acceptance Criteria: bullet list using verifiable statements.
- QA Steps: explicit steps the User will execute to verify.
- Labels: exactly one Sprint label, one Type, one Priority, optional Stack.

Rules:
- Do not move items from `Backlog` to `To Do` unless they meet the above.
- If information is missing or unclear, ask in chat AND comment on the card tagging its creator/owner.
### QA Gate (Ready for QA)

Before moving a card to `QA`, the Agent MUST:

1. Read all Acceptance Criteria and confirm they are implemented.
2. Tick off each Acceptance Criterion on the card (or link evidence if applicable).
3. Update the description/checkboxes with any relevant notes, links, or screenshots.
4. Add a comment summarizing what was done and tag the card owner.

After moving the card to `QA`, the Agent pauses execution and assists the User through the QA Steps (answer questions, provide test data, reproduce steps). The Agent must not move a card to `Done`; the User confirms and moves it after QA passes.

---

### Definition of Done (DoD) — Moving to Done

A card may only be moved to `Done` after it has passed QA and ALL are true. The User performs the final move; the Agent assists verification.

- [ ] All Acceptance Criteria are ticked.
- [ ] Code merged and deployed to the target environment.
- [ ] QA approved by card owner or designated QA.
- [ ] Dependent cards updated (dependency checklist items ticked).
- [ ] User sign-off recorded in a comment.

---

## 🗂️ Labels & Classification

### Task Types (Primary Labels)

| Label         | When to Use                               | Example                                  |
| ------------- | ----------------------------------------- | ---------------------------------------- |
| **Manual**    | Setup, configuration, or human-only tasks | Environment setup, API key configuration |
| **Feature**   | New functionality or enhancements         | New UI components, API endpoints         |
| **Bug**       | Fixing broken functionality               | Error handling, UI fixes                 |
| **Chore**     | Maintenance and housekeeping              | Documentation, refactoring               |
| **Tech Debt** | Improving code quality                    | Performance optimization, code cleanup   |

### Priority Levels

| Label               | Meaning                        |
| ------------------- | ------------------------------ |
| **Priority High**   | Critical path, blocking others |
| **Priority Medium** | Standard priority              |
| **Priority Low**    | Nice to have, non-urgent       |

### Stack Labels
| Label         | Team/Skill Focus           |
| ------------- | -------------------------- |
| **Frontend**  | UI/UX, client-side code    |
| **Backend**   | Server, API, database      |
| **Fullstack** | Both frontend and backend  |
| **DevOps**    | Infrastructure, deployment |

### Special Labels

| Label                   | Purpose                                   |
| ----------------------- | ----------------------------------------- |
| **Needs Clarification** | Requires more information before starting |

**Label Application Rules**:
- Format: `[Sprint] + [Type] + [Priority] + [Stack]` (Stack is optional).
- Backlog cards: Sprint label optional; add during Backlog Refinement or Replenishment if grouping makes sense.
- To Do and beyond: Exactly one Sprint label is REQUIRED. For Feature Sprints, create unique labels (e.g., `Sprint 2: User Profiles`). For Kanban Sprints, use standing labels (e.g., `Q4-Bugs-Chores`).
- Add `Needs Clarification` when requirements are unclear.

### Sprint Types

To categorize all work while staying agile, use two sprint label styles:

1) Feature Sprints
- Examples: `Sprint 1: Content Discovery`, `Sprint 2: User Profiles`
- Use for large, planned initiatives delivering cohesive value
- Always initiated via Sprint Planning and linked to a Sprint Description card

2) Kanban Sprints
- Examples: `Q4-Bugs-Chores`, `October-Maintenance`, `Ongoing-Improvements`
- Use for one-off bugs, chores, tech debt, small improvements
- No formal user journey or Sprint Planning required

---

## 🔗 Dependency Management

### Understanding Dependencies

Every task can have a **Dependencies** checklist that tracks what must be completed before the task can start.

### Dependency Types

1. **Manual Task Dependencies**
   - Format: `SXXX.TYYY {task_name} - https://trello.com/c/cardid` (e.g., `S001.T001 Manual Sprint Setup - https://trello.com/c/cardid`)
   - Must be completed before regular development tasks

2. **Task Dependencies**
   - Format: `SXXX.TYYY {task_name} - https://trello.com/c/cardid` (e.g., `S001.T002 URL Input Form - https://trello.com/c/cardid`)
   - One task depends on another's completion
   - Always use FULL PREFIXED NAMES (e.g., "S001.T001 Database Setup", "S001.T002 Environment Config")

3. **External Dependencies**
   - Format: `Database Configuration`
   - Non-Trello dependencies (APIs, third-party services)

---

## 🛑 Blocker & Expedite Policy

Defines how to handle blocked or urgent tasks without disrupting flow.

### Blocker Management

- When a task in `To Do` or `In Progress` cannot proceed, move it to `On Hold`.
- Comment the reason, what is needed, and tag the responsible owner.
- Agent monitors and notifies the User; during maintenance, ask for updates on `On Hold` items.

### Expedite Process

- User flags an urgent card by prefixing title with `[EXPEDITE]`.
- The card jumps to the top of `To Do`.
- Agent must ask permission to pause current work before starting the expedited item.
- WIP limit may be exceeded temporarily only with explicit User approval.

---

## 🚀 Board Operations

### Create/Refine a Backlog Card

- **Apply naming convention**: Use format `SXXX.TYYY {clean_task_name}` when creating cards (e.g., `S001.T001 Setup Database Schema`).
- Clarify context and scope; add Dependencies checklist.
- Add Acceptance Criteria and QA Steps that are verifiable and concise.
- Include business value, user story, and technical context in the description.
- Split large/ambiguous items into vertical slices that each meet DoR. Optionally create a parent Epic linking to children.
- When unclear, ask in chat AND comment on the card tagging its creator/owner.
- The User and collaborators may add items directly to `Backlog`. The Agent may also propose and add future improvement items, but MUST ask the User for permission first.

### Promote Backlog → To Do

**CRITICAL**: Cards MUST be in the correct shape with all required elements before moving from `Backlog` to `To Do`. Do NOT move cards that are incomplete.

**Pre-move Checklist** — Verify ALL of the following are present:

- ✅ **Title**: Follows naming convention `SXXX.TYYY {clean_task_name}` (e.g., `S001.T001 Setup Database Schema`)
- ✅ **Description**: Includes Context, Scope/Out of Scope, Business Value, User Story, and Technical Context
- ✅ **Dependencies**: Checklist is filled with FULL PREFIXED NAMES (e.g., "S001.T001 Database Setup")
- ✅ **Acceptance Criteria**: Verifiable statements, each as a checkbox
- ✅ **QA Steps**: Explicit steps the User will execute to verify
- ✅ **Labels**: Exactly one Sprint label, one Type label, one Priority label, and optional Stack label
  - Sprint label: Required (e.g., "Sprint 1: Feature Name" or "Q4-Bugs-Chores")
  - Type label: One of ['Manual', 'Feature', 'Bug', 'Chore', 'Tech Debt']
  - Priority label: One of ['Priority High', 'Priority Medium', 'Priority Low']
  - Stack label (optional): One of ['Frontend', 'Backend', 'Fullstack', 'DevOps']

**Rules**:
- If ANY element is missing or incomplete, DO NOT move the card. Instead, refine it first (see Backlog Refinement).
- If information is unclear, ask in chat AND comment on the card tagging its creator/owner.
- Cards in `To Do` must be immediately actionable — they should not require clarification or additional planning.

### Choose the Next Task & Start Work

Pick the **first available task in priority order** from `To Do`, respecting dependencies. Process:

1. **Get all tasks** from `To Do` (already in priority order).
2. **Split into two groups**: Manual tasks (with Manual label) vs. Regular tasks (all others).
3. **Find first available regular task**: Check each regular task in order. If dependencies are complete, select it. If blocked, skip to next.
4. **If all regular tasks are blocked**: Recommend the manual task that would unblock the most regular tasks.
5. **If only manual tasks exist**: Pick the first manual task in priority order.

**Key principle**: Select the first task that CAN be started (highest priority among available tasks), not just any available task.

**Starting work**: Ask permission from the User. If granted, move the card from `To Do` to `In Progress` and leave a brief progress comment.

### Move to QA

- Ensure implementation is complete and tested locally.
- Verify all Acceptance Criteria are met and ticked.
- Move the card to the `QA` column.
- Add a comment tagging the owner; propose any QA steps the Agent can execute (e.g., smoke tests) and, with permission, run them and tick off completed steps with brief evidence links.

### Maintenance

- From time to time, to tidy up the board, check the following:
  - If cards are stuck in QA for more than 24h tag the owner of the card, or the person responsible for QA and ask them to have a look or update the status.
  - For cards in the Done column that have been moved there in the last 24h, double check if any of the cards in the To Do column had any dependencies on them; if so, tick off the dependency.
  - Reorder the Tasks in the To Do column based on priority and sprint labels.
- **Always** suggest a plan and ask for permission before doing any of the actions above. THIS IS VERY IMPORTANT — NEVER DO ANY CLEANUP BEFORE YOU ASK THE USER.
  - For cards in `Done` older than 7 days, propose archiving to keep the board clean.

---

## 🪴 Good Card Guidelines

Keep every card small, testable, and unambiguous. All DoR requirements are detailed in the [Definition of Ready](#definition-of-ready-dor--to-do) section above.

**Key principles**:
- **Size**: If too large for one flow, split into vertical slices and link via a parent Epic.
- **Clarity**: When requirements are unclear, ask clarifying questions in chat AND on the card, tagging the creator/owner.
- **Communication**: Keep brief progress comments when changing status (start, move to QA). Record blockers and proposed next actions.
- **Links**: Include PR/branch/reference designs when available.

---

## 🗓️ Board Ceremonies

Structured interactions that keep the board healthy. The User can initiate at any time. The Agent may propose and run them, but MUST ask for permission first.

### Backlog Refinement

- When to invoke: backlog items missing DoR elements, or before replenishment.
- Start: Agent requests permission to start refinement and lists candidates needing work.
- Process: For each candidate, the Agent asks clarifying questions, updates Description, Dependencies, Acceptance Criteria, QA Steps, and Labels until DoR is met.
  - **PostHog intake**: Fetch newly reported, untriaged bugs from PostHog; propose them as candidates and help the User triage (confirm severity, fill missing context).
  - **Clarify outcome**: Ask targeted questions to eliminate ambiguities; confirm the desired outcome and success criteria are very clear.
  - **Confirm priority**: Double-check the priority with the User before marking DoR-ready.
  - **Sprint label (optional)**: Suggest adding a Sprint label only if the User wants to group this work into a cohesive sprint; otherwise, leave optional for Backlog.
- End: Mark refined items as DoR-ready and tag the creator/owner with a summary comment.

### Replenishment

- When to invoke: `To Do` is running low or at the start of a new cycle.
- Start: Agent requests permission to replenish and proposes DoR-ready candidates to move.
- Process: Move approved items from `Backlog` to `To Do`, then order by priority and sprint.
  - **Verify DoR compliance**: Before moving ANY card, verify it meets ALL Definition of Ready requirements (see "Promote Backlog → To Do" checklist).
  - **Ensure complete labels**: Confirm each card has exactly one Sprint label, one Type label, one Priority label, and optional Stack label. Add missing labels before moving.
  - **Propose an explicit order**: Suggest a prioritized sequence for the batch to enter To Do (priority-driven, dependency-aware).
  - **Suggest sprint grouping**: Propose grouping selected work into a cohesive sprint only when it improves flow and clarity; otherwise, keep as Kanban.
  - **Final check**: Do not move cards that are incomplete — refine them first or skip them.
- End: Post a brief summary comment listing moved cards and next steps.

---

## 📄 Templates

Copy this into the card description when creating/refining a task:

```md
Title: SXXX.TYYY {clean_task_name}
  Example: S001.T001 Setup Database Schema

Description: 
  Context + Scope/Out of Scope.
  Synthesize technical work, business value, and context.

Business Value: 
  Focus on user impact and business outcomes.

User Story: 
  As a [user type], I want [goal], so that [benefit].

Technical Context:
  Stack details, patterns, constraints, and integration requirements.

Dependencies:
- [ ] SXXX.TYYY {dependency_name} - https://trello.com/c/cardid
  Example: S001.T001 Database Setup - https://trello.com/c/abc123

Acceptance Criteria:
- [ ] [verifiable criterion]

QA Steps:
1) [step 1]

Labels: Sprint X; [Type]; [Priority]; [Stack]
  Must include: ['Manual', 'Feature', 'Bug', 'Chore', 'Tech Debt'] + 
                ['Priority High', 'Priority Medium', 'Priority Low'] + 
                ['Frontend', 'Backend', 'Fullstack', 'DevOps'] (optional)
```

---

## 🧾 Quick Reference

- **Card naming**: Use format `SXXX.TYYY {clean_task_name}` (e.g., `S001.T001 Setup Database Schema`).
- **Backlog labels**: Type + Priority (+ optional Stack); Sprint label optional.
- **DoR (To Do)**: Title (with SXXX.TYYY prefix), Description (context/scope/business value/user story/technical context), Dependencies checklist (using full prefixed names), Acceptance Criteria, QA Steps, Labels (1 Sprint, 1 Type, 1 Priority, optional Stack).
- **Task order**: Pick the first available task in priority order. Respect dependencies; suggest the manual task that unblocks most if all are blocked.
- **QA Gate (DoD)**: Check off all Acceptance Criteria, move to QA, comment + tag owner, then pause and assist the user with QA steps. User moves to Done.
- **Backlog → To Do**: Cards MUST be in correct shape with ALL DoR elements (naming, description, dependencies, acceptance criteria, QA steps, labels) before moving. Verify complete label set (1 Sprint, 1 Type, 1 Priority, optional Stack). Do NOT move incomplete cards — refine first.
- **Backlog ownership**: User/collaborators may add items. Agent may propose/add improvements only after user approval.
- **Communication**: Ask clarifying questions in chat and on card (tag creator). Comment on status changes and blockers.
- **Cleanup**: Never tidy or reorganize without proposing a plan and getting approval.

---

## 🌿 Healthy Board Checklist

- To Do contains only DoR-ready cards, each with one Sprint label, one Type, one Priority, and optional Stack.
- In Progress respects WIP limits (2–3) and has brief progress comments.
- QA contains only cards truly at that stage with ticked Acceptance Criteria and any relevant links.
- On Hold contains only blocked cards with a comment explaining why and who is tagged to unblock.
- Done is reviewed daily; dependencies updated; items older than 7 days are proposed for archive.
- Backlog is coherent: large items are split into vertical slices; unclear items are tagged Needs Clarification; future improvements may exist but were added with user permission.

