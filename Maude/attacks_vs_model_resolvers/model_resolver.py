# For every resolver implementation, check the maxFetch and maxFetchParam, as well as
# whether CNAME chain validation should be enabled with rsvMinCacheCredClient
# and rsvMinCacheCredResolver, and the workBudget

MAX_SUBQUERIES = 100000


class ModelResolver():
    """This is the parent class for all resolver models.
        This will be used as a base and all implementations will contain
        different parameters specific to itself and its version number."""

    def __init__(self):
        self.name = "General resolver model"
        self.cname_chain_validation = False

        self.folder = "general"
        self.version = "0.0.0"

        self.cname_limit = 1000
        self.qmin_limit = 1000
        self.workBudget = 5000

        # No limit to the number of subqueries
        self.max_subqueries = MAX_SUBQUERIES

        self.overall_timeout = 0

    # Returns the configuration details of the resolver
    def config_text(self):
        res = ""

        if self.max_subqueries != MAX_SUBQUERIES:
            res += "\n\t---  maximum subqueries\n"
            res += "\teq maxFetch? = true .\n"
            res += "\teq maxFetchParam = {} .\n\n".format(self.max_subqueries)

        res += "\teq configWorkBudget = {} .\n\n".format(self.workBudget)

        if self.cname_chain_validation:
            res += "\t--- enable CNAME validation \n"
            res += "\teq rsvMinCacheCredClient = 5 . \n"
            res += "\teq rsvMinCacheCredResolver = 5 .\n\n"

        if self.overall_timeout != 0:
            res += "\t--- enable overall timeout \n"
            res += "\teq rsvOverallTimeout? = true . \n"
            res += "\teq rsvOverallTimeout = {} . \n\n".format(self.overall_timeout)

        return res


class Unbound1_10_0(ModelResolver):
    # no mitigation -> maxFetch = false,
    # q configWorkBudget = 5000 BEWARE !!
    def __init__(self):
        ModelResolver.__init__(self)
        self.version = "1.10.0"
        self.name = "Unbound" + " " + self.version

        self.folder = "unbound1_10_0"

        self.cname_chain_validation = True
        self.cname_limit = 9
        self.qmin_limit = 10

        self.workBudget = 5000

        # No limit to the number of subqueries
        self.max_subqueries = MAX_SUBQUERIES


class Unbound1_10_0_NO_CHAIN_VALIDATION(Unbound1_10_0):
    # For Subqueries + Unchained attacks
    def __init__(self):
        Unbound1_10_0.__init__(self)
        self.name += " NO CHAIN VALIDATION"
        self.folder = "unbound1_10_0_no_chain_val"

        self.cname_chain_validation = False


class Unbound1_10_0_CNAME_BYPASSED(Unbound1_10_0):
    # max cname chain length has been bypassed due to the type of AAAA queries not being checked
    # We artificially implement this bypass by creating another class with no cname chain limit

    def __init__(self):
        Unbound1_10_0.__init__(self)
        self.name += " CNAME_BYPASSED"

        self.folder = "unbound1_10_0_cname_bypassed"
        self.cname_limit = 1000000
        self.max_subqueries = MAX_SUBQUERIES


class Unbound1_16_0(ModelResolver):
    # max cname chain length 12
    # max subqueries a = 6

    def __init__(self):
        ModelResolver.__init__(self)
        self.version = "1.16.0"
        self.name = "Unbound" + " " + self.version

        self.folder = "unbound1_16_0"

        self.cname_chain_validation = True
        self.cname_limit = 12
        self.qmin_limit = 10

        self.workBudget = 5000

        self.max_subqueries = 6


class Unbound1_16_0_NO_CHAIN_VALIDATION(Unbound1_16_0):
    # For Subqueries + Unchained attacks
    def __init__(self):
        Unbound1_16_0.__init__(self)
        self.name += " NO CHAIN VALIDATION"
        self.folder = "unbound1_16_0_no_chain_val"

        self.cname_chain_validation = False


class Unbound1_16_0_CNAME_BYPASSED(Unbound1_16_0):
    # max cname chain length has been bypassed due to the type of AAAA queries not being checked
    # We artificially implement this bypass by creating another class with no cname chain limit
    # max subqueries a = 6

    def __init__(self):
        Unbound1_16_0.__init__(self)
        self.name += " CNAME_BYPASSED"

        self.folder = "unbound1_16_0_cname_bypassed"
        self.cname_limit = 1000000
        self.max_subqueries = 6


class PowerDNS4_7_0(ModelResolver):
    # This is the resolver when QMIN is disabled

    # max cname chain length 12, but last cname is not validated
    # max subqueries a = 5
    # workBudhet = 100

    def __init__(self):
        ModelResolver.__init__(self)
        self.version = "4.7.0"
        self.name = "PowerDNS" + " " + self.version

        self.folder = "powerDNS4_7_0"

        self.cname_chain_validation = True
        # The last cname is not validated
        self.cname_limit = 12-1
        self.qmin_limit = 10

        self.workBudget = 100

        # In time units only when QMIN is disabled
        self.overall_timeout = 6000.0
        
        # When QMIN is disabled -> maximum subqueries of 5
        self.max_subqueries = 5


class PowerDNS4_7_0_QMIN(PowerDNS4_7_0):
    def __init__(self):
        PowerDNS4_7_0.__init__(self)

        # self.name += " QMIN ENABLED"

        self.folder = "powerDNS4_7_0"
        self.cname_chain_validation = True
        
        self.max_subqueries = 9

        # In time units
        # 6 seconds when QMIN activated
        self.overall_timeout = 6000.0


class PowerDNS4_7_0_QMIN_NO_CHAIN_VALIDATION(PowerDNS4_7_0_QMIN):
    def __init__(self):
        PowerDNS4_7_0_QMIN.__init__(self)
        self.name += " No chain validation"
        self.cname_chain_validation = False


        self.folder = "powerDNS4_7_0_no_chain_val"
        self.cname_limit = 12


class PowerDNS4_7_0_MOD_FOR_DELAY(PowerDNS4_7_0):
    # Class to show that there is a change between the CCV and CCV+Delay in PowerDNS4_7_0()
    # related to the cname limit
    def __init__(self):
        PowerDNS4_7_0.__init__(self)
        self.name = "PowerDNS" + " " + self.version + " Modified"

        self.folder = "powerDNS4_7_0_mod"

        self.cname_chain_validation = True
        # The last cname is not validated
        self.cname_limit = 12


class PowerDNS4_7_0_NO_CHAIN_VALIDATION(PowerDNS4_7_0):
    # For Subqueries + Unchained attacks
    def __init__(self):
        PowerDNS4_7_0.__init__(self)
        self.name += " NO CHAIN VALIDATION"
        self.folder = "powerDNS4_7_0_no_chain_val"

        self.cname_chain_validation = False
        
        self.cname_limit = 12


class Bind9_18_4(ModelResolver):
    # no mitigation -> maxFetch = false,
    # configWorkBudget = 5000 
    # Here used for Unchained attacks (without subqueries)
    def __init__(self):
        ModelResolver.__init__(self)
        self.version = "9.18.4"
        self.name = "Bind" + " " + self.version

        self.folder = "bind9_18_4"

        self.cname_chain_validation = True
        self.cname_limit = 17
        self.qmin_limit = 5

        self.workBudget = 5000

        self.max_subqueries = MAX_SUBQUERIES


class Bind9_18_4_CNAME(Bind9_18_4):
    # Use for all attacks with cname and subqueries
    # since it doesn't follow cname in subqueries
    def __init__(self):
        Bind9_18_4.__init__(self)
        # self.name += " CNAME"
        self.folder = "bind9_18_4"

        self.cname_chain_validation = True
        self.cname_limit = 1


class Bind9_18_4_NO_CHAIN_VALIDATION(Bind9_18_4):
    # For Subqueries + Unchained attacks
    # Here Bind doesn't follow CNAME elements in subqueries
    # Also used for Subqueries + DNAME scrubbing
    def __init__(self):
        Bind9_18_4.__init__(self)
        # self.name += " NO CHAIN VALIDATION"
        self.folder = "bind9_18_4_no_chain_val"

        self.cname_chain_validation = False
        self.cname_limit = 1
