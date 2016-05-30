# set project path
path.project = "/Users/EB/Google Drive/Projects/Programming/Breweries/"

# load source files
setwd(path.project)
source("src.R")

# setwd to output folder
setwd(paste(path.project, "csv", sep = ""))

# functions
grab.beerid <- function(brew.id){
    url <- sprintf("http://www.beeradvocate.com/beer/profile/%s/?view=beers&show=all",
                   brew.id)  

    html  <- try(grab(url), silent = TRUE)

    links <- xpathApply(html, path = "//a", xmlGetAttr, "href")
    links <- links[grep(paste("/beer/profile/", sep = ""), links)]
    links <- gsub(paste("/beer/profile/", brew.id, sep = ""), "", links)
    
    # Quick and dirty fix: if brewery id != first scraped id use workaround
    if(length(links) == 0){
        links <- xpathApply(html, path = "//a", xmlGetAttr, "href")
        links <- links[grep(paste("/beer/profile/", sep = ""), links)]
        links <- links[grep("[[:digit:]]/[[:digit:]]", links)]
        links <- gsub("/beer/profile/", "", links)
        links <- strsplit(links, "/")
        links <- sapply(links, "[[", 2)
    }

    ids <- as.numeric(unlist(gsub("[^0-9]", "", links)))
    ids <- unique(ids)
    ids <- ids[!is.na(ids)]

    return(ids)
}

# load brewery ids
breweries <- read.csv("breweries.csv")
breweries <- breweries$id

ids.l <- list()
for(i in 1:length(breweries)){
    ids.l[[i]] <- try(grab.beerid(breweries[i]))

    if(length(ids.l[[i]]) == 0){
        print("Ooops, something happened: try again in 5 seconds")
        Sys.sleep(5)
        ids.l[[i]] <- try(grab.beerid(breweries[i]))
    }

    Sys.sleep(1)
    print(i)
}

beers.m <- do.call(rbind, mapply(cbind, breweries, ids.l))

colnames(beers.m) <- c("brewery", "beer")
write.csv(beers.m, "beers.csv", row.names = FALSE)
