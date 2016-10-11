
"""Jenkins Class."""

import json
import time
import urllib
import urllib2

import log

from datetime import datetime


class Jenkins(object):
    """Jenkins Class."""

    def __init__(self, jenkins_url):
        """Init."""
        super(Jenkins, self).__init__()
        self.jenkins_url = jenkins_url.rstrip('/')

    def job_task(self, jobName, task='enable'):
        """Job Task (enable / disable)."""
        jobUrl = '/'.join([self.jenkins_url, 'job', jobName, task])
        # print jobUrl

        data = urllib.urlencode({})
        urllib2.urlopen(jobUrl, data)

    def disable_job(self, jobName):
        """Disable Job."""
        self.job_task(jobName, 'disable')

    def enable_job(self, jobName):
        """Enable Job."""
        self.job_task(jobName, 'enable')

    # NOTE: lastBuild, lastStableBuild, lastSuccessfulBuild, lastFailedBuild,
    # lastUnstableBuild, lastUnsuccessfulBuild, lastCompletedBuild
    def get_job_info(self, jobName, jobBuild='lastBuild'):
        """Get Jenkins Build Info."""
        jobUrl = '/'.join([self.jenkins_url, 'job', jobName, jobBuild, 'api/json'])
        # print jobUrl

        jsonData = urllib2.urlopen(jobUrl)

        return json.load(jsonData)

    def wait_until_jobs_finished(self, jobName):
        """Wait until the job is finished."""
        data = self.get_job_info(self.jenkins_url, jobName)
        curJobNum = data['number']
        timeStamp = datetime.fromtimestamp(data['timestamp'] / 1e3).replace(microsecond=0)

        log.print_log("Job Started At: {0:s}".format(timeStamp.strftime('%Y-%m-%d %H:%M:%S')))

        while data['building'] and data['number'] == curJobNum:
            duration = datetime.now().replace(microsecond=0) - timeStamp
            estimatedPercentage = ((duration.total_seconds() * 1000) /
                                   data['estimatedDuration']) * 100

            log.print_log("Building: {0:d} {1:s} {2:.2f}%".format(
                data['number'], str(duration), estimatedPercentage))
            time.sleep(5)

            data = self.get_job_info(self.jenkins_url, jobName)

        print(data['result'])

        if data['result'] == 'FAILURE':
            log.failed("Jenkins job '%s' %s" % (data['result'], jobName))
            log.info("Fix Jenkins job before trying again.")
            return 1

        return 0

    def disable_job_and_wait(self, jobName):
        """Disable Job and Wait."""
        self.disable_job(self.jenkins_url, jobName)
        return self.wait_until_jobs_finished(self.jenkins_url, jobName)
