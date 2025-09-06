import csv, os, time, requests, sys
API='https://api.hevyapp.com/v1'
HEAD={'accept':'application/json','api-key':os.environ['HEVY_API_KEY']}

def get(url):
    r = requests.get(url, headers=HEAD, timeout=30)
    r.raise_for_status(); return r.json()

rows=[['workoutId','date','exercise','setIndex','weightKg','reps','rpe','isWarmup']]
page=1
while True:
    data=get(f'{API}/workouts?page={page}&pageSize=50')
    wos=data.get('workouts',[])
    if not wos: break
    for w in wos:
        wd=get(f'{API}/workouts/{w["id"]}')
        date=wd.get('startedAt') or wd.get('date')
        for ex in wd.get('exercises',[]):
            name=ex.get('name') or ex.get('exerciseName')
            for i,s in enumerate(ex.get('sets',[]),1):
                rows.append([w['id'], date, name, i, s.get('weightKg') or s.get('weight') or 0,
                             s.get('reps') or s.get('repetitions') or 0, s.get('rpe',''), bool(s.get('isWarmup'))])
    page+=1; time.sleep(0.2)

os.makedirs('out', exist_ok=True)
with open('out/hevy_sets.csv','w',newline='') as f:
    csv.writer(f).writerows(rows)
print('Wrote out/hevy_sets.csv')
