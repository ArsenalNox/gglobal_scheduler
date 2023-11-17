import uvicorn
import time
import re
import logging
import sys 
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from fastapi import FastAPI

app = FastAPI()


def check_list_len(user_id):
    logging.info(f'Sending reminder to user {user_id}')
    request = requests.get(f'http://127.0.0.1:8080/api/trigger_reminder/{user_id}')


@app.get("/remove_timer/{user_id}")
async def remove_trigger(user_id:int):
    try:
        scheduler.remove_job(str(user_id))
        return 200
    except Exception as err:
        print(err)
        return 500


@app.get("/add_timer/{user_id}/{time}")
async def list_pop(user_id: int, time:str):

    hours = int(re.findall(r'[\d]+', time)[0]) if len(re.findall(r'H:[\d]+', time)) > 0 else 0
    minutes = int(re.findall(r'[\d]+', time)[0]) if len(re.findall(r'M:[\d]+', time)) > 0 else 0

    print(f"setting job: {user_id} Hours: {hours}, minutes: {minutes}")
    try: 
        scheduler.remove_job(str(user_id))
    except:
        pass
    finally:
        scheduler.add_job(func=check_list_len, trigger='interval', args=[user_id], hours=hours, minutes=minutes, id=str(user_id))

    return 200


@app.get('/jobs')
async def get_jobs():
    print(scheduler.get_jobs())
    return 200

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    jobstores = {
        "default": SQLAlchemyJobStore('postgresql://postgres:admin@127.0.0.1:5432/my_app')
    }
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.start()
    uvicorn.run(app, host="0.0.0.0", port=8081)