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

grab.review <- function(html, beers.df, sql.l,  i, j){
    url <- sprintf("http://www.beeradvocate.com/beer/profile/%s/%s/", 
                   beers.df$brewery[i], beers.df$beer[i]) 

    iter <- 0
    html <- try(grab(url), silent = TRUE)

    j <- 0

    maxp <- try(maxpage(html))
    # check if there are reviews
    checkreview = xpathApply(html, "//h6", xmlValue)

    while(j <= maxp){
        con <- dbConnect(MySQL(), host = sql.l$host, user = sql.l$user, 
                         password = sql.l$pwd, dbname = sql.l$db)

        if(j != 0){
            url <- paste(url, "?view=beer&sort=&start=", j, sep = "")
            html <- try(grab(url), silent = TRUE)
        }

        if(length(grep("No Reviews", checkreview)) == 0){
            # rating
            rating <- grab.rating(html)

            # text
            txt <- grab.text(html)

            # style: better would be extra table for beer info.
            style <- grab.style(html)

            res <- data.frame(review  = (j+1):(j+length(txt)), 
                  brewery = rep(beers.df$brewery[i], length(txt)),
                  beer    = rep(beers.df$beer[i], length(txt)),
                  rating, 
                  txt,
                  style = rep(style, length(txt)))

            dbWriteTable(con, value = res, name = "reviews", row.names = FALSE,
                         append = TRUE) 
            dbDisconnect(con)
        }



        j <- j + 25
        
        Sys.sleep(1)
    }

}

beers.df <- read.csv("beers.csv")

n <- length(beers.df$beer)
  
for(i in 1:n){
    print(i)
    grab.review(html, beers.df, sql.l,  i, j)
}
