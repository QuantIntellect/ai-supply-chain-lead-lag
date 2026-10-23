#!/bin/zsh
# Rebuild every analysis, the report and docs/generated from the downloaded data (no network calls). Order matters.
set -e
cd "$(dirname "$0")"
PY=(.venv/bin/python -I)
LOG=reports/run_all.log
: > $LOG
for s in merge_relations panel events spill analyze_spill pair_map cascade backtest_events network_model customer_momentum \
         orders_panel playbook keynote_effect fundamentals_leadlag capex_signal transcripts_nlp digests customer_concentration \
         press_release_kpis report_data build_report build_docs; do
  echo "=== $s" | tee -a $LOG
  "${PY[@]}" src/$s.py >> $LOG 2>&1
done
echo "done; see $LOG"
