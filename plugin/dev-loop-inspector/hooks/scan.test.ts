import { expect, test } from 'claude-code/testing'

import { laneOfFile, parseFindings, parsePlanLanes, parseTriageIds, parseWontfixIds, reconcile } from './scan'

/** A round-2 plan as the full loop writes it: three-cell applicable rows, two-cell skipped rows. */
const PLAN_ROUND_2 = [
  '# Round 2 plan',
  '',
  '| Lane | Status | Reason |',
  '| --- | --- | --- |',
  '| technical | applicable | behaviour-changing fix; owned tech-001 |',
  '| tests | applicable | owned tests-001; new tests added |',
  '| requirements | skipped — its only finding took no code change |',
  '| security | skipped — fix delta touches no input handling |',
].join('\n')

/** An ultra round names the column Decision instead of Status. */
const PLAN_ULTRA = [
  '| Lane | Decision | Reason |',
  '| --- | --- | --- |',
  '| requirements | applicable | owned req-r2-001..003 |',
  '| minimalism | skipped — fix delta adds no guard |',
].join('\n')

const findingsOf = (...ids: string[]) =>
  JSON.stringify(ids.map(id => ({ id, lane: 'technical', severity: 'Major', evidence: 'direct' })))

test('a plan classifies lanes whether the reason is its own cell or folded into the verdict', () => {
  expect(parsePlanLanes(PLAN_ROUND_2)).toEqual([
    { lane: 'technical', status: 'applicable' },
    { lane: 'tests', status: 'applicable' },
    { lane: 'requirements', status: 'skipped' },
    { lane: 'security', status: 'skipped' },
  ])
  expect(parsePlanLanes(PLAN_ULTRA)).toEqual([
    { lane: 'requirements', status: 'applicable' },
    { lane: 'minimalism', status: 'skipped' },
  ])
})

test('only a lane’s adjudicated findings file counts as the lane', () => {
  expect(laneOfFile('technical.json')).toBe('technical')
  expect(laneOfFile('requirements.prosecution.json')).toBe(null)
  expect(laneOfFile('requirements.defence.json')).toBe(null)
  expect(laneOfFile('triage.md')).toBe(null)
  expect(laneOfFile('wontfix.json')).toBe(null)
  expect(laneOfFile('verify.json')).toBe(null)
})

test('triage ids are read from decision rows and from prose', () => {
  const triage = [
    '| id | sev | decision | reason |',
    '| --- | --- | --- | --- |',
    '| tech-001 | Critical | ACCEPT | reproduced against the built DLL |',
    '| req-r2-001 | Minor | ACCEPT | wording |',
    '',
    'arts-004 was folded into std-002 and needs no row of its own.',
  ].join('\n')

  const { table, mentioned } = parseTriageIds(triage)
  expect([...table].sort()).toEqual(['req-r2-001', 'tech-001'])
  expect(mentioned.has('arts-004')).toBe(true)
  expect(mentioned.has('std-002')).toBe(true)
})

test('a finding in no triage file is an alarm, and the pane says which', () => {
  const run = reconcile(
    '20261014-0900-demo',
    [
      {
        round: 1,
        plan: PLAN_ROUND_2,
        triage: '| id | sev | decision |\n| --- | --- | --- |\n| tech-001 | Major | ACCEPT |',
        lanes: [
          { lane: 'technical', findings: parseFindings(findingsOf('tech-001', 'tech-002'), 'technical') },
          { lane: 'tests', findings: parseFindings(findingsOf('tests-001'), 'tests') },
        ],
      },
    ],
    new Set(),
    0,
  )

  const alarms = run.problems.filter(one => one.kind === 'alarm').map(one => one.text)
  expect(alarms.some(text => text.includes('tech-002'))).toBe(true)
  expect(alarms.some(text => text.includes('tests-001'))).toBe(true)
  expect(alarms.some(text => text.includes('tech-001'))).toBe(false)
  expect(run.rounds[0].raised).toBe(3)
  expect(run.rounds[0].decided).toBe(1)
})

test('an applicable lane that never drained is an alarm', () => {
  // The `dead code` row carries the other half: the alarm has to name the file
  // the loop would really have written, which is the slug and not the prose.
  const plan = `${PLAN_ROUND_2}\n| dead code | applicable | owned dead-001 |`
  const run = reconcile(
    '20261014-0900-demo',
    [{ round: 2, plan, triage: '', lanes: [{ lane: 'technical', findings: [] }] }],
    new Set(),
    0,
  )

  const alarms = run.problems.filter(one => one.kind === 'alarm').map(one => one.text)
  expect(alarms.some(text => text.includes('tests is applicable but never drained'))).toBe(true)
  expect(alarms.some(text => text.includes('technical is applicable'))).toBe(false)
  expect(alarms.some(text => text.includes('dead code is applicable but never drained — no deadcode.json'))).toBe(true)
  // A skipped lane with no file is the normal case and never an alarm.
  expect(alarms.some(text => text.includes('security'))).toBe(false)
})

test('a plan row written with a space matches its one-word findings file', () => {
  const run = reconcile(
    '20261014-0900-demo',
    [
      {
        round: 1,
        // Every full round writes `| Dead code |` in the plan and `deadcode.json` beside it.
        plan: '| Lane | Status | Reason |\n| --- | --- | --- |\n| dead code | applicable | owned dead-001 |',
        triage: '| id | sev | decision |\n| --- | --- | --- |\n| dead-001 | Major | ACCEPT |',
        lanes: [{ lane: 'deadcode', findings: parseFindings(findingsOf('dead-001'), 'deadcode') }],
      },
    ],
    new Set(),
    0,
  )

  expect(run.problems).toEqual([])
  expect(run.rounds[0].lanes).toEqual([
    { lane: 'dead code', status: 'applicable', hasFindings: true, raised: 1, critical: 0, major: 1, minor: 0 },
  ])
})

test('a lite plan row matches its lite-prefixed findings file', () => {
  const run = reconcile(
    '20261014-0900-demo',
    [
      {
        round: 1,
        // `dev-loop-lite` writes `| Correctness |` in the plan; `reviewer-lite-correctness`
        // writes `lite-correctness.json` beside it. Same for Structure, Tests and Security.
        plan: '| Lane | Status | Reason |\n| --- | --- | --- |\n| Correctness | applicable | always |',
        triage: '| id | sev | decision |\n| --- | --- | --- |\n| corr-001 | Major | ACCEPT |',
        lanes: [{ lane: 'lite-correctness', findings: parseFindings(findingsOf('corr-001'), 'lite-correctness') }],
      },
    ],
    new Set(),
    0,
  )

  expect(run.problems).toEqual([])
  expect(run.rounds[0].lanes).toEqual([
    { lane: 'correctness', status: 'applicable', hasFindings: true, raised: 1, critical: 0, major: 1, minor: 0 },
  ])
})

test('a wontfix entry accounts for a finding no triage table decided', () => {
  const wontfix = parseWontfixIds(
    '[{"id":"tech-002","round":1,"class":"stale","reason":"pre-dates the change"}]',
  )
  const run = reconcile(
    '20261014-0900-demo',
    [
      {
        round: 1,
        plan: '| Lane | Status | Reason |\n| --- | --- | --- |\n| technical | applicable | always |',
        triage: '| id | sev | decision |\n| --- | --- | --- |\n| tech-001 | Major | ACCEPT |',
        lanes: [{ lane: 'technical', findings: parseFindings(findingsOf('tech-001', 'tech-002'), 'technical') }],
      },
    ],
    wontfix,
    0,
  )

  expect(run.problems.filter(one => one.kind === 'alarm')).toEqual([])
  expect(run.rounds[0].decided).toBe(2)
})

test('a lane file the plan classifies nowhere is a note, not an alarm', () => {
  const run = reconcile(
    '20261014-0900-demo',
    [
      {
        round: 1,
        plan: '| Lane | Status | Reason |\n| --- | --- | --- |\n| technical | applicable | always |',
        triage: 'std-001 wrapped.',
        lanes: [{ lane: 'standards', findings: parseFindings(findingsOf('std-001'), 'standards') }],
      },
    ],
    new Set(),
    0,
  )

  const notes = run.problems.filter(one => one.kind === 'note').map(one => one.text)
  expect(notes.some(text => text.includes('standards.json exists but plan.md classifies no such lane'))).toBe(true)
  expect(run.problems.filter(one => one.kind === 'alarm').map(one => one.text)).toEqual([
    'round 1: technical is applicable but never drained — no technical.json',
  ])
})

test('a run whose record adds up reports no problems', () => {
  const run = reconcile(
    '20261014-0900-demo',
    [
      {
        round: 1,
        plan: '| Lane | Status | Reason |\n| --- | --- | --- |\n| technical | applicable | always |\n| tests | skipped — no test file changed |',
        triage: '| id | sev | decision |\n| --- | --- | --- |\n| tech-001 | Major | ACCEPT |',
        lanes: [{ lane: 'technical', findings: parseFindings(findingsOf('tech-001'), 'technical') }],
      },
    ],
    new Set(),
    0,
  )

  expect(run.problems).toEqual([])
  expect(run.rounds[0].lanes.find(one => one.lane === 'technical')?.major).toBe(1)
})
