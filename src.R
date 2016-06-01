options(stringsAsFactors = FALSE)

# install and load packages
libraries <- c("RCurl", "XML")
lapply(libraries, function(x) if (!(x %in% installed.packages())) {
    install.packages(x)
})
lapply(libraries, library, quietly = TRUE, character.only = TRUE)

# functions
grab <- function(url){
    html <- try(readLines(url, encoding = "UTF-8"), silent = TRUE)
    if("try-error" %in% class(html)) html <- "ERROR" ;

    html <- htmlParse(html, encoding = "utf-8")
    return(html)
}
