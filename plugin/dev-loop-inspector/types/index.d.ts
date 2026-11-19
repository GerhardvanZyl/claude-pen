export type LaneReport = {
  lane: string
  status: 'applicable' | 'skipped' | 'unclassified'
  hasFindings: boolean
  raised: number
  critical: number
  major: number
  minor: number
}

export type RoundReport = {
  round: number
  hasPlan: boolean
  hasTriage: boolean
  lanes: LaneReport[]
  raised: number
  decided: number
}

export type Problem = {
  kind: 'alarm' | 'note'
  text: string
}

export type RunReport = {
  runId: string
  rounds: RoundReport[]
  problems: Problem[]
  checkedAtMs: number
}

declare module 'claude-code' {
  interface PluginState {
    'dev-loop-inspector': { report: RunReport | null }
  }
}
