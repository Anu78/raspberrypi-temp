LC=$(wc -l backend/run.py backend/communications/*.py backend/games/*.py backend/drivers/*.py src/*.tsx src/*.css | tail -1)
echo "$LC lines"