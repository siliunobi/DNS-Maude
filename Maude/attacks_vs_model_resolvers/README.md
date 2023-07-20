# Description of the models

  To have a way to predict the results of the experiments, we have to model the resolver implementations in Maude, to be able to
  compare the predicted values and the actual values of real resolver implementations. Therefore, other than observing the
  amplification factor of the attack, we can also see whether there are any discrepancy between the model and the implementation.
  This could give us more hindsight on the reasons why a query resolution acts this way and allow use to detect strange behaviors.

# Concept

  The main point is that we will create with Python the Maude files that correspond to various systems, with client(s), nameservers and resolver.
  Those generated files will be located inside [create...../resolver_name/files]

  We will then execute the files which gives a summary of number of messages sent/received as well as the amplification between the attacker(s)
  and the victim(s). So far, we'll only keep the first value of the summary (the amplification factor) and add it in txt files located
  in [create..../resolver_name/results/measurements]. Depending on what the last parameter we'll loop one, we consider the others as fixed
  and make the amplification factor vary by this last parameter. The resulting factors will be combined in the file discussed above, with its
  name containing the 2 fixed variables.

  Then, after all this computation, we can run "create_plots..", which will look at the values created in one file and create a plot with the
  corresponding x-axis (the missing attribute in the name).
  Other "plots" files can be found : some combined the model and real values in plots. Others are used for the creation of specific plots


# How to run the Maude models of resolver implementations

  Example : in the file "create_sub_ccv_files.py", we have 3 main variables we can play with to tune the attacks : the number of NS delegations, the length of the CNAME chain (in case
    of CNAME chain vaidation enabled), and the number of labels (useful for QMIN attacks).

  The function 'main' typically uses the cname chain length as a variable, while the other parameters are fixed.

  To create the Maude file, we will use ranges for the 3 main variables so that we can create multiple files at once.

  Furthermore, we'll have to choose the resolver implementation through a list of supported implementations.
  This will set the base folder being the current folder where we run the create_sub_ccv_files.py with
  the name of the chosen resolver. This means all the files that will be created will be located under
  this parent folder.
  
  ----

One could for instance run the "run_commands" to trigger the simulation of the different attacks and resolvers.
Note that we can choose which resolvers and which attacks are being launched inside the files mentioned in the "run_commands" bash file.



# Model Resolvers available

  - BIND 9.18.4
  - Unbound 1.10.0
  - Unbound 1.16.0
  - PowerDNS 4.7.0

  Note : BIND doesn't follow CNAME chain in subqueries.

# Resolvers parameters

  Following the limits of depth of the resolvers previously collected, we can use the below values as parameters to tune the maude files.
  To make it easier, Implementation() is the parent class of the resolvers and we can create in a straightforward way other resolvers by
  defining a new Implementation object.

  Resolver              | BIND 9.18.4     | Unbound1_10_0   | Unbound1_16_0 | PowerDNS4_7_0
  CNAME chain length    | 17              | 12              | 9             | 12
  QMIN iterations       | 5               | 10              | 10            | 10
  Max subqueries(a+aaaa)| 5 + 5           | No limit        | 6 + 6         | 5 in total
  configWorkBudget      | 5000            | 5000            | 5000          | 100
