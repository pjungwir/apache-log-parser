import apache_log_parser
import argparse
import csv
import sys
import traceback

def interpret_pattern(pattern):
    # We include a few hard-coded patterns based on common apache configs.
    # Nicknames and patterns are based on the default /etc/apache2/apache2.conf from Ubuntu:
    if pattern == 'vhost_combined':
        return "%v:%p %h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\""
    elif pattern == 'combined':
        return "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\""
    elif pattern == 'common':
        return "%h %l %u %t \"%r\" %>s %b"
    else:
        return pattern

def main():
    argparser = argparse.ArgumentParser(
        prog='apache_log_parser',
        description="Parse apache log files")
    argparser.add_argument('-p', '--pattern')
    argparser.add_argument('-i', '--ignore-errors', action='store_true')
    argparser.add_argument('filename')

    args = argparser.parse_args()

    pattern = interpret_pattern(args.pattern or 'combined')
    parser = apache_log_parser.Parser(pattern)
    writer = csv.DictWriter(sys.stdout, fieldnames=parser.names)
    writer.writeheader()
    with open(args.filename, 'r') as logfile:
        for line in logfile:
            try:
                fields = parser.parse(line)
                # Throw out extra fields:
                fields = {k: fields[k] for k in parser.names}
                writer.writerow(fields)
            except apache_log_parser.LineDoesntMatchException as e:
                if args.ignore_errors:
                    traceback.print_exc()
                else:
                    raise e
            except BrokenPipeError as e:
                # chill
                break
