LC=$(wc -l backend/run.py backend/test.py backend/communications/*.py backend/games/*.py backend/drivers/*.py src/*.tsx src/components/*.tsx  | tail -1)
echo "$LC lines of code"
