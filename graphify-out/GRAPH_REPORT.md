# Graph Report - C:\src\tec001ada\2. playpen\claude-pen  (2026-07-29)

## Corpus Check
- 46 files · ~38,179 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 229 nodes · 475 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Sprint Orchestration & Triage
- Review Lane Agents
- Loop Phases & Review Mechanics
- Adversarial Ultra Review
- Architecture Skill & Triage Gates
- Coding Standards & Architecture Docs
- Implementation Tiers & Routing
- Delegation Policy & Global Rules
- Loop Cost Model
- Installer Behaviour
- Bash Installer
- Subagent Model Override

## God Nodes (most connected - your core abstractions)
1. `dev-loop skill` - 24 edges
2. `solution-architecture skill` - 18 edges
3. `dev-loop-lite skill` - 16 edges
4. `reviewer-ultralight` - 15 edges
5. `One owner per concern (lane ownership boundary)` - 14 edges
6. `reviewer-lite-structure consolidated lane` - 14 edges
7. `reviewer-ultra-defence` - 14 edges
8. `reviewer-ultra-prosecution` - 14 edges
9. `dev-loop-ultra skill` - 14 edges
10. `reviewer-architecture lane` - 13 edges

## Surprising Connections (you probably didn't know these)
- `MUST / SHOULD severity marking` --shares_data_with--> `Findings JSON format`  [INFERRED]
  project/.claude/skills/coding-standards/SKILL.md → README.md
- `An eligibility argument is a disqualification` --semantically_similar_to--> `One-way mandatory loop escalation`  [INFERRED] [semantically similar]
  project/.claude/skills/implement-sprint/references/item-triage.md → README.md
- `Leave the repository as you found it` --semantically_similar_to--> `Phase 9 commit and PR file-list verification`  [INFERRED] [semantically similar]
  project/.claude/agents/sprint-item-runner.md → README.md
- `Minimal output to protect the caller's context window` --semantically_similar_to--> `One owner per concern (lane ownership boundary)`  [INFERRED] [semantically similar]
  user/.claude/agents/Explore.md → user/.claude/agents/reviewer-architecture.md
- `Precision-optimised review posture` --semantically_similar_to--> `An empty findings array is a correct result`  [INFERRED] [semantically similar]
  user/.claude/agents/reviewer-ultra-defence.md → user/.claude/agents/reviewer-architecture.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **The five-loop review ladder, selected by risk surface** — readme_dev_loop_ultralight, readme_dev_loop_lite, readme_dev_loop, readme_dev_loop_ultra, readme_dev_loop_ultra_opus, readme_escalation [EXTRACTED 1.00]
- **Adversarial review triple: prosecution, defence, adjudicator** — readme_reviewer_ultra_prosecution, readme_reviewer_ultra_defence, readme_reviewer_ultra_adjudicator, readme_dev_loop_ultra [EXTRACTED 1.00]
- **Sprint orchestration flow: plan, skip, triage, run, checkpoint** — project__claude_skills_implement_sprint_skill, project__claude_skills_implement_sprint_references_item_triage, project__claude_sprint_skip, project__claude_agents_sprint_item_runner, project__claude_skills_implement_sprint_skill_manifest, project__claude_skills_implement_sprint_skill_non_configurable_checkpoints [EXTRACTED 1.00]
- **The dev-loop nine-lane review set, one owner per concern** — user__claude_agents_reviewer_requirements_reviewer_requirements, user__claude_agents_reviewer_technical_reviewer_technical, user__claude_agents_reviewer_security_reviewer_security, user__claude_agents_reviewer_architecture_reviewer_architecture, user__claude_agents_reviewer_standards_reviewer_standards, user__claude_agents_reviewer_tests_reviewer_tests, user__claude_agents_reviewer_artifacts_reviewer_artifacts, user__claude_agents_reviewer_deadcode_reviewer_deadcode, user__claude_agents_reviewer_minimalism_reviewer_minimalism, user__claude_skills_dev_loop_references_review_lanes_review_lanes [EXTRACTED 1.00]
- **Adversarial review trio: prosecution, defence, adjudicator** — user__claude_agents_reviewer_ultra_prosecution_reviewer_ultra_prosecution, user__claude_agents_reviewer_ultra_defence_reviewer_ultra_defence, user__claude_agents_reviewer_ultra_adjudicator_reviewer_ultra_adjudicator, user__claude_agents_reviewer_ultra_adjudicator_adversarial_reconciliation [EXTRACTED 1.00]
- **Implementation tier ladder: lite, default, heavy** — user__claude_agents_sidekick_lite_sidekick_lite, user__claude_agents_sidekick_sidekick, user__claude_agents_sidekick_heavy_sidekick_heavy, user__claude_agents_sidekick_brief_as_spec [EXTRACTED 1.00]
- **One-way escalation ladder across the five dev loops** — user__claude_skills_dev_loop_ultralight_skill_dev_loop_ultralight, user__claude_skills_dev_loop_lite_skill_dev_loop_lite, user__claude_skills_dev_loop_skill_dev_loop, user__claude_skills_dev_loop_ultra_skill_dev_loop_ultra, user__claude_skills_dev_loop_ultra_opus_skill_dev_loop_ultra_opus, user_claude_escalation_ladder [EXTRACTED 1.00]
- **Adversarial triple: prosecution, defence, adjudicator per lane** — user__claude_agents_reviewer_ultra_prosecution_reviewer_ultra_prosecution, user__claude_agents_reviewer_ultra_defence_reviewer_ultra_defence, user__claude_agents_reviewer_ultra_adjudicator_reviewer_ultra_adjudicator, user__claude_skills_dev_loop_ultra_skill_adversarial_triple, user__claude_skills_dev_loop_ultra_skill_opposed_error_profiles [EXTRACTED 1.00]
- **Working-tree integrity mechanism spanning snapshot, check, scratch worktree and the review phases** — user__claude_skills_dev_loop_references_tree_snapshot_working_tree_snapshot, user__claude_skills_dev_loop_references_tree_snapshot_integrity_check, user__claude_skills_dev_loop_references_tree_snapshot_scratch_worktree, user__claude_skills_dev_loop_references_tree_snapshot_mutation_testing, user__claude_skills_dev_loop_skill_phase_3_plan_the_review_round, user__claude_skills_dev_loop_skill_phase_4_delegate, user__claude_skills_dev_loop_skill_phase_9_commit_push_pull_request [EXTRACTED 1.00]

## Communities (14 total, 1 thin omitted)

### Community 0 - "Sprint Orchestration & Triage"
Cohesion: 0.08
Nodes (40): sprint-item-runner agent, When to stop and report a blocker, Leave the repository as you found it, One-line return contract, Generic project-layer instructions, Triage bias is heavy; escalate never de-escalate, Item triage reference, Automatic skips by type, state, content, dependency (+32 more)

### Community 1 - "Review Lane Agents"
Cohesion: 0.16
Nodes (37): .claude/review/conventions.md accepted-deviation ledger, An empty findings array is a correct result, Evidence and cause honesty, One owner per concern (lane ownership boundary), reviewer-architecture lane, reviewer-artifacts lane, Run the generate-and-diff check rather than reason about currency, Establish reachability by search; deduplicate by family (+29 more)

### Community 2 - "Loop Phases & Review Mechanics"
Cohesion: 0.09
Nodes (35): Bounded loops with evidence gates, Cause gate (introduced/worsened fixed, stale not), Findings JSON format, missing-required cause, Lite Lane: Security (kept whole), Lite Lane: Tests, dev-loop-lite skill, Lite Escalation to the Full Loop on a Round-1 Critical (+27 more)

### Community 3 - "Adversarial Ultra Review"
Cohesion: 0.14
Nodes (27): Read-only reviewer enforcement via disallowedTools, reviewer-lite-tests consolidated lane, Mutation testing in a scratch worktree, Primary working tree immutability and the lead's digest check, Adversarial pair reconciliation, The dropped list as pair calibration, reviewer-ultra-adjudicator, The defence log matters more than its findings (+19 more)

### Community 4 - "Architecture Skill & Triage Gates"
Cohesion: 0.12
Nodes (26): Establish the architecture in force before judging, Lite Lane: Structure (architecture + standards + minimalism + dead code), Lane: Architecture, Lane: Artifacts, Lane: Dead code, Lane: Minimalism, Lane: Security, Lane: Standards (+18 more)

### Community 5 - "Coding Standards & Architecture Docs"
Cohesion: 0.15
Nodes (14): Three things to configure without -Gpos, Coding standards scaffold, Explicitly not standards, MUST / SHOULD severity marking, Configuration table (org, project, team, base branch), ARCHITECTURE template, Derive the document from the graph, not a preferred design, Record conventions enforced by something, not merely tidy (+6 more)

### Community 6 - "Implementation Tiers & Routing"
Cohesion: 0.23
Nodes (14): Explore agent, Minimal output to protect the caller's context window, coding-standards skill, Project agent memory for repo conventions, A precise blocker report is a success, not a failure, Treat the brief as a spec, Push back on the brief, but do not expand scope, sidekick-heavy implementation worker (+6 more)

### Community 7 - "Delegation Policy & Global Rules"
Cohesion: 0.22
Nodes (9): Phase 0 — Frame the Slice, Phase 1 — Implement, Phase 2 — Tests, Delegation Policy (lead / orchestrator), Git & Branch Rules — merge back into parent branch, Global Instructions (user CLAUDE.md), Know When NOT To Delegate, Pull Request Review Rule — post findings on the PR (+1 more)

### Community 8 - "Loop Cost Model"
Cohesion: 0.50
Nodes (6): cost(), fixes(), lane(), loop_cost(), review_round(), total()

### Community 9 - "Installer Behaviour"
Cohesion: 0.29
Nodes (8): Timestamped backup of existing agents and skills, CLAUDE.md merge guard (writes CLAUDE.new.md), One-command installer (install.ps1 / install.sh), gpos-after-project overlay ordering, Restart required for the agent directory watcher, review/runs excluded from version control, gpos/ as an overlay on project/, SubagentStart/Stop hook logging

### Community 10 - "Bash Installer"
Cohesion: 0.83
Nodes (3): add_ignore_rule(), install.sh script, backup_tree()

## Ambiguous Edges - Review These
- `gpos-after-project overlay ordering` → `Timestamped backup of existing agents and skills`  [AMBIGUOUS]
  INSTALL.md · relation: conceptually_related_to

## Knowledge Gaps
- **10 isolated node(s):** `Cost projections model`, `solution-architecture four-tier evidence model`, `SubagentStart/Stop hook logging`, `Sidekick implementation tiers`, `gpos/ as an overlay on project/` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `gpos-after-project overlay ordering` and `Timestamped backup of existing agents and skills`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Findings JSON format` connect `Loop Phases & Review Mechanics` to `Architecture Skill & Triage Gates`, `Coding Standards & Architecture Docs`?**
  _High betweenness centrality (0.380) - this node is a cross-community bridge._
- **Why does `Coding standards scaffold` connect `Coding Standards & Architecture Docs` to `Sprint Orchestration & Triage`?**
  _High betweenness centrality (0.331) - this node is a cross-community bridge._
- **Why does `MUST / SHOULD severity marking` connect `Coding Standards & Architecture Docs` to `Loop Phases & Review Mechanics`?**
  _High betweenness centrality (0.326) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `reviewer-ultralight` (e.g. with `reviewer-lite-correctness consolidated lane` and `reviewer-lite-structure consolidated lane`) actually correct?**
  _`reviewer-ultralight` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `One owner per concern (lane ownership boundary)` (e.g. with `Minimal output to protect the caller's context window` and `The dropped list as pair calibration`) actually correct?**
  _`One owner per concern (lane ownership boundary)` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Cost projections model`, `solution-architecture four-tier evidence model`, `SubagentStart/Stop hook logging` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._