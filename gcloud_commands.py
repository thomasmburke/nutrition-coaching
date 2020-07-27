import subprocess
import os


def deploy_gcf() -> "int":
    """
    Summary: Redeploys the GCF with updated environmant variables
    """
    filePath = os.path.dirname(os.path.realpath(__file__))
    deployPath = os.path.join(filePath, "src/")
    return subprocess.call(args=f"gcloud functions deploy pull-mfp-data --entry-point pull_mfp_data --runtime python37 --trigger-topic mfp-1-topic --timeout 540s --env-vars-file .env.yaml --project {os.getenv('NUTRITION_GCP_PROJECT_ID')}".split(" "), cwd=deployPath)


def deploy_scheduler(user: "str") -> "int":
    """
    Summary: Creates new Cloud Scheduler job the new client
    """
    # gcloud scheduler jobs create pubsub JOB-NAME --schedule "30 2 * * *" --topic mfp-1-topic --message-body "USER" --time-zone "America/Los_Angeles" --description "job to pull mfp data for USER" --project nutrition-coaching
    cmd = ['gcloud', 'scheduler', 'jobs', 'create', 'pubsub', f"{user}-JOB", '--schedule', '30 2 * * *', '--topic', 'mfp-1-topic', '--message-body', user,
           '--time-zone', 'America/Los_Angeles', '--description', f"job to pull mfp data for {user}", '--project', os.getenv('NUTRITION_GCP_PROJECT_ID')]
    return subprocess.call(cmd)
