import type { LaneReport, Problem, RoundReport, RunReport } from '../types'

/** A finding id as every loop writes it: `tech-001`, `req-r2-001`, `artifacts-r2-001`. */
const FINDING_ID = /\b[a-z]{2,14}(?:-r\d+)?-\d{2,4}\b/g

/** Files under a round directory that are not a lane's authoritative findings. */
const NOT_A_LANE = /^(plan|triage|verify|wontfix|run|notes|brief)$/

/** A lane's own working files in the adversarial loops; the adjudicated `<lane>.json` is the record. */
const UNADJUDICATED = /\.(prosecution|defence|adjudication)$/

/**
 * A plan table names a lane in prose (`Dead code`); its findings file is a slug
 * (`deadcode.json`), which the lite reviewers additionally prefix (`Correctness`
 * against `lite-correctness.json`). No loop pairs a lane with its lite twin, so
 * dropping the prefix cannot make two lanes of one round share a key.
 */
const laneKey = (lane: string): string =>
  lane.toLowerCase().replace(/[^a-z0-9]/g, '').replace(/^lite/, '')

export type Finding = { id: string; lane: string; severity: string }

export function parsePlanLanes(text: string): { lane: string; status: 'applicable' | 'skipped' }[] {
  const lanes: { lane: string; status: 'applicable' | 'skipped' }[] = []

  for (const line of text.split(/\r?\n/)) {
    if (!line.trimStart().startsWith('|')) continue
    const cells = line.trim().split('|').slice(1, -1).map(cell => cell.trim())
    if (cells.length < 2) continue

    const lane = cells[0].toLowerCase()
    if (!/^[a-z][a-z ]*$/.test(lane) || lane === 'lane') continue

    // A skipped row often folds its reason into the second cell, so match the prefix.
    const verdict = cells[1].toLowerCase()
    if (verdict.startsWith('applicable')) lanes.push({ lane, status: 'applicable' })
    else if (verdict.startsWith('skipped')) lanes.push({ lane, status: 'skipped' })
  }

  return lanes
}

export function parseFindings(text: string, lane: string): Finding[] {
  let raw: unknown
  try {
    raw = JSON.parse(text)
  } catch {
    return []
  }
  if (!Array.isArray(raw)) return []

  return raw
    .filter((one): one is Record<string, unknown> => typeof one === 'object' && one !== null)
    .map(one => ({
      id: String(one.id ?? ''),
      lane: typeof one.lane === 'string' ? one.lane : lane,
      severity: String(one.severity ?? 'Minor'),
    }))
    .filter(one => one.id !== '')
}

/**
 * Ids a triage file accounts for. `table` holds the ids it decided in a row of
 * its own, `mentioned` every id its prose names too: a finding in neither was
 * dropped on the floor, which is the failure this mod exists to catch.
 */
export function parseTriageIds(text: string): { table: Set<string>; mentioned: Set<string> } {
  const table = new Set<string>()
  const mentioned = new Set<string>(text.match(FINDING_ID) ?? [])

  for (const line of text.split(/\r?\n/)) {
    if (!line.trimStart().startsWith('|')) continue
    const first = line.trim().split('|').slice(1, -1)[0]?.trim().toLowerCase() ?? ''
    if (new RegExp(`^${FINDING_ID.source}$`).test(first)) table.add(first)
  }

  return { table, mentioned }
}

export function parseWontfixIds(text: string): Set<string> {
  let raw: unknown
  try {
    raw = JSON.parse(text)
  } catch {
    return new Set()
  }
  if (!Array.isArray(raw)) return new Set()

  return new Set(
    raw
      .filter((one): one is Record<string, unknown> => typeof one === 'object' && one !== null)
      .map(one => String(one.id ?? ''))
      .filter(id => id !== ''),
  )
}

export function laneOfFile(name: string): string | null {
  if (!name.endsWith('.json')) return null
  const stem = name.slice(0, -'.json'.length)
  if (NOT_A_LANE.test(stem) || UNADJUDICATED.test(stem)) return null

  return stem
}

export type RoundInput = {
  round: number
  plan: string | null
  triage: string | null
  lanes: { lane: string; findings: Finding[] }[]
}

/**
 * Builds the report the pane draws. Every problem is an arithmetic fact about
 * the run's own files: nothing here judges the code, only whether the loop's
 * record of itself adds up.
 */
export function reconcile(runId: string, rounds: RoundInput[], wontfix: Set<string>, nowMs: number): RunReport {
  const problems: Problem[] = []
  const everyFindingId = new Set(rounds.flatMap(r => r.lanes.flatMap(l => l.findings.map(f => f.id))))
  const reported: RoundReport[] = []

  for (const round of rounds) {
    const planned = round.plan === null ? [] : parsePlanLanes(round.plan)
    const triaged = parseTriageIds(round.triage ?? '')
    const lanes: LaneReport[] = []
    let raised = 0
    let decided = 0

    if (round.plan === null && round.lanes.length > 0) {
      problems.push({ kind: 'alarm', text: `round ${round.round}: lane findings exist with no plan.md` })
    }

    for (const entry of planned) {
      const found = round.lanes.find(one => laneKey(one.lane) === laneKey(entry.lane))
      const findings = found?.findings ?? []
      raised += findings.length

      if (entry.status === 'applicable' && found === undefined) {
        const file = `${laneKey(entry.lane)}.json`
        problems.push({
          kind: 'alarm',
          text: `round ${round.round}: ${entry.lane} is applicable but never drained — no ${file}`,
        })
      }

      lanes.push({
        lane: entry.lane,
        status: entry.status,
        hasFindings: found !== undefined,
        raised: findings.length,
        critical: findings.filter(one => one.severity === 'Critical').length,
        major: findings.filter(one => one.severity === 'Major').length,
        minor: findings.filter(one => one.severity === 'Minor').length,
      })
    }

    for (const entry of round.lanes) {
      if (planned.some(one => laneKey(one.lane) === laneKey(entry.lane))) continue
      raised += entry.findings.length
      problems.push({
        kind: 'note',
        text: `round ${round.round}: ${entry.lane}.json exists but plan.md classifies no such lane`,
      })
      lanes.push({
        lane: entry.lane,
        status: 'unclassified',
        hasFindings: true,
        raised: entry.findings.length,
        critical: entry.findings.filter(one => one.severity === 'Critical').length,
        major: entry.findings.filter(one => one.severity === 'Major').length,
        minor: entry.findings.filter(one => one.severity === 'Minor').length,
      })
    }

    for (const entry of round.lanes) {
      for (const finding of entry.findings) {
        if (triaged.mentioned.has(finding.id) || wontfix.has(finding.id)) {
          decided += 1
          continue
        }
        problems.push({
          kind: 'alarm',
          text: `round ${round.round}: ${finding.id} (${finding.severity}, ${entry.lane}) is in no triage file`,
        })
      }
    }

    if (round.triage === null && round.lanes.length > 0) {
      problems.push({ kind: 'alarm', text: `round ${round.round}: lanes drained but no triage.md` })
    }

    for (const id of triaged.table) {
      if (everyFindingId.has(id) || wontfix.has(id)) continue
      problems.push({ kind: 'note', text: `round ${round.round}: triage decides ${id}, which no lane raised` })
    }

    reported.push({
      round: round.round,
      hasPlan: round.plan !== null,
      hasTriage: round.triage !== null,
      lanes,
      raised,
      decided,
    })
  }

  return { runId, rounds: reported, problems, checkedAtMs: nowMs }
}
