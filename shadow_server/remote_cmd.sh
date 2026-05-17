# 复制以下整段命令，粘贴到终端执行即可
# 它会自动 SSH 登录、部署、重启、验证

expect -c '
set timeout 60
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@43.143.169.226
expect "password:"
send "010824Wy?\r"
expect "#"

send "cd /opt/xinyu && git pull origin main\r"
expect "#"

send "source venv/bin/activate && pip install -r shadow_server/requirements.txt -q\r"
expect "#"

send "mysql -u root -p'010824Wy?' xintujie < shadow_server/sql/create_assessment_results.sql 2>/dev/null || true\r"
expect "#"

send "pkill -f uvicorn || true\r"
expect "#"

send "sleep 2\r"
expect "#"

send "cd /opt/xinyu/shadow_server && nohup venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /var/log/shadow.log 2>&1 &\r"
expect "#"

send "sleep 3 && curl -s http://127.0.0.1:8000/api/assessments/submit -X POST -H Content-Type:application/json -d '{\"user_id\":1,\"test_type\":\"holland\",\"summary\":\"test\",\"result_json\":{}}' && echo && curl -s 'http://127.0.0.1:8000/api/fortune?user_id=1' | head -c 100\r"
expect "#"

send "exit\r"
expect eof
'
