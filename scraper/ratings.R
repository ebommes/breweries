# set project path
path.project = "/Users/EB/Google Drive/Projects/Programming/Breweries/"

# load source files
setwd(path.project)
source("src.R")

# setwd to output folder
setwd(paste(path.project, "csv", sep = ""))

# functions
grab.rating <- function(html){
    nodes <- getNodeSet(html, "//div[@id='rating_fullview_content_2']")
    nodes <- lapply(nodes, function(x) xmlParse(saveXML(x)))
    nodes <- lapply(nodes, function(x) xpathApply(x, path = "//span[@class='muted']", xmlValue))

    rating <- strsplit(sapply(nodes, "[[", 1), "|", fixed = TRUE)
    rating <- as.data.frame(t(sapply(rating, function(x) gsub("[^0-9.]", "", x))))
    rating <- as.data.frame(sapply(rating, as.numeric))

    names(rating) <- c("look",  "smell",  "taste", "feel",  "overall")

    return(rating)
}

grab.text <- function(html){
    nodes <- getNodeSet(html, "//div[@id='rating_fullview_content_2']")
    nodes <- lapply(nodes, function(x) xmlParse(saveXML(x)))
    xpath <- "//div[@id='rating_fullview_content_2']/text()"
    nodes <- lapply(nodes, function(x) xpathApply(x, path = xpath, xmlValue))
    nodes <- lapply(nodes, unlist)
    nodes <- lapply(nodes, function(x) paste(x, collapse = " "))
    nodes <- unlist(nodes)

    # clean up a bit
    txt <- gsub("rDev", "", nodes)
    txt <- gsub("\302\240", "", txt, fixed = TRUE)
    txt <- gsub("  ", "", txt, fixed = TRUE)

    return(txt)
}

grab.style <- function(html){
    links <- xpathApply(html, "//a", xmlGetAttr, "href")
    links <- unique(links[grep("/beer/style", links)])
    style <- as.numeric(unlist(gsub("[^0-9]", "", links)))
    style <- style[!is.na(style)]
    return(style)
}


beers.df <- read.csv("beers.csv")

i = 1

url <- sprintf("http://www.beeradvocate.com/beer/profile/%s/%s/", beers.df$brewery[i], beers.df$beer[i])  

html <- try(grab(url), silent = TRUE)

# check if there are reviews
checkreview = xpathApply(html, "//h6", xmlValue)

if(length(grep("No Reviews", checkreview)) == 0){
    # rating
    rating <- grab.rating(html)

    # text
    txt <- grab.text(html)

    # style
    style <- grab.style(html)
}




