import logging
import time
import schedule

from delta_refresh.tenant_pipeline import process_tenant_pipeline

logging.basicConfig(level=logging.INFO)


def schedule_tenant_refresh(interval_minutes: int = 1):
    """Schedule the tenant pipeline to run at a fixed interval."""

    def job():
        try:
            logging.info("Starting tenant refresh pipeline")
            process_tenant_pipeline()
            logging.info("Tenant refresh pipeline completed")
        except Exception as exc:
            logging.error("Tenant pipeline failed: %s", exc)

    schedule.every(interval_minutes).minutes.do(job)

    logging.info("Scheduler started with %s minute interval", interval_minutes)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    schedule_tenant_refresh()
