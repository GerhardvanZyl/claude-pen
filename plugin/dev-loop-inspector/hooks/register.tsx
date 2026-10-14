import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { RunReport } from '../types'
import { type Finding, type RoundInput, laneOfFile, parseFindings, parseWontfixIds, reconcile } from './scan'

const PANE = 'dev-loop-inspector'
const RUNS = '.claude/review/runs'
const PERIOD_MS = 5000

const report = atom({ plugin: 'dev-loop-inspector', key: 'report' } as const, null as RunReport | null)

/** The last listing digest scanned, so an unchanged run costs a few directory listings. */
let lastDigest = ''
let isScanning = false
/** A run id the person named with the command, which pins the scan to that run. */
let pinned: string | null = null

const join = (...parts: string[]) => parts.join('/')

const readOrNull = async ($: EngineInterface, path: string): Promise<string | null> => {
  try {
    return await $.fs.read(path)
  } catch {
    return null
  }
}

async function newestRunId($: EngineInterface): Promise<string | null> {
  if (pinned !== null) return pinned
  if (!(await $.fs.exists(RUNS))) return null

  const dirs = (await $.fs.list(RUNS)).filter(entry => entry.kind === 'dir').map(entry => entry.name)
  if (dirs.length === 0) return null

  // Run ids are minted `<yyyymmdd-hhmm>-<slug>`, so the greatest sorts newest.
  // A directory's mtime is 0 in a listing, so only the older unprefixed ids are stat'd.
  const stamped = dirs.filter(name => /^\d{8}-\d{4}-/.test(name)).sort()
  if (stamped.length > 0) return stamped[stamped.length - 1]

  let newest: { name: string; mtimeMs: number } | null = null
  for (const name of dirs) {
    const { mtimeMs } = await $.fs.stat(join(RUNS, name))
    if (newest === null || mtimeMs > newest.mtimeMs) newest = { name, mtimeMs }
  }

  return newest?.name ?? null
}

async function scan($: EngineInterface): Promise<void> {
  const runId = await newestRunId($)
  if (runId === null) {
    lastDigest = ''
    await update($, report, () => null)
    $.ui.status(undefined)

    return
  }

  const runDir = join(RUNS, runId)
  const top = await $.fs.list(runDir)
  const roundDirs = top
    .filter(entry => entry.kind === 'dir' && /^round-\d+$/.test(entry.name))
    .map(entry => entry.name)
    .sort()

  const listings = new Map<string, readonly { name: string; size: number; mtimeMs: number }[]>()
  for (const round of roundDirs) listings.set(round, await $.fs.list(join(runDir, round)))

  const digest = [
    runId,
    ...top.map(entry => `${entry.name}:${entry.size}:${entry.mtimeMs}`),
    ...[...listings].flatMap(([round, entries]) =>
      entries.map(entry => `${round}/${entry.name}:${entry.size}:${entry.mtimeMs}`),
    ),
  ].join('|')
  if (digest === lastDigest) return

  const wontfix = top.some(entry => entry.name === 'wontfix.json')
    ? await readOrNull($, join(runDir, 'wontfix.json'))
    : null

  const rounds: RoundInput[] = []
  for (const round of roundDirs) {
    const dir = join(runDir, round)
    const lanes: { lane: string; findings: Finding[] }[] = []

    for (const entry of listings.get(round) ?? []) {
      const lane = laneOfFile(entry.name)
      if (lane === null) continue
      const text = await readOrNull($, join(dir, entry.name))
      if (text === null) continue
      lanes.push({ lane, findings: parseFindings(text, lane) })
    }

    rounds.push({
      round: Number(round.slice('round-'.length)),
      plan: await readOrNull($, join(dir, 'plan.md')),
      triage: await readOrNull($, join(dir, 'triage.md')),
      lanes,
    })
  }

  const fresh = reconcile(runId, rounds, parseWontfixIds(wontfix ?? ''), await $.clock.now())
  lastDigest = digest
  await update($, report, () => fresh)
  $.ui.status(statusOf(fresh))
}

async function refresh($: EngineInterface): Promise<void> {
  if (isScanning) return
  isScanning = true
  try {
    await scan($)
  } catch (failure) {
    $.ui.log(`dev-loop-inspector: scan failed: ${String(failure)}`)
  } finally {
    isScanning = false
  }
}

function statusOf(run: RunReport): string {
  const last = run.rounds[run.rounds.length - 1]
  const alarms = run.problems.filter(one => one.kind === 'alarm').length
  const drained = last?.lanes.filter(one => one.hasFindings).length ?? 0
  const applicable = last?.lanes.filter(one => one.status === 'applicable').length ?? 0
  const where = last === undefined ? 'no rounds' : `r${last.round} ${drained}/${applicable} lanes`
  const raised = run.rounds.reduce((sum, one) => sum + one.raised, 0)

  return `DL ${where} · ${raised} raised · ${alarms === 0 ? 'reconciled' : `${alarms} UNRECONCILED`}`
}

function textOf(run: RunReport | null): string {
  if (run === null) return 'dev-loop-inspector: no run directory under .claude/review/runs.'

  const lines = [run.runId]
  for (const round of run.rounds) {
    const drained = round.lanes.filter(one => one.hasFindings).length
    const applicable = round.lanes.filter(one => one.status === 'applicable').length
    lines.push(
      `  round ${round.round}: ${drained}/${applicable} applicable lanes drained, ` +
        `${round.raised} raised, ${round.decided} accounted for in triage` +
        `${round.hasTriage ? '' : ' (no triage.md)'}`,
    )
  }
  if (run.problems.length === 0) {
    lines.push('  every finding is accounted for and every applicable lane drained.')
  }
  for (const problem of run.problems) {
    lines.push(`  ${problem.kind === 'alarm' ? '!!' : '--'} ${problem.text}`)
  }

  return lines.join('\n')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'dev-loop-inspect',
      description: 'Reconcile the current dev-loop run: dropped findings, undrained lanes',
    })
    $.clock.every(PERIOD_MS, () => void refresh($))
    void refresh($)

    return next(e)
  })

  on('command.run', { command: 'dev-loop-inspect' }, async ($, e) => {
    const asked = e.args.trim()
    if (asked !== '') {
      pinned = asked
      lastDigest = ''
    }
    await refresh($)
    const opened = await $.ui.open({ id: PANE, title: 'dev-loop run' })
    const run = await read($, report)
    const text = textOf(run)

    return { text: opened.isPlaced ? text : `${text}\n\n(widen the terminal for the live pane)` }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const run = await read($, report)
    if (run === null) return <Text dimColor>No run under .claude/review/runs.</Text>

    const room = Math.max(3, (e.viewport?.rows ?? 24) - 4)
    const alarms = run.problems.filter(one => one.kind === 'alarm')
    const notes = run.problems.filter(one => one.kind === 'note')

    return (
      <Box flexDirection="column">
        <Text bold wrap="truncate-start">
          {run.runId}
        </Text>
        {run.rounds.map(round => {
          const drained = round.lanes.filter(one => one.hasFindings).length
          const applicable = round.lanes.filter(one => one.status === 'applicable').length
          const critical = round.lanes.reduce((sum, one) => sum + one.critical, 0)
          const starved = round.lanes.some(one => one.status === 'applicable' && !one.hasFindings)

          return (
            <Text color={starved ? 'red' : undefined}>
              {`r${round.round}  ${drained}/${applicable} lanes  ${round.raised} raised`}
              {critical > 0 ? `  ${critical} Critical` : ''}
              {round.raised === round.decided ? '  ok' : `  ${round.raised - round.decided} unaccounted`}
            </Text>
          )
        })}
        {run.problems.length === 0 && <Text color="green">All findings triaged; all applicable lanes drained.</Text>}
        {alarms.slice(0, room).map(problem => (
          <Text color="red" wrap="truncate-end">
            {`! ${problem.text}`}
          </Text>
        ))}
        {notes.slice(0, Math.max(0, room - alarms.length)).map(problem => (
          <Text color="yellow" wrap="truncate-end">
            {`? ${problem.text}`}
          </Text>
        ))}
      </Box>
    )
  })
}
