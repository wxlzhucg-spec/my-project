#!/bin/bash
cd /opt/xinyu
git pull origin main 2>&1
source /opt/xinyu/venv/bin/activate
pip install -r shadow_server/requirements.txt -q 2>&1 | tail -3
mysql -u root -p010824Wy? xintujie < shadow_server/sql/create_assessment_results.sql 2>/dev/null || true
pkill -f uvicorn 2>/dev/null || true
sleep 2
cd /opt/xinyu/shadow_server
nohup /opt/xinyu/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /var/log/shadow.log 2>&1 &
sleep 4
echo "=== TEST ASSESSMENTS ==="
curl -s http://127.0.0.1:8000/api/assessments/submit -X POST -H "Content-Type: application/json" -d '{"user_id":1,"test_type":"holland","summary":"test","result_json":{}}'
echo ""
echo "=== TEST FORTUNE ==="
curl -s "http://127.0.0.1:8000/api/fortune?user_id=1" | head -c 200
echo ""
echo "=== DONE ==="
