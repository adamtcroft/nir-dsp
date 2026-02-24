#!/bin/bash

# build-dsp.sh : this runs an LLM instance in hopes to build cool DSP effects 
# over time
#

set -euo pipefail

REPO_DIR="/home/acroft/GitHub/nir-dsp"
TASKS_FILE="${REPO_DIR}/docs/Tasks.md"

if [ ! -s "${TASKS_FILE}" ]; then
	exit 0
fi

cd "${REPO_DIR}"
git pull --rebase

codex exec --dangerously-bypass-approvals-and-sandbox -C "${REPO_DIR}" "Read and follow the instructions outlined in AGENTS.md. Before finishing, delete any completed items from docs/Tasks.md (don't mark them complete; remove them). If a task is open-ended (e.g. 'continue improving'), rewrite it into a few tiny, concrete sub-tasks so it can be pruned over time."

cd "${REPO_DIR}"
git diff --quiet || HAS_CHANGES=1
git diff --cached --quiet || HAS_CHANGES=1
if [ "${HAS_CHANGES:-0}" -eq 0 ]; then
	exit 0
fi

git add -A
git diff --cached --quiet && exit 0
git commit -m "Nightly update"
git push
