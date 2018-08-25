from celery import shared_task
from django.conf import settings

from ta_platform.celery_app import app

@app.task(bind=True, default_retry_delay=60, retry_kwargs={'max_retries': 5})
def send_user_email(self, address):
    pass