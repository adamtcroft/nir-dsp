#!/bin/bash

# build-dsp.sh : this runs an LLM instance in hopes to build cool DSP effects 
# over time
#

TASKS_FILE="/home/acroft/GitHub/nir-dsp/docs/Tasks.md"

if [ ! -s "${TASKS_FILE}" ]; then
	exit 0
fi

codex exec --dangerously-bypass-approvals-and-sandbox -C "/home/acroft/GitHub/nir-dsp" "Read and follow the instructions outlined in AGENTS.md"
cd /home/acroft/GitHub/nir-dsp
git add -A
git commit -m "Nightly update"
git push
