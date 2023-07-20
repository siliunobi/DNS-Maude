from pathlib import Path
from operator import itemgetter

IN_A_ = "\t\tIN\t\tA\t\t"

zones_folder = Path("zones")
IN_NS_ = "\t\tIN\t\tNS\t\t"
MODEL_ZONE = """$TTL 3600
@\t\t\t\tIN\t\tSOA\t\tserver.{zone} username.{zone} (2006032201 7200 3600 1209600 36000)
\t\t\t\tIN\t\tNS\t\t{hosting_zone}
{hosting_zone}\t\tIN\t\tA\t\t{hosting_zone_ip}

"""


def folder_attack_zones():
    """Creates the folder containing the new zones"""
    new_folder = f"r{rewrite_length}-n{fanout}-ref{referral_length}"
    new_folder_path = zones_folder / new_folder
    new_folder_path.mkdir(parents=True, exist_ok=True)

    return new_folder_path


def a(new_folder_path):
    """Writes the zone file of a.com"""
    zone = MODEL_ZONE.format(zone="a.com.", hosting_zone="ns.a.com.", hosting_zone_ip="172.20.0.5")

    # 1st fanout
    for i in range(1, fanout + 1):
        zone += "q.a.com." + IN_NS_ + "n0n" + str(i) + ".b.com.\n"
    zone += "\n"

    # Rewrite chain and fanout
    for i in range(1, rewrite_length + 1):
        for j in range(1, fanout + 1):
            zone += f"r{i}.a.com." + IN_NS_ + f"n{i}n{j}" + ".b.com.\n"
        zone += "\n"

    new_zone = new_folder_path / "a-com.zone"
    with new_zone.open("w") as zonefile:
        zonefile.write(zone)

    return zone


def b(new_folder_path):
    """Writes the zone file of b.com"""
    zone = MODEL_ZONE.format(zone="b.com.", hosting_zone="ns.b.com.", hosting_zone_ip="172.20.0.5")

    for r in range(0, rewrite_length):
        for f in range(1, fanout + 1):
            zone += f"n{r}n{f}.b.com." + IN_NS_ + \
                    f"n{r}n{f}n1.c.com." + "\n"
        zone += "\n\n"
    new_zone = new_folder_path / "b-com.zone"
    with new_zone.open("w") as zonefile:
        zonefile.write(zone)
    return zone


def related_b_zones(new_folder_path):
    """Writes the zones files of subdomain of b.com and c.com"""

    for r in range(0, rewrite_length):
        for f in range(1, fanout + 1):
            # Write all n...b zones
            zone = MODEL_ZONE.format(zone=f"n{r}n{f}.b.com.", hosting_zone=f"n{r}n{f}n1.c.com.",
                                     hosting_zone_ip="172.20.0.6")
            zone += f"n{r}n{f}.b.com." + IN_A_ + "172.20.0.6"
            new_zone = new_folder_path / f"n{r}n{f}-b-com.zone"
            with new_zone.open("w") as zonefile:
                zonefile.write(zone)

            for n in range(1, referral_length + 1):
                # Write all n.n.n.c.com zones
                # TODO: check if we should add a non-existing domain nxnxnx.A.com
                zone = MODEL_ZONE.format(zone=f"n{r}n{f}n{n}.c.com.", hosting_zone=f"n{r}n{f}n{n + 1}.c.com.",
                                         hosting_zone_ip="172.20.0.6")
                zone += f"n{r}n{f}n{n}.c.com." + IN_A_ + "172.20.0.6"
                new_zone = new_folder_path / f"n{r}n{f}n{n}-c-com.zone"
                with new_zone.open("w") as zonefile:
                    zonefile.write(zone)


def c(new_folder_path):
    """Writes the zone file of c.com"""
    zone = MODEL_ZONE.format(zone="c.com.", hosting_zone="ns.c.com.", hosting_zone_ip="172.20.0.5")
    for r in range(0, rewrite_length):
        for f in range(1, fanout + 1):
            for n in range(1, referral_length + 1):
                zone += f"n{r}n{f}n{n}.c.com." + IN_NS_ + \
                        f"n{r}n{f}n{n + 1}.c.com." + "\n"
            # Write the A record for the last element of the referral chain
            zone += f"n{r}n{f}n{referral_length + 1}.c.com." + "\t\tIN\t\tA\t\t" + \
                    "172.20.0.6" + "\n\n"
        zone += "\n\n"

    new_zone = new_folder_path / "c-com.zone"
    with new_zone.open("w") as zonefile:
        zonefile.write(zone)
    return zone


def create_zone_q(new_folder_path):
    """Write the zone file of q.a.com"""
    zone_q = """$TTL 3600
@\t\t\t\tIN\t\tSOA\t\tserver.q.a.com. username.q.a.com. (2006032201 7200 3600 1209600 36000)
"""
    for i in range(1, fanout + 1):
        hosting_zone = f"n0n{i}.b.com."
        zone_q += f"\t\t\t\tIN\t\tNS\t\t{hosting_zone}\n"

    for i in range(1, fanout + 1):
        hosting_zone = f"n0n{i}.b.com."
        hosting_zone_ip = "172.20.0.6"
        zone_q += f"{hosting_zone}\t\tIN\t\tA\t\t{hosting_zone_ip}\n"

    zone_q += "\n\n" + "w.q.a.com." + "\t\tIN\t\tCNAME\t\t" + "w.r1.a.com.\n"
    new_zone = new_folder_path / "q-a-com.zone"
    with new_zone.open("w") as zonefile:
        zonefile.write(zone_q)
    return zone_q


def rewrite_zones(new_folder_path):
    """Write the rewrite zones (q.a.com., r1.a.com., ...)"""
    zone_q = create_zone_q(new_folder_path)

    for r in range(1, rewrite_length + 1):
        zone = f"""$TTL 3600
@\t\t\t\tIN\t\tSOA\t\tserver.r{r}.a.com. username.r{r}.a.com. (2006032201 7200 3600 1209600 36000)
"""
        for i in range(1, fanout + 1):
            hosting_zone = f"n{r}n{i}.b.com."
            zone += f"\t\t\t\tIN\t\tNS\t\t{hosting_zone}\n"

        for i in range(1, fanout + 1):
            hosting_zone = f"n{r}n{i}.b.com."
            hosting_zone_ip = "172.20.0.6"
            zone += f"{hosting_zone}\t\tIN\t\tA\t\t{hosting_zone_ip}\n"

        zone += "\n\n" + f"w.r{r}.a.com." + "\t\tIN\t\tCNAME\t\t" + f"w.r{r + 1}.a.com.\n"
        print(zone)
        new_zone = new_folder_path / f"r{r}-a-com.zone"
        with new_zone.open("w") as zonefile:
            zonefile.write(zone)


def values_testbed():
    """Prints the names of the zones in the same format as the testbed.yaml file"""
    qname_model = '\t\t- qname: "{zone}"\n'
    qnames = qname_model.format(zone="a.com.")
    qnames += qname_model.format(zone="b.com.")
    qnames += qname_model.format(zone="c.com.")
    qnames += qname_model.format(zone="q.a.com.")
    for i in range(1, max_rew + 1):
        qnames += qname_model.format(zone=f"r{i}.a.com.")

    for r in range(0, max_rew + 1):
        for f in range(1, max_fanout + 1):
            qnames += qname_model.format(zone=f"n{r}n{f}.b.com.")
            for n in range(1, max_ref + 1):
                qnames += qname_model.format(zone=f"n{r}n{f}n{n}.c.com.")

    return qnames


def main():
    new_folder_path = folder_attack_zones()
    a(new_folder_path)
    b(new_folder_path)
    related_b_zones(new_folder_path)
    c(new_folder_path)
    rewrite_zones(new_folder_path)


if __name__ == "__main__":
    # List of tuples containing the rewrite_length, the fanout and the referral length
    t = [(2, 2, 4), (2, 2, 7), (2, 2, 15),
         (17, 5, 4), (17, 5, 7), (17, 5, 15),
         (17, 6, 4), (17, 6, 7), (17, 6, 15),
         (17, 20, 4), (17, 20, 7), (17, 20, 15)]
    # 17 is max rew for BIND, 20, is max fanout (secondary size) for BIND, 15 is max ref for Powerdsn
    # Create the zones for each tuple
    for tup in t:
        rewrite_length, fanout, referral_length = tup
        main()

    # Get the maximum values of the attack parameters to add the correct zones to the testbed
    max_rew = max(t, key=itemgetter(0))[0]
    max_fanout = max(t, key=itemgetter(1))[1]
    max_ref = max(t, key=itemgetter(2))[2]
    print(f"{max_rew} - {max_fanout} - {max_ref}")

    # TODO : write the testbed
    val = values_testbed()
    print(val)

    with open(f"test-rew{max_rew}-n{max_fanout}-ref{max_ref}.txt", "w") as f:
        f.write(val)

    # rewrite_length = 3
    # fanout = 3
    # referral_length = 4
    # main()
