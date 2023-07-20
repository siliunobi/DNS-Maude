# Toy Example

_Note: This may be out of date!_

Based on [NXNS paper](https://www.usenix.org/conference/usenixsecurity20/presentation/afek).

Assumptions:

- All participants start with an empty cache.

```mermaid
sequenceDiagram
    %% participant C as Client
    participant R as Resolver
    participant NSroot as Root NS<br/>(1.1.1.1)
    participant NScom as .com NS<br/>(2.2.2.2)
    participant NSnet as .net NS<br/>(3.3.3.3)
    participant NSms1 as ns1.msft.net NS<br/>(208.84.5.53)

    %% C->>+R: query(A, www.microsoft.com)
    note over R: from client: receive<br/>query(A, www.microsoft.com)

    R->>+NSroot: query(A, www.microsoft.com)
    NSroot->>-R: refer(auth: <br>{<NS com. ns.example.com>}, glue: {ns.example.com -> 2.2.2.2})

    R->>+NScom: query(A, ns.example.com)
    NScom->>-R: resolved(ns.example.com, ...)
    R->>+NScom: query(A, www.microsoft.com)
    NScom->>-R: refer(auth: {(microsoft.com., ns1.msft.net), ...}, glue: {})

    loop for all NS in auth, resolve them
        R->>+NSroot: query(A, .net)
        NSroot->>-R: resolved(.net, <A 3.3.3.3>)
        R->>+NSnet: query(A, ns1.msft.net)
        NSnet->>-R: resolved(ns1.msft.net, <A 208.84.5.53>)
        note over R: add to cache
    end

    note over R: pick random auth NS,<br/>in this case ns1.msft.net

    R->>+NSms1: query(A, microsoft.com)
    NSms1->>+R: resolved(www.microsoft.com, 13.77.161.179)
```

Based on this, we can derive the following flow chart:

```mermaid
flowchart TD
    Init[Query] --> R[Resolve];
    R --> Q1{Look up in cache};
    Q1 -- Direct hit --> End[Reply];
    Q1 -- Parent domain hit --> R;
    Q1 -- No hit --> Root[Forward to root];
```
