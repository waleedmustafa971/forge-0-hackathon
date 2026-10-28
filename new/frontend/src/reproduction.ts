import type { InvestigationReportData } from './api/types';

/** The "Observed failure" badge: how the target failure behaved when re-run (flaky-test triage). */
export function reproductionBadge(
  report: Pick<InvestigationReportData, 'reproduction_confirmed' | 'flakiness'> | null | undefined,
): { label: string; tone: 'green' | 'yellow' } | null {
  const flaky = report?.flakiness;
  const runs = flaky?.isolated_runs ?? [];
  const failed = runs.filter((r) => r === 'failed').length;
  switch (flaky?.classification) {
    case 'deterministic':
      return { label: `reproduced in isolation (${failed}/${runs.length})`, tone: 'green' };
    case 'order_dependent':
      return { label: 'order-dependent: passes alone, fails with its file', tone: 'yellow' };
    case 'intermittent':
      return { label: `intermittent: failed ${failed}/${runs.length} isolated re-runs`, tone: 'yellow' };
  }
  if (report?.reproduction_confirmed == null) return null;
  return report.reproduction_confirmed
    ? { label: 'reproduced in isolation', tone: 'green' }
    : { label: 'not reproducible in isolation', tone: 'yellow' };
}
