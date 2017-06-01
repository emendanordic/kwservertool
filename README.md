# kwservertool
One tool to Rule them all! This handy utility allows you to execute any Klocwork command or API query over a collection of Klocwork projects (defined using a regular expression)

# Usage
Baselining: To edit all issues across matching projects, use the following call:
python kwservertool.py --url http://emenda:8080 --user emenda --issues --api '{"action":"update_status","status":"Fix in Later Release"}'
