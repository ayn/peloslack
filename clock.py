from apscheduler.schedulers.blocking import BlockingScheduler

from rq import Queue
from worker import conn

from peloslack.peloslack import mainloop

POLL_INTERVAL_SECONDS = 30

q = Queue(connection=conn)

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=POLL_INTERVAL_SECONDS)
def timed_job():
    print('This job is run every 30s.'.format(POLL_INTERVAL_SECONDS))
    result = q.enqueue(poll_slack)
    print(result)


sched.start()