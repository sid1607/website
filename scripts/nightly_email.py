import scripts.config_nightly_email as config
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from website.models import Result
from tabulate import tabulate

from django.core.mail import EmailMultiAlternatives

import sys
import pprint

EMAIL_SUBJECT = 'Nightly Benchmark Results'
FROM_ADDRESS = 'webmaster@pelotodb.io'

# Identify attr value has increased or decreased
def evaluate_res(attr, res_list):
    status = 'Decreased'
    if getattr(res_list[0], attr) > getattr(res_list[1], attr):
        status = 'Increased'
    return status + ' ' + attr.capitalize()

def make_report_table_row(res, attr):
    return [res.creation_time, getattr(res, attr)]

# Generate the report for db_bench
def get_db_bench_report(db_bench, res_list):
    report = []
    db_bench_str = pprint.pformat(db_bench)
    dashes = '='*len(db_bench_str)
    report.extend(('\n', dashes, db_bench_str, dashes))
    for (attr,units) in config.result_attributes:
        attr_units_str = attr + ' (' + units + ')'
        header = evaluate_res(attr, res_list)
        report.extend(('\n'+header, '-'*len(header)))
        report.append(tabulate(
	    [['current']+make_report_table_row(res_list[0], attr),
	     ['previous']+make_report_table_row(res_list[1], attr)],
	    headers = ['', 'Completion Timestamp', attr_units_str.capitalize()],
	    tablefmt='psql'))
    return report

def send_email(email_body, recepients):
   text_body = "\n".join(email_body)
   html_body = "<pre>\n" + text_body + "\n</pre>"
   print text_body
   email = EmailMultiAlternatives(
		EMAIL_SUBJECT,
		text_body,
		FROM_ADDRESS,
		to=recepients)
   email.attach_alternative(html_body, "text/html")
   email.send()

def main():
    email_body = []
    try:
        map(validate_email, config.recepients)
    except ValidationError:
        print 'Enter valid email_ids in config_nightly_email.py'
        sys.exit(1)
    for db_bench in config.db_bench_configs:
        try:
            # retrieve the latest two results
            res = Result.objects.filter(
		    db_conf__db_type=db_bench[0],
		    benchmark_conf__benchmark_type=db_bench[1]
		).order_by('-creation_time')[:2]
            report = get_db_bench_report(db_bench, res)
        except:
            print 'Insufficient data for ' + str(db_bench)
	    continue
        email_body += report
    print '\n'
    # send email only if there is a body
    if len(email_body) > 0:
        send_email(email_body, config.recepients)

main()
