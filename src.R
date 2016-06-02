options(stringsAsFactors = FALSE)

# set this to TRUE if you run code for first time (initialize schema and db)
init.db = TRUE

# Mysql 
source("sql-credentials.R")
# sql.l <- list(user = "user", pwd = "password",
#               db = "db name", host = "localhost")

# install and load packages
libraries <- c("RCurl", "XML", "RMySQL")
lapply(libraries, function(x) if (!(x %in% installed.packages())) {
    install.packages(x)
})
lapply(libraries, library, quietly = TRUE, character.only = TRUE)

# functions
grab <- function(url){
    html <- try(readLines(url, encoding = "UTF-8"), silent = TRUE)
    if("try-error" %in% class(html)){
        Sys.sleep(5)
        html <- try(readLines(url, encoding = "UTF-8"), silent = TRUE)
    }

    html <- htmlParse(html, encoding = "utf-8")
    return(html)
}

create.schema <- function(sql.l){
    con <- dbConnect(MySQL(), host = sql.l$host, user = sql.l$user,
                     password = sql.l$pwd)

    quer <- dbSendQuery(con, paste("create database ", sql.l$db, ";", sep = ""))
    dbClearResult(quer)
    dbDisconnect(con)

    # create review db
    con <- dbConnect(MySQL(), host = sql.l$host, user = sql.l$user,
                     password = sql.l$pwd, db = sql.l$db)

    qer <- "CREATE TABLE `reviews` (
             `review` int(11) NOT NULL,
             `brewery` bigint(20) NOT NULL,
             `beer` bigint(20) NOT NULL,
             `look` double DEFAULT NULL,
             `smell` double DEFAULT NULL,
             `taste` double DEFAULT NULL,
             `feel` double DEFAULT NULL,
             `overall` double DEFAULT NULL,
             `txt` text,
             `style` int(11) DEFAULT NULL,
             PRIMARY KEY (`review`,`brewery`,`beer`)
           ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"

    quer <- dbSendQuery(con, qer)
    dbClearResult(quer)
    dbDisconnect(con)
}

# Initialize schema, database
try(create.schema(sql.l), silent = TRUE)
