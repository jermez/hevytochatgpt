      - name: Export from Hevy API
        env:
          HEVY_API_KEY: ${{ secrets.HEVY_API_KEY }}
        run: |
          python - <<'PY'
          import os, csv, time, requests, datetime as dt, sys
          API='https://api.hevyapp.com/v1'
          HEAD={'accept':'application/json','api-key':os.environ['HEVY_API_KEY']}
          SINCE=(dt.datetime.utcnow()-dt.timedelta(days=30)).isoformat()+'Z'
          PAGE_SIZE=10

          def get(url):
            r=requests.get(url, headers=HEAD, timeout=30)
            if r.status_code>=400:
              print('ERROR', r.status_code, url, file=sys.stderr)
              print(r.text[:500], file=sys.stderr)
              r.raise_for_status()
            return r.json()

          rows=[['workoutId','date','exercise','setIndex','weightKg','reps','rpe','isWarmup']]
          page=1
          while True:
            url=f'{API}/workouts?page={page}&pageSize={PAGE_SIZE}&from={SINCE}'
            data=get(url)
            wos=data.get('workouts',[]) or []
            if not wos:
              break

            for w in wos:
              wd=get(f'{API}/workouts/{w["id"]}')
              date=wd.get('startedAt') or wd.get('date') or w.get('date')
              for ex in (wd.get('exercises') or []):
                name=ex.get('name') or ex.get('exerciseName') or 'Unknown'
                for i,s in enumerate(ex.get('sets') or [],1):
                  rows.append([
                    w['id'],
                    date,
                    name,
                    i,
                    s.get('weightKg') or s.get('weight') or 0,
                    s.get('reps') or s.get('repetitions') or 0,
                    s.get('rpe',''),
                    bool(s.get('isWarmup'))
                  ])
            print(f'Fetched page {page} with {len(wos)} workouts')
            page+=1
            time.sleep(0.2)
            if len(wos) < PAGE_SIZE:
              break

          os.makedirs('out', exist_ok=True)
          with open('out/hevy_sets.csv','w',newline='') as f:
            csv.writer(f).writerows(rows)
          print(f'Wrote out/hevy_sets.csv with {len(rows)-1} rows')
          PY
