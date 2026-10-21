# Recording PR evidence

Use a short video when motion, timing, or a sequence of interactions is part
of the change. Prepare the flow before capture so model deliberation never
determines the pacing. This applies to device, browser, and desktop recordings.

## Prepare, then capture

1. Build, install, pair, navigate, dismiss incidental prompts, and warm up the
   automation runner before recording. Inspect the UI and rehearse the complete
   flow, including the expected result. Resolve selectors and command syntax
   during this phase.
2. Restore the intended starting state. For before/after evidence, use matching
   device, dimensions, theme, orientation, data, and actions. Adapt the expected
   result to the revision so the before clip can show the original bug.
3. Execute the entire capture in one tool invocation or autonomous script:
   start recording, wait about 1 second, perform the prepared actions, hold the
   visible result for about 1 second, and stop. Do not return to the model for
   screenshots, decisions, or a separate stop call while recording is active.
4. Use short, explicit pacing delays only where they improve readability
   (usually 200–500 ms). Synchronize actual transitions with bounded waits for
   the expected state. A sleep alone is not proof that the app is ready. Keep
   real app latency visible when it is relevant to the change.
5. Stop in a `finally`/exit trap even if an action or assertion fails. Inspect
   the completed clip and action results afterward. A failed run is diagnostic
   evidence, not successful verification; correct the flow and reset before
   another take.

## T3 Code devices

Call `device_list`, select the host and simulator/emulator, then `device_open`.
Follow its `quickStart`. Store the exact `agentDevice.command` and the complete
`agentDevice.targetArgs` array; preserve every argument, including `--config`
and `--session`, on every CLI invocation. This also keeps remote devices and
concurrent sessions correctly targeted.

Use the returned CLI for interaction and recording. Use platform tools for
builds, logs, and other operations it does not cover. If device access or a
required recording capability is unavailable, report the specific gap. Follow
the repository's mobile verification workflow for client and backend setup.

Before capture, inspect the returned executable's recording, interaction, and
batch help with the returned target arguments. Use its supported syntax; tool
versions differ. The batch and wrapper below are illustrative and require
support for the shown commands and step schema. Prefer observed stable IDs or
semantic selectors. Snapshot references expire across resets and transitions.
Keep recording lifecycle outside the batch so a failed step cannot skip stop.

For example, adapt this `steps.json` to labels and expected states observed in
the actual app. It demonstrates a hypothetical menu-to-details flow:

```json
[
  {
    "command": "click",
    "input": { "target": { "kind": "selector", "selector": "label=\"More actions\" role=button" } }
  },
  {
    "command": "wait",
    "input": { "kind": "selector", "selector": "label=\"Details\"", "timeoutMs": 3000 }
  },
  {
    "command": "wait",
    "input": { "kind": "duration", "durationMs": 250 }
  },
  {
    "command": "click",
    "input": { "target": { "kind": "selector", "selector": "label=\"Details\"" } }
  },
  {
    "command": "wait",
    "input": { "kind": "text", "text": "Item details", "timeoutMs": 3000 }
  }
]
```

Save this Bash wrapper beside the task's temporary evidence, then invoke it once
as `bash record-flow.sh <steps.json> <output.mp4> <agentDevice.command>
<all targetArgs...>`, passing each value as a separately quoted argument. Use
absolute paths. Run the rehearsal and return to the starting screen first.

```bash
#!/usr/bin/env bash
set -euo pipefail

steps_file=$1
output_file=$2
agent_device_command=$3
shift 3
agent_device_target_args=("$@")

ad() {
  "$agent_device_command" "$@" "${agent_device_target_args[@]}"
}

recording_started=0
cleanup() {
  result=$?
  trap - EXIT
  if (( recording_started )); then
    if ! ad record stop; then
      printf '%s\n' 'Recording stop failed; inspect and retry in this session.' >&2
      if (( result == 0 )); then result=1; fi
    fi
  fi
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

ad record start "$output_file"
recording_started=1
sleep 1
ad batch --steps-file "$steps_file" --on-error stop --json
sleep 1
# The EXIT trap stops recording immediately, including on batch failure.
```

Do not close the session if exporting fails; inspect the error and retry
`record stop` in the owning session. A start failure needs inspection before
retrying; do not stop a recording owned by another session. For remote hosts,
use the artifact location actually returned and transfer it before review or
upload; do not assume a host path is available locally.

## Review and publish

Watch the result for correct actions, readable state changes, and unnecessary
idle time. Check duration and the first and last frames as well as the key
transition. On Android, the native recorder may omit unchanged trailing frames,
so a one-second sleep does not guarantee a one-second tail in the encoded video.
Review the exported artifact rather than inferring its duration from the script.

If recording startup/export overhead still leaves excess head or tail, trim
only the idle edges and retain roughly one second around the meaningful flow.
Preserve the original. Do not speed up or cut through a transition or a wait
that demonstrates the bug or fix. Repeat the take if a model pause slipped into
the middle. Keep evidence outside the code branch and upload using the repo's
established PR asset workflow.

For browser/desktop evidence, use the available automation API's supported
sequential runner with the same prepare/start/actions/stop structure and
failure cleanup. If it cannot execute the whole capture without model turns,
report that limitation and review/trim idle edges instead of promising exact
pacing or inventing unsupported batching APIs.
