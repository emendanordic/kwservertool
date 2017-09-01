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

import argparse, ast, copy, getpass, logging, json, sys

#API example
#python kwservertool.py --url http://emenda:8080 --user emenda --api '{"action":"version"}'

parser = argparse.ArgumentParser(description='Klocwork Server Utility Tool')
parser.add_argument('--url', required=True,
    help='URL to the Klocwork server, e.g. "http://kw.server:8080"')
parser.add_argument('--user', required=False, default=getpass.getuser(),
    help='The username to use for connecting to the Klocwork server')
parser.add_argument('--project-query', required=False, default='',
    help='To be used with --projects flag. Regular expression for which matching projects will be processed')
parser.add_argument('--projects', required=False, dest='runonprojects',
    action='store_true', help='Execute the cmd/API query for all projects')
parser.add_argument('--issue-query', required=False, default='',
    help='TO be used with --issues flag - API query will only be executed on issues matching this search query (e.g. status=Analyze)')
parser.add_argument('--issues', required=False, dest='runonissues',
    action='store_true', help='Execute the API query for all issues in matching project(s)')

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
    
    #check that we have at least projects or issues flag, and not both
    if args.runonissues and args.runonprojects:
        print "Error: both --issues and --projects flags are present. Do you want to execute the query on projects or issues? Exiting without doing anything."
        sys.exit()
    elif not args.runonissues and not args.runonprojects:
        print "Error: neither --issues nor --projects flags are present. Do you want to execute the query on projects or issues? Exiting without doing anything."
        sys.exit()

    kw_api = kwplib.KwApiCon(url=args.url, user=args.user, verbose=args.verbose)

    # get list of projects
    projects = kw_api.get_project_list(args.project_query)

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
            #Delete any issue ids left in the query
            if 'ids' in values.keys():            
                del values['ids']
            #Set the project of the query
            values['project'] = project
            # if we are to execute the api command over all issues, we must first fetch the issues
            if args.runonissues:
                if args.issue_query:
                    print "Fetching issues on which to execute with query: " + args.issue_query
                    values['query'] = args.issue_query
                issue_groups_list = fetch_issues(copy.deepcopy(values), kw_api)
                #Iterate over each group of issues
		id_list = ""
                for g in issue_groups_list:
                    id_list = ','.join(str(id) for id in g)
                    values['ids'] = id_list
                    #Execute the query for this set of ids
                    query_response = execute_query(copy.deepcopy(values), kw_api)
                    if not query_response.response == None:
                        for i in query_response.response:
                            print i
                if len(id_list) < 1:
                    print "No issues returned, continuing to next project."
            # nope, we're not doing issues, so just run the query
            else:
                query_response = execute_query(copy.deepcopy(values), kw_api)
                if not query_response.response == None:
                    for i in query_response.response:
                        print i

def execute_query(query, kw_api):
    print "Using query: " + str(query)
    # perform query using kwplib
    query_response = kw_api.execute_query(query)
    # if response is None, then there was an error
    if query_response.response == None:
        print "Error when executing query: " + query_response.error_msg
    return query_response

def fetch_issues(query, kw_api):
    query['action'] = "search"
    print "Fetching issue list..."
    query_response = execute_query(query, kw_api)
    #Extract issue ids
    issues = []
    for issue in query_response.response:
        data = json.loads(issue)
        issues.append(data['id'])
    #Split the results into groups to make running queries on them manageable
    return group_issues(issues)
        
def group_issues(issues):
    ISSUE_GROUP_SIZE = 500
    for i in range(0,len(issues),ISSUE_GROUP_SIZE):
        yield issues[i:i + ISSUE_GROUP_SIZE]
    
if __name__ == "__main__":
    main()
