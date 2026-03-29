
# Optional: install/start Redis (example commands kept commented)
#rm -rf redis-6.0.8
#wget http://download.redis.io/releases/redis-6.0.8.tar.gz
#tar -xzvf redis-6.0.8.tar.gz
#rm -rf redis-6.0.8.tar.gz
#cd redis-6.0.8
#make -j 10
#cd ..
#nohup ./redis-6.0.8/src/redis-server > log/redis.log 2>&1 &
#echo "Redis starting..."
#sleep 5s

# Reject classifier :8007
cd train
nohup python reject_infer.py > ../log/reject.log 2>&1 &
echo "reject_infer started"
sleep 5s

# Intent BERT :8008
nohup python intent_infer.py > ../log/intent.log 2>&1 &
echo "intent_infer started"
sleep 5s

# Chat NLU :8009
cd ../function_call
nohup python chatnlu_infer.py > ../log/nlu.log 2>&1 &
echo "chatnlu_infer started"
sleep 5s

# Gateway :8080
cd ../
nohup python start.py > ./log/start.log 2>&1 &
echo "start.py started"
sleep 5s

echo "done"
