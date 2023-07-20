
def a():
    zone = ""
    for i in range(1, n1 + 1):
        zone += "q.a.com." + "\t\tIN\t\tNS\t\t" + "n" + str(i) + ".a.com.\n"
    zone += "\n"

    for i in range(1, n1 + 1):
        zone += "n" + str(i) + ".a.com." + "\t\tIN\t\tNS\t\t" + "n" + str(i) + "n1" + ".b.com.\n"
    return zone


def b():
#     zone = """$TTL 3600
# @                       IN      SOA     server.b.com. username.b.com. (2006032201 7200 3600 1209600 3600)
#
# ns.b.com IN  A 172.20.0.5"""
    zone = ""
    for i in range(1, n1+1):
        for j in range(1, n2):
            zone += "n" + str(i) + "n" + str(j) + ".b.com." + "\t\tIN\t\tNS\t\t" +\
                    "n" + str(i) + "n" + str(j+1) + ".b.com." + "\n"
        zone += "\n\n"
    return zone


def main():
    print(b())


if __name__ == "__main__":
    n1 = 10
    n2 = 15
    main()
