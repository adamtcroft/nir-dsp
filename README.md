# nir-dsp

This is a repository of audio plugins/effects serving as an LLM-first 
experiment.

(Most of) the code in this repository has been created by an LLM overnight, as tasked out 
by me (Adam).

As of 1/30/26, the repo is only .jsfx files for use in REAPER

## Sequence of Work
*Tasks* are written in docs/Tasks.md.  The LLM agent runs once a night and is 
instructed to follow the rules in AGENTS.md (which serves as its main work 
prompt and directs it to do work as outlined in Tasks.md).

The LLM is directed to accomplish only one task a night, with encouragement to 
take it slow and do small sub-tasks (it typically doesn't go slow).

If there's no work outlined in docs/Tasks.md, the LLM doesn't run for the night.

As of 1/30/26, the LLM used is GPT Codex 5.2 (Medium Reasoning)

The LLM agent is directed to communicate its nightly summary of work back in 
Communication.md so I can review it after completion

## Usage Rights
Feel free to sync the repo (or download individual effects) and use to your 
heart's content.  There is no price tag on this experiment in this form.

Regarding copyright -

All effects are "closed source"/copywritten with the following understandings:
1. If you download this repo, you have the code, I can't/won't actually do much 
   because there's no money involved in this.
2. LLM copyright is a... ironic/tenuous idea.  I wrote some of this code by 
   hand, I didn't write other bits.

I ask that you respect the copyright as you would any other original work 
(until/unless copyright law changes)

## FAQs
_Are you reviewing the code at all?_

Yes, and I've modified some of it, too.  The purpose here isn't to strictly 
adhere to a "rule", but to play.  I want to see how far I can take the agent, 
and also what I can learn about LLMs, development, and DSP.

One of the most important things about this is that the resulting effects need 
to actually be useful.  If they're garbage, I won't use them - and I want to use 
them all!

_Will you ever make VSTs (other plugin variants)?_

If I get that far, absolutely.  LLMs know enough of EEL2 (REAPER's language for 
JSFX) to be dangerous.  It's one of the least complex ways to get into plugin 
development as you don't have/need a massive library and basic UI is 
pre-written.  I want to walk before I can run.

_Did you know that XYZ effect is terribly coded?  LLMs write awful code_

Honestly, I'm really not expecting much of it.  If it works, that's huge.  If we 
can improve it, maybe I'll task it out to do so.  This is an autonomous process 
that occurs based on thoughts in my head and things I learn.

## Repository layout
- AI/               (stored memory and learnings)
- plugins/          (completed or WIP plugins)
- plugins/archive   (older versions of effects in "plugins")
- docs/             (design notes, specs)
- testing/          (experimental test suite built by LLM)
