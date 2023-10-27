# Description of the models in Maude

  The formal framework allows to test the expected behaviour of DNS servers and actors that follow closely a specific set of RFCs.
  As a way to expand this testing to englobe "more realistic" behaviour of resolvers, we create Maude models of such resolvers with some of their known parameters.

  Therefore, in order to predict the results of the experiments, we need to model the resolver implementations in Maude. The resulting AFs are useful to help comparing the predicted values and the actual values of real resolver implementations (for instance generated via the testbed).
  
Thus, rather than solely observing the amplification factor of an attack, we can also detect whether there are any discrepancy between the model and the implementation.
  This could give us more hindsight on the reasons why a query resolution acts this way and allow use to identify strange patterns as well limits imposed by the resolvers themselves.

# Concept

  The main concept is that we will create with Python the Maude files that correspond to various systems, with client(s), nameservers and resolvers.
  Those generated files will be located inside `[create.../resolver_name/files]` folders, where `...` specifies the type of attack used.

  We will then execute those files in Maude. This process outputs each time a summary of the number of messages sent/received, as well as the amplification between the attacker(s)
  and the victim(s). So far, we will only keep the first value of the summary (the amplification factor) and add it in `txt` files located
  in `[create..../resolver_name/results/measurements]`. Depending on which last parameter (ns, cname, labels) we loop on, we consider the other ones as fixed
  and make the amplification factor vary by this very last parameter. The resulting factors will be combined in the file discussed above, with its
  name containing the 2 fixed variables for more clarity.

  Then, after all this computation, we can run `create_plots...`, which will look at the values created in the output files and create a plot with the
  corresponding x-axis (the missing attribute in the name).
  Other "plots" files can be found : some combined the model and real values in plots. Others are used for the creation of specific plots.


# How to run the Maude models of resolver implementations

  If one wants to execute the attack `Subqueries + CNAME Scrubbing`, the following command will execute the attack against all the model resolvers available:
```bash
python3 create_sub_ccv_files.py
```

  Example : in the file `create_sub_ccv_files.py`, we have 3 main variables we can play with to tune the attacks : the number of NS delegations, the length of the CNAME chain (in case
    of CNAME chain validation enabled), and the number of labels (useful for QMIN attacks).

  The function `main` typically uses the cname chain length as a variable, while the other parameters are fixed.

  To create the Maude file, we will use ranges for the 3 main variables so that we can create multiple files at once.

  Furthermore, the tested resolver will be chosen among a list of supported implementations (see below).
  This will set the base folder being the current folder where we run the `create_sub_ccv_files.py` with
  the name of the chosen resolver. This means all the files that will be created will be located under
  this parent folder.


One could for instance run the `run_commands` to trigger the simulation of the different attacks and resolvers.

Note that we can choose which resolvers and which attacks are being launched inside the files mentioned in the `run_commands` bash file.



# Model Resolvers available

  - BIND 9.18.4
  - Unbound 1.10.0
  - Unbound 1.16.0
  - PowerDNS 4.7.0

  Note : BIND doesn't follow CNAME chain in subqueries.

# Resolvers parameters

  Following the limits of depth of the resolvers previously collected, we can use the below values as parameters to tune the Maude files.
  To simplify the creation/import of a resolver (mostly its behaviour), `Implementation()` is the parent class of the resolvers which can be used in a straightforward way to model other resolvers by
  defining a new `Implementation` object with appropriate parameters.

| Resolver               | BIND 9.18.4 | Unbound 1.10.0 | Unbound 1.16.0 | PowerDNS 4.7.0 |
|------------------------|-------------|----------------|----------------|----------------|
| CNAME chain length     | 17          | 12             | 9              | 12             |
| QMIN iterations        | 5           | 10             | 10             | 10             |
| Max subqueries(a+aaaa) | 5 + 5       | No limit       | 6 + 6          | 5 in total     |
| configWorkBudget       | 5000        | 5000           | 5000           | 100            |
