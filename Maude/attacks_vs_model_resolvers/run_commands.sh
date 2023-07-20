
# Run the DNAME + Scrubbing files and the DNAME attack, then create the combined plots
python3 create_unchained_cname_files.py && python3 create_sub_dcv_files.py && python3 create_sub_dcv_qmin_files.py && python3 create_sub_dname_files.py && python3 create_sub_cname_files.py && python3 create_sub_ccv_qmin_files.py && python3 create_sub_ccv_files.py && python3 create_sub_cname_files.py 

# && python3 create_combined_plots.py

# To activate QMIN need to modify it in all those files
# For the delay attack need to specific the correct attack in ...cv_files.py
