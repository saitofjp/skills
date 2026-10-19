#!/bin/bash
# Ask for a summary of a past session under one condition, and keep what comes back.
#
#   run_condition.sh NAME UPTO COND SAMPLE
#
# Reads  $WORK/sessions/NAME/records.jsonl (session_transcript.py collect).
# Writes $WORK/runs/NAME_COND_sSAMPLE/: out.json, answer.md (the reply),
#        session_id, files/ (whatever the model wrote while answering).
#
# Conditions
#   C1  the session is resumed, then: ここまでの調査をまとめて
#   C2  the session is resumed, then: …主目的に沿って構成を組み直してまとめて
#   C3  the session is resumed, then: …このセッションを見ていない人が読む資料としてまとめて
#   C4  a fresh session gets the transcript as a document: この調査をまとめて
#   C5  as C4, but the turns are in a fixed random order
#   C6  resumed, then the purpose axis plus a fixed layout (目的と結論を冒頭、退けた案は末尾、経緯は書かない)
#   C7  as C6, and also names the purpose, read from $WORK/purpose_NAME.txt
#   C8  as C7, but asked as a document for a named person who has not seen the session
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${WORK:-$PWD/work}
MODEL=${MODEL:-claude-opus-5-5}
N=$1; U=$2; C=$3; S=$4
REC=$WORK/sessions/$N/records.jsonl
R=$WORK/runs/${N}_${C}_s$S
rm -rf "$R"; mkdir -p "$R/cwd" "$R/files"; cd "$R/cwd"
TOOLS="Read,Write,Edit"
OPTS=(--model "$MODEL" --tools "$TOOLS" --allowedTools "$TOOLS" --strict-mcp-config --output-format json)
case $C in
  C1) ASK="ここまでの調査をまとめて" ;;
  C2) ASK="ここまでの調査を、主目的に沿って構成を組み直してまとめて" ;;
  C3) ASK="ここまでの調査を、このセッションを見ていない人が読む資料としてまとめて" ;;
  C6) ASK="ここまでの調査を、主目的に沿って構成を組み直してまとめて。冒頭に目的と結論を置き、退けた案は理由を1行ずつ付けて末尾にまとめて。経緯（いつ何が分かったか）は書かないで。" ;;
  C7) ASK="ここまでの調査を、主目的に沿って構成を組み直してまとめて。主目的は、$(cat "$WORK/purpose_$N.txt")。冒頭に目的と結論を置き、退けた案は理由を1行ずつ付けて末尾にまとめて。経緯（いつ何が分かったか）は書かないで。" ;;
  C8) P=$(cat "$WORK/purpose_$N.txt"); ASK="このセッションを見ていない田中さんが、${P%こと}ための資料にして。冒頭に目的と結論。退けた案は理由を1行ずつ付けて末尾に。経緯（いつ何が分かったか）は書かない。" ;;
  C4) INTRO="以下は、ユーザーとAIの調査セッションの記録です。この調査をまとめて。"; FLAG="" ;;
  C5) INTRO="以下は、ユーザーとAIの調査セッションの記録から、やり取りを順不同で抜き出したものです。この調査をまとめて。"; FLAG="--shuffle" ;;
esac
touch "$R/.start"
if [ "$C" = C4 ] || [ "$C" = C5 ]; then
  python3 "$HERE/transcript_text.py" "$REC" "$U" $FLAG > "$R/input.txt"
  { printf '%s\n\n<記録>\n' "$INTRO"; cat "$R/input.txt"; printf '</記録>\n'; } \
    | claude -p "${OPTS[@]}" > "$R/out.json" 2> "$R/err.txt"
else
  SID=$(python3 "$HERE/build_replay.py" "$REC" . --upto "$U")
  claude --resume "$SID" --fork-session -p "$ASK" "${OPTS[@]}" < /dev/null > "$R/out.json" 2> "$R/err.txt"
fi
python3 - "$R" <<'PY'
import glob, json, os, re, shutil, sys
R = sys.argv[1]
o = json.load(open(f"{R}/out.json"))
open(f"{R}/answer.md", "w").write(o.get("result", ""))
open(f"{R}/session_id", "w").write(o.get("session_id", ""))
start = os.path.getmtime(f"{R}/.start")
cwd = f"{R}/cwd"
for root in (cwd, f"/tmp/claude-0/{re.sub(r'[^A-Za-z0-9]', '-', cwd)}"):
    for d, _, names in os.walk(root):
        for n in names:
            p = os.path.join(d, n)
            if os.path.getmtime(p) > start and not n.endswith(".jsonl"):
                shutil.copy(p, f"{R}/files/{n}")
PY
echo "done $N $C $S"
