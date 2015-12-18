# dbus_parser

This tool will collect analytical data from a dbus log. 



## Example 
### Input
[dbus sample log](https://github.com/djmunro/dbus_parser/blob/master/sample_logs/dbus_sample1.log)

### Output 
| Signals: (Member=Emit) | Occurences | Path |
|------------------------|:----------:|-----:|
"POS_PositionInformation" | 2 | /com/foobar/service/Navigation;
"RT_NextDestinationInfo" | 1 | /com/foobar/service/Navigation;
"currentStationInfo" | 1 | /com/foobar/service/XMApp;
"favAllowed" | 1 | /com/foobar/service/XMFavorites;
"insideTemp" | 2 | /com/foobar/service/Climate;
"playTimeValue" | 1 | /com/foobar/service/Rse;
"tagContentTaggableInd" | 1 | /com/foobar/service/TaggingService;

| Methods: (Member=Invoke) | Occurrence | Sender | Destination |
|--------------------------|:----------:|:------:|------------:|
"JSON_GetProperties" | 1 | :1.11 | com.foobar.service.Navigation
"checkTag" | 1 | :1.26 | com.foobar.service.iPodTagger

| Services | Occurrence |
|----------|------------|
/com/foobar/service/Rse; | 1
/com/foobar/service/Climate; | 2
/com/foobar/service/XMApp; | 1
/com/foobar/service/TaggingService; | 1
/com/foobar/service/XMFavorites; | 1
/com/foobar/service/Navigation; | 4
/com/foobar/service/iPodTagger; | 1
    