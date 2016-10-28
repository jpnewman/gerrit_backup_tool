
"""Gerrit API."""

import urllib2
import httplib
import json
import ssl

import log


class Api(object):
    """Api."""

    def __init__(self, url, verify_ssl=False):
        """Init."""
        super(Api, self).__init__()
        self.url = url
        self.verify_ssl = verify_ssl

        self.verbose = False

    def get_repos(self):
        """Get Gerrit Repos via API."""
        log.print_log("Getting Gerrit Repos via API")

        api_url = self.url + '/projects/?t'

        if self.verbose:
            extra_options = ''

            if not self.verify_ssl:
                extra_options += 'k'

            log.verbose("curl -L%s %s" % (extra_options, api_url))

        try:
            context = ssl.create_default_context()

            if not self.verify_ssl:
                context = ssl._create_unverified_context()

            response = urllib2.urlopen(api_url, context=context)

        except urllib2.HTTPError as err:
            raise RuntimeError("ERROR: (Gerrit API) HTTPError = %s (%s)" % (str(err.code), err.reason))
        except urllib2.URLError as err:
            raise RuntimeError("ERROR: (Gerrit API) URLError = %s (%s)" % (str(err.reason), err.reason))
        except httplib.HTTPException as err:
            raise RuntimeError("ERROR: (Gerrit API) HTTPException = %s" % str(err.reason))
        except Exception:
            import traceback
            raise RuntimeError('ERROR: (Gerrit API) ' + traceback.format_exc())

        if response.getcode() != 200:
            raise RuntimeError("ERROR: (Gerrit API) Did not get 200 response from: %s" % api_url)

        magic_prefix = ")]}'"
        response_body = response.read()
        if response_body.startswith(magic_prefix):
            response_body = response_body[len(magic_prefix):]

        data = json.loads(response_body)

        repos = []
        for repo in data:
            repos.append(repo)

        return repos

    def output_repo_list_to_file(self, repos, repo_list_file):
        """Write Repo List to file."""
        log.print_log("Repo Count: %d" % len(repos))

        repos = sorted(repos)
        with open(repo_list_file, 'w') as output_file:
            output_file.write('\n'.join(repos))

        return repo_list_file
