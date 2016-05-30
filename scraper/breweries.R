# set project path
path.project = "/Users/EB/Google Drive/Projects/Programming/Breweries/"

# load source files
setwd(path.project)
source("src.R")

# setwd to output folder
setwd(paste(path.project, "csv", sep = ""))

# functions

grab.id <- function(page.id, country){
    url <- sprintf("http://www.beeradvocate.com/place/list/?start=%s&c_id=%s&brewery=Y&sort=reviews",
                   page.id, country)  

    html  <- try(grab(url), silent = TRUE)
    links <- xpathApply(html, path = "//a", xmlGetAttr, "href")
    links <- links[grep("/profile/", links)]
    ids   <- as.numeric(unlist(gsub("[^0-9]", "", links)))
    return(ids)
}

# scrape top 100 US breweries
country <- "US"
i.range <- seq(0, 80, by = 20)
ids.l   <- list()

for(i in 1:length(i.range)){
    page.id    <- i.range[i]
    ids.l[[i]] <- try(grab.id(page.id, country))
    Sys.sleep(1)
}

ids = data.frame(ids = unique(unlist(ids.l)))
write.csv(ids, "breweries.csv", row.names = FALSE)
