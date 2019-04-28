# pogs

Police log visualization platform for UNCC.

## fetcher

Fetcher is a small script for downloading every log file listed on the [UNCC Police](https://police.uncc.edu/police-log) website.

### running

Run the following command from your Terminal or Command Prompt:

```
python3.7 ./fetcher/fetcher.py
```

This will create the `pdfs/` directory and write each log PDF inside that folder.

## scanner (unfinished)

Scanner reads each log file in `pdfs/`, extracts, parses, and cleans up the text, then stores the formatted data in a CSV file.
