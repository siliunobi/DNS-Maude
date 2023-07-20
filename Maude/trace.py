#!/usr/bin/env python3
import argparse

# The rule labels that should be printed
LABELS = [
    "client-start",
    "resolver-reply-local",
    "resolver-recv-query",
    "nameserver-recv-query-unbounded",
    "nameserver-recv-query",
    "nameserver-process-query",
    "resolver-recv-ans-for-client",
    "resolver-recv-ans-for-resolver",
    "resolver-recv-cname-reply-for-client-answered",
    "resolver-recv-cname-reply-for-resolver-answered",
    "resolver-recv-cname-reply-not-answered",
    "resolver-recv-dname-reply-for-client-answered",
    "resolver-recv-dname-reply-for-resolver-answered",
    "resolver-recv-dname-reply-not-answered",
    "resolver-recv-referral-reply",
    "resolver-recv-qmin-noerror-reply",
    "resolver-recv-bad-referral-reply-for-client",
    "resolver-recv-bad-referral-reply-for-resolver",
    "resolver-recv-refused-reply-for-client",
    "resolver-recv-refused-reply-for-resolver",
    "resolver-timeout-for-client",
    "resolver-timeout-for-resolver",
    "resolver-overall-timeout",
    "resolver-overall-timeout-ignore",
    "resolver-timeout-ignore",
    "resolver-recv-response-ignore",
    "client-recv-resp-send-next",
    "client-recv-resp-done",
    "nxdomain-client-send-next",
    "repeating-client-send-next",
    "malicious-client-stop",
    "malicious-client-recv-response",
    "malicious-nxns-nameserver-recv-query-unbounded",
    "malicious-idns-nameserver-recv-full-query-unbounded",
    "malicious-idns-nameserver-recv-minimized-query-unbounded",
    "delayed-nameserver-recv-query-unbounded",
    "unresponsive-nameserver-drop-query",
]

def ff(x):
    return x in LABELS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', help="file with the recorded trace")
    parser.add_argument('--outfile', help="file where the output should be written to")
    args = parser.parse_args()

    with open(args.infile, "r") as infile:
        lines = infile.read().splitlines()
        filtered = filter(ff, lines)
        with open(args.outfile, "w") as outfile:
            for line in filtered:
                outfile.write(line + "\n")

if __name__ == "__main__":
    main()
