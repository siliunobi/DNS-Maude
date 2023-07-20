
def a():
    n1 = 10
    n2 = 9

    zone = ""
    for i in range(1, n2 +1):
        zone += "q.a.com." + "\t\tIN\t\tNS\t\t" + "n" + str(i) + ".a.com.\n"
    zone += "\n"

    for i in range(1, n1 + 1):
        for j in range(1, n2 + 1):
            zone += "n" + str(i) + ".a.com."  + "\t\tIN\t\tNS\t\t" + "n" +str(i) + str(j) + ".b.com.\n"
        zone += "\n"
    return zone


def b():
    zone = """$TTL 3600
@                       IN      SOA     server.b.com. username.b.com. (2006032201 7200 3600 1209600 3600)

ns.b.com A 172.20.0.5"""
    return zone


def main():
    print(a())


if __name__ == "__main__":
    main()
