# kwservertool
One tool to Rule them all! This handy utility allows you to execute any Klocwork command or API query over a collection of Klocwork projects (defined using a regular expression)

# Usage
Baselining: To update all issues which have status "Analyze" across all projects to new status "Fix in Later Release", use the following call:
python kwservertool.py --url http://emenda:8080 --user emenda --issues --issue-query status:Analyze --api '{"action":"update_status","status":"Fix in Later Release"}'
