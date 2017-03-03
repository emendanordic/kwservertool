# MIT License
#
# Copyright (c) 2016 Emenda Nordic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# TODO - NEED TO REFACTOR THIS SCRIPT...

from kwplib import kwplib
from subprocess import call

import argparse, ast, copy, getpass, logging

parser = argparse.ArgumentParser(description='Klocwork Server Utility Tool')
parser.add_argument('--url', required=True,
    help='URL to the Klocwork server, e.g. "http://kw.server:8080"')
parser.add_argument('--user', required=False, default=getpass.getuser(),
    help='The username to use for connecting to the Klocwork server')
parser.add_argument('--re-project', required=False, default='',
    help='Regular expression for which matching projects will be processed')

parser.add_argument('--cmd', required=False, default=None,
    help='Provide a command to execute where {project} will be replaced')
parser.add_argument('--api', required=False, default=None,
    help='Provide an api query to execute. Do not provide the project as this is automatically added')

parser.add_argument('--silent', required=False, dest='silent', action='store_true',
    help='Do not prompt user about performing updates')
parser.add_argument('--verbose', required=False, dest='verbose',
    action='store_true', help='Provide verbose output')

def main():
    args = parser.parse_args()
    logLevel = logging.INFO
    if args.verbose:
        logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel,
        format='%(levelname)s:%(asctime)s %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S')
    logger = logging.getLogger('kwservertool')

    kw_api = kwplib.KwApiCon(url=args.url, user=args.user, verbose=args.verbose)

    # get list of projects
    projects = kw_api.get_project_list(args.re_project)

    if args.cmd:
        # execute a command
        for project in projects:
            cmd = args.cmd.replace("{project}", project)
            choice = 'n'
            if not args.silent:
                print 'Are you sure you want to call "{}"? [y/n] '.format(cmd)
                choice = raw_input().lower()
                if choice == 'y':
                    print cmd
                    call(cmd.split(' '))
            else:
                print cmd
                call(cmd.split(' '))

    if args.api:
        # execute API
        values = ast.literal_eval(args.api)
        if not isinstance(values,dict):
            sys.exit("Error: Incorrectly parsed --api command")
        for project in projects:
            values['project'] = project
            print "Using query: " + values
            # perform action "builds" on project git, on Klocwork server at xubuntu:8080
            query_response = kw_api.execute_query(copy.deepcopy(values))
            # if response is None, then there was an error
            if query_response.response == None:
                print "Error: " + query_response.error_msg
            else:
                for i in query_response.response:
                    print i

if __name__ == "__main__":
    main()