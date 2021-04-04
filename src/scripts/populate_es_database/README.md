### The script reads the stocks dataset files and populates Elasticsearch index "stocks".

### Index "stock\_prices" is populated from stock\_prices.json dataset or using YahooFinancials library to get histroical price data for each ticker if dataset file is missing. 