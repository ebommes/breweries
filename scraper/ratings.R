# set project path
path.project = "/Users/EB/breweries/"

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
    # rating <- as.data.frame(t(sapply(rating, function(x) gsub("[^0-9.]", "", x))))
    rating <- sapply(rating, function(x) gsub("[^0-9.]", "", x))
    
    if(class(rating) != "matrix"){
        rating <- do.call(rbind, rating)
    }else{
        rating <- t(rating)
    }
    
    rating <- as.data.frame(rating)
    rating <- as.data.frame(sapply(rating, as.numeric))

    names(rating) <- c("look",  "smell",  "taste", "feel",  "overall")

    # Quick fix if there is no rating -> words usually > 5 = max rating -> remove values > 5
    rating[rating > 5] <- NA

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

maxpage <- function(html){
    links <- xpathApply(html, path = "//a", xmlGetAttr, "href")
    links <- unlist(links[grepl("&start=", links, fixed = TRUE) &
                          grepl("beer&sort", links, fixed = TRUE)])

    if(is.null(links)) return(1);

    links <- strsplit(links, "=")
    maxp  <- max(as.numeric(sapply(links, "[[", 4)))

    return(maxp)
}

beers.df <- read.csv("beers.csv")

i = 2

#url <- sprintf("http://www.beeradvocate.com/beer/profile/%s/%s/", beers.df$brewery[i], beers.df$beer[i])  

url <- "http://www.beeradvocate.com/beer/profile/28743/136936/"

maxp <- 1
iter <- 0
html <- try(grab(url), silent = TRUE)

j = 0
while(j <= maxp){
    if(j == 0) {
        maxp <- try(maxpage(html))
        # check if there are reviews
        checkreview = xpathApply(html, "//h6", xmlValue)
    }
    
    if(j != 0){
        url <- paste(url, "?view=beer&sort=&start=", j, sep = "")
        html <- try(grab(url), silent = TRUE)
    }

    if(length(grep("No Reviews", checkreview)) == 0){
        # rating
        rating <- grab.rating(html)

        # text
        txt <- grab.text(html)

        # style
        style <- grab.style(html)
    }

    j <- j + 25
    
    Sys.sleep(1)
    print(j)
}





