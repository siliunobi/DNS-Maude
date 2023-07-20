# Notes on the DNS model

_Note: For a more structured presentation of the assumptions, see thesis report._

The model is compliant with the following RFCs (if not indicated otherwise below):
- RFC 1034/35 (Core spec)
- RFC 2181 (Data ranking)
- RFC 2308 (Negative caching, NXDOMAIN and NODATA only)
- RFC 4592 (Wildcards)
- RFC 6672 (DNAME)
- RFC 6604 (xNAME RCODE)
- RFC 8020 (NXDOMAIN)
- RFC 9156 (QNAME minimization)

## General setting
- We strictly separate the following actors:
  - Clients: send queries to a (single) recursive resolver
  - Recursive resolvers: resolve queries on behalf of clients, have a cache
    - In RFC 1034 terminology, this would be a "recursive name server".
  - Authoritative name servers: No recursive service, no cache.
- The model covers standard DNS. DNSSEC is _not_ covered.
- We do not consider forged responses (cache poisoning etc.)
  - The resolver does not perform any sanity checks on the responses (such as enforcing the bailiwick rules).
  - Resolvers and clients accept responses from any address (i.e., from any resolver or name server).

## Not modelled
- Retransmissions after timeouts
- Record classes such as `IN` or `CH` (essentially, we only model the `IN` class)
- Certain record types:
  - `HINFO` and `PTR` record types
  - `AAAA` record type (from a later RFC)
- Multi-homed name servers (name servers with multiple addresses): The SLIST can store only one address per name server
- "History" information in the SLIST data structure of a resolver (5.3.2)
- AA flag in responses: due to the strict separation of actors, it can always be inferred if a response is authoritative or not.
- Upward referrals (optional, if name server is not authoritative for any part of `QNAME`)
- Inverse queries (obsoleted in RFC 3425)
- Zone transfers, `AXFR` query type

## Further assumptions
- The `Additional` section is only used for glue records in referral responses. In all other cases, it is expected to be empty.
  - RFC 1034 vaguely states to "add other RRs which may be useful to the additional section" (Alg. 4.3.2, step 6).
- Name servers send a `REFUSED` response if they are not authoritative for the QNAME and also cannot provide a delegation. There are no upward referrals.
- Handling of `ANY` QTYPE: If the resolver has any records for the QNAME in cache, those are returned (no name servers are contacted). If there are no cached records, the query is sent to name servers.
- For resolver subqueries, we require an answer with credibility level 2 (same as for client queries) before acting upon the data.
  - In particular, this means that if the "answer" to a subquery is first received as glue, it will not yet be used.
  - This can be seen as somewhat inconsistent because if the address was provided from the beginning as glue (such that no subquery is created), then the resolver _does_ use data of the lowest credibility level.
- The resolver follows `CNAME`s in resolver subqueries.
  - I.e., if the resolver encounters a `NS` record where the value is an alias, the resolver still tries to resolve the address.
  - The RFCs state that `NS` records must not have an alias as their value (RFC 2181, 10.3).
  - However, the RFC 1034 also states that "by the robustness principle, domain software should not fail when presented with CNAME chains or loops; CNAME chains should be followed and CNAME loops signalled as an error."
- `CNAME`/`DNAME` loops:
  - Resolver detects loops and sends a SERVFAIL to the client.
  - Nameservers do not detect them (this is a local configuration error!)
    - Name server will enter an infinite loop if queried for any name that is part of the loop.
- SLIST initialization:
  - The resolver follows `CNAME`s in resolver subqueries (i.e., when resolving name server addresses).
    - However, the SLIST contains the names as they appear in `NS` records, not the canonical names of the name servers.
    - Note that the specification forbids `NS` records pointing to an alias, but also demands "fault-tolerance", so it is unclear what the correct behavior is.
  - SLIST initialization looks up name server names in the negative caches; if there is a hit, the name server is not added to the SLIST.
    - If this happens for _all_ name servers that were determined based on `NS` records, SBELT is used instead.
  - Detection of "circular dependencies" in SLIST:
    - RFC 1035, §7.2 states the following circular dependency condition:
      > no addresses are available for any of the name servers named in SLIST, and [...] the servers in the list are precisely those  which would normally be used to look up their own addresses
    - It further states that in this case, the resolver should restart the search at the next ancestor zone, or alternatively at the root. In the model, the search is restarted at the next ancestor zone.
    - Note that if _some_ addresses are available, and the second part of the condition holds, this would lead to non-termination because infinitely many subqueries are created! To prevent this in the model, we impose that the QNAME cannot appear in the SLIST _unless_ its address is known. In other words, if the SLIST is initialized for a QNAME that is actually a name server, and the address of that name server is unknown, that name server is removed from the SLIST.
    - If the config option `configTsuNAMEslistCircDep` is enabled, the SLIST initialization is also restarted at the ancestor zone if there is a circular delegation (cf. TsuNAME).
      - Note that the interaction with QNAME minimization in this case leads to slightly weird behavior, where the same minimized name is queried multiple times until the max QMIN iterations are exceeded.
- When the resolver receives a delegation for a query, it only re-initializes the SLIST for that query. It does not check whether the newly learned name servers could also be useful for other ongoing queries.
  - This is in line with the resolver algorithm in RFC 1034.
- When a resolver query is answered, it checks if that answer is useful to enhance (or remove names from) the SLISTs of _any_ `blockedQueries` and `sentQueries`, not just the one which led to the creation of that query.
  - This is unclear in the spec. In some sense, this is inconsistent with the previous point (where delegations are only used for the current query).
- Interpretation of the different cases in the resolver algorithm in RFC 1034:
  - The way they are stated, multiple cases can apply to the same response.
  - We disambiguate this as follows:
    - Case a (answer) applies when the data in the response answers the query _directly_, i.e., without any rewriting and without any cache lookups.
    - Case b (delegation) applies only for "pure" referral responses, i.e., the Answer section must be empty (no rewrite chain).
    - Case c (CNAME) applies when the Answer section starts with a CNAME (and the QTYPE doesn't match CNAME). The QNAME is rewritten based on this first CNAME, all data is inserted into cache, and then the _rewritten_ query is looked up in the cache. Note that this case applies even if the response "answers" the question, as long as it has a CNAME.
    - DNAMEs are handled similarly to CNAMEs.
- The resolver does not do any "micro-caching" (coalescing identical requests into one, or answering multiple client requests when an authoritative answer is received to one of them). (Term "micro-caching" is taken from the Unchained paper.)
- For the modelled 0-TTL semantics, see below under "Hints".
- Negative caching:
  - We only cache `NXDOMAIN` and `NODATA`, but not `SERVFAIL` or unreachability (the latter two are optional in the spec).
  - When we update one of these caches, we do not update the other caches. E.g., when a `NXDOMAIN` is received for a domain, any records at or below that name in the positive cache will remain valid until their TTL expires.
- QNAME minimization:
  - Step (5) in RFC 9156 is weird; we implement our own version of step (5) that only looks at the NODATA cache trying to infer further information on (the absence of) zone cuts.
- Wildcard `NS` records:
  - Name servers do not synthesize `NS` records from wildcard records _for delegation_, only when queried for `NS` type.
  - This is in line with the name server algorithm in RFC 1034.
- When the max domain length is exceeded after `DNAME` substitution, the resolver sends a `SERVFAIL` to the client.
  - Note that it does not return the `YXDOMAIN` RCODE that an authoritative name server would send in this case.


## Hints
### Resolver state
- Queries in the resolver can be in one of two states/queues:
  - `blockedQueries`: the query is currently blocked because there is no name server with known address; queries to resolve the unknown name server addresses have been sent out.
  - `sentQueries`: the query has been sent out to a name server and is awaiting a response.
- The per-query state of the resolver (`QueryState`) consists of:
  - original query (either the query received from the client, or the original subquery created by the resolver)
  - address where the original query came from (client or resolver)
  - SNAME: the name that is currently being queried; note that this may be a "minimized" version of the "full" SNAME due to QNAME minimization
  - query id: the id of the current query (note that this is different from the id in the original query)
  - QNAME minimization state: a tuple consisting of the "full" SNAME, the `MAX_MINIMISE_COUNT` and `MINIMISE_ONE_LAB` parameters, and a flag indicating whether QNAME minimization is done
  - partial Answer section: contains the `CNAME`/`DNAME` records that have been followed so far
  - SLIST: name servers suitable for this query and their addresses
- Work budget:
  - The work budget is a map from (client query) `Id`s to `Nat`s
  - Used to limit the number of queries sent as a result of a single client query. This means that whenever a query related to a certain client query is sent (e.g., the client query itself, after following referrals or rewrites, or an internally generated subquery to resolve a name server address), the work budget for that client query is decremented by 1.
  - If the work budget is zero, the client request is aborted and answered with `SERVFAIL`.

### Query ids
- Each query has a unique id (assuming each client query starts with a unique id).
  - Hierarchical ids are used for queries sent by the resolver. Ids are composed using `..`.
    - `init` indicates that the resolver received the client query and initialized the internal state for it.
    - `ref` indicates that a referral was followed.
    - `cn` indicates that the query was restarted due to `CNAME`/`DNAME` record(s).
    - `qm` inidates that the resolver made an extra iteration due to QNAME minimization.
    - A numerical component indicates a subquery to resolve an unknown name server address.
    - `nxt` indicates that another name server was tried for the same query (e.g., because a `REFUSED` reply was received)
  - Examples:
    - `1 .. init`: The `1` is the id of the original client query. Upon receipt, the resolver added `init` and relayed the client query to a name server.
    - `1 .. init .. 1 .. 1`: In addition to the above, the resolver created a subquery to resolve an unknown name server address. To resolve this subquery, it had to create another subquery (= this one).
    - `1 .. init .. 1 .. 2`: Same as above, but the second subquery of the subquery.
    - `1 .. init .. cn`: The name server contacted by the resolver responded with a `CNAME`. The resolver changed the `SNAME` to the canonical name and sent out a query (= this one) for that new `SNAME`.

### Time-to-Live (TTL)
- In the probabilistic model, expiration of cache records is modelled.
  - Expired records are removed on the fly in each rule application that looks at the cache. There is no "explicit" expiration in the form of self-addressed messages or the like.
- In the non-deterministic model, the only distinction made is between 0-TTL records (which are not cached), and non-zero-TTL records (which are cached forever).
  - This is conveniently modelled by fixing the global time at 0.0. This leads to the desired caching behavior for 0-TTL records.
- 0-TTL semantics of the model:
  - 0-TTL records can only be used by the current _step_ of the current query. Essentially, they are removed from cache at the "end" of a rule application.
  - The specification actually suggests that they should also be usable by later steps of the same query, i.e., they should be inserted into cache and the TTL compared to a start-of-query timestamp. However, it is unclear how it should then be prevented that _other_ concurrent queries also use this cache record (unless the 0-TTL records are cached along with information that they should only be used by a particular query; the spec does not contain any hints in that direction).
  - Note that this only matters when a query requires looking at the same 0-TTL record multiple times during resolution (e.g., before and after a query rewrite or referral).
- Note that the same TTL field of a record is interpreted in different ways, depending on the context:
  - In zone files and responses, the TTL is the _relative_ time-to-live (duration in time units until it expires).
  - In resolver caches, the TTL is the _absolute_ expiration time of the record.

## Understanding Resolution
The monitor in the final state contains a name server query log, i.e., a list of the queries received by name servers (if `monitorQueryLog?` is true). Similarly, there is a log of the responses received by clients. This allows to reconstruct the resolution process.
