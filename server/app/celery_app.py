from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Standalone Celery instance for background tasks
celery = Celery(
    'public_pulse',
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
