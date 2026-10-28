import { describe, expect, it } from 'vitest';
import { reproductionBadge } from './reproduction';

describe('reproductionBadge', () => {
  it('describes an order-dependent failure as passing alone', () => {
    const badge = reproductionBadge({
      reproduction_confirmed: true,
      flakiness: { classification: 'order_dependent', isolated_runs: ['passed', 'passed', 'passed'], file_run: 'failed', summary: '' },
    });
    expect(badge).toEqual({ label: 'order-dependent: passes alone, fails with its file', tone: 'yellow' });
  });

  it('counts isolated failures for deterministic and intermittent failures', () => {
    const runs = (r: string[], classification: 'deterministic' | 'intermittent') =>
      reproductionBadge({ reproduction_confirmed: true, flakiness: { classification, isolated_runs: r, file_run: null, summary: '' } });
    expect(runs(['failed', 'failed', 'failed'], 'deterministic')?.label).toBe('reproduced in isolation (3/3)');
    expect(runs(['failed', 'passed', 'passed'], 'intermittent')?.label).toBe('intermittent: failed 1/3 isolated re-runs');
  });

  it('falls back to the reproduction flag without a triage result', () => {
    expect(reproductionBadge({ reproduction_confirmed: false, flakiness: null })?.label).toBe('not reproducible in isolation');
    expect(reproductionBadge({ reproduction_confirmed: null, flakiness: null })).toBeNull();
  });
});
