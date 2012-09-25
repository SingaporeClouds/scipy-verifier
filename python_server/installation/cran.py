
from rpy2.robjects import r

execute  = """# get names of installed packages
packs <- installed.packages()
exc <- names(packs[,'Package'])

# get available package names
av <- names(available.packages()[,1])

# create loooong string
ins <- av[!av %in% exc]
install.packages(ins,'/usr/lib/R/site-library/')
"""
r(execute)