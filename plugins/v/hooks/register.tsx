import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { DiffRow, DiffView } from '../types'

const PANE = 'v-diff'
const view = atom(
  { plugin: 'v', key: 'diffView' } as const,
  { title: 'Diff', rows: [], note: 'Run /v:compare OLD NEW' } as DiffView,
  { shape: 'view-1' },
)

const STAMP = /^(.*)_(\d{8}-\d{6})(\.[^./]+)?$/

const tokens = (args: string): string[] => {
  const out: string[] = []
  const re = /"([^"]*)"|'([^']*)'|(\S+)/g
  let m: RegExpExecArray | null
  while ((m = re.exec(args))) out.push(m[1] ?? m[2] ?? m[3])
  return out
}

const split = (path: string) => {
  const i = path.lastIndexOf('/')
  return { dir: i < 0 ? '.' : path.slice(0, i) || '/', name: path.slice(i + 1) }
}

const classify = (line: string): DiffRow => {
  if (line.startsWith('@@')) return { kind: 'hunk', text: line }
  if (line.startsWith('+++') || line.startsWith('---')) return { kind: 'head', text: line }
  if (line.startsWith('diff ') || line.startsWith('index ')) return { kind: 'head', text: line }
  if (line.startsWith('+')) return { kind: 'add', text: line }
  if (line.startsWith('-')) return { kind: 'del', text: line }
  return { kind: 'ctx', text: line }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'compare',
      description: 'Diff two files in a scrollable pane: /v:compare [-f] OLD [NEW]',
    })
    return next(e)
  })

  on('command.run', { command: 'compare' }, async ($, e) => {
    let full = false
    const files: string[] = []
    for (const t of tokens(e.args)) {
      if (t === '-f') full = true
      else files.push(t)
    }

    // One file: pair it with its neighbour among the timestamped siblings.
    if (files.length === 1) {
      const { dir, name } = split(files[0])
      const m = STAMP.exec(name)
      const stem = m ? m[1] : name.replace(/\.[^./]+$/, '')
      const ext = m ? (m[3] ?? '') : (/\.[^./]+$/.exec(name)?.[0] ?? '')
      const entries = await $.fs.list(dir)
      const stamped = entries
        .map(x => x.name)
        .filter(n => {
          const s = STAMP.exec(n)
          return s !== null && s[1] === stem && (s[3] ?? '') === ext
        })
        .sort()
      const base = `${stem}${ext}`
      const chain = [base, ...stamped]
      const at = chain.indexOf(name)
      const pair = m
        ? [chain[Math.max(at - 1, 0)], name]
        : [name, chain[chain.length - 1]]
      if (pair[0] === pair[1]) return { text: `No other version of ${name} found.` }
      files.splice(0, 1, `${dir}/${pair[0]}`, `${dir}/${pair[1]}`)
    }
    if (files.length !== 2) return { text: 'Usage: /v:compare [-f] OLD NEW  (or one file: its timestamped neighbour)' }

    const [a, b] = files
    const run = await $.process.run([
      'git', 'diff', '--no-index', '--no-color', `-U${full ? 99999 : 4}`, '--', a, b,
    ])
    if (run.exitCode > 1) return { text: `git diff failed: ${run.stderr.trim()}` }

    const lines = run.stdout.split('\n')
    if (lines[lines.length - 1] === '') lines.pop()
    const rows = lines.map(classify)
    const adds = rows.filter(r => r.kind === 'add').length
    const dels = rows.filter(r => r.kind === 'del').length
    const label = (p: string) => p.slice(p.lastIndexOf('/') + 1)
    const next: DiffView = {
      title: `${label(a)} → ${label(b)}`,
      rows,
      note: rows.length === 0 ? 'Files are identical.' : `+${adds} −${dels}   ↑↓ PgUp PgDn wheel scroll`,
    }
    await update($, view, () => next)
    await $.ui.open({ id: PANE, title: 'Diff' })
    return { text: `Diff pane opened: ${next.title}` }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const v = await read($, view)
    return (
      <Box flexDirection="column">
        <Text bold>{v.title}</Text>
        <Text dimColor>{v.note}</Text>
        {v.rows.map(r => (
          <Text
            color={r.kind === 'add' ? 'green' : r.kind === 'del' ? 'red' : r.kind === 'hunk' ? 'cyan' : undefined}
            bold={r.kind === 'head'}
            dimColor={r.kind === 'ctx'}
          >
            {r.text === '' ? ' ' : r.text}
          </Text>
        ))}
      </Box>
    )
  })
}
