import sys
import os
sys.path.insert(0, 'src')
from googlesheets import add_new_client
from gcloud_commands import deploy_gcf, deploy_scheduler
import argparse
import re
import logging

# Add logging config
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout)

# Set logger
logger = logging.getLogger(__name__)


def set_client_env_vars(user: "str", username: "str", password: "str"):
    logger.info('saving env vars...')
    with open("src/.env.yaml", "a") as envFile:
        envFile.write(
            f"{user}_USERNAME: {username}\n{user}_PASSWORD: {password}\n")
    return


class EmailType(object):
    """
    Supports checking email agains different patterns. The current available patterns is:
    RFC5322 (http://www.ietf.org/rfc/rfc5322.txt)
    """

    patterns = {
        'RFC5322': re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),
    }

    def __init__(self, pattern):
        if pattern not in self.patterns:
            raise KeyError('{} is not a supported email pattern, choose from:'
                           ' {}'.format(pattern, ','.join(self.patterns)))
        self._rules = pattern
        self._pattern = self.patterns[pattern]

    def __call__(self, value):
        if not self._pattern.match(value):
            raise argparse.ArgumentTypeError(
                "'{}' is not a valid email - does not match {} rules".format(value, self._rules))
        return value


def main():
    # Gather args and validate them
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', required=True)
    parser.add_argument('--email', type=EmailType('RFC5322'), required=True)
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    args = parser.parse_args()
    USER = args.user.upper()
    EMAIL = args.email

    # Set env vars
    # This should call function from another file that will be in the .gitignore
    set_client_env_vars(user=USER, username=args.username,
                        password=args.password)

    # redeploy function
    deploy_gcf()

    # create new scheduler job
    deploy_scheduler(user=USER)
    # gcloud scheduler jobs create pubsub JOB-NAME --schedule "30 2 * * *" --topic mfp-1-topic --message-body "USER" --time-zone "America/Los_Angeles" --description "job to pull mfp data for USER" --project <PROJECT-ID>

    # Create, format and share spreadsheet
    add_new_client(user=USER, email=EMAIL)


if __name__ == '__main__':
    # usage (fake example command): python3 new_client.py --user tmunz --email info@example.com --username tmoney884 --password p@$$W0rD!
    main()
