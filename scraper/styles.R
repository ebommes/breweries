# set project path
path.project = "/Users/EB/breweries/"

# load source files
setwd(path.project)
source("src.R")

# setwd to output folder
setwd(paste(path.project, "csv", sep = ""))

url <- "http://www.beeradvocate.com/beer/style/"
html <- grab(url)

# select links
links <- xpathApply(html, "//a", xmlGetAttr, "href")
links.txt <- xpathApply(html, "//a", xmlValue)
links.txt <- unlist(links.txt[grep("/beer/style", links)])
links <- unlist(links[grep("/beer/style", links)]) 
style <- as.numeric(unlist(gsub("[^0-9]", "", links)))

# create dataframe
styles.df <- data.frame(style, desc = links.txt)

# clean up a bit
styles.df <- styles.df[!is.na(styles.df$style), ]
styles.df <- unique(styles.df)

# store results in sql database
con <- dbConnect(MySQL(), host = sql.l$host, user = sql.l$user, 
         password = sql.l$pwd, dbname = sql.l$db)

dbWriteTable(con, value = styles.df, name = "styles", row.names = FALSE,
             append = TRUE) 
dbDisconnect(con)
