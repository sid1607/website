# Enter the email-id of all the recepients here
recepients=[]

# Enter the DB-BENCH pairs that need to be reported.
# All names should be in upper-case.
db_bench_configs = [
    ('PELOTON', 'TPCC'),
    ('POSTGRES', 'TPCC')
]

# Enter all the attributes of Result model that
# need to be reported, paired with units
result_attributes = [
    ('throughput', 'rps'),
    ('avg_latency', 'ms')
]
