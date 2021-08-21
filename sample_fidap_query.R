library(tidyverse)
library(fidap)

client_init <- fidap_cleint(api_key = read_lines("./config.txt"), source = 'bq')