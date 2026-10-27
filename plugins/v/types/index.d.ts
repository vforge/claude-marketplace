export type DiffRow = { kind: 'head' | 'hunk' | 'add' | 'del' | 'ctx'; text: string }
export type DiffView = { title: string; rows: DiffRow[]; note: string }

declare module 'claude-code' {
  interface PluginState {
    v: { diffView: Shaped<DiffView> }
  }
}
