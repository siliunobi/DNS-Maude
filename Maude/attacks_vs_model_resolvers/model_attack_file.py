#!/usr/bin/env python3


def qmin_text(QMIN_DEACTIVATED, qmin_limit=10):
    """
    Creates the required text to disable QMIN (enabled by default). The text can then be added to the Maude file.

    :param QMIN_DEACTIVATED: boolean value, True if we want to disable QMIN
    :returns: text that deactivates this feature
    """
    text = "\n"
    if QMIN_DEACTIVATED:
        text += "--- Deactivate QMIN\n"
        text += "eq maxMinimiseCount = 0 .\n"
    else:
        text += "--- Activate QMIN\n"
        text += "eq maxMinimiseCount = {} .\n".format(qmin_limit)
    return text


class ModelAttackFile():

    def __init__(self):

        self.folder = ""

        self.imports = ""

        self.description = ""

        self.start_text = ""

        self.continue_text = ""

        self.target_text = ""

        self.intermediary_text = ""

        self.attacker_text = ""

        self.end_text = ""

        self.print_text = ""

        self.victim = "UNDEFINED VICTIM"

        self.name_attack = "UNDEFINED NAME ATTACK"


class IDNSAttack(ModelAttackFile):

    def __init__(self):
        ModelAttackFile.__init__(self)

        self.imports = '''load {PATH_TO_MAIN_DIR}/src/probabilistic-model/dns
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/sampler
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/properties
        '''

        self.start_text = '''
mod TEST is
  inc SAMPLER + APMAUDE + DNS + PROPERTIES .

  eq rsvTimeout? = false .
  eq rsvTimeout = 1000.0 .

 {}
         '''

        self.continue_text = '''

  op q : -> Query .
  eq q = query(1, 'sub1 . 'attacker . 'com . root, a) .

  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNSattacker : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >, 1)
    cacheEntry(< 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker >, 1) .


  ops zoneRoot zoneCom zoneAttacker : -> List{Record} .
  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >
    < 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker > . --- glue
        '''

        self.attacker_text = '''
  eq zoneAttacker =
    --- authoritative data
    < 'attacker . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >
    < 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker >

    {}
            .
        '''
        self.end_text = '''
  op initConfig : -> Config .
  eq initConfig = run(initState, limit) .

  eq initState = { 0.0 | nil }
    --- Preliminaries
    initMonitor(mAddr)
    [id, to cAddr : start, 0]

    < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
    < rAddr : Resolver | cache: cache,
                         nxdomainCache: nilNxdomainCache,
                         nodataCache: nilNodataCache,
                         sbelt: sb,
                         workBudget: emptyIN,
                         blockedQueries: eptQSS,
                         sentQueries: eptQSS >

    --- Root name server
    < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
    --- .com authoritative name server
    < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
    --- attacker authoritative name server
    < addrNSattacker : Nameserver | db: zoneAttacker, queue: nilQueue > .

endm

--- uncomment for debugging purposes
--- set trace on .

set trace condition off . --- This does not seem to work
set trace whole off .
set trace substitution off .
set trace mb off .
set trace eq off .
set trace rl on . --- on
set trace select off .
set trace rewrite off .
set trace body off .
set trace builtin off .
        '''

        self.print_text = '''
rew initConfig .
rew numActorMsgsRecvd(rAddr, initConfig) .
---rew msgAmpFactor(cAddr, rAddr, initConfig) .
--- rew msgAmpFactor(cAddr ; addrNSattacker, rAddr, initConfig) .
--- rew numActorMsgsRecvdTerminal(rAddr, initConfig) .
--- rew numActorMsgsSentTerminal(cAddr ; addrNSattacker, initConfig) .
---rew msgAmpFactorTerminal(cAddr, rAddr, initConfig) .

--- rew msgAmpFactor(cAddr, rAddr, initConfig) .
--- rew msgAmpFactor(cAddr, addrNStargetANS, initConfig) .

--- rew msgAmpFactor(cAddr, addrNSintermediary, initConfig) .

--- rew msgAmpFactor(cAddr ; addrNStargetANS ; addrNSintermediary ; addrNScom, rAddr, initConfig) .
--- rew numActorMsgsRecvd(rAddr, initConfig) .

--- rew msgAmpFactor(cAddr, addrNStargetANS ; addrNSintermediary ; addrNScom, initConfig) .
--- rew msgAmpFactor(cAddr, addrNSintermediary, initConfig) .
        '''

        self.victim = "resolver"
        self.name_attack = "GENERIC IDNS ATTACK"


class IDNSVariant1(IDNSAttack):

    def __init__(self):
        IDNSAttack.__init__(self)
        self.folder = "idns/variant1"

        self.description = '''\t--- Created automatically with Python,
        \t--- This file simulates the variant 1 of the iDNS attack. It consists
        \t--- of an attacker nameserver that constantly sends one NS delegation
        \t--- to the resolver, this delegation is redirecting the resolver to
        \t--- to the attacker nameserver.
        \t--- Attackers: client, nameserver ; Victim : resolver
        '''

        # self.imports same as parent
        # self.start_text same as parent
        self.name_attack = "iDNS attack variant1"


class IDNSVariant2(IDNSAttack):

    def __init__(self):
        IDNSAttack.__init__(self)
        self.folder = "idns/variant2"

        self.description = '''\t--- Created automatically with Python,
        \t--- This file simulates the variant 2 of the iDNS attack. It consists
        \t--- of an attacker nameserver that constantly sends multiple NS delegations
        \t--- to the resolver, all these delegations are redirecting the resolver to
        \t--- to the attacker nameserver.
        \t--- Attackers: client, nameserver ; Victim : resolver
        '''

        # self.imports same as parent
        # self.start_text same as parent
        self.name_attack = "iDNS attack variant2"


class IDNSVariant3(IDNSAttack):

    def __init__(self):
        IDNSAttack.__init__(self)
        self.folder = "idns/variant3"

        self.description = '''\t--- Created automatically with Python,
        \t--- This file simulates the variant 3 of the iDNS attack. It consists
        \t--- of an attacker nameserver that constantly sends multiple NS delegations
        \t--- to the resolver, all these delegations are redirecting the resolver to
        \t--- to the victim nameserver.
        \t--- Attackers: client, attacker nameserver ; Victim : nameserver
        '''

        # self.imports same as parent
        # self.start_text same as parent
        self.continue_text = '''
        op q : -> Query .
      eq q = query(1, 'sub1 . 'attacker . 'com . root, a) .

      ops mAddr cAddr rAddr : -> Address .

      --- "SBELT": fallback if there are no known name servers
      op sb : -> ZoneState .
      eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

      op cache : -> Cache .
      eq cache =
        cacheEntry(< 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >, 1)
        cacheEntry(< 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker >, 1)
        cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
        cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
        .

      ops addrRoot addrNScom addrNSattacker addrNStargetANS : -> Address .

      ops zoneRoot zoneCom zoneAttacker zoneTarget : -> List{Record} .
      eq zoneRoot =
        --- authoritative data
        < root, soa, testTTL, soaData(testTTL) > --- dummy value
        < root, ns, testTTL, 'a . 'root-servers . 'net . root >

        --- non-authoritative data
        < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
        < 'com . root, ns, testTTL, 'ns . 'com . root >
        < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

      eq zoneCom =
        --- authoritative data
        < 'com . root, soa, testTTL, soaData(testTTL) >
        < 'com . root, ns, testTTL, 'ns . 'com . 'root >
        < 'ns . 'com . root, a, testTTL, addrNScom >

        --- non-authoritative data
        < 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >
        < 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker > --- glue

        < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
        < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS > . --- glue
    '''
        self.target_text = '''
      eq zoneTarget =
        --- authoritative data
        < 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
        < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
        < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >

        < wildcard . 'target-ans . 'com . root, mx, testTTL, nullAddr >
        . --- a wildcard record of arbitrary type
    '''

        self.attacker_text = '''
    eq zoneAttacker =
        --- authoritative data
        < 'attacker . 'com . root, soa, testTTL, soaData(testTTL) >
        < 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >
        < 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker >

        {}
        .


        '''

        self.end_text = '''
          op initConfig : -> Config .
          eq initConfig = run(initState, limit) .

          eq initState = { 0.0 | nil }
            --- Preliminaries
            initMonitor(mAddr)
            [id, to cAddr : start, 0]

            < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
            < rAddr : Resolver | cache: cache,
                                 nxdomainCache: nilNxdomainCache,
                                 nodataCache: nilNodataCache,
                                 sbelt: sb,
                                 workBudget: emptyIN,
                                 blockedQueries: eptQSS,
                                 sentQueries: eptQSS >

            --- Root name server
            < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
            --- .com authoritative name server
            < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
            --- attacker authoritative name server
            < addrNSattacker : Nameserver | db: zoneAttacker, queue: nilQueue >
            --- target authoritative name server
            < addrNStargetANS : Nameserver | db: zoneTarget, queue: nilQueue > .

        endm

        --- uncomment for debugging purposes
        --- set trace on .

        set trace condition off . --- This does not seem to work
        set trace whole off .
        set trace substitution off .
        set trace mb off .
        set trace eq off .
        set trace rl on . --- on
        set trace select off .
        set trace rewrite off .
        set trace body off .
        set trace builtin off .
        '''

        self.print_text = '''
        rew initConfig .
        rew numActorMsgsRecvd(addrNStargetANS, initConfig) .
        ---rew msgAmpFactorTerminal(cAddr, rAddr, initConfig) .
        ---rew msgAmpFactor(cAddr,  addrNStargetANS, initConfig) .
        --- rew msgAmpFactor(cAddr ; addrNSattacker, rAddr, initConfig) .
        --- rew numActorMsgsRecvdTerminal(rAddr, initConfig) .
        --- rew numActorMsgsSentTerminal(cAddr ; addrNSattacker, initConfig) .
        ---rew msgAmpFactorTerminal(cAddr, rAddr, initConfig) .

        --- rew msgAmpFactor(cAddr, rAddr, initConfig) .
        --- rew msgAmpFactor(cAddr, addrNStargetANS, initConfig) .

        --- rew msgAmpFactor(cAddr, addrNSintermediary, initConfig) .

        --- rew msgAmpFactor(cAddr ; addrNStargetANS ; addrNSintermediary ; addrNScom, rAddr, initConfig) .
        --- rew numActorMsgsRecvd(rAddr, initConfig) .

        --- rew msgAmpFactor(cAddr, addrNStargetANS ; addrNSintermediary ; addrNScom, initConfig) .
        --- rew msgAmpFactor(cAddr, addrNSintermediary, initConfig) .
        '''

        self.victim = "nameserver"
        self.name_attack = "iDNS attack variant3"


class SubqueriesUnchainedCNAME(ModelAttackFile):

    def __init__(self):
        SubqueriesCCV.__init__(self)
        self.folder = "sub-unchained-cname"

        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries-Unchained or Paralle NS + Unchained using CNAME chains. It consists
--- of an attacker client query to a resolver which will trigger multiple NS
--- delegations at a victim nameserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long CNAME chain between the nameserver and
--- the resolver. CNAME scrubbing is NOT used here
--- Attacker: client ; Victim : nameserver
        '''

        self.imports = '''load {PATH_TO_MAIN_DIR}/src/probabilistic-model/dns
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/sampler
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/properties
        '''

        self.start_text = '''
mod TEST is
  inc SAMPLER + APMAUDE + DNS + PROPERTIES .

  eq rsvTimeout? = false .
  eq rsvTimeout = 1000.0 .

 {}
         '''

        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  op q : -> Query .
  eq q = query(1, 'del . 'intermediary . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
'''

        self.target_text = '''
  eq zoneTargetANS =
    --- authoritative data
    < 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >

    {}
    .
'''

        self.intermediary_text = '''
  eq zoneIntermediary =
    --- authoritative data
    < 'intermediary . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >

    {}
    .
'''
        self.end_text = '''

  op initConfig : -> Config .
  eq initConfig = run(initState, limit) .

  eq initState = { 0.0 | nil }
    --- Preliminaries
    initMonitor(mAddr)
    [id, to cAddr : start, 0]

    < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
    < rAddr : Resolver | cache: cache,
                         nxdomainCache: nilNxdomainCache,
                         nodataCache: nilNodataCache,
                         sbelt: sb,
                         workBudget: emptyIN,
                         blockedQueries: eptQSS,
                         sentQueries: eptQSS >

    --- Root name server
    < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
    --- .com authoritative name server
    < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
    --- attacker authoritative name server
    < addrNStargetANS : Nameserver | db: zoneTargetANS, queue: nilQueue >
    --- intermediary.com authoritative name server
    < addrNSintermediary : Nameserver | db: zoneIntermediary, queue: nilQueue > .

endm

--- uncomment for debugging purposes
--- set trace on .

set trace condition off . --- This does not seem to work
set trace whole off .
set trace substitution off .
set trace mb off .
set trace eq off .
set trace rl on . --- on
set trace select off .
set trace rewrite off .
set trace body off .
set trace builtin off .
'''

        self.print_text = '''
rew initConfig .
rew numActorMsgsRecvd(addrNStargetANS, initConfig) .
        '''

        self.victim = "nameserver"
        self.name_attack = "Subqueries+Unchained"

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, cname_chain_in_target, ns_records_text_in_intermediary, cname_chain_intermediary) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(cname_chain_in_target)
        whole += self.intermediary_text.format(ns_records_text_in_intermediary + "\n" + cname_chain_intermediary)
        whole += self.end_text + self.print_text

        return whole


class UnchainedCNAME(SubqueriesUnchainedCNAME):
    # Need to change the query, it must be directly to target
    def __init__(self):
        SubqueriesUnchainedCNAME.__init__(self)
        self.folder = "unchained-cname"
        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  op q : -> Query .
  eq q = query(1, 'a . 'target-ans . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
'''

        self.name_attack = "Unchained+CNAME"

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, cname_chain_in_target,  cname_chain_intermediary) -> str:

            whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
            whole += self.description

            whole += self.start_text.format(resolver_model.config_text())
            whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
            whole += self.continue_text
            whole += self.target_text.format(cname_chain_in_target)
            whole += self.intermediary_text.format(cname_chain_intermediary)
            whole += self.end_text + self.print_text

            return whole

class UnchainedCNAMEQMIN(SubqueriesUnchainedCNAME):
    # Need to change the query, it must be directly to target
    def __init__(self):
        SubqueriesUnchainedCNAME.__init__(self)
        self.folder = "unchained-cname-qmin"

        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  op q : -> Query .
  eq q = query(1, 'fake8 . 'fake7 . 'fake6 . 'fake5 . 'fake4 . 'fake3 . 'fake2 . 'fake1 . 'fake0 . 'a . 'target-ans . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
'''

        self.name_attack = "Unchained+CNAME+QMIN"

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, cname_chain_in_target,  cname_chain_intermediary) -> str:

            whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
            whole += self.description

            whole += self.start_text.format(resolver_model.config_text())
            whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
            whole += self.continue_text
            whole += self.target_text.format(cname_chain_in_target)
            whole += self.intermediary_text.format(cname_chain_intermediary)
            whole += self.end_text + self.print_text

            return whole




class SubqueriesCCV(ModelAttackFile):

    def __init__(self):
        ModelAttackFile.__init__(self)
        self.folder = "sub-ccv"

        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries+Cname chain validation attack. It consists
--- of an attacker client query to a resolver which will trigger multiple NS
--- delegations at a victim nameserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long CNAME chain between the nameserver and
--- the resolver. This is using the CNAME chain validation.
--- Attacker: client ; Victim : nameserver
        '''
        self.imports = '''load {PATH_TO_MAIN_DIR}/src/probabilistic-model/dns
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/sampler
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/properties
        '''

        self.start_text = '''
mod TEST is
  inc SAMPLER + APMAUDE + DNS + PROPERTIES .

  eq rsvTimeout? = false .
  eq rsvTimeout = 1000.0 .

 {}
         '''

        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  op q : -> Query .
  eq q = query(1, 'del . 'intermediary . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS > . --- glue
'''

        self.target_text = '''
  eq zoneTargetANS =
    --- authoritative data
    < 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >

    {} .
    '''

        self.intermediary_text = '''
  eq zoneIntermediary =
    --- authoritative data
    < 'intermediary . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >

    {}
    .
'''
        self.end_text = '''

  op initConfig : -> Config .
  eq initConfig = run(initState, limit) .

  eq initState = { 0.0 | nil }
    --- Preliminaries
    initMonitor(mAddr)
    [id, to cAddr : start, 0]

    < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
    < rAddr : Resolver | cache: cache,
                         nxdomainCache: nilNxdomainCache,
                         nodataCache: nilNodataCache,
                         sbelt: sb,
                         workBudget: emptyIN,
                         blockedQueries: eptQSS,
                         sentQueries: eptQSS >

    --- Root name server
    < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
    --- .com authoritative name server
    < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
    --- attacker authoritative name server
    < addrNStargetANS : Nameserver | db: zoneTargetANS, queue: nilQueue >
    --- intermediary.com authoritative name server
    < addrNSintermediary : Nameserver | db: zoneIntermediary, queue: nilQueue > .

endm

--- uncomment for debugging purposes
--- set trace on .

set trace condition off . --- This does not seem to work
set trace whole off .
set trace substitution off .
set trace mb off .
set trace eq off .
set trace rl on . --- on
set trace select off .
set trace rewrite off .
set trace body off .
set trace builtin off .
'''

        self.print_text = '''
rew initConfig .
rew numActorMsgsRecvd(addrNStargetANS, initConfig) .
---rew msgAmpFactor(cAddr, addrNStargetANS, initConfig) .
--- rew msgAmpFactor(cAddr ; addrNSattacker, rAddr, initConfig) .
--- rew numActorMsgsRecvdTerminal(rAddr, initConfig) .
--- rew numActorMsgsSentTerminal(cAddr ; addrNSattacker, initConfig) .
---rew msgAmpFactorTerminal(cAddr, rAddr, initConfig) .

--- rew msgAmpFactor(cAddr, rAddr, initConfig) .
--- rew msgAmpFactor(cAddr, addrNStargetANS, initConfig) .

--- rew numActorMsgsRecvd(rAddr, initConfig) .
        '''

        self.victim = "nameserver"
        self.name_attack = "Subqueries+CNAME+Scrubbing"

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, target_records, ns_records_text_in_intermediary) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(target_records)
        whole += self.intermediary_text.format(ns_records_text_in_intermediary)
        whole += self.end_text + self.print_text

        return whole

class CCV(SubqueriesCCV):
    def __init__(self):
        SubqueriesCCV.__init__(self)
        self.folder = "ccv"

        self.name = "CNAME+Scrubbing"
        self.continue_text = '''

      op testTTL : -> Float .
      eq testTTL = 3600.0 .

      --- op q : -> Query .
      --- eq q = query(1, 'a . 'target-ans . 'com . root, a) .


      ops mAddr cAddr rAddr : -> Address .

      --- "SBELT": fallback if there are no known name servers
      op sb : -> ZoneState .
      eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

      ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

      op cache : -> Cache .
      eq cache =
        cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
        cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
        cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
        cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


      ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

      eq zoneRoot =
        --- authoritative data
        < root, soa, testTTL, soaData(testTTL) > --- dummy value
        < root, ns, testTTL, 'a . 'root-servers . 'net . root >

        --- non-authoritative data
        < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
        < 'com . root, ns, testTTL, 'ns . 'com . root >
        < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

      eq zoneCom =
        --- authoritative data
        < 'com . root, soa, testTTL, soaData(testTTL) >
        < 'com . root, ns, testTTL, 'ns . 'com . 'root >
        < 'ns . 'com . root, a, testTTL, addrNScom >

        --- non-authoritative data
        < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
        < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS > . --- glue
    '''
    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, query_from_client, cname_chain_in_target) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(resolver_model.config_text()+ "\n\t\t" + query_from_client + "\n")
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(cname_chain_in_target)
        whole += self.end_text + self.print_text

        return whole

class CCV_QMIN(SubqueriesCCV):
    def __init__(self):
        SubqueriesCCV.__init__(self)
        self.folder = "ccv-qmin"
        self.name = "CNAME+Scrubbing+QMIN"
        self.name_attack = "CNAME+Scrubbing+QMIN"
        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  --- op q : -> Query .
  ---eq q = query(1, 'fake8 . 'fake7 . 'fake6 . 'fake5 . 'fake4 . 'fake3 . 'fake2 . 'fake1 . 'fake0 . 'a . 'target-ans . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS > . --- glue
'''

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED,query_from_client, cname_chain_in_target) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(resolver_model.config_text()+ "\n\t\t" + query_from_client + "\n")
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(cname_chain_in_target)
        whole += self.end_text + self.print_text

        return whole

class SubqueriesCCV_Delay(SubqueriesCCV):
    def __init__(self):
        SubqueriesCCV.__init__(self)
        self.folder = "sub-ccv-delay"

        self.imports += '''
load {PATH_TO_MAIN_DIR}/attacker-models/probabilistic-model/attacker
load {PATH_TO_MAIN_DIR}/test/probabilistic-model/test_helpers'''


        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries+Cname chain validation +delay (slow) attack. It consists
--- of attacker client which queries the first element of each Cname chains contained into then
--- target namwserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long CNAME chain between the nameserver and
--- the resolver. This is using the CNAME chain validation.
--- Attacker: client ; Victim : nameserver
        '''

        self.start_text = '''\n
mod TEST is
  inc SAMPLER + APMAUDE + DNS + PROPERTIES + ATTACKER + TEST-HELPERS .


  ---eq configTsuNAMEslistCircDep = true .
  --- eq rsvTimeout? = true .
  --- eq rsvTimeout = 100.0 .
  ---eq dropMsgsForNXActors? = true .
  ---eq rsvTimeout? = false .
  ---eq rsvTimeout = 1000.0 .

  --- nameserver delay
  op testNsDelay : -> Float .
  eq testNsDelay =  {}
                 '''

        self.continue_text = '''
    op testTTL : -> Float .
    eq testTTL = 36000.0 .

    ops mAddr cAddr rAddr : -> Address .

    --- "SBELT": fallback if there are no known name servers
    op sb : -> ZoneState .
    eq sb = < root ('a  . 'root-servers . 'net . root |-> addrRoot) > .

    ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

    op cache : -> Cache .
    eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


    ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

    eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

    eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
        '''

        self.target_text = '''
    eq zoneTargetANS =
    --- authoritative data
    < 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >

    {}
    .
        '''

        self.intermediary_text = '''
    eq zoneIntermediary =
    --- authoritative data
    < 'intermediary . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >

    {}
    .
        '''
        self.end_text = r'''
  op initConfig : -> Config .
  eq initConfig = run(initState, limit) .

  eq initState = { 0.0 | nil }
    --- Preliminaries
    initMonitor(mAddr)
    [id, to cAddr : start, 0]

    < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
    < rAddr : Resolver | cache: cache,
                         nxdomainCache: nilNxdomainCache,
                         nodataCache: nilNodataCache,
                         sbelt: sb,
                         workBudget: emptyIN,
                         blockedQueries: eptQSS,
                         sentQueries: eptQSS >

    --- Root name server
    < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
    --- .com authoritative name server
    < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
    --- target authoritative name server
    < addrNStargetANS : DelayedNameserver | db: zoneTargetANS, nsDelay: testNsDelay, queue: nilQueue >
    .
endm

--- uncomment for debugging purposes
--- set trace on .

set trace condition off . --- This does not seem to work
set trace whole off .
set trace substitution off .
set trace mb off .
set trace eq off .
set trace rl on . --- on
set trace select off .
set trace rewrite off .
set trace body off .
set trace builtin off .
                '''

        self.print_text = '''
    rew initConfig .
    rew avgQueryDuration(initConfig) .
    --- rew maxQueryDuration(initConfig) .
    --- rew numActorMsgsRecvd(addrNStargetANS, initConfig) .
                '''
        self.name_attack = "SlowDNS+CNAME+scrubbing"

        self.victim = "nameserver"

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, ns_delay, query_from_client, cname_chain_in_target) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(str(ns_delay) + ".0 . \n" + query_from_client + "\n" + resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(cname_chain_in_target)
        whole += self.end_text + self.print_text

        return whole


class CCV_Delay(SubqueriesCCV_Delay):

    def __init__(self):
        SubqueriesCCV_Delay.__init__(self)
        self.folder = "ccv-delay"
        self.name_attack ="CNAME+Scrubbing+Delay"


    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, ns_delay, query_from_client, cname_chain_in_target) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(str(ns_delay) + ".0 . \n" + query_from_client + "\n" + resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(cname_chain_in_target)
        whole += self.end_text + self.print_text

        return whole


class CCV_QMIN_Delay(SubqueriesCCV_Delay):

    def __init__(self):
        SubqueriesCCV_Delay.__init__(self)
        self.folder = "ccv-qmin-delay"
        self.name_attack = "slowDNS+CNAME+Scrubbing+QMIN"


    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, ns_delay, query_from_client, cname_chain_in_target) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(str(ns_delay) + ".0 . \n" + query_from_client + "\n" + resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(cname_chain_in_target)
        whole += self.end_text + self.print_text

        return whole


class SubqueriesCCVQMINA(SubqueriesCCV):

    def __init__(self):
        SubqueriesCCV.__init__(self)
        self.folder = "sub-ccv-qmin-a"

        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries + Cname chain validation + QMIN attack. It consists
--- of an attacker client query to a resolver which will trigger multiple NS
--- delegations at a victim nameserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long CNAME chain between the nameserver and
--- the resolver. This is using the CNAME chain validation. Each CNAME answer contains
--- a long response (with many labels) which increases the number of queries by the resolver.
--- Attacker: client ; Victim : nameserver
        '''
        # self.imports same as parent
        # self.start_text same as parent
        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  op q : -> Query .
  eq q = query(1, 'del . 'intermediary . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
'''

        self.target_text = '''
  eq zoneTargetANS =
    --- authoritative data
    < 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >

    {}
    .
'''

        self.intermediary_text = '''
  eq zoneIntermediary =
    --- authoritative data
    < 'intermediary . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >

    {}
    .
'''
        self.end_text = '''

  op initConfig : -> Config .
  eq initConfig = run(initState, limit) .

  eq initState = { 0.0 | nil }
    --- Preliminaries
    initMonitor(mAddr)
    [id, to cAddr : start, 0]

    < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
    < rAddr : Resolver | cache: cache,
                         nxdomainCache: nilNxdomainCache,
                         nodataCache: nilNodataCache,
                         sbelt: sb,
                         workBudget: emptyIN,
                         blockedQueries: eptQSS,
                         sentQueries: eptQSS >

    --- Root name server
    < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
    --- .com authoritative name server
    < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
    --- attacker authoritative name server
    < addrNStargetANS : Nameserver | db: zoneTargetANS, queue: nilQueue >
    --- intermediary.com authoritative name server
    < addrNSintermediary : Nameserver | db: zoneIntermediary, queue: nilQueue > .

endm

--- uncomment for debugging purposes
--- set trace on .

set trace condition off . --- This does not seem to work
set trace whole off .
set trace substitution off .
set trace mb off .
set trace eq off .
set trace rl on . --- on
set trace select off .
set trace rewrite off .
set trace body off .
set trace builtin off .
'''

        self.print_text = '''
rew initConfig .
rew numActorMsgsRecvd(addrNStargetANS, initConfig) .
---rew msgAmpFactor(cAddr, addrNStargetANS, initConfig) .
--- rew msgAmpFactor(cAddr ; addrNSattacker, rAddr, initConfig) .
--- rew numActorMsgsRecvdTerminal(rAddr, initConfig) .
--- rew numActorMsgsSentTerminal(cAddr ; addrNSattacker, initConfig) .
---rew msgAmpFactorTerminal(cAddr, rAddr, initConfig) .

--- rew msgAmpFactor(cAddr, rAddr, initConfig) .
--- rew msgAmpFactor(cAddr, addrNStargetANS, initConfig) .
        '''

        self.victim = "nameserver"
        self.name_attack = "Subqueries+Scrubbing+QMIN"


class SubqueriesUnchainedDNAME(ModelAttackFile):

    def __init__(self):
        ModelAttackFile.__init__(self)
        self.folder = "sub-unchained-dname"

        self.imports = '''load {PATH_TO_MAIN_DIR}/src/probabilistic-model/dns
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/sampler
load {PATH_TO_MAIN_DIR}/src/probabilistic-model/properties
        '''

        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries-Unchained using DNAME chains. It consists
--- of an attacker client query to a resolver which will trigger multiple NS
--- delegations at a victim nameserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long DNAME chain between the nameserver and
--- the resolver.
--- Attacker: client ; Victim : nameserver
        '''

        self.start_text = '''
mod TEST is
  inc SAMPLER + APMAUDE + DNS + PROPERTIES .

  eq rsvTimeout? = false .
  eq rsvTimeout = 1000.0 .

 {}
         '''

        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  op q : -> Query .
  eq q = query(1, 'del . 'intermediary . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
'''

        self.target_text = '''
  eq zoneTargetANS =
    --- authoritative data
    < 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >

    {}
    .
'''

        self.intermediary_text = '''
  eq zoneIntermediary =
    --- authoritative data
    < 'intermediary . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >

    {}
    .
'''
        self.end_text = '''

  op initConfig : -> Config .
  eq initConfig = run(initState, limit) .

  eq initState = { 0.0 | nil }
    --- Preliminaries
    initMonitor(mAddr)
    [id, to cAddr : start, 0]

    < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
    < rAddr : Resolver | cache: cache,
                         nxdomainCache: nilNxdomainCache,
                         nodataCache: nilNodataCache,
                         sbelt: sb,
                         workBudget: emptyIN,
                         blockedQueries: eptQSS,
                         sentQueries: eptQSS >

    --- Root name server
    < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
    --- .com authoritative name server
    < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
    --- attacker authoritative name server
    < addrNStargetANS : Nameserver | db: zoneTargetANS, queue: nilQueue >
    --- intermediary.com authoritative name server
    < addrNSintermediary : Nameserver | db: zoneIntermediary, queue: nilQueue > .

endm

--- uncomment for debugging purposes
--- set trace on .

set trace condition off . --- This does not seem to work
set trace whole off .
set trace substitution off .
set trace mb off .
set trace eq off .
set trace rl on . --- on
set trace select off .
set trace rewrite off .
set trace body off .
set trace builtin off .
'''

        self.print_text = '''
rew initConfig .
rew numActorMsgsRecvd(addrNStargetANS, initConfig) .
        '''

        self.victim = "nameserver"
        self.name_attack = "Subqueries+DNAME"

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, dname_chain_in_target, ns_records_text_in_intermediary, dname_intermediary) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(dname_chain_in_target)
        whole += self.intermediary_text.format(ns_records_text_in_intermediary + dname_intermediary)
        whole += self.end_text + self.print_text

        return whole


class SubqueriesDNAME_Chain_validation(SubqueriesUnchainedDNAME):

    # The only thing that changes here is that it's the resolver swhole
    # who set whether there is cname chain validation or not
    # The solution was to use another resolver without this feature
    def __init__(self):
        SubqueriesUnchainedDNAME.__init__(self)
        self.folder = "sub-dcv"

        self.name_attack = "Subqueries+DNAME+scrubbing"

        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries+Dname chain validation attack. It consists
--- of attacker client which queries the first element of each Dname chains contained into then
--- target nameserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long DNAME chain between the nameserver and
--- the resolver. This is using the DNAME chain validation.
--- Attacker: client ; Victim : nameserver
        '''

    def whole_file(self, PATH_TO_MAIN_DIR, resolver_model, QMIN_DEACTIVATED, dname_chain_in_target, ns_records_text_in_intermediary) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(dname_chain_in_target)
        whole += self.intermediary_text.format(ns_records_text_in_intermediary)
        whole += self.end_text + self.print_text

        return whole


class SubqueriesCCVQMINA_Delay(SubqueriesCCV_Delay):

    def __init__(self):
        SubqueriesCCV_Delay.__init__(self)
        self.folder = "sub-ccv-qmin-a-delay"

        self.name_attack = "SlowDNS+CNAME+Scrubbing+QMIN"


class SubqueriesDNAMEChainVal_Delay(SubqueriesDNAME_Chain_validation):

    def __init__(self):
        SubqueriesUnchainedDNAME.__init__(self)
        self.folder = "sub-dcv-delay"

        self.imports += '''load {PATH_TO_MAIN_DIR}/attacker-models/probabilistic-model/attacker'''

        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries+Dname chain validation +delay (slow) attack. It consists
--- of attacker client which queries the first element of each Dname chains contained into then
--- target nameserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long DNAME chain between the nameserver and
--- the resolver. This is using the DNAME chain validation. The target delays
--- each of its response by a certain delay -> increasing the total time the query
--- is 'alive'.
--- Attacker: client ; Victim : nameserver
        '''

        self.start_text = '''\n
mod TEST is
  inc SAMPLER + APMAUDE + DNS + PROPERTIES + ATTACKER .

  eq rsvTimeout? = false .
  eq rsvTimeout = 1000.0 .

  --- nameserver delay
  op testNsDelay : -> Float .
  eq testNsDelay =  {}
                 '''

        self.continue_text = '''

op testTTL : -> Float .
eq testTTL = 36000.0 .

op q : -> Query .
eq q = query(1, 'sub . 'a1 . 'target-ans . 'com . root , a) .

ops mAddr cAddr rAddr : -> Address .

--- "SBELT": fallback if there are no known name servers
op sb : -> ZoneState .
eq sb = < root ('a  . 'root-servers . 'net . root |-> addrRoot) > .

ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

op cache : -> Cache .
eq cache =
cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

eq zoneRoot =
--- authoritative data
< root, soa, testTTL, soaData(testTTL) > --- dummy value
< root, ns, testTTL, 'a . 'root-servers . 'net . root >

--- non-authoritative data
< 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
< 'com . root, ns, testTTL, 'ns . 'com . root >
< 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

eq zoneCom =
--- authoritative data
< 'com . root, soa, testTTL, soaData(testTTL) >
< 'com . root, ns, testTTL, 'ns . 'com . 'root >
< 'ns . 'com . root, a, testTTL, addrNScom >

--- non-authoritative data
< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
'''

        self.target_text = '''
eq zoneTargetANS =
--- authoritative data
< 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >

{}
.
'''

        self.intermediary_text = '''
eq zoneIntermediary =
--- authoritative data
< 'intermediary . 'com . root, soa, testTTL, soaData(testTTL) >
< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >

{}
.
'''
        self.end_text = r'''
  op initConfig : -> Config .
  eq initConfig = run(initState, limit) .

  eq initState = { 0.0 | nil }
    --- Preliminaries
    initMonitor(mAddr)
    [id, to cAddr : start, 0]

    < cAddr : Client | queries: q, resolver: rAddr, notifyDone: nullAddr >
    < rAddr : Resolver | cache: cache,
                         nxdomainCache: nilNxdomainCache,
                         nodataCache: nilNodataCache,
                         sbelt: sb,
                         workBudget: emptyIN,
                         blockedQueries: eptQSS,
                         sentQueries: eptQSS >

    --- Root name server
    < addrRoot : Nameserver | db: zoneRoot, queue: nilQueue >
    --- .com authoritative name server
    < addrNScom : Nameserver | db: zoneCom, queue: nilQueue >
    --- target authoritative name server
    < addrNStargetANS : DelayedNameserver | db: zoneTargetANS, nsDelay: testNsDelay, queue: nilQueue >
    --- intermediary.com authoritative name server
    < addrNSintermediary : Nameserver | db: zoneIntermediary, queue: nilQueue >
    .

endm

--- uncomment for debugging purposes
--- set trace on .

set trace condition off . --- This does not seem to work
set trace whole off .
set trace substitution off .
set trace mb off .
set trace eq off .
set trace rl on . --- on
set trace select off .
set trace rewrite off .
set trace body off .
set trace builtin off .
        '''

        self.print_text = '''
rew initConfig .
rew avgQueryDuration(initConfig) .
--- rew maxQueryDuration(initConfig) .
--- rew numActorMsgsRecvd(addrNStargetANS, initConfig) .
        '''
        self.name_attack = "SlowDNS+DNAME+scrubbing"

    def whole_file(self, PATH_TO_MAIN_DIR, ns_delay, resolver_model, QMIN_DEACTIVATED, dname_chain_in_target, ns_records_text_in_intermediary) -> str:

        whole = self.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR)
        whole += self.description

        whole += self.start_text.format(str(ns_delay) + ".0 . \n" + resolver_model.config_text())
        whole += qmin_text(QMIN_DEACTIVATED, resolver_model.qmin_limit)
        whole += self.continue_text
        whole += self.target_text.format(dname_chain_in_target)
        whole += self.intermediary_text.format(ns_records_text_in_intermediary)
        whole += self.end_text + self.print_text

        return whole


class SubqueriesDCVQMINA(SubqueriesCCVQMINA):

    def __init__(self):
        SubqueriesCCVQMINA.__init__(self)
        self.folder = "sub-dcv-qmin-a"

        self.description = '''
--- Created automatically with Python.
--- This file simulates the Subqueries + Dname chain validation + QMIN attack. It consists
--- of an attacker client query to a resolver which will trigger multiple NS
--- delegations at a victim nameserver. The attacker managed to install some records in
--- this victim nameserver, which trigger a long DNAME chain between the nameserver and
--- the resolver. This is using the DNAME chain validation. Each DNAME answer contains
--- a long response (with many labels) which increases the number of queries by the resolver.
--- Attacker: client ; Victim : nameserver
        '''
        
        # The only difference with the parent class is the query
        self.continue_text = '''

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  op q : -> Query .
  eq q = query(1, 'del . 'intermediary . 'com . root, a) .


  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNStargetANS addrNSintermediary : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >, 1)
    cacheEntry(< 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >, 1)
    cacheEntry(< 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary >, 1) .


  ops zoneRoot zoneCom zoneTargetANS zoneIntermediary : -> List{Record} .

  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >  --- glue
    < 'intermediary . 'com . root, ns, testTTL, 'ns . 'intermediary . 'com . root >
    < 'ns . 'intermediary . 'com . root, a, testTTL, addrNSintermediary > . --- glue
'''
        self.name_attack = "Subqueries+DNAME+Scrubbing+QMIN"
